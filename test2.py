import pandas as pd
from multiprocessing import Pool
from sqlite import SQLite
from variables import DB_NAME, ZONES_A, ZONES_B, ELAST
import warnings
from datetime import datetime
from test import divide_into_parts


def prepare_dfs():
    df = SQLite(DB_NAME).run_sql_query('SELECT * FROM results')
    df_t3 = SQLite(DB_NAME).run_sql_query('SELECT * FROM table3')
    df_5a = SQLite(DB_NAME).run_sql_query('SELECT * FROM input5a')
    df_5b = SQLite(DB_NAME).run_sql_query('SELECT * FROM input5b')
    df_elast = pd.DataFrame(data=ELAST)
    shops_5a = df_5a['shop_id'].unique().tolist()
    df.rename(columns={'IDProduktu': 'product_id', 'L1_SECTOR_ID': 'L1', 'L2_DEPARTMENT_ID': 'L2',
                       'Final role': 'final_role'}, inplace=True)
    df_t3.rename(columns={'ID_Sklepu': 'shop_id', 'ID_Produktu': 'product_id'}, inplace=True)
    df_5a.rename(columns={'dept': 'L1'}, inplace=True)
    df_5b.rename(columns={'dept': 'L2'}, inplace=True)
    print(f'Step 1 done')

    # step 2 - stworzenie wszystkich par zone A oraz zone B
    cols_x = [f'price_zone_{x}a' for x in ZONES_A]
    cols_y = [f'price_zone_{x}b' for x in ZONES_B]
    new_cols = [f"{x.split('_')[-1]}_{y.split('_')[-1]}" for x in cols_x for y in cols_y]
    df_base = df[['product_id', 'L1', 'L2', 'final_role']]
    df = df[['product_id'] + cols_x + cols_y]
    print(f'Step 2 done')

    # step 3 - dodanie do df kolumn z parami cen i wyliczenie współczynnika zone A/zone B
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
        for col in new_cols:
            df[col] = df[f"price_zone_{col.split('_')[0]}"] / df[f"price_zone_{col.split('_')[1]}"] - 1
    print(f'Step 3 done')

    # step 4 - Zrobienie z tego formy tabelarycznej, odfiltrowanie nulli i dolozenie kolum z df_short i elastycznosci
    df = pd.melt(df[[col for col in df.columns if 'price_zone' not in col]], id_vars='product_id',
                 var_name='zones_pair',
                 value_name='value')
    df = df[~df['value'].isna()]
    df = pd.merge(left=df, right=df_base, how='inner', on='product_id')
    df = pd.merge(left=df, right=df_elast, how='left', on='final_role')
    print(f'Step 4 done')
    all_dfs = {'df': df, 'df_base': df_base, 'df_t3': df_t3, 'df_5a': df_5a, 'df_5b': df_5b, 'shops_5a': shops_5a}
    return all_dfs


def work_log(params):
    t0 = datetime.now()
    df_tmp_all = pd.DataFrame()
    rng_1 = params['ranges'][0]
    rng_2 = params['ranges'][1]
    df_t3 = params['all_dfs']['df_t3']
    df_base = params['all_dfs']['df_base']
    df_5a = params['all_dfs']['df_5a']
    df_5b = params['all_dfs']['df_5b']
    shops_5a = params['all_dfs']['shops_5a']
    print(f'Process for ranges: {rng_1}-{rng_2} started')
    for r in range(rng_1, rng_2):
        # najpierw sprawdzamy w których sklepach sprzedawano dany produkt (ale interesują nas tylko sklepy z 5a)
        df_t3_tmp = df_t3[df_t3['product_id'] == df_base.loc[r, 'product_id']]
        shops = df_t3.loc[df_t3['product_id'] == df_base.loc[r, 'product_id'], 'shop_id'].tolist()
        shops = [shop for shop in shops if shop in shops_5a]
        df_tmp = pd.DataFrame(data={'shop_id': shops})
        df_tmp['product_id'] = df_base.loc[r, 'product_id']
        df_tmp['L1'] = df_base.loc[r, 'L1']
        df_tmp['L2'] = df_base.loc[r, 'L2']
        # teraz sprawdzamy w których strefach cenowych są te sklepy dla poszczególnych L1 (5a) i L2 (5b)
        df_tmp = pd.merge(left=df_tmp, right=df_5a, how='left', on=['shop_id', 'L1'])
        df_tmp.rename(columns={'price_zone': 'zone_a'}, inplace=True)
        df_tmp = pd.merge(left=df_tmp, right=df_5b, how='left', on=['shop_id', 'L2'])
        df_tmp.rename(columns={'price_zone': 'zone_b'}, inplace=True)
        # df_tmp = df_tmp[~(df_tmp['zone_a'].isna() & df_tmp['zone_b'].isna())]
        df_tmp['zones_pair'] = [f'{str(int(x))}a_{str(int(y))}b' for x, y in zip(df_tmp['zone_a'], df_tmp['zone_b'])]
        # a teraz sprawdźmy jaki wolumen danego produktu został sprzedany w danym sklepie
        df_tmp = pd.merge(left=df_tmp, right=df_t3_tmp, how='inner', on=['product_id', 'shop_id'])
        df_group = df_tmp.groupby(['product_id', 'zones_pair'])['volume'].sum().reset_index()
        df_tmp_all = pd.concat([df_tmp_all, df_group])
        if r % 1000 == 0:
            print(f'r:{r}: {datetime.now() - t0}')
    print(f'Process for ranges: {rng_1}-{rng_2} done')


def pool_handler():
    p = Pool(8)
    all_dfs = prepare_dfs()
    x = int(len(all_dfs['df_base']))
    ranges = divide_into_parts(x, 16)
    params = tuple([{'ranges': x, 'all_dfs': all_dfs} for x in ranges])
    p.map(work_log, params)


if __name__ == '__main__':
    t0 = datetime.now()
    pool_handler()
    print(f'{datetime.now() - t0}')
