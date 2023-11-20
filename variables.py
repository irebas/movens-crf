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

ZONES_PARAMS = {
    'Wizerunek': {
        'zone_2': {'PDK': 1.01, 'PFT': 1.01, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 0},
        'zone_3': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 0},
        'zone_4': {'PDK': 1.04, 'PFT': 1.04, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0},
        'zone_5': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0}
    },
    'Gama': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 0},
        'zone_3': {'PDK': 1.03, 'PFT': 1.03, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 0},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0},
        'zone_5': {'PDK': 1.08, 'PFT': 1.08, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0}
    },
    'Kompensacja': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 0},
        'zone_3': {'PDK': 1.03, 'PFT': 1.03, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 0},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0},
        'zone_5': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0.0}
    },
    'Super Kompensacja': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 0},
        'zone_3': {'PDK': 1.03, 'PFT': 1.03, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 0},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0.0},
        'zone_5': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 0, 'TEKSTYLIA': 0, 'EPCS': 0}
    }
}
