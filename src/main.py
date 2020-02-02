from IQNewsClipThread import IQNewsClipThread as Scraper

if __name__ == '__main__':

    with open('config/sources.csv', 'r', encoding='utf-8-sig') as f:
        sources = [source.strip() for source in f.readlines()]
    with open('config/symbols.csv', 'r', encoding='utf-8-sig') as f:
        keys = [symbol.strip() for symbol in f.readlines()]
    
    
    scraper = Scraper(keys, sources, n_thread=5)
    scraper.start()
    # scraper.create_newscount_file('NewsCount')

    # scraper.start(whole_file=True)
    # scraper.create_newscount_file(d_dup=False)