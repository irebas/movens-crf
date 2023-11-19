from datetime import datetime

import numpy as np
import pandas as pd

from sqlite import SQLite
from utils import calc_price, calc_price2, second_smallest, open_excel_file
from variables import DB_NAME, INPUTS, MEDIANS, PERC_DIFF


def insert_inputs():
    for file in INPUTS:
        df = pd.read_excel(file['file'], skiprows=file['skiprows'])
        SQLite(DB_NAME).create_table(df=df, table_name=file['file'].split('/')[1].replace('.xlsx', ''))


def calculate() -> pd.DataFrame:
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
                    price = calc_price(df.loc[r, 'CZ4B'])
                    calc_method = 'Wizerunek - cz4n_price'
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
                price = -1
                calc_method = 'Other role'
        df.loc[r, 'final_price'] = price
        df.loc[r, 'calc_method'] = calc_method

    return df


def save_csv(df: pd.DataFrame):
    df.to_csv('outputs/test.csv', index=False)


def save_and_open_xlsx(df: pd.DataFrame):
    df.to_excel('outputs/results.xlsx', index=False)
    open_excel_file('results.xlsx')


if __name__ == '__main__':
    t0 = datetime.now()
    df_results = calculate()
    save_csv(df_results)
    save_and_open_xlsx(df_results)
    print(datetime.now() - t0)
