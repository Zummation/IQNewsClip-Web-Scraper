
with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]

    print(keys)