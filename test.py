from multiprocessing import Pool
from datetime import datetime
import time
import pandas as pd


def get_df():
    df = pd.DataFrame(data={'id': [1, 2, 3, 4, 5, 6],
                            'val': [3, 4, 2, 5, 4, 3]})
    return df


def work_log(param):
    rng_1 = param['ranges'][0]
    rng_2 = param['ranges'][1]
    df = param['df']
    for r in range(rng_1, rng_2):
        print(f"Process started for id: {df.loc[r, 'val']}")
        # time.sleep(int(df.loc[r, 'val']))
        print(f"Process for id {df.loc[r, 'val']} finished")
        df.loc[r, 'val'] = df.loc[r, 'val'] * 2

    new_df = df.iloc[rng_1:rng_2].copy()

    return new_df


def pool_handler(params):
    # p = Pool(4)

    with Pool(8) as p:
        results = p.map(work_log, params)

    concatenated_df = pd.concat(results, ignore_index=True)
    return concatenated_df


if __name__ == '__main__':
    t0 = datetime.now()
    df = get_df()
    params = ({'ranges': (0, 2), 'df': df}, {'ranges': (2, 4), 'df': df}, {'ranges': (4, 6), 'df': df})
    results_df = pool_handler(params)
    print(results_df)
    print(f'{datetime.now() - t0}')
