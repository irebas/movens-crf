import pandas as pd
from google.cloud import bigquery, storage
from google.cloud.bigquery.schema import SchemaField


class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def run_query(self, query: str) -> pd.DataFrame:
        results = self.client.query(query).result()
        df = results.to_dataframe()
        return df

    def load_table_from_df(self, table, df, disposition):
        job_config = bigquery.LoadJobConfig()
        job_config.ignore_unknown_values = True
        job_config.autodetect = True
        job_config.write_disposition = disposition
        job = self.client.load_table_from_dataframe(dataframe=df, destination=table, job_config=job_config)
        job.result()
        print(f"Table {table} updated with disposition {disposition}. Rows added: {len(df)}")

    def load_table_from_df_schema(self, table, df, disposition, schema):
        job_config = bigquery.LoadJobConfig()
        job_config.ignore_unknown_values = True
        job_config.schema = schema
        job_config.autodetect = False
        job_config.write_disposition = disposition
        job = self.client.load_table_from_dataframe(dataframe=df, destination=table, job_config=job_config)
        job.result()
        print(f"Table {table} updated with disposition {disposition}. Rows added: {len(df)}")

    @staticmethod
    def map_dict_to_bq_schema(d: dict) -> list:
        schema = []
        for k, v in d.items():
            schema_field = SchemaField(k, v)
            schema.append(schema_field)
        return schema


class GoogleCloudStorage:
    def __init__(self):
        self.client = storage.Client()

    def get_blob_xlsx(self, bucket: str, filename: str):
        bucket = self.client.get_bucket(bucket)
        blob = bucket.get_blob(filename)  # blob
        data_bytes = (blob.download_as_bytes())  # blob in bytes - this form can be loaded to pandas
        return data_bytes

    def delete_blob(self, bucket: str, filename: str):
        return self.client.bucket(bucket).delete(filename)

    def list_all_blobs(self, bucket: str, directory_name: str):
        return self.client.bucket(bucket).list_blobs(prefix=directory_name)

    def upload_file_from_string(self, bucket: str, filename: str, blob: str):
        self.client.bucket(bucket).blob(filename).upload_from_string(blob, "text/csv")

    def upload_blob_xlsx(self, bucket: str, filename: str, data_bytes: bytes):
        bucket = self.client.get_bucket(bucket)
        blob = bucket.blob(filename)
        blob.upload_from_string(data_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        print(f'File {filename} uploaded to {bucket.name}')
