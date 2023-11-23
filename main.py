from datetime import datetime

import numpy as np
import pandas as pd

from sqlite import SQLite
from utils import calc_price, calc_price2, calc_superkomp_price, second_smallest, save_and_open_xlsx
from variables import DB_NAME, INPUTS, MEDIANS, PERC_DIFF, ZONES_PARAMS, ZONES_A, ZONES_B


def insert_inputs():
    for file in INPUTS:
        df = pd.read_excel(file['file'], skiprows=file['skiprows'])
        SQLite(DB_NAME).create_table(df=df, table_name=file['file'].split('/')[1].replace('.xlsx', ''))


def calc_final_price() -> pd.DataFrame:
    df = SQLite(DB_NAME).run_sql_query_from_file('queries/first_view.sql')
    df['min_price'] = df[MEDIANS].min(axis=1)
    df['min_price_2'] = df[MEDIANS].apply(second_smallest, axis=1)
    df['avg_price'] = df[MEDIANS].mean(axis=1)
    df['median_price'] = df[MEDIANS].median(axis=1)
    df['final_min_price'] = np.where(df['min_price_2'] / df['min_price'] - 1 > PERC_DIFF,
                                     df['min_price_2'], df['min_price'])
    df['margin'] = pd.NA
    df['calc_method'] = pd.NA
    df['price_gross'] = pd.NA
    for r in range(len(df)):
        min_price = df.loc[r, 'final_min_price']
        final_role = df.loc[r, 'Final role']
        match final_role:
            case 'Super Wizerunek':
                if not pd.isna(df.loc[r, 'min_price']):
                    price = calc_price(min_price)
                    calc_method = 'Super Wizerunek'
                else:
                    price = 0
                    calc_method = f'{final_role} - no min price'
            case 'Wizerunek':
                if not pd.isna(df.loc[r, 'min_price']):
                    if calc_price(min_price) < df.loc[r, 'CZ4B']:
                        price = calc_price2(df.loc[r, 'CZ4B'])
                        calc_method = 'Wizerunek - cz4b_price'
                    else:
                        price = calc_price(min_price)
                        calc_method = 'Wizerunek - min_price'
                else:
                    price = 0
                    calc_method = f'{final_role} - no min price'
            case 'Gama' | 'Kompensacja' | 'Super Kompensacja':
                d_cols = {'Gama': 'margin_gama', 'Kompensacja': 'margin_komp', 'Super Kompensacja': 'margin_super_komp'}
                if not pd.isna(df.loc[r, 'median_price']):
                    if final_role == 'Gama':
                        price_gross = calc_price2(df.loc[r, 'avg_price'])
                    elif final_role == 'Kompensacja':
                        price_gross = calc_price2(df.loc[r, 'median_price'] * 1.01)
                    elif final_role == 'Super Kompensacja':
                        price_gross = calc_price2(df.loc[r, 'median_price'] * 1.03)
                    else:
                        price_gross = 0
                    df.loc[r, 'price_gross'] = price_gross
                    price_net = price_gross / (1 + df.loc[r, 'VAT'])
                    margin = 0 if price_net == 0 else (price_net - df.loc[r, 'CZ3N']) / price_net
                    df.loc[r, 'margin'] = margin
                    if margin < df.loc[r, 'margin_min']:
                        price_tmp = df.loc[r, 'CZ3B'] / (1 - df.loc[r, 'margin_min'])
                        price = calc_price2(price_tmp)
                        calc_method = f'{final_role} - margin lower'
                    else:
                        price = price_gross
                        calc_method = f'{final_role} - margin higher'
                else:
                    price_to_calc = df.loc[r, 'CZ3B'] / (1 - df.loc[r, d_cols[final_role]])
                    price = calc_price2(price_to_calc)
                    calc_method = f'{final_role} - no median price'
            case _:
                price = 0
                calc_method = final_role
        price = price if price > 0 else pd.NA
        df.loc[r, 'final_price'] = price
        df.loc[r, 'calc_method'] = calc_method

    print('final_price calculated')
    return df


def calc_price_zone_1(df: pd.DataFrame) -> pd.DataFrame:
    df['final_price_idx'] = df['final_price'] / df['Indeks'] * 100
    df['role_group'] = ['G1' if x in ['Super Wizerunek', 'Wizerunek'] else 'G2' for x in df['Final role']]
    df['group_price_avg'] = df.groupby(['role_group', 'Synonim'])['final_price_idx'].transform('mean')
    df['price_zone_1a'] = df['group_price_avg'] * df['Indeks'] / 100
    df['price_zone_1a'] = [calc_price2(x) for x in df['price_zone_1a']]
    df['price_zone_1a'] = np.where(pd.isna(df['Synonim']), df['final_price'], df['price_zone_1a'])
    df['price_zone_1a'] = np.where((df['price_zone_1a'] - df['CZ3B']) / df['price_zone_1a'] >= 0,
                                   df['price_zone_1a'], df['final_price'])

    print('price_zone_1a calculated')
    return df


