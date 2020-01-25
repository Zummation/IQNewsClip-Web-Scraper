import pandas as pd
from time import sleep
from threading import Thread
from src.IQNewsClipScraper import IQNewsClipScraper



class IQNewsClipThread():


    def __init__(self, keys=[], sources=[], n_thread=2):
        self.keys = keys
        self.sources = sources
        self.n_thread = n_thread
        self.threads = []
        self.container = []


    def _task(self):
        """this is a function that will be running in a thread"""
        scraper = IQNewsClipScraper()

        # attempt to book a session
        while self.container:
            response = scraper.login()
            if response.status_code == 200 and response.content.decode('UTF-8') != '003':
                break # booking a session is complete
            sleep(60)

        # scraping section
        while self.container:
            key, source = self.container.pop(0)
            df = scraper.search_all(key, source)
            df.to_csv(f'result/{key}-{source}.csv', index=False, encoding='utf-8-sig')
            print(f'Completed {key}-{source}.csv')


    def start(self):
        """create threads and run"""
        self.container = [(key, source) for key in self.keys for source in self.sources]
        self.threads = [Thread(target=self._task) for i in range(self.n_thread)]
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        

    def create_newscount_file(self, d_dup=False):
        """create aggregate file from those .CSVs in the result folder"""
                
        df_out = pd.DataFrame()
        for key in self.keys:
            for source in self.sources:
                
                try:
                    df = pd.read_csv(f'result/{key}-{source}.csv')
                    if d_dup is True: # drop duplicates
                        df = df.drop_duplicates()
                    df = df.pivot_table(index=['Date'], aggfunc='size') \
                        .to_frame('Count') \
                        .reset_index()
                    df.insert(0, 'Stock', key)
                    df.insert(1, 'Source', source)
                    df_out = df_out.append(df, ignore_index=True)

                except:
                    print(f'result/{key}-{source}.csv not found')
        
        df_out.to_csv('NewsCount.csv', index=False, encoding='utf-8-sig')
    