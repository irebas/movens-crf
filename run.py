from main import insert_inputs, save_model_as_csv, save_and_open_xlsx


def main():
    code = input('Select function code:\nI - update inputs\nS - save results as csv\n'
                 'O - save results as xlsx and open file\nCode: ')
    match code:
        case 'I':
            input_id = input('Select input_id (1,2,3,5a,5b,6) or press Enter for all: ')
            insert_inputs(input_id)
        case 'S': save_model_as_csv()
        case 'O': save_and_open_xlsx()
        case 'Q': quit()
        case _: print('Wrong code')
    main()


if __name__ == '__main__':
    main()
