from datetime import datetime

import numpy as np
import pandas as pd

from utils.sqlite import SQLite
from funcs import calc_price, calc_price2, calc_superkomp_price, second_smallest
from variables import DB_NAME, MEDIANS, PERC_DIFF, KOMP_COEFF, SUPER_KOMP_COEFF, ZONES_PARAMS, ZONES_A, ZONES_B
from utils.gcp import GoogleCloudStorage, BigQueryClient


class ModelModOne:

    def __init__(self, src: str):
        self.src = src
        if self.src == 'SQLite':
            self.df = SQLite(DB_NAME).run_sql_query_from_file('queries/queries_sqlite/first_view.sql')
            self.df6 = SQLite(DB_NAME).run_sql_query('SELECT * FROM input_final_grid')
            self.df_vol_zones_a = SQLite(DB_NAME).run_sql_query('SELECT * FROM vol_zones_a')
            self.df_vol_zones_b = SQLite(DB_NAME).run_sql_query('SELECT * FROM vol_zones_b')
        elif self.src == 'GCP':




    def calc_final_price(self):
        self.df['min_price'] = self.df[MEDIANS].min(axis=1)
        self.df['min_price_2'] = self.df[MEDIANS].apply(second_smallest, axis=1)
        self.df['avg_price'] = self.df[MEDIANS].mean(axis=1)
        self.df['median_price'] = self.df[MEDIANS].median(axis=1)
        self.df['final_min_price'] = np.where(self.df['min_price_2'] / self.df['min_price'] - 1 > PERC_DIFF,
                                              self.df['min_price_2'], self.df['min_price'])
        self.df['margin'] = pd.NA
        self.df['calc_method'] = pd.NA
        self.df['price_gross'] = pd.NA
        for r in range(len(self.df)):
            min_price = self.df.loc[r, 'final_min_price']
            final_role = self.df.loc[r, 'final_role']
            match final_role:
                case 'Super Wizerunek':
                    if not pd.isna(self.df.loc[r, 'min_price']):
                        price = calc_price(min_price)
                        calc_method = 'Super Wizerunek'
                    else:
                        price = 0
                        calc_method = f'{final_role} - no min price'
                case 'Wizerunek':
                    if not pd.isna(self.df.loc[r, 'min_price']):
                        if calc_price(min_price) < self.df.loc[r, 'CZ4B']:
                            price = calc_price2(self.df.loc[r, 'CZ4B'])
                            calc_method = 'Wizerunek - cz4b_price'
                        else:
                            price = calc_price(min_price)
                            calc_method = 'Wizerunek - min_price'
                    else:
                        price = 0
                        calc_method = f'{final_role} - no min price'
                case 'Gama' | 'Kompensacja' | 'Super Kompensacja':
                    d_cols = {'Gama': 'margin_gama', 'Kompensacja': 'margin_komp', 'Super Kompensacja': 'margin_super_komp'}
                    if not pd.isna(self.df.loc[r, 'median_price']):
                        if final_role == 'Gama':
                            price_gross = calc_price2(self.df.loc[r, 'avg_price'])
                        elif final_role == 'Kompensacja':
                            price_gross = calc_price2(self.df.loc[r, 'median_price'] * KOMP_COEFF)
                        elif final_role == 'Super Kompensacja':
                            price_gross = calc_price2(self.df.loc[r, 'median_price'] * SUPER_KOMP_COEFF)
                        else:
                            price_gross = 0
                        self.df.loc[r, 'price_gross'] = price_gross
                        price_net = price_gross / (1 + self.df.loc[r, 'VAT'])
                        margin = 0 if price_net == 0 else (price_net - self.df.loc[r, 'CZ3N']) / price_net
                        self.df.loc[r, 'margin'] = margin
                        if margin < self.df.loc[r, 'margin_min']:
                            price_tmp = self.df.loc[r, 'CZ3B'] / (1 - self.df.loc[r, 'margin_min'])
                            price = calc_price2(price_tmp)
                            calc_method = f'{final_role} - margin lower'
                        else:
                            price = price_gross
                            calc_method = f'{final_role} - margin higher'
                    else:
                        price_to_calc = self.df.loc[r, 'CZ3B'] / (1 - self.df.loc[r, d_cols[final_role]])
                        price = calc_price2(price_to_calc)
                        calc_method = f'{final_role} - no median price'
                case _:
                    price = 0
                    calc_method = final_role
            price = price if price > 0 else pd.NA
            self.df.loc[r, 'final_price'] = price
            self.df.loc[r, 'calc_method'] = calc_method

        print('final_price calculated')

    def calc_price_zone_1(self):
        self.df['final_price_idx'] = self.df['final_price'] / self.df['Indeks'] * 100
        self.df['role_group'] = ['G1' if x in ['Super Wizerunek', 'Wizerunek'] else 'G2' for x in self.df['final_role']]
        self.df['group_price_avg'] = self.df.groupby(['role_group', 'Synonim'])['final_price_idx'].transform('mean')
        self.df['price_zone_1a'] = self.df['group_price_avg'] * self.df['Indeks'] / 100
        self.df['price_zone_1a'] = [calc_price2(x) for x in self.df['price_zone_1a']]
        self.df['price_zone_1a'] = np.where(pd.isna(self.df['Synonim']), self.df['final_price'], self.df['price_zone_1a'])
        self.df['price_zone_1a'] = np.where(self.df['price_zone_1a'].fillna(0) == 0, self.df['final_price'],
                                            self.df['price_zone_1a'])
        self.df['price_zone_1a'] = np.where((self.df['price_zone_1a'] - self.df['CZ3B']) / self.df['price_zone_1a'] >= 0,
                                            self.df['price_zone_1a'], self.df['final_price'])

        print('price_zone_1a calculated')

    def calc_zones_prices(self):
        price_zones = ['price_zone_2a', 'price_zone_3a', 'price_zone_4a', 'price_zone_5a']
        self.df[price_zones] = pd.NA
        for r in range(len(self.df)):
            final_role = self.df.loc[r, 'final_role']
            l1 = self.df.loc[r, 'L1_name']
            price_zone_1 = self.df.loc[r, 'price_zone_1a'] if not pd.isna(self.df.loc[r, 'price_zone_1a']) else 0
            if final_role in ['Wizerunek', 'Gama', 'Kompensacja', 'Super Kompensacja']:
                price_zone_2 = calc_price2(ZONES_PARAMS[final_role]['zone_2'][l1] * price_zone_1)
                price_zone_3 = calc_price2(ZONES_PARAMS[final_role]['zone_3'][l1] * price_zone_1)
                price_zone_4 = calc_price2(ZONES_PARAMS[final_role]['zone_4'][l1] * price_zone_1)
                price_zone_5 = calc_price2(ZONES_PARAMS[final_role]['zone_5'][l1] * price_zone_1)
            elif final_role == 'Super Wizerunek':
                price_zone_2 = price_zone_1
                price_zone_3 = price_zone_1
                price_zone_4 = price_zone_1
                price_zone_5 = calc_superkomp_price(price_zone_1)
            else:
                price_zone_2 = 0
                price_zone_3 = 0
                price_zone_4 = 0
                price_zone_5 = 0

            self.df.loc[r, 'price_zone_2a'] = float(price_zone_2)
            self.df.loc[r, 'price_zone_3a'] = float(price_zone_3)
            self.df.loc[r, 'price_zone_4a'] = float(price_zone_4)
            self.df.loc[r, 'price_zone_5a'] = float(price_zone_5)

        print('price_zones calculated')

    def calc_plxb_prices(self):
        cols = ['price_zone_1a', 'price_zone_2a', 'price_zone_3a', 'price_zone_4a', 'price_zone_5a']
        self.df6 = pd.merge(left=self.df6[['product_id_plxb', 'brand_id', 'final_grid']],
                            right=self.df[['product_id'] + [col for col in cols]],
                            how='left', left_on='brand_id', right_on='product_id')
        for col in cols:
            self.df6[f'{col}_plxb'] = self.df6[col] * self.df6['final_grid']
            self.df6[f'{col}_plxb'] = [calc_price2(x) for x in self.df6[f'{col}_plxb']]
        self.df = pd.merge(left=self.df, right=self.df6[['product_id_plxb'] + [f'{col}_plxb' for col in cols]],
                           how='left', left_on='product_id', right_on='product_id_plxb')
        for col in cols:
            self.df[col] = np.where(self.df['final_role'] == 'PLxB', self.df[f'{col}_plxb'], self.df[col])
        self.df = self.df[[col for col in self.df.columns if '_plxb' not in col]]
        self.df['has_price_zone_1a'] = ['No' if pd.isna(x) or x == 0 else 'Yes' for x in self.df['price_zone_1a']]

        print('price_zones for plxb calculated')

    def calc_model_zones(self, zones: list, v: str):
        df_vol_zones = pd.DataFrame()
        if v == 'a':
            df_vol_zones = self.df_vol_zones_a
        elif v == 'b':
            df_vol_zones = self.df_vol_zones_b
        self.df = pd.merge(left=self.df, right=df_vol_zones, how='left', on='product_id')
        self.df[f'vol_all_zones_{v}'] = 0
        for zone in zones:
            self.df[f'vol_all_zones_{v}'] = self.df[f'vol_all_zones_{v}'] + self.df[f'vol_zone_{zone}{v}'].fillna(0)
            self.df[f'sales_zone_{zone}{v}'] = self.df[f'vol_zone_{zone}{v}'] * self.df[f'price_zone_{zone}{v}']
        self.df[f'sales_all_zones_{v}'] = 0
        for zone in zones:
            self.df[f'sales_all_zones_{v}'] = (self.df[f'sales_all_zones_{v}'] + self.df[f'sales_zone_{zone}{v}'].fillna(0))
            self.df[f'margin_zone_{zone}{v}'] = (self.df[f'price_zone_{zone}{v}'] -
                                                 self.df['CZ4B']) * self.df[f'vol_zone_{zone}{v}']
        self.df[f'margin_all_zones_{v}'] = 0
        for zone in zones:
            self.df[f'margin_all_zones_{v}'] = (self.df[f'margin_all_zones_{v}'] + self.df[f'margin_zone_{zone}{v}'].fillna(0))
        m_types = ['vol', 'sales', 'margin']
        all_cols = [f'{x}_zone_{y}{v}' for x in m_types for y in zones] + [f'{x}_all_zones_{v}' for x in m_types]
        if v == 'a':
            for col in all_cols:
                self.df[col] = np.where(self.df['has_price_zone_1a'] == 'Yes', self.df[col], np.nan)

        print(f'Model calculated for version {v}')

    def create_results(self):
        if self.src == 'SQLite':
            SQLite(DB_NAME).create_table(df=self.df, table_name='results')
            file_name = f"outputs/results_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
            self.df.to_csv(file_name, encoding='utf-8-sig')
            print(f'File saved')


t0 = datetime.now()
model_mod_one = ModelModOne('SQLite')
model_mod_one.calc_final_price()
model_mod_one.calc_price_zone_1()
model_mod_one.calc_zones_prices()
model_mod_one.calc_plxb_prices()
model_mod_one.calc_model_zones(zones=ZONES_A, v='a')
model_mod_one.calc_model_zones(zones=ZONES_B, v='b')
model_mod_one.create_results()
print(f'All model calculated in : {datetime.now() - t0}')
