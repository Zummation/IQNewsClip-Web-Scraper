import pandas as pd


sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]

for key in keys:
    for source in sources:
        df = pd.read_csv(f'result/{key}-{source}.csv')
        if True in set(pd.isnull(df['HeadLine'])):
            print('is null', key, source)
        if len(df.index) == 0:
            print('0 row', key, source)