import pandas as pd

# Sample DataFrame
data = {'field_1': ['A', 'A', 'B', 'B', 'A', 'B'],
        'field_2': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
        'Final role': ['Wizerunek', 'Super Wizerunek', 'U2', 'U2', 'U3', 'Wizerunek'],
        'column': [1, 2, 3, 4, 5, 6]}
df = pd.DataFrame(data)

df['role_group'] = ['G1' if x in ['Super Wizerunek', 'Wizerunek'] else 'G2' for x in df['Final role']]



# Calculate the average for each combination of 'field_1' and 'field_2'
df['avg_column'] = df.groupby(['field_1', 'field_2'])['column'].transform('mean')

print(df)
