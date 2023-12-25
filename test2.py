import pandas as pd

PRODUCTS_NB = 4
FACTOR_SUPER_W = 5
FACTOR_W = 10

d_roles = {'Traffic': [0.025, 0.035, 0.54, 0.35, 0.05], 'Turnover': [0.02, 0.035, 0.535, 0.35, 0.06],
           'Basket': [0.01, 0.03, 0.48, 0.40, 0.08], 'Margin': [0.005, 0.035, 0.425, 0.435, 0.1]}


def get_role(row):
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
    elif ratio <= sum(ranges[:5]):
        role = 'Super Kompensacja'
    else:
        role = 'NA'

    if role == 'Super Wizerunek' and row['avg_product_value'] < FACTOR_SUPER_W:
        role = 'Wizerunek'
    elif role == 'Wizerunek' and row['avg_product_value'] < FACTOR_W:
        role = 'Gama'

    return role


df = pd.DataFrame(data={'product_id': [x for x in range(22)],
                        'L1': [0] * 22,
                        'L2': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                        'L3': [3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6],
                        'L4': [7, 7, 7, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 13, 13, 13, 13, 13],
                        'category_role': ['Traffic'] * 22,
                        'val': [10, 15, 10, 20, 25, 35, 40, 30, 90, 5, 9, 12, 15, 11, 10, 16, 7, 4, 9, 1, 3, 3],
                        })


def calc_lev_roles(lev: str, products_excl: list, df: pd.DataFrame):
    df = df[~df['product_id'].isin(products_excl)].reset_index(drop=True)
    if len(df) == 0:
        return None, None
    df['items_nb'] = df.groupby(lev)['val'].transform('count')
    df_filtered = df[df['items_nb'] >= PRODUCTS_NB].reset_index(drop=True)
    if len(df_filtered) >= PRODUCTS_NB:
        df = df_filtered
    df['rn'] = df.groupby(lev)['val'].rank(method='first')
    df['ratio'] = df['rn'] / df['items_nb']
    df['role'] = df.apply(func=get_role, axis=1)
    products_assigned = df['product_id'].tolist()

    return df, products_assigned


df_L4, ids_ok_L4 = calc_lev_roles(lev='L4', products_excl=[], df=df)
df_L3, ids_ok_L3 = calc_lev_roles(lev='L3', products_excl=ids_ok_L4, df=df)
df_L2, ids_ok_L2 = calc_lev_roles(lev='L2', products_excl=ids_ok_L4 + ids_ok_L3, df=df)
df_L1, ids_ok_L1 = calc_lev_roles(lev='L1', products_excl=ids_ok_L4 + ids_ok_L3 + ids_ok_L2, df=df)

df_final = pd.concat([df_L4, df_L3, df_L2, df_L1], ignore_index=True)
df_final = df_final.sort_values(by='product_id').reset_index(drop=True)
print(df_final)
