from IQNewsClipScraper import IQNewsClipScraper



keys = ['CPF']
sources = ['ข่าวหุ้น', 'ทันหุ้น']

with open('SET100.csv', 'r') as f:
    keys = [symbol.strip() for symbol in f.readlines()]

scraper = IQNewsClipScraper()
scraper.login()

for key in keys:
    if key < 'EGCO': continue
    for source in sources:
        df = scraper.search_all(key, source)
        df.to_csv(f'result/{key}-{source}.csv', index=False)
        print(f'Completed {key}-{source}.csv')