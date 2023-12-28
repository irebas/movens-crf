from datetime import datetime
import pandas as pd
from utils.sqlite import SQLite
from utils.gcp import BigQueryClient
from variables import PROJECT_ROOT
from elast_vol_function import process_rows


SQLITE = SQLite('carrefour.db')
BQ = BigQueryClient()


def divide_into_parts(x: int, n: int):
    base_size = x // n
    remainder = x % n
    result = []
    start = 0

    for i in range(n):
        end = start + base_size
        if i < remainder:
            end += 1
        result.append((start, end))
        start = end

    return result


def calc_elast_vol_sqlite():
    t0 = datetime.now()
    df_vol = SQLITE.run_sql_query('SELECT * FROM input_volume')
    df_5a = SQLITE.run_sql_query('SELECT shop_id, price_zone, dept AS L1 FROM input_price_zone_a')
    df_5b = SQLITE.run_sql_query('SELECT shop_id, price_zone, dept AS L2 FROM input_price_zone_b')
    df_base = SQLITE.run_sql_query_from_file('queries/queries_sqlite/elast_base.sql')
    shops_5a = df_5a['shop_id'].unique().tolist()
    ranges = divide_into_parts(x=len(df_base), n=20)
    SQLITE.truncate_table('elast_vol')
    for rng in ranges:
        params = {'ranges': rng, 'df_t3': df_vol, 'df_5a': df_5a, 'df_5b': df_5b, 'df_base': df_base, 'shops_5a': shops_5a}
        t1 = datetime.now()
        process_rows(params=params, src='SQLite')
        print(f'{rng} done: {datetime.now() - t1}')
    print(f'Table elast_vol created in: {datetime.now() - t0}')


calc_elast_vol_sqlite()
