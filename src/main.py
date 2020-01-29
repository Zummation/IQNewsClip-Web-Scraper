from IQNewsClipThread import IQNewsClipThread as Scraper

if __name__ == '__main__':
    sources = ['ข่าวหุ้น', 'ทันหุ้น']

    with open('res/SET100.csv', 'r') as f:
        keys = [symbol.strip() for symbol in f.readlines()]

    scraper = Scraper(keys, sources, n_thread=11)
    scraper.start(whole_file=True)
    scraper.create_newscount_file('NewsCount')

    # scraper.start(whole_file=True)
    # scraper.create_newscount_file(d_dup=False)