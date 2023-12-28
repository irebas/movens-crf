from io import BytesIO
from os import getenv

import pandas as pd

from utils.gcp import GoogleCloudStorage, BigQueryClient
from utils.sqlite import SQLite
from variables import DB_NAME

GCS = GoogleCloudStorage()
BQ = BigQueryClient()
SQLITE = SQLite(DB_NAME)


def price_reports(df: pd.DataFrame) -> pd.DataFrame:
    zones = [1, 11, 12, 13, 21, 22, 23, 211, 212, 213, 300, 301, 302, 410, 420, 430, 440, 450, 502, 505, 506, 507, 900]
    d_new_cols = {'Artykuł': 'product_id', 'Median Auchan': 'med_auchan', 'Median Leclerc': 'med_leclerc',
                  'Median Kaufland': 'med_kaufland', 'Median Biedronka': 'med_biedronka', 'Median Rossmann': 'med_rossmann',
                  'Median Lidl': 'med_lidl', 'Median Netto': 'med_netto', 'Median Intermarche': 'med_intermarche'}
    for zone in zones:
        d_new_cols[zone] = str(zone)

    df = df[['Artykuł', 'VAT', 'CZN', 'CZB', 'CZ3N', 'CZ3B', 'CZ4N', 'CZ4B', 'Synonim', 'Indeks', 1, 11, 12, 13, 21, 22, 23, 211,
             212, 213, 300, 301, 302, 410, 420, 430, 440, 450, 502, 505, 506, 507, 900, 'Median Auchan',
             'Median Leclerc', 'Median Kaufland', 'Median Biedronka', 'Median Rossmann', 'Median Lidl',
             'Median Netto', 'Median Intermarche']].copy()
    df.rename(columns=d_new_cols, inplace=True)
    df['Synonim'] = df['Synonim'].astype(str)
    return df


class TableLoaderGCP:

    def __init__(self, bucket: str, filename: str):
        self.bucket = bucket
        self.filename = filename

    def load_table_to_bq(self):
        if 'price_reports' in self.filename:
            df = pd.DataFrame()
            blobs = GCS.list_all_blobs(bucket='pricing-app', directory_name='inputs/price_reports/')
            for blob in blobs:
                if blob.name.endswith('.xlsx'):
                    content = blob.download_as_bytes()
                    df_tmp = pd.read_excel(BytesIO(content), engine='openpyxl', skiprows=5)
                    df = pd.concat([df, df_tmp], ignore_index=True)
                    print(blob.name)
            df = price_reports(df)
            BQ.load_table_from_df(table='pric-labo.pricing_app.input_price_reports', df=df, disposition='WRITE_TRUNCATE')
        else:
            blob = GCS.get_blob_xlsx(bucket=self.bucket, filename=f"{self.filename}")
            table_name = f"pric-labo.pricing_app.{self.filename.split('/')[1].split('.')[0]}"
            file_io = BytesIO(blob)
            df_input = pd.read_excel(file_io)

            for col in df_input.columns:
                if df_input[col].dtype == object:
                    df_input[col] = df_input[col].astype(str)
            BQ.load_table_from_df(table=table_name, df=df_input, disposition='WRITE_TRUNCATE')


class TableLoaderSQLite:

    def __init__(self, input_id: str):
        self.input_id = input_id

    def insert_inputs(self):
        if self.input_id == 'price_reports':
            inputs_list = ['Bazar', 'EPCS', 'PDK', 'PFT']
            df = pd.DataFrame()
            for input_id in inputs_list:
                df_tmp = pd.read_excel(f'inputs/price_reports/{input_id}.xlsx', skiprows=5)
                df = pd.concat([df, df_tmp], ignore_index=True)
            df = price_reports(df)
            SQLite(DB_NAME).create_table(df=df, table_name=f'input_price_reports')
        else:
            inputs_list = ['margin', 'price_zone_a', 'price_zone_b', 'final_grid', 'typology',
                           'category_role', 'benchmark', 'scoring_factors']
            if self.input_id in inputs_list:
                df = pd.read_excel(f'inputs/input_{self.input_id}.xlsx')
                SQLite(DB_NAME).create_table(df=df, table_name=f'input_{self.input_id}')
            else:
                for input_id in inputs_list:
                    df = pd.read_excel(f'inputs/input_{input_id}.xlsx')
                    SQLite(DB_NAME).create_table(df=df, table_name=f'input_{input_id}')


def main(event, context):
    bucket = event["bucket"]
    filename = event["name"]
    print(f"Bucket: {bucket}, File: {filename}")
    TableLoaderGCP(bucket=bucket, filename=filename).load_table_to_bq()


if __name__ == '__main__':
    if getenv('TEMP'):
        event = {
            'bucket': 'pricing-app',
            'name': 'inputs/price_reports/Bazar.xlsx'
        }
        context = None
    # main(event, context)
    TableLoaderSQLite('price_reports').insert_inputs()
