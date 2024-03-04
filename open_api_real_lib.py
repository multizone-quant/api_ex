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

APP_KEY = "본인의 key"
SECRET_KEY = "본인의 sec key"

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

async def real_api(tr_code, func, ticker):
    while True:
    # 웹 소켓에 접속을 합니다.
        async with websockets.connect(BASE_URL_WEBS) as websocket:
            # real code 등록
            print('real 등록 시작')
            str = reg_future_real(tr_code, ticker)
            # 웹 소켓 서버로 데이터를 전송합니다.
            await websocket.send(str);
            print('real 등록 끝')
            time.sleep(1)

            while True:
                # 웹 소켓 서버로 부터 메시지가 오면 콘솔에 출력합니다.
                data_s = await websocket.recv();
#                print(data_s)
                data = json.loads(data_s)
                if data['body'] == None: # 시세가 바로 오지 않음 None이면 waiting
                    time.sleep(1)
                    continue

                func(data['body'])  # tr_code에 해당하는 callback 부름

def main_loop(tr_code, func, ticker):
    asyncio.run(real_api(tr_code, func, ticker))
    
if __name__ == '__main__':
    print('open_api_real_lib')

