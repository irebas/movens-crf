import math
import os

import numpy as np
import pandas as pd
import win32com.client as win32

from variables import PRICES_RANGES_1, PRICES_RANGES_2


def calc_price(x: float):
    if not pd.isna(x) and x > 0:
        x_rnd = math.floor(x * 10) / 10.0
        if x < PRICES_RANGES_1[0]:
            price = x - (x - x_rnd - 0.05) if round(x - x_rnd, 2) > 0.05 else x - (x - x_rnd + 0.01)
        elif PRICES_RANGES_1[1] - 0.01 > x >= PRICES_RANGES_1[0]:
            price = x_rnd - 0.01
        elif PRICES_RANGES_1[2] - 0.01 > x >= PRICES_RANGES_1[1]:
            price = math.floor(x) + 0.49 if round(x - math.floor(x), 2) > 0.5 else math.floor(x) - 0.01
        elif x >= PRICES_RANGES_1[2]:
            price = math.floor(x) - 0.01
        else:
            price = 0

        return round(price, 2)
    else:
        return 0


def calc_price2(x: float):
    if not pd.isna(x) and x > 0:
        x_rnd = math.floor(x * 10) / 10.0
        if x < PRICES_RANGES_2[0]:
            if round(x - x_rnd, 2) == 0.05:
                price = x + 0.04
            elif round(x - x_rnd, 2) == 0.09:
                price = x + 0.06
            elif round(x - x_rnd, 2) > 0.05:
                price = math.ceil(x * 10) / 10 - 0.01
            else:
                price = x_rnd + 0.05
        elif PRICES_RANGES_2[1] - 0.01 > x >= PRICES_RANGES_2[0]:
            if math.ceil(x * 10) / 10 - x == 0:
                price = x + 0.09
            else:
                price = math.ceil(x * 10) / 10 - 0.01
        elif PRICES_RANGES_2[2] - 0.01 > x >= PRICES_RANGES_2[1]:
            if round(x - math.floor(x), 2) in [0.49, 0.99]:
                price = x + 0.5
            else:
                price = math.ceil(x) - 0.01 if round(x - math.floor(x), 2) > 0.5 else math.floor(x) + 0.49
        elif PRICES_RANGES_2[3] - 0.01 > x >= PRICES_RANGES_2[2]:
            price = math.ceil(x) - 0.01
        elif x >= PRICES_RANGES_2[3]:
            if 10 * round((x - math.floor(x / 10) * 10), 2) in [49.9, 99.9]:
                price = x + 5
            elif x / 10 - math.floor(x / 10) > 0.5:
                price = math.floor(x / 10) * 10 + 9.99
            else:
                price = math.floor(x / 10) * 10 + 4.99
        else:
            price = 0

        return round(price, 2)
    else:
        return 0


def calc_superkomp_price(x: float):
    if not pd.isna(x) and x > 0:
        if x < PRICES_RANGES_2[0]:
            price = calc_price2(x + 0.05)
        elif PRICES_RANGES_2[2] - 0.01 > x >= PRICES_RANGES_2[0]:
            price = calc_price2(x + 0.49)
        elif PRICES_RANGES_2[3] - 0.01 > x >= PRICES_RANGES_2[2]:
            price = calc_price2(x + 0.99)
        elif x >= PRICES_RANGES_2[3]:
            price = calc_price2(x + 1.99)
        else:
            price = 0

        return price

    else:
        return 0


def second_smallest(row):
    values = [value for value in row if pd.notna(value)]
    return sorted(values)[1] if len(values) > 1 else np.nan


def open_excel_file(file_name: str):
    file_path = f'{os.getcwd()}\\outputs\\{file_name}'
    excel_app = win32.gencache.EnsureDispatch('Excel.Application')
    excel_app.Visible = True
    try:
        excel_app.Workbooks.Open(file_path)
    except Exception as e:
        print(f"Error: {e}")


def save_csv(df: pd.DataFrame):
    df.to_csv('outputs/test.csv', index=False)


def save_and_open_xlsx(df: pd.DataFrame):
    df.to_excel('outputs/results.xlsx', index=False)
    open_excel_file('results.xlsx')