def calc_zones_prices(df: pd.DataFrame) -> pd.DataFrame:
    price_zones = ['price_zone_2a', 'price_zone_3a', 'price_zone_4a', 'price_zone_5a']
    df[price_zones] = pd.NA
    for r in range(len(df)):
        final_role = df.loc[r, 'Final role']
        l1 = df.loc[r, 'L1_name']
        price_zone_1 = df.loc[r, 'price_zone_1a']
        if final_role in ['Wizerunek', 'Gama', 'Kompensacja', 'Super Kompensacja']:
            price_zone_2 = calc_price2(ZONES_PARAMS[final_role]['zone_2'][l1] * price_zone_1)
            price_zone_3 = calc_price2(ZONES_PARAMS[final_role]['zone_3'][l1] * price_zone_1)
            price_zone_4 = calc_price2(ZONES_PARAMS[final_role]['zone_4'][l1] * price_zone_1)
            price_zone_5 = calc_price2(ZONES_PARAMS[final_role]['zone_5'][l1] * price_zone_1)
        elif final_role == 'Super Wizerunek':
            price_zone_2 = price_zone_1 if l1 in ['PDK', 'PFT', 'Bazar', 'Tekstylia'] else 0
            price_zone_3 = price_zone_1
            price_zone_4 = price_zone_1
            price_zone_5 = calc_superkomp_price(price_zone_1)
        else:
            price_zone_2 = 0
            price_zone_3 = 0
            price_zone_4 = 0
            price_zone_5 = 0

        df.loc[r, 'price_zone_2a'] = price_zone_2
        df.loc[r, 'price_zone_3a'] = price_zone_3
        df.loc[r, 'price_zone_4a'] = price_zone_4
        df.loc[r, 'price_zone_5a'] = price_zone_5

    print('price_zones calculated')
    return df


def calc_plxb_prices(df: pd.DataFrame):
    cols = ['price_zone_1a', 'price_zone_2a', 'price_zone_3a', 'price_zone_4a', 'price_zone_5a']
    df6 = SQLite(DB_NAME).run_sql_query('SELECT * FROM input6')
    df6 = pd.merge(left=df6[['IDProduktu_plxb', 'IDBrand', 'final_grid']],
                   right=df[['IDProduktu'] + [col for col in cols]],
                   how='left', left_on='IDBrand', right_on='IDProduktu')
    # for col in cols:
    #     df6[f'{col}_plxb'] = df6[col] * df6['final_grid']
    #     df6[f'{col}_plxb'] = [calc_price2(x) for x in df6[f'{col}_plxb']]
    df6 = df6.assign(**{f'{col}_plxb': df6[col] * df6['final_grid'] for col in cols})
    df6[cols] = df6[cols].apply(lambda x: x.map(calc_price2))
    df = pd.merge(left=df, right=df6[['IDProduktu_plxb'] + [f'{col}_plxb' for col in cols]], how='left',
                  left_on='IDProduktu', right_on='IDProduktu_plxb')
    for col in cols:
        df[col] = np.where(df['Final role'] == 'PLxB', df[f'{col}_plxb'], df[col])
    df = df[[col for col in df.columns if '_plxb' not in col]]

    print('price_zones for plxb calculated')
    return df


def calc_model_zones(df: pd.DataFrame, zones: list, v: str) -> pd.DataFrame:
    table_name = f'vol_zones_{v}'
    df_vol_zones = SQLite(DB_NAME).run_sql_query(f"""SELECT * FROM {table_name}""")
    df = pd.merge(left=df, right=df_vol_zones, how='left', on='IDProduktu')
    df[f'vol_all_zones_{v}'] = 0
    for zone in zones:
        df[f'vol_all_zones_{v}'] = df[f'vol_all_zones_{v}'] + df[f'vol_zone_{zone}{v}'].fillna(0)
        df[f'sales_zone_{zone}{v}'] = df[f'vol_zone_{zone}{v}'] * df[f'price_zone_{zone}{v}']
    df[f'sales_all_zones_{v}'] = 0
    for zone in zones:
        df[f'sales_all_zones_{v}'] = df[f'sales_all_zones_{v}'] + df[f'sales_zone_{zone}{v}'].fillna(0)
        df[f'margin_zone_{zone}{v}'] = (df[f'price_zone_{zone}{v}'] - df['CZ4B']) * df[f'vol_zone_{zone}{v}']
    df[f'margin_all_zones_{v}'] = 0
    for zone in zones:
        df[f'margin_all_zones_{v}'] = df[f'margin_all_zones_{v}'] + df[f'margin_zone_{zone}{v}'].fillna(0)

    print(f'Model calculated for version {v}')
    return df


def main():
    t0 = datetime.now()
    df = calc_final_price()
    df = calc_price_zone_1(df)
    df = calc_zones_prices(df)
    df = calc_plxb_prices(df)
    df = calc_model_zones(df, zones=ZONES_A, v='a')
    df = calc_model_zones(df, zones=ZONES_B, v='b')
    print(f'Model calculated in : {datetime.now() - t0}')
    save_and_open_xlsx(df)
    print(f'Done in: {datetime.now() - t0}')


if __name__ == '__main__':
    main()
