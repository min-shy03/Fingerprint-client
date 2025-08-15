import requests
import json

url = "http://fingerprint.bannote.org/api/fingerprint/logs"


datas = {
    "std_num": "1",
    "action": "등교"
}

responce = requests.post(url, json=datas)

responce_data = responce.json()

print(responce_data)
if responce.status_code == 200 or responce.status_code == 400 :
    print(responce_data["message"])
else :
    print("실패")