# -*- coding: euc-kr -*-
import json
import time

from open_api_real_lib import main_loop 

# OpenAPI 문서
# https://openapi.ebestsec.co.kr/intro

# 절차
# 1.  pip install websockets
#     pip install asyncio
#     pip install colored
#     등등 package 없다고 하면 같은 방식으로 install

# 2. 본인의 KEY 정보 추가 (open_api_real_lib.py에서 추가)
# 3. 실행  
#    python my_open_api_real.py

# 만약 새로운 real 함수로 변경하고 싶다면
#  1. real code 정의
#     예) FUTURE_ORDER_BOOK = 'FH0'
#  2. 1번 real code 등록 후 받을 함수 정의
#     예)on_future_order_book(data):
#  3. input() 전 print문에 추가, input() 후 elif에 1,2번 정보 추가


# 선물 체결 정보가 불리어지는 부분
# 이 함수에서 원하는 형태로 가공

sise_head = 1
def on_future_sise(data):
    global sise_head
    if sise_head : # 처음 불리어질 때만 출력
        print('----------------------------------')
        print(' 체결가  수량   매도호가  매수호가')
        print('----------------------------------')
        sise_head = 0
    
    price    = float(data['price'])
    vol      = int(data['cvolume'])
    offerho1 = float(data['offerho1'])
    bidho1   = float(data['bidho1'])

    print(format(price, '5.2f'), format(vol, '4d'), '    ', format(offerho1, '5.2f'), '  ', format(bidho1, '5.2f'))

# 선물 호가창, 아래/위 2개만 추가함. 최대 5개까지 호가 정보가 옴
def on_future_order_book(data):
    print(data['hotime'])
    print('--------------------------------')
    print(' 건수  수량   가격   수량  건수')
    print('--------------------------------')
    print(format(int(data['offercnt2']), '4,d'),
          format(int(data['offerrem2']), '4,d'), ' ',
          format(data['offerho2']))
    print(format(int(data['offercnt1']), '4,d'),
          format(int(data['offerrem1']), '4,d'), ' ',
          format(data['offerho1']))
    print(format(' ',  '11s'), 
          format(data['bidho1']), 
          format(int(data['bidcnt1']), '5,d'),
          format(int(data['bidrem1']), '5,d'))
    print(format(' ', '11s'), 
          format(data['bidho2']), 
          format(int(data['bidcnt2']), '5,d'),
          format(int(data['bidrem2']), '5,d'))

if __name__ == '__main__':
    # TR codes
    FUTURE_SISE       = 'FC0'
    FUTURE_ORDER_BOOK = 'FH0'

    # 관심있는 ticker 정보
    ticker = '101V3000'     # 2024년 3월 만기 선물

    print('선택')
    
    # 새로운 REAL TR 추가시 print문에도 추가
    print('1: 선물시세  2:선물호가창')
    sel = input()

    if sel == '1' :
        tr_code = FUTURE_SISE
        func    = on_future_sise

    elif sel == '2' :
        tr_code = FUTURE_ORDER_BOOK
        func    = on_future_order_book

#   새로운 REAL TR 추가시 elif로 추가
#    elif sel == '3' :
#        tr_code = 새로운 REAL_TR
#        func    = on_...  # tr_code 메세지를 받을 함수

    main_loop(tr_code, func, ticker)

