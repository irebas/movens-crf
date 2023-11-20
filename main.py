from datetime import datetime

import numpy as np
import pandas as pd

from sqlite import SQLite
from utils import calc_price, calc_price2, calc_superkomp_price, second_smallest, save_and_open_xlsx
from variables import DB_NAME, INPUTS, MEDIANS, PERC_DIFF, ZONES_PARAMS


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
                price = calc_price(min_price)
                calc_method = 'Super Wizerunek'
            case 'Wizerunek':
                if calc_price(min_price) < df.loc[r, 'CZ4B']:
                    price = calc_price2(df.loc[r, 'CZ4B'])
                    calc_method = 'Wizerunek - cz4b_price'
                else:
                    price = calc_price(min_price)
                    calc_method = 'Wizerunek - min_price'
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
                calc_method = 'Other role'
        price = price if price > 0 else pd.NA
        df.loc[r, 'final_price'] = price
        df.loc[r, 'calc_method'] = calc_method

    return df


def calc_price_zone_1(df: pd.DataFrame) -> pd.DataFrame:
    df['final_price_idx'] = df['final_price'] / df['Indeks'] * 100
    df['role_group'] = ['G1' if x in ['Super Wizerunek', 'Wizerunek'] else 'G2' for x in df['Final role']]
    df['group_price_avg'] = df.groupby(['role_group', 'Synonim'])['final_price_idx'].transform('mean')
    df['price_zone_1'] = df['group_price_avg'] * df['Indeks'] / 100
    df['price_zone_1'] = [calc_price2(x) for x in df['price_zone_1']]
    df['price_zone_1'] = np.where(pd.isna(df['Synonim']), df['final_price'], df['price_zone_1'])
    df['price_zone_1'] = np.where((df['price_zone_1'] - df['CZ3B']) / df['price_zone_1'] >= 0,
                                  df['price_zone_1'], df['final_price'])
    return df


def calc_zones_prices(df: pd.DataFrame) -> pd.DataFrame:
    price_zones = ['price_zone_2', 'price_zone_3', 'price_zone_4', 'price_zone_5']
    df[price_zones] = pd.NA
    for r in range(len(df)):
        final_role = df.loc[r, 'Final role']
        l1 = df.loc[r, 'L1_name']
        price_zone_1 = df.loc[r, 'price_zone_1']
        if final_role in ['Wizerunek', 'Gama', 'Kompensacja', 'Super Kompensacja']:
            price_zone_2 = calc_price2(ZONES_PARAMS[final_role]['zone_2'][l1] * price_zone_1)
            price_zone_3 = calc_price2(ZONES_PARAMS[final_role]['zone_3'][l1] * price_zone_1)
            price_zone_4 = calc_price2(ZONES_PARAMS[final_role]['zone_4'][l1] * price_zone_1)
            price_zone_5 = calc_price2(ZONES_PARAMS[final_role]['zone_5'][l1] * price_zone_1)
        elif final_role == 'Super Wizerunek':
            price_zone_2 = price_zone_1 if l1 in ['PDK', 'PFT', 'Bazar', 'Tekstylia'] else 0
            if l1 in ['PDK', 'PFT']:
                price_zone_3 = price_zone_1
                price_zone_4 = price_zone_1
                price_zone_5 = calc_superkomp_price(price_zone_1)
            elif l1 in ['Bazar', 'Tekstylia']:
                price_zone_3 = calc_superkomp_price(price_zone_1)
                price_zone_4 = 0
                price_zone_5 = 0
            else:
                price_zone_3 = 0
                price_zone_4 = 0
                price_zone_5 = 0
        else:
            price_zone_2 = 0
            price_zone_3 = 0
            price_zone_4 = 0
            price_zone_5 = 0

        df.loc[r, 'price_zone_2'] = price_zone_2
        df.loc[r, 'price_zone_3'] = price_zone_3
        df.loc[r, 'price_zone_4'] = price_zone_4
        df.loc[r, 'price_zone_5'] = price_zone_5

    return df


def main():
    df = calc_final_price()
    df = calc_price_zone_1(df)
    df = calc_zones_prices(df)
    save_and_open_xlsx(df)


if __name__ == '__main__':
    t0 = datetime.now()
    main()
    print(datetime.now() - t0)
