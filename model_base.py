from io import BytesIO

import pandas as pd

from funcs import calc_ntile, assign_single_role
from utils.gcp import GoogleCloudStorage, BigQueryClient
from utils.sqlite import SQLite
from variables import WAGES, PRODUCTS_NB, PROJECT_ROOT

SQLITE = SQLite('carrefour.db')
GCS = GoogleCloudStorage()
BQ = BigQueryClient()


class ModelBase:

    def __init__(self, src: str):
        self.src = src
        self.df_final = pd.DataFrame()
        if self.src == 'SQLite':
            self.df_base = SQLITE.run_sql_query_from_file('queries/queries_sqlite/input_base.sql')
        elif self.src == 'GCP':
            with open('queries/queries_bq/input_base.sql', 'r') as file:
                query_str = file.read()
            self.df_base = BQ.run_query(query_str)

    def assign_points(self):
        cols = ['sales_value', 'unique_receipts', 'avg_receipt_share', 'shopping_frequency', 'sales_margin',
                'nb_of_shops_with_sales', 'promo_sales_share']
        for col in cols:
            self.df_base[col] = pd.to_numeric(self.df_base[col], errors='coerce')
            self.df_base = self.df_base.groupby('L1_SECTOR_ID', group_keys=False).apply(func=calc_ntile, col=col)
        self.df_base['benchmark_list_score'] = [4 if x == 1 else 0 for x in self.df_base['benchmark_list']]
        self.df_base['avg_product_value_score'] = [0 if x <= 3 else 1 if x <= 10 else 2 if x <= 20 else 3 if x <= 40
                                                   else 4 for x in self.df_base['avg_product_value']]
        cols_score = [f'{col}_score' for col in cols] + ['benchmark_list_score', 'avg_product_value_score']
        for col in cols_score:
            self.df_base[col] = self.df_base[col] * WAGES[col]
        self.df_base['total_score'] = self.df_base[cols_score].sum(axis=1)

    @staticmethod
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

    def get_final_df(self):
        df_l4, ids_ok_l4 = ModelBase.calc_lev_roles(lev='L4_name', products_excl=[], df=self.df_base)
        df_l3, ids_ok_l3 = ModelBase.calc_lev_roles(lev='L3_name', products_excl=ids_ok_l4, df=self.df_base)
        df_l2, ids_ok_l2 = ModelBase.calc_lev_roles(lev='L2_name', products_excl=ids_ok_l4 + ids_ok_l3, df=self.df_base)
        df_l1, ids_ok_l1 = ModelBase.calc_lev_roles(lev='L1_name', products_excl=ids_ok_l4 + ids_ok_l3 + ids_ok_l2,
                                                    df=self.df_base)
        self.df_final = pd.concat([df_l4, df_l3, df_l2, df_l1], ignore_index=True)
        self.df_final = self.df_final.sort_values(by=['L1_SECTOR_ID', 'L2_DEPARTMENT_ID', 'L3_GROUP_ID',
                                                      'L4_GROUP_SUB_ID', 'rn']).reset_index(drop=True)

    def create_base_input(self):
        if self.src == 'SQLite':
            self.df_final.to_csv('outputs/df_final.csv', sep=';', encoding='utf-8-sig', index=False)
            SQLITE.create_table(df=self.df_final, table_name='input_base')
        elif self.src == 'GCP':
            BQ.load_table_from_df(table=f'{PROJECT_ROOT}input_base', df=self.df_final, disposition='WRITE_TRUNCATE')
            xlsx_data_bytes = BytesIO()
            self.df_final.to_excel(xlsx_data_bytes, index=False, header=True, engine='openpyxl')
            xlsx_data_bytes = xlsx_data_bytes.getvalue()
            GCS.upload_blob_xlsx(bucket='pricing-app', filename='outputs/input_base.xlsx', data_bytes=xlsx_data_bytes)


model_base = ModelBase('GCP')
model_base.assign_points()
model_base.get_final_df()
model_base.create_base_input()
