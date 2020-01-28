import pandas as pd


sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]


def test_charset_is_correct(keys, sources):
    for key in keys:
        for source in sources:
            df = pd.read_csv(f'result/{key}-{source}.csv')
            if True in set(pd.isnull(df['HeadLine'])):
                print('is null', key, source)
        
def find_zero_row_page(keys, source):        
    for key in keys:
        for source in sources:
            df = pd.read_csv(f'result/{key}-{source}.csv')
            if len(df.index) == 0:
                print('0 row', key, source)

test_charset_is_correct(keys, sources)
find_zero_row_page(keys, sources)