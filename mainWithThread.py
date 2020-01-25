from src.IQNewsClipThread import IQNewsClipThread as Scraper

if __name__ == '__main__':
    sources = ['ข่าวหุ้น', 'ทันหุ้น']

    with open('SET100.csv', 'r') as f:
        keys = [symbol.strip() for symbol in f.readlines() if symbol > 'W']

    scraper = Scraper(keys, sources, n_thread=2)
    
    import time
    start_time = time.time()
    scraper.start()
    print(time.time() - start_time)
    # scraper.create_newscount_file()