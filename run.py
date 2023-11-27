from main import insert_inputs, save_model_as_csv
from elast_vol import calc_elast_vol
from elast import calc_elasticity


def main():
    code = input('Select function code:\nI - update inputs\nM - calculate model and save results as csv\n'
                 'V - calculate elasticity volume\nE - calculate full model with elasticity\n'
                 'Q - quit\nCode: ')
    match code:
        case 'I':
            input_id = input('Select input_id (1,2,3,5a,5b,6) or press Enter for all: ')
            insert_inputs(input_id)
        case 'M': save_model_as_csv()
        case 'V': calc_elast_vol()
        case 'E': calc_elasticity()
        case 'Q': quit()
        case _: print('Wrong code')
    main()


if __name__ == '__main__':
    main()
