import requests
import csv

def load_csv(filename):
    data = []
    with open(filename) as f:
        reader = csv.reader(f)
        for r in reader:
            data.append(r)
    return data

host = "http://dapi.kakao.com/v2/local/search/address.json"
headers = {
    'Authorization' : 'KakaoAK cc116147fce20da7314166dce21f0305'
}

data = load_csv('1007.csv')

for i, d in enumerate(data):
    title, tag, address, _, like, insta, img, timestamp = d

    data = {
        "query" : address
    }

    res = requests.get(host, params=data, headers=headers)

    resJson = res.json()
    try:
        a = resJson['documents'][0]

        try:
            y,x = a['address']['y'], a['address']['x']
        except:
            y,x = a['road_address']['y'], a['road_address']['x']

    except:
        print(title, address, resJson)
        y,x = 0,0
    finally:
        with open('1007_f.csv', 'a', newline='', encoding='cp949') as f:
            writer = csv.writer(f)
            writer.writerow([i, title , y, x, tag, address, like, insta, img])