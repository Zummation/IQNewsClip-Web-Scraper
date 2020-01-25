from src.IQNewsClipThread import IQNewsClipThread as Scraper

if __name__ == '__main__':
    sources = ['ข่าวหุ้น', 'ทันหุ้น']

    with open('SET100.csv', 'r') as f:
        keys = [symbol.strip() for symbol in f.readlines() if symbol > 'Z']

    scraper = Scraper(keys, sources, n_thread=2)
    scraper.start()
    # scraper.create_newscount_file(d_dup=False)
    # scraper.create_newscount_file(d_dup=True)