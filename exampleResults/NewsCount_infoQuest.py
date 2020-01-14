# -*- coding: utf-8 -*-
"""
Created on Fri May 13 12:55:27 2016

@author: Nim
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

cwd = os.getcwd()
cwdMain = cwd #os.path.normpath(cwd + os.sep + os.pardir)

try:
    if os.name == 'posix':
        sys.path.insert(0, cwdMain+"/Packages")
    elif os.name == 'nt':
        sys.path.insert(0, cwdMain+"\\Packages")
except:
    print('No \'Packages\' folder import')

os.chdir(cwd)


#### Logging
def loggerCreate(log_file):
    import logging
    logger = logging.getLogger('Logger')
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)
    return logger

def createTable(c, table_name):
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name= '%s';" %table_name)
    if c.fetchone() == None:
        c.execute('CREATE TABLE ' + table_name + ' (searchNews text, topic text, newspapers text, newsDate text, headline text, column text)' )
    else:
        c.execute("DROP TABLE "+table_name)
        c.execute('CREATE TABLE ' + table_name + ' (searchNews text, topic text, newspapers text, newsDate text, headline text, column text)' )


#### Function: Waiting and Click
class wait_for_newspage_change(object):
    def __init__(self, browser):
        self.browser = browser
    def __enter__(self):
        try:
            soup = BeautifulSoup(d.page_source)
            t = soup.find('table',id = 'grdAllNews')
            rows = t.findAll('tr')
            row = rows[0]
            cols = row.find_all('td')
            self.old = cols[0]
        except:
            self.old = 0
    def page_has_loaded(self):
        try:
            soup = BeautifulSoup(d.page_source)
            t = soup.find('table',id = 'grdAllNews')
            rows = t.findAll('tr')
            row = rows[0]
            cols = row.find_all('td')
            new = cols[0]
        except:
            new = self.old
        Check = new != self.old
        return Check
    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)
    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 20:
            if condition_function():
                return True
                break
            else:
                time.sleep(0.1)

class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser
    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')
    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        Check = new_page.id != self.old_page.id
        return Check
    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)
    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 5:
            if condition_function():
                return True
                break
            else:
                time.sleep(0.1)

def clickAndHold(d,obj,t):
    objAction = ActionChains(d).move_to_element(obj)
    objAction.click_and_hold().perform()
    time.sleep(t)
    objAction.release().perform()

#### Function: About date
def genDate(para):  #### Remind: date format is dd/mm/yyyy A.D.'

    def endDayOfMon(m,y):
        if m == 1 or m==3 or m==5 or m==7 or m==8 or m==10 or m==12:
            d = 31
        elif m == 4 or m==6 or m==9 or m==11:
            d = 30
        elif m==2:
            if y%4==0:
                d = 29
            else:
                d = 28
        return d

    def strDate(d,m,y):
        d = str(d)
        if len(d) == 1:
            d = '0'+d
        m = str(m)
        if len(m) == 1:
            m = '0'+m
        y = str(y+543)
        result = d+'/'+m+'/'+y
        return result

    #### Create factors from para
    beginDate = para['beginDate']
    endDate = para['endDate']
    #### Begin of selected date
    [d,m,y] = beginDate.split('/')
    db=int(float(d))
    mb=int(float(m))
    yb=int(float(y))
    if db > 1:
        db = 1
    #### End of selected date
    [d,m,y] = endDate.split('/')
    me=int(float(m))
    ye=int(float(y))
    #### Cal
    dateRange = []
    dateStartMon = strDate(db,mb,yb)
    dateEndMon = strDate(endDayOfMon(me,ye),me,ye)
    dateRange.append({'dateStartMon':dateStartMon, 'dateEndMon':dateEndMon})
    return dateRange

def selectDateFromTable(dateSelect,tableElement):
    yea = dateSelect.split('/')[2]
    mon = dateSelect.split('/')[1]
    day = dateSelect.split('/')[0]

    imgTableClick = d.find_element_by_id(tableElement)
    imgTableClick.click()

    #### #### Year
    imgCalendarYear = d.find_element_by_id('spanYear')
    imgCalendarYear.click()
    time.sleep(1)

    yMinus = d.find_element_by_css_selector("td[onmousedown*='clearInterval(intervalID1);intervalID1=CSCOCall_setInterval(null,setInterval,\"decYear()\",30)']")
    yPlus = d.find_element_by_css_selector("td[onmousedown*='clearInterval(intervalID2);intervalID2=CSCOCall_setInterval(null,setInterval,\"incYear()\",30)']")

    yeaSelectCheck = 0
    while yeaSelectCheck == 0:
        y0 = int(d.find_element_by_id('y0').text)
        y6 = int(d.find_element_by_id('y6').text)
        if int(yea) >= y0:
            if int(yea) <= y6:
                yeaSelect = 'y'+ str(int(yea) - y0)
                yeaSelectCheck = 1
            else:
                clickAndHold(d,yPlus,0.1)
        else:
            clickAndHold(d,yMinus,0.1)
        time.sleep(0.3)

    imgCalendarYearSelect = d.find_element_by_id(yeaSelect)
    imgCalendarYearSelect.click()
    time.sleep(1)

    #### #### Month
    imgCalendarMonth = d.find_element_by_id('spanMonth')
    imgCalendarMonth.click()
    time.sleep(1)

    monSelect = 'm'+str(int(mon)-1)
    imgCalendarMonthSelect = d.find_element_by_id(monSelect)
    imgCalendarMonthSelect.click()
    time.sleep(1)

    #### #### Day
    daySelect = "a[href*='javascript:dateSelected=" + str(int(day)) + ";closeCalendar();']"
    imgCalendarDay = d.find_element_by_css_selector(daySelect)
    imgCalendarDay.click()
    time.sleep(1)

#### Function: Login and save to Excel
def loginToInfoQ(d,para):
    username = para['username']
    password = para['password']
    with wait_for_page_load(d):
        d.get('https://vpn.chula.ac.th/+CSCOE+/logon.html#form_title_text')
    with wait_for_page_load(d):
        txtLogin = d.find_element_by_name('username')
        txtPassword = d.find_element_by_name('password')
        txtLogin.send_keys(username)
        txtPassword.send_keys(password)
        txtPassword.send_keys(Keys.ENTER)
    while True:
        try:
            txtGoToInfoQ = d.find_element_by_id('unicorn_form_url')
            txtGoToInfoQ.send_keys('edu.iqnewsclip.com')
            txtGoToInfoQ.send_keys(Keys.ENTER)
            break
        except:
            pass
            print('wait')
    time.sleep(10)

def genDateAll(para):
    [ds,ms,ys] = para['beginDate'].split('/')
    ms = int(ms)
    ys = int(ys)-543
    [de,me,ye] = para['endDate'].split('/')
    me = int(me)
    ye = int(ye)-543

    dateAll = []
    for yloop in range(ys,ye+1):
        if ys == ye:
            mstart = ms
            men = me+1
        else:
            if yloop==ys:
                mstart = ms
                men = 13
            elif yloop==ye:
                mstart = 1
                men = me+1
            else:
                mstart = 1
                men = 13
        for myloop in range(mstart,men):
            dateAll.append(int(yloop)*100+int(myloop))
    return dateAll


if __name__ == "__main__":

    #### Parameters
    para = {
        'username' : 'lpongsak',
        'password' : 'home2981',
        'topicNum' : [1],
        'newspapersNum' : [6,8,9,12,16],
        'searchNews' : [u'("ปฏิรูป" และ "การเมือง")', u'(("รัฐธรรมนูญ" หรือ "รธน") และ ("ยกร่าง" หรือ "แก้ไข"))'],
        'beginDate' : '1/6/2549',
        'endDate' : '16/2/2561',
        'table_name': 'headlines',
        'db_name': 'dbNewsCount.db',
        'paraContinue' : {
            'topicNum' : 0,
            'newspapersNum' :0,
            'searchNews' : 0,
        }
    }

    newspapersSelect = [u'ไทยรัฐ',u'มติชน',u'ข่าวสด',u'เดลินิวส์',u'คม ชัด ลึก']

    '''
    ###########################################################################
    ###########################################################################

    Note:

    'newspapersNum'

    0  - สิ่งพิมพ์ทุกฉบับ
    1  - หนังสือพิมพ์รายวัน
    2  - BANGKOK POST
    3  - M2F
    4  - THE NATION
    5  - กรุงเทพธุรกิจ
    6  - ข่าวสด
    7  - ข่าวหุ้น
    8  - คม ชัด ลึก
    9  - เดลินิวส์
    10 - ทันหุ้น
    11 - ไทยโพสต์
    12 - ไทยรัฐ
    13 - แนวหน้า
    14 - ผู้จัดการรายวัน 360 องศา
    15 - โพสต์ทูเดย์
    16 - มติชน
    17 - โลกวันนี้
    18 - สยามกีฬา
    19 - สยามรัฐ

    'topicNum'

    0    - ทุกหัวเรื่องที่รับบริการ
    1    - ข่าวหน้าหนึ่ง
    100  - ธุรกิจ
    200  - ไอทีและสื่อสาร
    300  - สินค้าอุปโภค/บริโภค
    400  - เศรษฐกิจ
    500  - การเมือง
    600  - เกษตรกรรม/สินค้าโภคภัณฑ์
    700  - ท่องเที่ยว
    800  - บันเทิงและกีฬา
    900  - การศึกษา
    1000 - อื่นๆ

    ###########################################################################
    ###########################################################################
    '''

    para['paraContinue']['beginDate'] = {'status':'off','value':para['beginDate']}

    #### Database and Logging
    table_name = para['table_name']
    conn = sqlite3.connect(para['db_name'])
    c = conn.cursor()
    createTable(c,table_name);



    if os.name == 'posix':
        chromedriverDirectory = cwdMain+'/chromedriver'
        log_file = cwd+'/Logger.log'
    elif os.name == 'nt':
        chromedriverDirectory = cwdMain+'\\chromedriver.exe'
        log_file = cwd+'\\Logger.log'

    while True:

        try:

            logger = loggerCreate(log_file)
            d = webdriver.Chrome(chromedriverDirectory)
            loginToInfoQ(d,para)

            #### Click "Since" checklist
            clickSince = d.find_element_by_id('CtrlSearch1_rbtBasic')
            clickSince.click()
            time.sleep(0.3)

            #### Select "DateFrom"
            dateStartMon = para['beginDate']
            tableElement = 'CtrlSearch1_imgDateFrom'
            selectDateFromTable(dateStartMon,tableElement)

            #### Select "DateTo"
            dateEndMon = para['endDate']
            tableElement = 'CtrlSearch1_imgDateTo'
            selectDateFromTable(dateEndMon,tableElement)

            try:

                #### Calculation
                tN = para['paraContinue']['topicNum']
                while tN < len(para['topicNum']):
                    topicNum = para['topicNum'][tN]

                    #### Select topic
                    if topicNum == 0:
                        topicNumHTML = 0
                    elif topicNum == 1:
                        topicNumHTML = 1
                    elif topicNum == 100:
                        topicNumHTML = 2
                    elif topicNum == 200:
                        topicNumHTML = 41
                    elif topicNum == 300:
                        topicNumHTML = 51
                    elif topicNum == 400:
                        topicNumHTML = 65
                    elif topicNum == 500:
                        topicNumHTML = 82
                    elif topicNum == 600:
                        topicNumHTML = 93
                    elif topicNum == 700:
                        topicNumHTML = 99
                    elif topicNum == 800:
                        topicNumHTML = 103
                    elif topicNum == 900:
                        topicNumHTML = 109
                    elif topicNum == 1000:
                        topicNumHTML = 111

                    time.sleep(2)
                    clickTopic = d.find_element_by_id('divTopRight')
                    clickTopic.click()
                    time.sleep(2)
                    topicList = d.find_element_by_id('CtrlSearch1_TreeViewCategoryt'+str(topicNumHTML))
                    topic = topicList.text
                    topicList.click()

                    checkDailyNewsExpand = 0
                    nN = para['paraContinue']['newspapersNum']
                    while nN < len(para['newspapersNum']):
                        newspapersNum = para['newspapersNum'][nN]

                        #### Select news source
                        time.sleep(2)
                        clickNewsSource = d.find_element_by_id('divNewsTopRight')
                        clickNewsSource.click()
                        if checkDailyNewsExpand == 0:
                            time.sleep(2)
                            clickDailyNewsExpand = d.find_element_by_id('CtrlSearch1_TreeViewNewspapern1')
                            clickDailyNewsExpand.click()
                            checkDailyNewsExpand = 1
                        time.sleep(2)
                        newspaperList = d.find_element_by_id('CtrlSearch1_TreeViewNewspapert'+str(newspapersNum))
                        newspaper = newspaperList.text
                        newspaperList.click()

                        #### Search
                        sN = para['paraContinue']['searchNews']
                        while sN < len(para['searchNews']):
                            searchNews = para['searchNews'][sN]

                            #### Fill searching texts
                            time.sleep(2)
                            fillSearch = d.find_element_by_name('CtrlSearch1:txtSearch')
                            keyword = searchNews
                            fillSearch.clear()
                            fillSearch.send_keys(keyword)

                            #### Set begin date
                            if para['paraContinue']['beginDate']['status'] == 'on':
                                dateStartMon = para['paraContinue']['beginDate']['value']
                                tableElement = 'CtrlSearch1_imgDateFrom'
                                selectDateFromTable(dateStartMon,tableElement)
                                c.execute('DELETE FROM ' + para['table_name'] + ' WHERE searchNews LIKE "' + searchNews.replace('"','_').replace(' ','_') + '" AND newspapers LIKE "' + newspaper.replace('"','_').replace(' ','_') + '" AND topic LIKE "' + topic.replace('"','_').replace(' ','_') +  '" AND newsDate = "' + dateStartMon + '"')

                            #### Submit search text
                            submit = d.find_element_by_name('CtrlSearch1:btnSearch')
                            time.sleep(2)
                            submit.click()
                            time.sleep(2)

                            #### Click next to the end of pages
                            t1 = time.time()

                            t_start = time.time()
                            refreshTimes = 0
                            pageClickCount = 0
                            while True:
                                while time.time()-t_start < 15:
                                    try:
                                        nex = d.find_element_by_xpath("//*[contains(text(), 'Next>>')]")
                                        pageClickCount += 1
                                        soup = BeautifulSoup(d.page_source)
                                        t = soup.find('table',id = 'grdAllNews')
                                        rows = t.findAll('tr')
                                        for row in rows:
                                            cols = row.find_all('td')
                                            cols_text0 = [ele.text.strip() for ele in cols]
                                            newspaper = cols_text0[2]
                                            newsDate = cols_text0[1]
                                            headline = cols_text0[3]
                                            if headline.find(u'คอลัมน์')==0:
                                                colum = headline.split(':')[0]
                                            else:
                                                colum = ''
                                            cols_text = [searchNews, topic, newspaper, newsDate, headline, colum]
                                            c.execute('INSERT INTO ' + para['table_name'] + ' VALUES (?,?,?,?,?,?)', cols_text)
                                        [dd,mm,yy] = cols_text[3].split('/')
                                        para['paraContinue']['beginDate']['value'] = dd+'/'+mm+'/'+str(int(yy)+2500)
                                        nex.click()
                                        conn.commit()
                                        t_start = time.time()
                                    except:
                                        pass

                                try:
                                    prev = d.find_element_by_xpath("//*[contains(text(), '<<Prev')]")
                                    soup = BeautifulSoup(d.page_source)
                                    t = soup.find('table',id = 'grdAllNews')
                                    rows = t.findAll('tr')
                                    for row in rows:
                                        cols = row.find_all('td')
                                        cols_text0 = [ele.text.strip() for ele in cols]
                                        newspaper = cols_text0[2]
                                        newsDate = cols_text0[1]
                                        headline = cols_text0[3]
                                        if headline.find(u'คอลัมน์')==0:
                                            colum = headline.split(':')[0]
                                        else:
                                            colum = ''
                                        cols_text = [searchNews, topic, newspaper, newsDate, headline, colum]
                                        c.execute('INSERT INTO ' + para['table_name'] + ' VALUES (?,?,?,?,?,?)', cols_text)
                                    para['paraContinue']['beginDate']['value'] = para['beginDate']
                                    para['paraContinue']['beginDate']['status'] = 'off'
                                    conn.commit()
                                    dateStartMon = para['beginDate']
                                    tableElement = 'CtrlSearch1_imgDateFrom'
                                    selectDateFromTable(dateStartMon,tableElement)
                                    print('Achieve '+str(tN)+'-'+str(nN)+'-'+str(sN)+' in '+str(int(time.time()-t1))+' seconds')
                                    logger.warning('Achieve '+str(tN)+'-'+str(nN)+'-'+str(sN)+' in '+str(int(time.time()-t1))+' seconds')
                                    break
                                except:
                                    if pageClickCount != 0:
                                        raise ValueError('Refresh driver error')
                                    else:
                                        break

        #                                d.refresh()
        #                                refreshTimes+=1
        #                                print('Refresh driver: '+str(tN)+'-'+str(nN)+'-'+str(sN)+'-'+str(para['paraContinue']['beginDate']['value'])+' - '+str(refreshTimes))
        #                                logger.error('Refresh driver: '+str(tN)+'-'+str(nN)+'-'+str(sN)+'-'+str(para['paraContinue']['beginDate']['value'])+' - '+str(refreshTimes))
        #                                time.sleep(10)
        #                                if refreshTimes >= 10:
        #                                    print('Refresh driver error')
        #                                    logger.error('Refresh driver error')
        #                                    raise ValueError('Refresh driver error')

                            sN+=1
                            para['paraContinue']['searchNews'] = sN

                        nN+=1
                        para['paraContinue']['searchNews'] = 0
                        para['paraContinue']['newspapersNum'] = nN

                    tN+=1
                    para['paraContinue']['searchNews'] = 0
                    para['paraContinue']['newspapersNum'] = 0
                    para['paraContinue']['topicNum'] = tN

                d.close()
                d.quit()
                break

            except:
                d.close()
                d.quit()
                para['paraContinue']['beginDate']['status'] = 'on'
                print('Error and re-login to start from ' + str(para['paraContinue']['beginDate']['value']))
                logger.error('Error and re-login to start from ' + str(para['paraContinue']['beginDate']['value']))

        except:

            d.close()
            d.quit()
            para['paraContinue']['beginDate']['status'] = 'on'
            print('Error and re-login to start from ' + str(para['paraContinue']['beginDate']['value']))
            logger.error('Error and re-login to start from ' + str(para['paraContinue']['beginDate']['value']))

            d = webdriver.Chrome(chromedriverDirectory)
            loginToInfoQ(d,para)
            logger.error('Re-login to IQNewsClip')

    dateAll = genDateAll(para)
    Result = [dateAll]
    Header = ['date']
    for nspS in range(len(newspapersSelect)):
        uniq = c.execute('SELECT DISTINCT topic,searchNews FROM '+table_name+' WHERE newspapers = "'+newspapersSelect[nspS] +'"').fetchall()
        for un in uniq:
            countA = [0]*len(dateAll)
            result = c.execute('SELECT newsDate FROM ' + table_name + ' WHERE topic LIKE "' + un[0].replace('"','_').replace(' ','_') + '" AND searchNews LIKE "' + un[1].replace('"','_').replace(' ','_') + '" AND newspapers LIKE "' + newspapersSelect[nspS].replace('"','_').replace(' ','_') + '"').fetchall()
            for res in result:
                [d,m,y] = res[0].split('/')
                dateA = ((int(y)+2500)-543)*100+int(m)
                countA[dateAll.index(dateA)] = countA[dateAll.index(dateA)]+1
            Result.append(countA)
            Header.append(un[0]+'/'+un[1]+'/'+newspapersSelect[nspS])

    ResultDF = pd.DataFrame(Result)
    ResultDF = pd.DataFrame.transpose(ResultDF)
    excelName = 'NewsCount'
    writer = pd.ExcelWriter(excelName+'.xlsx',engine='xlsxwriter')
    sheetName = 'NewsCount'
    ResultDF.to_excel(writer, sheet_name=sheetName,header=Header, index=False, startrow=2)
    worksheet = writer.sheets[sheetName]
    worksheet.write(0, 0, 'News count')
    writer.save()
