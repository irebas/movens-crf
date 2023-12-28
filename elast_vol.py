from datetime import datetime
from multiprocessing import Pool

import pandas as pd

from utils.sqlite import SQLite
from funcs import divide_into_parts
from variables import DB_NAME


def work_log(params):
    df_tmp_all = pd.DataFrame()
    rng_1 = params['ranges'][0]
    rng_2 = params['ranges'][1]
    df_t3 = params['df_t3']
    df_base = params['df_base']
    print(f'Process for ranges: {rng_1}-{rng_2} started')
    for r in range(rng_1, rng_2):
        # najpierw sprawdzamy w których sklepach sprzedawano dany produkt (ale interesują nas tylko sklepy z 5a)
        df_t3_tmp = df_t3[df_t3['product_id'] == df_base.loc[r, 'product_id']]
        shops = df_t3.loc[df_t3['product_id'] == df_base.loc[r, 'product_id'], 'shop_id'].tolist()
        shops = [shop for shop in shops if shop in params['shops_5a']]
        df_tmp = pd.DataFrame(data={'shop_id': shops})
        df_tmp['product_id'] = df_base.loc[r, 'product_id']
        df_tmp['L1'] = df_base.loc[r, 'L1']
        df_tmp['L2'] = df_base.loc[r, 'L2']
        # teraz sprawdzamy w których strefach cenowych są te sklepy dla poszczególnych L1 (5a) i L2 (5b)
        df_tmp = pd.merge(left=df_tmp, right=params['df_5a'], how='left', on=['shop_id', 'L1'])
        df_tmp.rename(columns={'price_zone': 'zone_a'}, inplace=True)
        df_tmp = pd.merge(left=df_tmp, right=params['df_5b'], how='left', on=['shop_id', 'L2'])
        df_tmp.rename(columns={'price_zone': 'zone_b'}, inplace=True)
        # df_tmp = df_tmp[~(df_tmp['zone_a'].isna() & df_tmp['zone_b'].isna())]
        df_tmp['zones_pair'] = [f'{str(int(x))}a_{str(int(y))}b' for x, y in zip(df_tmp['zone_a'], df_tmp['zone_b'])]
        # sprawdzamy jaki wolumen danego produktu został sprzedany w danym sklepie i grupujemy po product_id, zones_pair
        df_tmp = pd.merge(left=df_tmp, right=df_t3_tmp, how='inner', on=['product_id', 'shop_id'])
        df_group = df_tmp.groupby(['product_id', 'zones_pair'])['volume'].sum().reset_index()
        df_tmp_all = pd.concat([df_tmp_all, df_group])
        print(r)
    print(f'Process for ranges: {rng_1}-{rng_2} done')
    return df_tmp_all


def pool_handler(params):
    with Pool(10) as p:
        results = p.map(work_log, params)
    df_all = pd.concat(results, ignore_index=True)
    return df_all


def calc_elast_vol():
    t0 = datetime.now()
    df_t3 = SQLite(DB_NAME).run_sql_query('SELECT * FROM input_volume')
    df_5a = SQLite(DB_NAME).run_sql_query('SELECT shop_id, price_zone, dept AS L1 FROM input_price_zone_a')
    df_5b = SQLite(DB_NAME).run_sql_query('SELECT shop_id, price_zone, dept AS L2 FROM input_price_zone_b')
    df_base = SQLite(DB_NAME).run_sql_query_from_file('queries/queries_sqlite/elast_base.sql')
    shops_5a = df_5a['shop_id'].unique().tolist()
    ranges = divide_into_parts(x=len(df_base), n=20)
    params = tuple([{'ranges': x, 'df_t3': df_t3, 'df_5a': df_5a, 'df_5b': df_5b,
                     'df_base': df_base, 'shops_5a': shops_5a} for x in ranges])

    if __name__ == '__main__':
        print('Data prepared - start multiprocessing...')
        df_elast_vol = pool_handler(params)
        SQLite(DB_NAME).create_table(df=df_elast_vol, table_name='elast_vol')
        print(f'Table elast_vol created in: {datetime.now() - t0}')


calc_elast_vol()
