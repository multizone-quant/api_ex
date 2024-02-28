# -*- coding: euc-kr -*-
import requests
import json
import time
from termcolor import colored

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

# val값을 col 색으로 변환
def get_colored_str(val, col):
    s_val = colored(val, col)
    return s_val
def TODAY_TIME_SP() :
    return time.strftime("%H:%M:%S")

#-----------------------------------------
# 실시간 메세지에 따라 개별 코딩이 필요함 부분
# 선물 실시간 시세용 message
def reg_future_sise(ticker):
    dt = {
        'header': {
            "token": get_token(),
            "tr_type": "3"  #3:실시간 등록
        },  
        'body' : {
            "tr_cd": 'FC0',
            "tr_key": ticker,     
        }         
    }
    return json.dumps(dt) # json을 string으로 변환
  
acc_vol = 0 # 누적 vol
# 선물 체결 정보가 불리어지는 부분
# 이 함수에서 원하는 형태로 가공

# 특정 체결수량 이상 모니터링하는 코드
# int_vol값을 변경하면 됨 현재는 10
def on_future_sise(data):
    global acc_vol
    int_vol = 10    
    tm = TODAY_TIME_SP()

    price    = float(data['price'])
    vol      = int(data['cvolume'])
    offerho1 = float(data['offerho1'])
    bidho1   = float(data['bidho1'])

    if vol >= int_vol:
        # 호가를 보고 매수호가에 체결이면 하방(파랑), 매도호가에 체결되면 상방(빨강)
        # off호가 빨강, bid호가 파랑
        if offerho1 == price : # 빨강            
            c_price = get_colored_str(format(price, '5.2f'), 'red')
            acc_vol += vol
        else: # 파랑            
            c_price = get_colored_str(format(price, '5.2f'), 'blue')
            acc_vol -= vol
        print(tm, c_price, vol, format(offerho1, '5.2f'), format(bidho1, '5.2f'), format(acc_vol, '6,d'))
    

# 웹 소켓 관련
import websockets
async def future_sise_real():
    ticker = '101V3000'
    while True:
    # 웹 소켓에 접속을 합니다.
        async with websockets.connect(BASE_URL_WEBS) as websocket:
            str = reg_future_sise(ticker)
#            print(str)

            # 웹 소켓 서버로 데이터를 전송합니다.
            await websocket.send(str);
            print('wait')
            time.sleep(10)
            
            while True:
                # 웹 소켓 서버로 부터 메시지가 오면 콘솔에 출력합니다.
                data_s = await websocket.recv();
#                print(data_s)
                data = json.loads(data_s)
                if data['body'] == None: # 시세가 바로 오지 않음 None이면 waiting
                    time.sleep(1)
                    continue
#                print(data)
                on_future_sise(data['body'])

if __name__ == '__main__':
    asyncio.run(future_sise_real())


