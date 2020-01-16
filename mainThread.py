from IQNewsClipThread import IQNewsClipThread as Scraper


# keys = ['zn', 'zo', 'zx', 'zy', 'zz']
sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]


scraper = Scraper(keys, sources, n_thread=6)
# scraper.start()
scraper.create_newscount_file()

# TODO: Implement multi-processing and re-run