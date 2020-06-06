import requests
import csv 


headers = {
    "X-Naver-Client-Id" : "xAE6EDvfAifDpjpPKlaL",
    "X-Naver-Client-Secret" : "qRbN6y9JxO"
}

url = "https://openapi.naver.com/v1/search/local.json"



query = "ㅊㅇ누"
location = "성수"

data = {
    "query" : query
}

res = requests.get(url, params=data, headers=headers)
resJson = res.json()

print(resJson)
if resJson['total'] > 0:
    for item in resJson['items']:
        print(item['address'])



    