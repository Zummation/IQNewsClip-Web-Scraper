from src.IQNewsClipThread import IQNewsClipThread as Scraper


sources = ['ข่าวหุ้น', 'ทันหุ้น']

# keys = ['zn', 'zo', 'zx', 'zy', 'zz']
with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]


scraper = Scraper(keys, sources, n_thread=7)
scraper.start()
scraper.create_newscount_file()

# TODO: Implement multi-processing and re-run