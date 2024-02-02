# -*- coding: euc-kr -*-

import requests
import json
import os
import csv

import websockets

# https://openapi.ebestsec.co.kr/intro

APP_KEY = "������ KEY"
SECRET_KEY = "������ SEC KEY"

BASE_URL = "https://openapi.ebestsec.co.kr:8080"

# ù ���� title�̶�� ����, ���Ŀ� title ���� key�� ���� dict�� �б�
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
    except  Exception as e : # �Ǵ� except : 
        data = []
        print(e, fname)
    
    return data
#
# for writing dic data to cvs format
#
def save_to_file_csv(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        # title ����
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


# �Ⱓ�� �ְ� ��ȸ t1305

# qrycnt : ��û�Ǽ� �ѹ� �Ҹ����� �� �ִ� tick �� max 500
# dwmcode : ��/��/��  1/2/3
# edate : �ް��� �ϴ� ����
# ctsdate : ���� ��ȸ�� ����
# ctsdate : ���� ��ȸ�� �ð�
def get_stock_dwm_info(ticker, qrycnt, dwmcode=1, edate = ' ', tr_cont_key=''):
    PATH = "/stock/market-data"
    # ���ӿ��� �Ǵ�
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
            "dwmcode": dwmcode,   # 1@��, 2@��, 3@��
            "date": edate,   # ó�� ��ȸ�ô� Space ���� ��ȸ�ÿ� ���� ��ȸ�� OutBlock�� date ������ ����
            "idx": 0,       # ����
            "cnt": qrycnt   # �Ǽ�
            } 
        }
    
    result = requests.post(BASE_URL+PATH, headers=headers, data=json.dumps(body))
    
    header = result.headers
    body = result.json()

    if 0:   # �ʿ��ϴٸ� �� return�Ǵ� �� ����
        header = result.headers
        print("-----header----")
        print(header)
        print("----------------\n\n")
        print("-----body-----")
        print(json.dumps(body, indent=4))
        print("--------------\n\n")
    # ����ϱ� ���� ���屸�� ����
    # api query �� �޾Ƽ� ����ϴ� �������� tr ��ȣ���� ó���ϱⰡ �����
    # ���� �ܼ��ϰ� dict ���¸� dict list�� ����
    
    return body["t1305OutBlock1"]

token = get_token()

ticker = '069500' # kodex 200
qrycnt = 2          # �� ���� ������
dwmcode = 1         # �Ϻ�:1,  �ֺ�:2, ����:3

# infos : candle info
infos = get_stock_dwm_info(ticker, qrycnt, dwmcode)
for info in infos : 
    print(json.dumps(info, indent=4))

# ����    
fname = ticker + '_day.csv'
save_to_file_csv(fname, infos)

# �б�
data = read_csv_to_dict(fname)
print('���� ��')
for info in data : 
    print(json.dumps(info, indent=4))
