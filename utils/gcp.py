import pandas as pd
from google.cloud import bigquery, storage


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
        r = f"Table {table} updated with disposition {disposition}. Rows added: {len(df)}"
        return r

    def load_table_from_df_schema(self, table, df, disposition, schema):
        job_config = bigquery.LoadJobConfig()
        job_config.ignore_unknown_values = True
        job_config.schema = schema
        job_config.autodetect = False
        job_config.write_disposition = disposition
        job = self.client.load_table_from_dataframe(dataframe=df, destination=table, job_config=job_config)
        job.result()
        r = f"Table {table} updated with disposition {disposition}. Rows added: {len(df)}"
        return r


class GoogleCloudStorage:
    def __init__(self):
        self.client = storage.Client()

    def get_blob_xlsx(self, bucket: str, filename: str) -> storage.Blob:
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
