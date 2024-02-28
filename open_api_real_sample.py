# -*- coding: euc-kr -*-
import requests
import json
import time

import asyncio
import websockets

# OpenAPI 문서
# https://openapi.ebestsec.co.kr/intro

# 절차
# 1.  pip install websockets
#     pip install asyncio
#     pip install colored
#     등등 package 없다고 하면 같은 방식으로 install
# 2. 본인의 KEY 정보 추가

# 만약 새로운 real 함수로 변경하고 싶다면
#  1. real함수 등록
#     reg_future_sise -> reg_new_my_func()
#  2. 함수명 변경하여 새로 작성
#     future_sise_real() -> new_my_func()
#     on_future_sise() -> on_new_my_func()  실시간 값을 받으면 불리어질 함수 callback이라고 부름
#  3. asyncio.run(new_my_func())

APP_KEY = "본인의 key"
SECRET_KEY = "본인의 sec key"

# 이하 수정할 필요없는 부분
BASE_URL        = "https://openapi.ebestsec.co.kr:8080"
BASE_URL_WEBS   = "wss://openapi.ebestsec.co.kr:9443/websocket"

   
# 파생인의 쉼터 꿈에님 코드 인용
def get_token():
    PATH = "/oauth2/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    body = {
        "appkey": APP_KEY,
        "appsecretkey": SECRET_KEY,
        "grant_type": "client_credentials",
        "scope": "oob"
    }
    result = requests.post(BASE_URL+PATH, headers=headers, data=body)

    body = result.json()

    return body["access_token"]


# 선물 실시간 시세용 message
def reg_future_real(cd, ticker):
    dt = {
        'header': {
            "token": get_token(),
            "tr_type": "3"  #3:실시간 등록
        },  
        'body' : {
            "tr_cd": cd,
            "tr_key": ticker,     
        }         
    }
    return json.dumps(dt) # json을 string으로 변환

# 선물 체결 정보가 불리어지는 부분
# 이 함수에서 원하는 형태로 가공

# 실시간 선물 체결정보 출력
def on_future_sise(data):
    price    = float(data['price'])
    vol      = int(data['cvolume'])
    offerho1 = float(data['offerho1'])
    bidho1   = float(data['bidho1'])

    print(format(price, '5.2f'), format(vol, '4d'), format(offerho1, '5.2f'), format(bidho1, '5.2f'))

FUTURE_SISE       = 'FC0'

# 웹 소켓 관련 신경쓸 필요없음
import websockets
async def real_api(real_code, ticker):
    while True:
    # 웹 소켓에 접속을 합니다.
        async with websockets.connect(BASE_URL_WEBS) as websocket:
            str = reg_future_real(real_code, ticker)

            # 웹 소켓 서버로 데이터를 전송합니다.
            await websocket.send(str);
            print('wait')
            time.sleep(2)
            
            while True:
                # 웹 소켓 서버로 부터 메시지가 오면 콘솔에 출력합니다.
                data_s = await websocket.recv();
                data = json.loads(data_s)
                if data['body'] == None: # 시세가 바로 오지 않음 None이면 waiting
                    time.sleep(1)
                    continue

                if real_code == FUTURE_SISE:
                    on_future_sise(data['body'])

if __name__ == '__main__':
  
    ticker = '101V3000'     # 2024년 3월 만기 선물
    cd = FUTURE_SISE
    asyncio.run(real_api(cd, ticker))

