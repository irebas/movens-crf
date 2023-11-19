DB_NAME = 'carrefour.db'
INPUTS = [{'file': 'inputs/input1.xlsx', 'skiprows': 0},
          {'file': 'inputs/input2.xlsx', 'skiprows': 5},
          {'file': 'inputs/input3.xlsx', 'skiprows': 0},
          {'file': 'inputs/input4.xlsx', 'skiprows': 0}]
MEDIANS = ['med_auchan', 'med_biedronka', 'med_intermarche', 'med_kaufland', 'med_leclerc', 'med_lidl', 'med_netto',
           'med_rossmann']

# PARAMS EDITABLE
PERC_DIFF = 0.1
PRICES_RANGES_1 = [15, 50, 100]
PRICES_RANGES_2 = [10, 50, 100, 500]
