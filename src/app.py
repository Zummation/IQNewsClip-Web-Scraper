import argparse
from IQNewsClipThread import IQNewsClipThread as Scraper



parser = argparse.ArgumentParser(
    description='IQNewsClip Scraper Command Line Interface'
)
parser.add_argument(
    'n_thread', 
    metavar='N', 
    type=int,
    help='Number of Threads',
)
parser.add_argument('-c', action="store_true", default=False, help='create aggregation file',)
parser.add_argument('-w', action="store_true", default=False, help='overwrite whole file',)
args = parser.parse_args()


with open('config/sources.csv', 'r', encoding='utf-8-sig') as f:
    sources = [source.strip() for source in f.readlines()]
with open('config/symbols.csv', 'r', encoding='utf-8-sig') as f:
    keys = [symbol.strip() for symbol in f.readlines()]        

scraper = Scraper(keys, sources, n_thread=args.n_thread)
scraper.start(whole_file=args.w)
if args.c: scraper.create_newscount_file('NewsCount')