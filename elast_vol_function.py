import pandas as pd
from utils.sqlite import SQLite
from utils.gcp import BigQueryClient
from variables import PROJECT_ROOT

SQLITE = SQLite('carrefour.db')
BQ = BigQueryClient()


def process_rows(params: dict, src: str):
    df_tmp_all = pd.DataFrame()
    rng_1, rng_2, df_vol, df_base, shops_5a, df_5a, df_5b = (
        params['ranges'][0],
        params['ranges'][1],
        params['df_t3'],
        params['df_base'],
        params['shops_5a'],
        params['df_5a'],
        params['df_5b'],
    )
    print(f'Process for ranges: {rng_1}-{rng_2} started')

    for r in range(rng_1, rng_2):
        # najpierw sprawdzamy w których sklepach sprzedawano dany produkt (ale interesują nas tylko sklepy z 5a)
        df_t3_tmp = df_vol[df_vol['product_id'] == df_base.loc[r, 'product_id']]
        shops = df_vol.loc[df_vol['product_id'] == df_base.loc[r, 'product_id'], 'shop_id'].tolist()
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

    print(f'Process for ranges: {rng_1}-{rng_2} completed')
    if src == 'SQLite':
        SQLITE.append_table(df=df_tmp_all, table_name='elast_vol')
    elif src == 'GCP':
        BQ.load_table_from_df(df=df_tmp_all, table=f'{PROJECT_ROOT}elast_vol', disposition='WRITE_APPEND')

    return None
