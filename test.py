from utils.gcp import BigQueryClient
import pandas as pd

BQ = BigQueryClient()

df = BQ.run_query('SELECT * FROM `pric-labo.pricing_app.input_scoring_factors`')
cols = ['sales_value', 'unique_receipts', 'avg_receipt_share', 'shopping_frequency', 'sales_margin',
        'avg_product_value', 'nb_of_shops_with_sales', 'promo_sales_share']
for col in cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
print(df.dtypes)
df.to_csv('inputs/input_scoring_factors.csv', encoding='utf-8-sig', index=False)
