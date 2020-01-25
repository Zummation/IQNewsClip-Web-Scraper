import requests
import pandas as pd
import src.logger as logger

from bs4 import BeautifulSoup
from src.utils import SOURCES_CODE

import logging

class IQNewsClipScraper():


    def __init__(self):
        self.session = requests.Session()
        self._has_next = None
        self.logger = logger.create_rotating_log()


    def login(self):
        response = self.session.get('http://edu.iqnewsclip.com/ajax/authentication.aspx')
        return response


    def search_once(self, search_key, source):
        """return pandas.DataFrame of one-time keyword searching"""

        payload = {
            'CtrlSearch1:txtCategory': 'ทุกหัวเรื่องที่รับบริการ',
            'CtrlSearch1:hdnews': SOURCES_CODE[source],
            'CtrlSearch1:txtSearch': search_key,
        }

        r = self.session.post('http://edu.iqnewsclip.com/ajax/GetResult.aspx?stype=search&rbt=false', data=payload)
        return self.extract_html(r.content)


    def search_next(self):
        """return pandas.DataFrame of the next page of current page"""

        r = self.session.get('http://edu.iqnewsclip.com/ajax/GetResult.aspx?pg=next')

        try:
            r.raise_for_status()
            df = self.extract_html(r.content)

        except requests.exceptions.RequestException as e:
            self._has_next = False
            df = None
            print('RequestException: ', e)

        return df
    

    def search_all(self, search_key: str, source: str):
        """return pandas.DataFrame of every-pages data of the given search_key and source"""

        df = self.search_once(search_key, source)
        i = 1

        while self.has_next():
            df = df.append(self.search_next(), ignore_index=True)
            i += 1
        self.logger.info(f'Searched {i}/{i} pages of {search_key}-{source}')
        return df


    def extract_html(self, html):
        """convert html to pandas.DataFrame"""
        
        soup = BeautifulSoup(html, features='lxml', from_encoding="windows-874")
        tags = soup.find_all(['a', 'td'], class_=['HeadlineBlue', 'normalGray'])
        data = {'Date': [], 'Source':[], 'HeadLine': []}
        it = iter(tags)
        for i in it:
            data['Date'].append(i.text.strip())
            data['Source'].append(next(it).text.strip())
            data['HeadLine'].append(next(it).text.strip())
        
        try:
            if 'Next>>' in soup.find('label', id='lblNavigate1').text: 
                self._has_next = True
            else:
                self._has_next = False
        except:
            self.logger.error('An error occurs in extracting html')

        return pd.DataFrame(data)


    def has_next(self):
        """return True if next pages exist"""

        return self._has_next

