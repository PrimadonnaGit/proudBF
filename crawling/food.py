from selenium.webdriver.chrome import webdriver, options

from bs4 import BeautifulSoup
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
        self.driver = webdriver.WebDriver('crawling/chromedriver.exe')

    # scorlling slowly by speed
    def scrolling(self, speed=8):
        current_scroll_position, new_height= 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")

    # Update Contents
    def scrollToBottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def getContents(self, limits):
        self.driver.get(self.baseUrl)
        uniqueHref = []
        while(True):
            soup = self.scrollToBottom()
            href = [uniqueHref.append(x['href']) for x in soup.select('article > div > div > div > div > a')]
            if len(set(uniqueHref)) > limits: break

        return uniqueHref

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

class Kakaoapi():

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
            id = d['id']
            if not loc in address_name:
                continue
            else:
                addresslist.append((id, address_name))
                break

            #x, y  = d['x'], d['y']
            #road_address_name = d['road_address_name']
        return addresslist[0] if len(addresslist) else (-1, False)

def load_csv(filename):
    data = []
    with open(filename) as f:
        reader = csv.reader(f)
        for r in reader:
            data.append((r[:2]))
    return data

if __name__ == '__main__':

    scraper = InstagramScrap(instaID = 'seoulbitz', tag = 'seoulbitz_foodie')
    uniqueHref = scraper.getContents(limits=300)
    for i, href in enumerate(uniqueHref):
        print('[{}/{}]'.format(i+1,len(uniqueHref)))
        try:
            content, img, kr_idx, like = scraper.getContent(href)
            title, loc = [x.strip().replace(',','').replace('\u200b','').replace('\u2063','') for x in content[kr_idx].split('/')]
        except:
            continue

        with open('output.csv', 'a', newline='', encoding='cp949') as f:
            writer = csv.writer(f)
            writer.writerow([title,loc,like, 'https://www.instagram.com' + href,img])

    scraper.driver.quit()

    data = load_csv('output.csv')
    api = Kakaoapi()

    for d in data:
        query, location = d
        id, address = api.keyword_req(query, location)
        if address:
            with open('output_kakao.csv', 'a', newline='', encoding='cp949') as f:
                writer = csv.writer(f)
                writer.writerow([query,location,address])

    df = pd.read_csv('output.csv', encoding='cp949')
    df = df.drop_duplicates(keep='first')
    df.to_csv('output_clean.csv', encoding='cp949')

    df = pd.read_csv('output_kakao.csv', encoding='cp949')
    df = df.drop_duplicates(keep='first')
    df.to_csv('output_kakao_clean.csv', encoding='cp949')










