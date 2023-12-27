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

ELAST = [{'final_role': 'Super Wizerunek', 'elast_increase': -2.5, 'elast_decrease': -3},
         {'final_role': 'Wizerunek', 'elast_increase': -2, 'elast_decrease': -2.5},
         {'final_role': 'Gama', 'elast_increase': -1, 'elast_decrease': -1},
         {'final_role': 'Kompensacja', 'elast_increase': -0.5, 'elast_decrease': -0.5},
         {'final_role': 'Super Kompensacja', 'elast_increase': -0.25, 'elast_decrease': -0.25},
         {'final_role': 'PLxB', 'elast_increase': -0.25, 'elast_decrease': -0.25}]

FACTOR_SUPER_W = 5
FACTOR_W = 10

D_ROLES = {'Traffic': [0.025, 0.035, 0.54, 0.35, 0.05], 'Turnover': [0.02, 0.035, 0.535, 0.35, 0.06],
           'Basket': [0.01, 0.03, 0.48, 0.40, 0.08], 'Margin': [0.005, 0.035, 0.425, 0.435, 0.1]}

WAGES = {'sales_value_score': 1, 'unique_receipts_score': 1, 'avg_receipt_share_score': 1,
         'shopping_frequency_score': 1, 'sales_margin_score': 1, 'nb_of_shops_with_sales_score': 1,
         'promo_sales_share_score': 1, 'benchmark_list_score': 1, 'avg_product_value_score': 1}
PRODUCTS_NB = 50

PROJECT_ROOT = 'pric-labo.pricing_app.'
