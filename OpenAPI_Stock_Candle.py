# -*- coding: euc-kr -*-

import requests
import json
import os
import csv

import websockets

# https://openapi.ebestsec.co.kr/intro

APP_KEY = "본인의 KEY"
SECRET_KEY = "본인의 SEC KEY"

BASE_URL = "https://openapi.ebestsec.co.kr:8080"

# 첫 줄은 title이라고 가정, 이후에 title 값을 key로 갖는 dict로 읽기
def get_new_item(keys, row) :
    data = {}
    num_none = 0
    for i in range(len(row)) :
        if row[i] == '' :
            num_none += 1
        data[keys[i]] = row[i]
    if num_none == len(row) : # end
        return None
    return data
def read_csv_to_dict(fname, encoding='utf-8') :
    data = []
    keys =[]
    first = 1
    cnt = 0
    try :
    #    with open(fname, 'r', encoding='cp949') as FILE :
        with open(fname, 'r') as FILE :
            csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
            for row in csv_reader :
                cnt+=1
                if first : # make dict keys
                    keys = row.copy()
    #                for key in row :
    #                    keys .append(key)
                    first = 0
                else :          
                    ret = get_new_item(keys, row)
                    if ret == None :
                        return data      
                    data.append(ret)
    except  Exception as e : # 또는 except : 
        data = []
        print(e, fname)
    
    return data
#
# for writing dic data to cvs format
#
def save_to_file_csv(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        # title 저장
        vals = data[0].keys()
        ss = ''
        for val in vals:
            val = val.replace(',','')
            ss += (val + ',')
        ss += '\n'
        make_file.write(ss)

        for dt in data:
            vals = dt.values()
            ss = ''
            for val in vals:
                sval = str(val) 
                sval = sval.replace(',','')
                ss += (sval + ',')
            ss += '\n'
            make_file.write(ss)
    make_file.close()

def get_token():
    URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "/oauth2/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    body = {
        "appkey": APP_KEY,
        "appsecretkey": SECRET_KEY,
        "grant_type": "client_credentials",
        "scope": "oob"
    }
    result = requests.post(URL+PATH, headers=headers, data=body)

    header = result.headers
    body = result.json()
    if 0:
        print("-----header----")
        print(header)
        print("----------------\n\n")
        print("-----body-----")
        print(body)
        print("--------------\n\n")

    return body["access_token"]


# 기간별 주가 조회 t1305

# qrycnt : 요청건수 한번 불리어질 때 최대 tick 수 max 500
# dwmcode : 일/주/월  1/2/3
# edate : 받고자 하는 일자
# ctsdate : 연속 조회시 일자
# ctsdate : 연속 조회시 시간
def get_stock_dwm_info(ticker, qrycnt, dwmcode=1, edate = ' ', tr_cont_key=''):
    PATH = "/stock/market-data"
    # 연속여부 판단
    cont = 'N'
    if tr_cont_key != '' :
        cont = 'Y'
        
    headers = {
            "content-type": "application/json; charset=utf-8", "authorization": "Bearer "+token,
            "tr_cd": "t1305", 
            "tr_cont": cont, 
            "tr_cont_key": tr_cont_key
    }
    
    body = {
        "t1305InBlock": { 
            "shcode": ticker, 
            "dwmcode": dwmcode,   # 1@일, 2@주, 3@월
            "date": edate,   # 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정
            "idx": 0,       # 무시
            "cnt": qrycnt   # 건수
            } 
        }
    
    result = requests.post(BASE_URL+PATH, headers=headers, data=json.dumps(body))
    
    header = result.headers
    body = result.json()

    if 0:   # 필요하다면 찍어서 return되는 값 보기
        header = result.headers
        print("-----header----")
        print(header)
        print("----------------\n\n")
        print("-----body-----")
        print(json.dumps(body, indent=4))
        print("--------------\n\n")
    # 사용하기 쉽게 저장구조 변경
    # api query 후 받아서 사용하는 곳에서는 tr 번호별로 처리하기가 어려움
    # 따라서 단순하게 dict 형태를 dict list로 변경
    
    return body["t1305OutBlock1"]

token = get_token()

ticker = '069500' # kodex 200
qrycnt = 2          # 몇 개를 받을지
dwmcode = 1         # 일봉:1,  주봉:2, 월봉:3

# infos : candle info
infos = get_stock_dwm_info(ticker, qrycnt, dwmcode)
for info in infos : 
    print(json.dumps(info, indent=4))

# 저장    
fname = ticker + '_day.csv'
save_to_file_csv(fname, infos)

# 읽기
data = read_csv_to_dict(fname)
print('읽은 값')
for info in data : 
    print(json.dumps(info, indent=4))
