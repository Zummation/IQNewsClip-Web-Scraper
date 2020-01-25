import os
import time
import logging
import pandas as pd
import src.logger as logger

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
        self.logger = logger.create_rotating_log()


    def _task(self):
        """this is a function that will be running in a thread"""
        scraper = IQNewsClipScraper()

        # attempt to book a session
        while self.container:
            response = scraper.login()
            if response.status_code == 200 and response.content.decode('UTF-8') != '003':
                self.logger.info('Login completed')
                break # booking a session is complete
            self.logger.info('Login failed')
            sleep(60)

        # scraping section
        while self.container:
            key, source = self.container.pop(0)
            df = scraper.search_all(key, source)
            df.to_csv(f'result/{key}-{source}.csv', index=False, encoding='utf-8-sig')
            self.logger.info(f'Created {key}-{source}.csv')


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
                    self.logger.warning(f'result/{key}-{source}.csv not found')
        
        # check path exists
        fname = 'NewsCount'
        if os.path.exists(f'{fname}.csv'):
            i = 1
            while os.path.exists(f'{fname} ({i}).csv'):
                i += 1
            fname = f'{fname} ({i}).csv'
        else:
            fname = f'{fname}.csv'

        df_out.to_csv(fname, index=False, encoding='utf-8-sig')
        self.logger.info(f'Created {fname}')