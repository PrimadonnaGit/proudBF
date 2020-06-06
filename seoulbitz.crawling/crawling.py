from selenium.webdriver.chrome import webdriver, options

from bs4 import BeautifulSoup
import glob
import os
import time
import re
import csv
import requests
import pandas as pd


class InstagramScrap():
    
    def __init__(self, instaID=None, tag=None):
        self.baseUrl = 'https://www.instagram.com/' + (instaID if tag is None else 'explore/tags/' + tag)
        self.instaID = instaID
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
            'referer': self.baseUrl
            }
        #self.options = options.Options.add_argument()
        self.driver = webdriver.WebDriver('driver/chromedriver_83_win32.exe')

    # scorlling slowly by speed
    def scrolling(self, speed=8):
        current_scroll_position, new_height= 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")

    # Update Contents
    def scrollToBottom(self):
        soupList = []
        speed = 1000
        new_height = 1001
        current_scroll_position = 0
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            soupList.append(BeautifulSoup(self.driver.page_source, 'html.parser'))

        return soupList

    def getContents(self):
        self.driver.get(self.baseUrl)       
        soupList = self.scrollToBottom()

        hrefs = []
        for soup in soupList:
            for x in soup.select('article > div > div > div > div > a'):
                hrefs.append(x['href'])

        return list(set(hrefs))

    def getContent(self, href):

        contentUrl = 'https://www.instagram.com/' + href
        self.driver.get(contentUrl)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        if not soup.select_one('article > header > div > div > div > a').text == self.instaID:
            return -1

        contentag = soup.select_one('article > div > div > ul > div > li > div > div > div > span')
        like = int(soup.select_one('article > div > section > div > div > button > span').text)

        img = soup.select_one('article > div > div > div > div > div > div > div > ul > li > div > div > div > div > div > img')
        if img == None:
            img = soup.select_one('article > div > div > div > div > div > div > div > ul > li > div > div > div > div > img')
        img = img['src']

        # clean html tags
        clean_html = re.compile('<.*?>')
        content = [re.sub(clean_html, '', text) if text.startswith('<') else text for text in str(contentag).split('<br/>')]

        for i, text in enumerate(content):
            hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
            if hanCount > 0:
                return content, img, i, like

class KakaoAPI():

    def __init__(self):
        self.apikey = 'cc116147fce20da7314166dce21f0305'
        self.host = 'http://dapi.kakao.com'
        self.header = {
            'Authorization' : 'KakaoAK ' + self.apikey
        }
        
    def keyword_req(self, q, loc):
        url = '/v2/local/search/keyword'

        params = {
            'query': q,
        }

        res = requests.get(self.host + url, params=params, headers=self.header)
        if res.status_code == 200:
            documents = res.json()['documents']
        else:
            print(res.text)
            return -1, False

        addresslist = []
        for d in documents:
            address_name = d['address_name']
            if not loc in address_name:
                continue
            else:
                addresslist.append(address_name)
                break

            #x, y  = d['x'], d['y']
            #road_address_name = d['road_address_name']
        return addresslist[0] if len(addresslist) else ''

class NaverAPI():

    def __init__(self):

        self.host = 'https://openapi.naver.com/v1/search/local.json'
        self.header = {
            "X-Naver-Client-Id" : "xAE6EDvfAifDpjpPKlaL",
            "X-Naver-Client-Secret" : "qRbN6y9JxO"
        }
        self.data = load_csv('output.csv')
    
    def keyword_req(self):
        for d in self.data:
            time.sleep(0.5)

            query , location, like, insta, img = d
            data = {
                "query" : query
            }

            res = requests.get(self.host, params=data, headers = self.header)
            resJson = res.json()
            addressList = []

            if resJson['total'] > 0:
                for item in resJson['items']:
                    if location in item['address'] and '서울' in item['address']:
                        addressList.append((item['address'], item['category']))
                    
                if len(addressList):
                    address_full, category = addressList[0]
                else:
                    address_full, category = '', ''
            else:
                address_full, category = '', ''

            with open('output_naver.csv', 'a', newline='', encoding='cp949') as f:
                writer = csv.writer(f)
                writer.writerow([query, location, address_full, category, like, insta, img])


def load_csv(filename):
    data = []
    with open(filename) as f:
        reader = csv.reader(f)
        for r in reader:
            data.append(r)
    return data

def deleteUnicode(text):
    return text.replace('\u200b','').replace('\u2063','')

if __name__ == '__main__':

    files = glob.glob('*.csv')
    for file in files:
        if os.path.isfile(file): os.remove(file)
            
    tag = 'seoulbitz_shopping'

    scraper = InstagramScrap(instaID = 'seoulbitz', tag = tag)
    uniqueHref = scraper.getContents()

    print('Get Instagram ...')
    for i, href in enumerate(uniqueHref):
        print('[{}/{}]'.format(i+1,len(uniqueHref)))
        try:
            content, img, kr_idx, like = scraper.getContent(href)

            if tag == 'seoulbitz_shopping':
                # 한글상호명 / 위치
                # 영어상호명 / 한글상호명
                try:
                    title, loc = [deleteUnicode(x.strip().replace(',','')) for x in content[kr_idx].split('/')]
                # 상호명
                except:
                    title = deleteUnicode(content[kr_idx].strip()) 
                    loc = '서울'
                    
            else:
                title, loc = [x.strip().replace(',','').replace('\u200b','').replace('\u2063','') for x in content[kr_idx].split('/')]
        except:
            print("Failed",i, href)
            continue

        with open('output.csv', 'a', newline='', encoding='cp949') as f:
            writer = csv.writer(f)
            writer.writerow([title , loc, like, 'https://www.instagram.com' + href, img])

    scraper.driver.quit()

    # KAKAO
    print('Finding Address ...')
    # data = load_csv('output.csv')
    # api = Kakaoapi()
 
    # for d in data:
    #     query, location, like, insta, img = d
    #     address = api.keyword_req(query, location)

    #     with open('output_kakao.csv', 'a', newline='', encoding='cp949') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([query,location,address, like, insta, img])

    # NAVER
    naverAPI = NaverAPI()
    naverAPI.keyword_req()










