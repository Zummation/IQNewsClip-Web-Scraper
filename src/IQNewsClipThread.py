import os
import time
import logger
import logging
import pandas as pd

from time import sleep
from threading import Thread
from datetime import timedelta, datetime, date
from IQNewsClipScraper import IQNewsClipScraper
from cookies_handler import CookiesHandler



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
        self.cookies_handler = CookiesHandler()

    
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


    def _task(self, thread_id):
        """this is a function that will be running in a thread"""
        
        # load cookies if exists
        try:
            cookies = self.cookies_handler.load_cookies(thread_id)
            scraper = IQNewsClipScraper(cookies=cookies)
        except Exception as e:
            self.logger.warning('Cookies: ' + str(e))
            scraper = IQNewsClipScraper()

        # attempt to book a session
        while self.container:
            response = scraper.login()
            if response.status_code == 200 and response.content.decode('UTF-8') != '003':
                self.logger.info('Login completed')
                # sometimes it returns no cookies
                if response.cookies.__dict__['_cookies'] != {}:
                    self.cookies_handler.save_cookies(response.cookies, thread_id)
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
                    recent_date = df['Date'].iloc[0]
                    # remove the recent_date from dataframe
                    df = df.set_index('Date').drop(recent_date, axis=0).reset_index()
                    recent_date = datetime.strptime(recent_date, '%d/%m/%y')
                    recent_date = datetime(recent_date.year-43, recent_date.month, recent_date.day)
                    if not self.from_date and not self.to_date:
                        new_df = scraper.search_all(key, source, datetime.now(), recent_date)
                    elif recent_date > self.from_date:
                        continue
                    elif recent_date > self.to_date:
                        new_df = scraper.search_all(key, source, self.from_date, recent_date)
                    df = pd.concat([new_df, df]).reset_index(drop=True) 
                except FileNotFoundError:
                    # create whole file
                    self.logger.warning(f'result/{key}-{source}.csv not found')
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
        self.threads = [Thread(target=self._task, args=(i,)) for i in range(self.n_thread)]
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        

    def create_newscount_file(self, name='NewsCount', d_dup=True):
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
                    df.insert(1, 'Source', source)
                    df.insert(2, 'Symbol', key)
                    df_out = df_out.append(df, ignore_index=True)

                except:
                    self.logger.warning(f'result/{key}-{source}.csv not found')

        # date formatting
        date_df = list(df_out.Date)
        for i, a_date in enumerate(date_df):
            day, month, year = map(int, a_date.split('/'))
            date_df[i] = date(year+1957, month, day).strftime('%Y-%m-%d')
        df_out['Date'] = pd.DataFrame(date_df)

        # sort DataFrame by date
        df_out = df_out.sort_values(by=['Date', 'Source', 'Symbol'])
        
        # check path exists
        fname = name
        if os.path.exists(f'aggregate/{fname}.csv'):
            i = 1
            while os.path.exists(f'aggregate/{fname} ({i}).csv'):
                i += 1
            fname = f'aggregate/{fname} ({i}).csv'
        else:
            fname = f'aggregate/{fname}.csv'

        df_out.to_csv(fname, index=False, encoding='utf-8-sig')
        self.logger.info(f'Created {fname}')