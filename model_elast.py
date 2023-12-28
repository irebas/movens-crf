import warnings
from datetime import datetime

import numpy as np
import pandas as pd

from utils.sqlite import SQLite
from variables import PROJECT_ROOT
from variables import ELAST, ZONES_A, ZONES_B
from utils.gcp import GoogleCloudStorage, BigQueryClient

SQLITE = SQLite('carrefour.db')
BQ = BigQueryClient()
GCS = GoogleCloudStorage()


class ModelElast:

    def __init__(self, src: str):
        self.src = src
        if self.src == 'SQLite':
            self.df = SQLITE.run_sql_query('SELECT * FROM results')
            self.df_elast_vol = SQLITE.run_sql_query('SELECT * FROM elast_vol')
        elif self.src == 'GCP':
            with open(f'queries/queries_bq/results.sql', 'r') as file:
                query_str = file.read()
            self.df = BQ.run_query(query_str)
            with open(f'queries/queries_bq/elast_vol.sql', 'r') as file:
                query_str = file.read()
            self.df_elast_vol = BQ.run_query(query_str)
        self.df_results = pd.DataFrame()

    def calc_elasticity(self):
        # step 1 - pobranie tabel z bazy danych - results, elast_vol i parametrów elastycznosci z variables test_id =1422281
        self.df.rename(columns={'L1_SECTOR_ID': 'L1', 'L2_DEPARTMENT_ID': 'L2'}, inplace=True)
        self.df_results = self.df.copy()
        df = self.df[self.df['has_price_zone_1a'] == 'Yes']
        df_elast = pd.DataFrame(data=ELAST)
        # step 2 - stworzenie wszystkich par zone A oraz zone B
        cols_x = [f'price_zone_{x}a' for x in ZONES_A]
        cols_y = [f'price_zone_{x}b' for x in ZONES_B]
        new_cols = [f"{x.split('_')[-1]}_{y.split('_')[-1]}" for x in cols_x for y in cols_y]
        df_base = df[['product_id', 'L1', 'L2', 'final_role']]
        df_prices = pd.melt(df[['product_id'] + cols_x], id_vars='product_id', var_name='zone_a', value_name='price_zone_a')
        df_prices = df_prices[~df_prices['price_zone_a'].isna()]
        df_prices = pd.merge(left=df_prices, right=df[['product_id', 'CZ4B']], how='left', on='product_id')
        df = df[['product_id'] + cols_x + cols_y]
        # step 3 - dodanie do df kolumn z parami cen i wyliczenie współczynnika zone A/zone B
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
            for col in new_cols:
                df[col] = df[f"price_zone_{col.split('_')[0]}"] / df[f"price_zone_{col.split('_')[1]}"] - 1
        # step 4 - Zrobienie z tego formy tabelarycznej, odfiltrowanie nulli i dolozenie kolum z df_base i elastycznosci
        df = pd.melt(df[[col for col in df.columns if 'price_zone' not in col]], id_vars='product_id',
                     var_name='zones_pair', value_name='price_change')
        # na tym etapie odpadają niektóre produkty !!!
        df = df[~df['price_change'].isna()]
        df = pd.merge(left=df, right=df_base, how='inner', on='product_id')
        df = pd.merge(left=df, right=df_elast, how='left', on='final_role')
        df['elasticity'] = np.where(df['price_change'] >= 0, df['elast_increase'], df['elast_decrease'])
        # step 5 - Połączenie tabeli z tabelą z elast_vol po product_id i zones_pair oraz z tabelą df_prices
        df_summary = pd.merge(left=df, right=self.df_elast_vol, how='inner', on=['product_id', 'zones_pair'])
        df_summary['zone_a'] = [f"price_zone_{x.split('_')[0]}" for x in df_summary['zones_pair']]
        df_summary = pd.merge(left=df_summary, right=df_prices, how='left', on=['product_id', 'zone_a'])
        df_summary['vol_elast'] = df_summary['volume'] * (df_summary['elasticity'] * df_summary['price_change'] + 1)
        df_summary['vol_elast'] = [max(0, x) for x in df_summary['vol_elast']]
        df_summary['sales_elast'] = df_summary['vol_elast'] * df_summary['price_zone_a']
        df_summary['margin_elast'] = df_summary['vol_elast'] * (df_summary['price_zone_a'] - df_summary['CZ4B'])
        df_summary_group = df_summary.groupby(['product_id']).agg({'volume': 'sum', 'vol_elast': 'sum',
                                                                   'sales_elast': 'sum', 'margin_elast': 'sum'}
                                                                  ).reset_index()
        df_final = pd.merge(left=df_base, right=df_summary_group, how='left', on='product_id')
        df_final = df_final[['product_id', 'volume', 'vol_elast', 'sales_elast', 'margin_elast']]
        self.df_results = pd.merge(left=self.df_results, right=df_final, how='left', on='product_id')

    def create_elast(self):
        if self.src == 'SQLite':
            self.df_results.to_csv(f"outputs/elast_{datetime.now().strftime('%Y%m%d%H%M')}.csv", sep=';',
                                   encoding='utf-8-sig', index=False)
            SQLITE.create_table(df=self.df_results, table_name='elasticity')
        elif self.src == 'GCP':
            BQ.load_table_from_df(table=f'{PROJECT_ROOT}elasticity', df=self.df_results, disposition='WRITE_TRUNCATE')


model_elast = ModelElast('SQLite')
model_elast.calc_elasticity()
model_elast.create_elast()
