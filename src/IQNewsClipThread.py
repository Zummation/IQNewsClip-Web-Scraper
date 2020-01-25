import os
import time
import logging
import pandas as pd
import src.logger as logger

from time import sleep
from threading import Thread
from datetime import timedelta, datetime
from src.IQNewsClipScraper import IQNewsClipScraper



class IQNewsClipThread():


    def __init__(self, keys=[], sources=[], n_thread=2, from_date=None, to_date=None):
        self.keys = keys
        self.sources = sources
        self.n_thread = n_thread
        self.threads = []
        self.container = []
        self.logger = logger.create_rotating_log()
        self.set_date(from_date, to_date)
        self.whole_file = None

    
    def set_date(self, from_date=None, to_date=None):
        self.from_date = from_date
        self.to_date = to_date
        
        if type(self.from_date) == str:
            self.from_date = datetime.strptime(self.from_date, '%d/%m/%Y')
        if type(self.to_date) == str:
            self.to_date = datetime.strptime(self.to_date, '%d/%m/%Y')
        
        # swap, so from_date is the most recent
        if self.from_date and not self.to_date:
            self.to_date = datetime.now()
        elif not self.from_date and self.to_date:
            self.from_date = datetime.now()
        if self.to_date and self.from_date and self.to_date > self.from_date:
            self.to_date, self.from_date = self.from_date, self.to_date


    def set_today(self):
        self.from_date = datetime.now()
        self.to_date = datetime.now()


    def set_yesterday(self):
        self.from_date = datetime.now() - timedelta(days=1)
        self.to_date = datetime.now() - timedelta(days=1)


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
            
            # append only missing date
            if not self.whole_file:
                try:
                    df = pd.read_csv(f'result/{key}-{source}.csv')
                    if len(df.index) == 0: # for zero-row file
                        raise FileNotFoundError
                    recent_date = datetime.strptime(df['Date'].iloc[0], '%d/%m/%y')
                    recent_date = datetime(recent_date.year-43, recent_date.month, recent_date.day) + timedelta(days=1)
                    if not self.from_date and not self.to_date:
                        new_df = scraper.search_all(key, source, datetime.now(), recent_date)
                    elif recent_date > self.from_date:
                        continue
                    elif recent_date > self.to_date:
                        new_df = scraper.search_all(key, source, self.from_date, recent_date)
                    df = pd.concat([new_df, df]).reset_index(drop=True) 
                except FileNotFoundError:
                    # create whole file
                    df = scraper.search_all(key, source, self.from_date, self.to_date)
            # replace whole file with new one
            else:
                df = scraper.search_all(key, source, self.from_date, self.to_date)

            df.to_csv(f'result/{key}-{source}.csv', index=False, encoding='utf-8-sig')
            self.logger.info(f'Updated {key}-{source}.csv')


    def start(self, whole_file=False):
        """create threads and run"""
        self.whole_file = whole_file
        self.container = [(key, source) for key in self.keys for source in self.sources]
        self.threads = [Thread(target=self._task) for i in range(self.n_thread)]
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        

    def create_newscount_file(self, d_dup=True):
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