import sqlite3

import pandas as pd


class SQLite:

    def __init__(self, db_name: str):
        self.db_name = db_name

    def create_table(self, df: pd.DataFrame, table_name: str):
        with sqlite3.connect(self.db_name) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f'Table {table_name} created')

    def append_table(self, df: pd.DataFrame, table_name: str):
        with sqlite3.connect(self.db_name) as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f'Table {table_name} appended')

    def truncate_table(self, table_name: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name};')
        print(f'Table {table_name} truncated')

    def run_sql_query_from_file(self, query_file: str):
        with open(query_file, 'r') as file:
            query = file.read()

        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query(query, conn)

        return df

    def run_sql_query(self, query_str: str):
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query(query_str, conn)

        return df
