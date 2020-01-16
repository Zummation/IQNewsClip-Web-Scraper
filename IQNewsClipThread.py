import pandas as pd

from time import sleep
from threading import Thread
from IQNewsClipScraper import IQNewsClipScraper



class IQNewsClipThread():


    def __init__(self, keys=[], sources=[], n_thread=2):
        self.keys = keys
        self.sources = sources
        self.n_thread = n_thread
        self.scrapers = [IQNewsClipScraper() for i in range(n_thread)]
        self.threads = []
        self.thread_queue = [[] for i in range(n_thread)]
        self.container = []


    def _task(self, scraper, queue):
        scraper.login()
        while queue:
            key, source = queue.pop(0)
            df = scraper.search_all(key, source)
            df.to_csv(f'result/{key}-{source}.csv', index=False)
            print(f'Completed {key}-{source}.csv')


    def start(self):
            
        self.container = [(key, source) for key in self.keys for source in self.sources]
        
        # put ones to every queue
        for q in self.thread_queue:
            if self.container:
                q += [self.container.pop(0)]

        self.threads = [Thread(target=self._task, args=(self.scrapers[i], self.thread_queue[i])).start() for i in range(self.n_thread)]
        
        # queue arguments in self.container in self.thread_queue
        while True:
            for q in self.thread_queue:
                if len(q) == 1:
                    q += [self.container.pop(0)]
                if not self.container:
                    return
            sleep(1)
    
    
    def create_newscount_file(self):
        
        # wait until all threads are finish
        for thread in self.threads:
            while thread.isAlive():
                sleep(1)
        
        df_out = pd.DataFrame()
        for key in self.keys:
            for source in self.sources:
                
                try:
                    df = pd.read_csv(f'result/{key}-{source}.csv')
                    df = df.pivot_table(index=['Date'], aggfunc='size') \
                        .to_frame('Count') \
                        .reset_index()
                    df.insert(0, 'Stock', key)
                    df.insert(1, 'Source', source)
                    df_out = df_out.append(df, ignore_index=True)

                except:
                    print(f'result/{key}-{source}.csv not found')

        df_out.to_csv('SET100NewsCount.csv', index=False)
    