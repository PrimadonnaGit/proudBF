import requests
import csv

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

    data = load_csv('서울비츠(05_03)_1.csv')
    api = Kakaoapi()

    for d in data:
        query, location = d
        id, address = api.keyword_req(query, location)
        if address:
            print(id, query, location, address)
