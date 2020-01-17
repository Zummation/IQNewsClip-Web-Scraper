import pandas as pd


sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines() if symbol > 'K']

for key in keys:
    for source in sources:
        df = pd.read_csv(f'result/{key}-{source}.csv')
        # df = pd.read_csv(f'result/TOC-{sources[0]}.csv')
        if True in set(pd.isnull(df['HeadLine'])):
            print(key, source)
