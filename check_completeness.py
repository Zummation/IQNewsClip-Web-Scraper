sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]
# keys = ['TPC', 'TONG']

for key in keys:
    for source in sources:
        try:
            open(f'result/{key}-{source}.csv')
        except:
            print(f'{key}-{source}')