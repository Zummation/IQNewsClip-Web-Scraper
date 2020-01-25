import pandas as pd

from time import sleep
from threading import Thread
from multiprocessing import Process
from src.IQNewsClipScraper import IQNewsClipScraper



class IQNewsClipThread():


    def __init__(self, keys=[], sources=[], n_thread=2):
        self.keys = keys
        self.sources = sources
        self.n_thread = n_thread
        self._available_thread = None
        self.scrapers = []
        self.threads = []
        self.container = []

    
    def _book_sessions(self):
        for _ in range(self.n_thread):
            scraper = IQNewsClipScraper()
            response = scraper.login()
            if response.status_code != 200 or response.content.decode('UTF-8') == '003':
                break # booking a session is incomplete
            self.scrapers += [scraper]
        self._available_thread = len(self.scrapers)
        print(f'Number of threads: {self._available_thread}')


    def _task(self, scraper):
        while self.container:
            key, source = self.container.pop(0)
            df = scraper.search_all(key, source)
            df.to_csv(f'result/{key}-{source}.csv', index=False, encoding='utf-8-sig')
            print(f'Completed {key}-{source}.csv')


    def start(self):

        self._book_sessions()
        if self._available_thread == 0: 
            return
        self.container = [(key, source) for key in self.keys for source in self.sources]

        # create threads and run
        self.threads = [Process(target=self._task, args=(self.scrapers[i],)) for i in range(self._available_thread)]
        for thread in self.threads:
            thread.start()

        # main loop while waiting threads running
        while True:
            if not self.container:
                return
            sleep(1)
    

    def create_newscount_file(self):
        """create aggregate file from those .CSVs in the result folder"""
        
        # wait until all threads are finish
        for thread in self.threads:
            while thread.is_alive():
                sleep(1)
        
        df_out = pd.DataFrame()
        for key in self.keys:
            for source in self.sources:
                
                try:
                    df = pd.read_csv(f'result/{key}-{source}.csv')
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
    