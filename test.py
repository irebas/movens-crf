import pandas as pd
import numpy as np

d = [{'cc': 'USA', 'v1': 5, 'v2': None, 'v3': 3},
     {'cc': 'USA', 'v1': 6, 'v2': 7, 'v3': 9},
     {'cc': 'USA', 'v1': 5, 'v2': 11, 'v3': 3}]

df = pd.DataFrame(d)

medians = ['v1', 'v2', 'v3']

df['min_price_2'] = df[medians].apply(lambda x: pd.Series(x).nsmallest(2).iloc[-1], axis=1)
print(df)
