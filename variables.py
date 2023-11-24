# INPUTS NON EDITABLE !!!
DB_NAME = 'carrefour.db'

MEDIANS = ['med_auchan', 'med_biedronka', 'med_intermarche', 'med_kaufland', 'med_leclerc', 'med_lidl', 'med_netto',
           'med_rossmann']

ZONES_A = ['1', '2', '3', '4', '5']
ZONES_B = ['410', '420', '430', '440', '450', '502', '505', '506', '507', '900', '11', '12', '13', '21', '22', '23',
           '1', '211', '212', '213', '300', '301', '302']

# INPUTS EDITABLE BELOW
PERC_DIFF = 0.1
PRICES_RANGES_1 = [15, 50, 100]
PRICES_RANGES_2 = [10, 50, 100, 500]

KOMP_COEFF = 1.01
SUPER_KOMP_COEFF = 1.03

ZONES_PARAMS = {
    'Wizerunek': {
        'zone_2': {'PDK': 1.01, 'PFT': 1.01, 'BAZAR': 1.01, 'TEKSTYLIA': 1.01, 'EPCS': 1.01},
        'zone_3': {'PDK': 1.02, 'PFT': 1.04, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 1.04},
        'zone_4': {'PDK': 1.04, 'PFT': 1.06, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.06},
        'zone_5': {'PDK': 1.06, 'PFT': 1.08, 'BAZAR': 1.08, 'TEKSTYLIA': 1.08, 'EPCS': 1.08}
    },
    'Gama': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 1.01},
        'zone_3': {'PDK': 1.04, 'PFT': 1.04, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.04},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.060},
        'zone_5': {'PDK': 1.08, 'PFT': 1.08, 'BAZAR': 1.08, 'TEKSTYLIA': 1.08, 'EPCS': 1.08}
    },
    'Kompensacja': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 1.01},
        'zone_3': {'PDK': 1.03, 'PFT': 1.03, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.04},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.06},
        'zone_5': {'PDK': 1.08, 'PFT': 1.08, 'BAZAR': 1.08, 'TEKSTYLIA': 1.08, 'EPCS': 1.080}
    },
    'Super Kompensacja': {
        'zone_2': {'PDK': 1.02, 'PFT': 1.02, 'BAZAR': 1.04, 'TEKSTYLIA': 1.04, 'EPCS': 1.01},
        'zone_3': {'PDK': 1.03, 'PFT': 1.03, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.04},
        'zone_4': {'PDK': 1.06, 'PFT': 1.06, 'BAZAR': 1.06, 'TEKSTYLIA': 1.06, 'EPCS': 1.06},
        'zone_5': {'PDK': 1.08, 'PFT': 1.08, 'BAZAR': 1.08, 'TEKSTYLIA': 1.08, 'EPCS': 1.08}
    }
}
