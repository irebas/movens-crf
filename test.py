from sqlite import SQLite
import pandas as pd

SQLITE = SQLite('carrefour.db')


def calc_ntile(df_group, col: str):
    df_group[f'{col}_score'] = pd.qcut(df_group[col], q=[0, 0.2, 0.4, 0.6, 0.8, 1], labels=False, duplicates='drop')
    return df_group


def assign_points():
    df = SQLITE.run_sql_query_from_file('queries/input_zero.sql')
    cols = ['sales_value_ly', 'unique_receipts_ly', 'avg_receipt_share_ly', 'shopping_frequency', 'sales_margin',
            'nb_of_shops_with_sales', 'promo_sales_share']
    for col in cols:
        df = df.groupby('L1_SECTOR_ID', group_keys=False).apply(func=calc_ntile, col=col)
    df['benchmark_list_score'] = [10 if x == 1 else 0 for x in df['benchmark_list']]
    df['avg_product_value_score'] = [0 if x <= 3 else 1 if x <= 10 else 2 if x <= 20 else 3 if x <= 40 else 5
                                     for x in df['avg_product_value']]
    cols_score = [f'{col}_score' for col in cols] + ['benchmark_list_score', 'avg_product_value_score']
    df['total_score'] = df[cols_score].sum(axis=1)

    df.to_csv('test.csv', sep=';', encoding='utf-8-sig')


assign_points()
