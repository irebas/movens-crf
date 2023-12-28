import json
from os import getenv

import gspread

if getenv('TEMP'):
    gc = gspread.service_account(filename='../keys/creds.json')
else:
    gc = gspread.service_account_from_dict(json.loads(getenv('secret')))


def main():
    wkb = gc.open('Inputs_panel')
    wks = wkb.worksheet('Inputs')
    perc_diff = wks.cell(1, 1).value
    price_ranges_1 = list()
    for r in range(3):
        price_ranges_1.append(wks.cell(2, r + 2).value)


    print(perc_diff)
    print(price_ranges_1)


if __name__ == '__main__':
    main()


# https://callmefred.com/how-to-connect-python-to-google-sheets/