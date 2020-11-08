from selenium.webdriver.chrome import webdriver, options

from bs4 import BeautifulSoup
import glob
import os
import time
import re
import csv
import requests
import pandas as pd


def load_csv(filename):
    data = []
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        for r in reader:
            data.append(r)
    return data

def deleteUnicode(text):
    return text.replace('\u200b','').replace('\u2063','')

class InstagramScrap():
    def __init__(self, instaID=None, tag=None):
        self.baseUrl = 'https://www.instagram.com/' + (instaID if tag is None else 'explore/tags/' + tag + '?hl=ko')
        self.instaID = instaID
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
            'referer': self.baseUrl
            }
        #self.options = options.Options.add_argument()
        self.driver = webdriver.WebDriver('driver/chromedriver_85_win32.exe')

    # scorlling slowly by speed
    def scrolling(self, speed=30):
        current_scroll_position, new_height= 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")

    def login(self):
      time.sleep(1.5)
      self.driver.find_element_by_css_selector("input[name='username']").send_keys('01092141833')
      self.driver.find_element_by_css_selector("input[name='password']").send_keys('kbj2277!')
      self.driver.find_elements_by_tag_name("button")[1].click()
      time.sleep(3)
      self.driver.find_elements_by_tag_name("button")[1].click()


    # Update Contents
    def scrollToBottom(self):
        soupList = []
        speed = 1000
        new_height = 1
        current_scroll_position = 0
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            soupList.append(BeautifulSoup(self.driver.page_source, 'html.parser'))

        return soupList

    def getContents(self):
        self.driver.get(self.baseUrl)
        try:
            self.login()
        except:
            pass
        soupList = self.scrollToBottom()

        hrefs = []
        for soup in soupList:
            for x in soup.select('article > div > div > div > div > a'):
                hrefs.append(x['href'])

        return list(set(hrefs))

    def getContent(self, href):
        # instaID_tag = 'article > header > div > div > div > span > a'
        content_tag = 'article > div > div > ul > div > li > div > div > div > span'
        like_tag = 'article > div > section > div > div > button > span'
        img_tag = 'article > div > div > div > div > div > div > div > ul > li > div > div > div > div > div > img'
        sub_img_tag = 'article > div > div > div > div > div > div > div > ul > li > div > div > div > div > img'
        timestamp_tag = 'article > div> div > a > time'
        contentUrl = 'https://www.instagram.com/' + href
        
        self.driver.get(contentUrl)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')           
        try:
            # print(soup.select_one(instaID_tag))
            # if not soup.select_one(instaID_tag).text in ['seoulbitz','seoulbitz_archive']:
            #     return -1

            content = soup.select_one(content_tag)
            like = int(soup.select_one(like_tag).text)

            imgs = []
            
            # Thumbnail
            img = soup.select_one(img_tag)
            subImgs = [i['src'] for i in soup.select(sub_img_tag)]
            # print(img,subImgs)
            if img == None:
                # SubImages
                imgs += subImgs
            else:
                imgs.append(img['src'])
                imgs += subImgs
            
            # print(imgs)
            timestamp = soup.select_one(timestamp_tag)['title']

            # clean html tags
            clean_html = re.compile('<.*?>')
            content = [re.sub(clean_html, '', text) if text.startswith('<') else text for text in str(content).split('<br/>')]
            # print(content)
            for i, text in enumerate(content):
                hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
                if hanCount > 0:
                    return content, imgs, i, like, timestamp
        except Exception as e:
            print(e)
            

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

    def getXY(self):
        self.host = "http://dapi.kakao.com/v2/local/search/address.json"

        data = load_csv('output_naver.csv')

        for i, d in enumerate(data):
            title, tag, address, _, like, insta, img, timestamp = d

            data = {
                "query" : address
            }

            res = requests.get(self.host, params=data, headers=self.header)

            resJson = res.json()
            try:
                a = resJson['documents'][0]

                try:
                    y,x = a['address']['y'], a['address']['x']
                except:
                    y,x = a['road_address']['y'], a['road_address']['x']

            except:
                y,x = 0,0
            finally:
                with open('output_final.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([i, title , y, x, tag, address, like, insta, img])

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

            query , location, like, insta, img, timestamp = d
            data = {
                "query" : query
            }

            res = requests.get(self.host, params=data, headers = self.header)
            resJson = res.json()
            addressList = []

            if resJson['total'] > 0:
                for item in resJson['items']:
                    # 서울내, location이 들어있을때 우선순위,
                    if location in item['address'] and '서울' in item['address']:
                        addressList.append((item['address'], item['category']))
                
                # 주소가 여러개면 첫번째것을 고름
                if len(addressList):
                    address_full, category = addressList[0]
                # location과 일치하지 않을경우
                else:
                    address_full, category = resJson['items'][0]['address'],resJson['items'][0]['category']
            # 결과가 없을 경우
            else:
                address_full, category = 'empty', 'empty'

            with open('output_naver.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([query, location, address_full, category, like, insta, img, timestamp])

if __name__ == '__main__':

    files = glob.glob('*.csv')
    for file in files:
        if os.path.isfile(file): os.remove(file)
            
    tag = 'seoulbitz_foodie'

    scraper = InstagramScrap(instaID = 'seoulbitz', tag = tag)
    uniqueHref = scraper.getContents()

    print('Get Instagram ...')
    for i, href in enumerate(uniqueHref):
        print('[{}/{}]'.format(i+1,len(uniqueHref)))
        try:
            content, imgs, kr_idx, like, timestamp = scraper.getContent(href)
            
            

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
                try:
                    title, loc = [x.strip().replace(',','').replace('\u200b','').replace('\u2063','') for x in content[kr_idx].split('/')]
                except:
                    title = [x.strip().replace(',','').replace('\u200b','').replace('\u2063','') for x in content[kr_idx].split('/')][0]
                    loc = '서울'
                    
        except Exception as e:
            print("Failed", e, href)
            continue

        with open('output.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([title , loc, like, 'https://www.instagram.com' + href, ','.join(imgs), timestamp])

    scraper.driver.quit()

    print('Finding Address ...')

    # NAVER get address
    naverAPI = NaverAPI()
    naverAPI.keyword_req()
    
    print('Finding lat&long ...')

    # KAKAO get lat,log
    kakaoAPI = KakaoAPI()
    kakaoAPI.getXY()
    
    # replace " to empty










