from sqlite import SQLite
import pandas as pd
from utils import calc_ntile

SQLITE = SQLite('carrefour.db')
PRODUCTS_NB = 50
FACTOR_SUPER_W = 5
FACTOR_W = 10

d_roles = {'Traffic': [0.025, 0.035, 0.54, 0.35, 0.05], 'Turnover': [0.02, 0.035, 0.535, 0.35, 0.06],
           'Basket': [0.01, 0.03, 0.48, 0.40, 0.08], 'Margin': [0.005, 0.035, 0.425, 0.435, 0.1]}

wages = {'sales_value_ly_score': 1, 'unique_receipts_ly_score': 1, 'avg_receipt_share_ly_score': 1,
         'shopping_frequency_score': 1, 'sales_margin_score': 1, 'nb_of_shops_with_sales_score': 1,
         'promo_sales_share_score': 1, 'benchmark_list_score': 1, 'avg_product_value_score': 1}


def assign_points() -> pd.DataFrame:
    df = SQLITE.run_sql_query_from_file('queries/input_zero.sql')
    cols = ['sales_value_ly', 'unique_receipts_ly', 'avg_receipt_share_ly', 'shopping_frequency', 'sales_margin',
            'nb_of_shops_with_sales', 'promo_sales_share']
    for col in cols:
        df = df.groupby('L1_SECTOR_ID', group_keys=False).apply(func=calc_ntile, col=col)
    df['benchmark_list_score'] = [4 if x == 1 else 0 for x in df['benchmark_list']]
    df['avg_product_value_score'] = [0 if x <= 3 else 1 if x <= 10 else 2 if x <= 20 else 3 if x <= 40 else 4
                                     for x in df['avg_product_value']]
    cols_score = [f'{col}_score' for col in cols] + ['benchmark_list_score', 'avg_product_value_score']
    for col in cols_score:
        df[col] = df[col] * wages[col]
    df['total_score'] = df[cols_score].sum(axis=1)
    return df


def assign_single_role(row):
    ranges = d_roles[row['category_role']]
    ratio = row['ratio']
    if ratio <= ranges[0]:
        role = 'Super Wizerunek'
    elif ratio <= sum(ranges[:2]):
        role = 'Wizerunek'
    elif ratio <= sum(ranges[:3]):
        role = 'Gama'
    elif ratio <= sum(ranges[:4]):
        role = 'Kompensacja'
    else:
        role = 'Super Kompensacja'

    if row['typology'] == 'PLxB':
        final_role = 'PLxB'
    elif row['typology'] in ['PLxOPP', 'NP']:
        final_role = 'Super Wizerunek'
    elif row['typology'] in ['Fixed Prices', 'In-out/ Seasonal', 'Out of project']:
        final_role = row['typology']
    elif role == 'Super Wizerunek' and row['avg_product_value'] < FACTOR_SUPER_W:
        final_role = 'Wizerunek'
    elif role == 'Wizerunek' and row['avg_product_value'] < FACTOR_W:
        final_role = 'Gama'
    else:
        final_role = role

    return role, final_role


def calc_lev_roles(lev: str, products_excl: list, df: pd.DataFrame):
    df = df[~df['product_id'].isin(products_excl)].reset_index(drop=True)
    if len(df) == 0:
        return None, None
    df['items_nb'] = df.groupby(lev)['total_score'].transform('count')
    df_filtered = df[df['items_nb'] >= PRODUCTS_NB].reset_index(drop=True)
    if len(df_filtered) >= PRODUCTS_NB:
        df = df_filtered
    df['rn'] = df.groupby(lev)['total_score'].rank(method='first', ascending=False)
    df['ratio'] = df['rn'] / df['items_nb']
    df['agg_level'] = lev
    df[['role', 'final_role']] = df.apply(func=assign_single_role, axis=1, result_type='expand')
    products_assigned = df['product_id'].tolist()

    return df, products_assigned


def get_final_df(df: pd.DataFrame) -> pd.DataFrame:
    df_l4, ids_ok_l4 = calc_lev_roles(lev='L4_name', products_excl=[], df=df)
    df_l3, ids_ok_l3 = calc_lev_roles(lev='L3_name', products_excl=ids_ok_l4, df=df)
    df_l2, ids_ok_l2 = calc_lev_roles(lev='L2_name', products_excl=ids_ok_l4 + ids_ok_l3, df=df)
    df_l1, ids_ok_l1 = calc_lev_roles(lev='L1_name', products_excl=ids_ok_l4 + ids_ok_l3 + ids_ok_l2, df=df)

    df_final = pd.concat([df_l4, df_l3, df_l2, df_l1], ignore_index=True)
    df_final = df_final.sort_values(by=['L1_SECTOR_ID', 'L2_DEPARTMENT_ID', 'L3_GROUP_ID',
                                        'L4_GROUP_SUB_ID', 'rn']).reset_index(drop=True)
    return df_final


def get_base_input():
    df = assign_points()
    df_final = get_final_df(df)
    df_final.to_csv('df_final.csv', sep=';', encoding='utf-8-sig', index=False)
    SQLITE.create_table(df=df_final, table_name='input1')


get_base_input()
# df = pd.read_excel('inputs/test.xlsx')
# df['shopping_frequency'] = df['shopping_frequency'].round(2)
# bin_edges = [0, 2, 4, 6, 8, 10]
# df['ntiles'] = pd.cut(df['shopping_frequency'], bins=bin_edges, labels=False)
# # df['ntiles'] = pd.qcut(df['shopping_frequency'], q=[0, 0.2, 0.4, 0.6, 0.8, 1], labels=False, duplicates='drop')
# df.to_csv('test.csv')
