# -*- coding: euc-kr -*-
import requests
import json
import time
import os
import csv
from pathlib import Path

import websockets

# OpenAPI ����
# https://openapi.ebestsec.co.kr/intro

# ����
# 1. pip install websockets
# 2. ������ KEY ���� �߰�
# 3. down�ϰ��� �ϴ� ����
# 4. down�ϰ��� �ϴ� ticker
# 5. tick-download.py ����
#    �ѹ� �� �����϶�� �ϸ� �� ȭ��ǥ ������ �ѹ� �� ����
# 6. download �������� tick-merge.py ����
# 7. down ���� tick data�� future_tick folder�� ����

APP_KEY = "������ key"
SECRET_KEY = "������ sec key"

date   = '20240125'
ticker = '101V3000'


# ���� ������ �ʿ���� �κ�
BASE_URL = "https://openapi.ebestsec.co.kr:8080"

n_tick = 1 # �����ϰ��ϴ� ƽ ����

# download ������ �ʿ��� folder.
# �ʿ��� dir�� �ִ��� Ȯ��, ������ �����.
FO_TICK_PATH_SEQ = '.\\future_tick_seq'

# download�� ����� ������ folder.
# �ٸ� �̸��� ���Ѵٸ� �Ʒ� �̸��� �ٲ۴�
FO_TICK_PATH = '.\\future_tick'

# ���� ������ �ʿ���� �κ� ��


if not os.access(FO_TICK_PATH_SEQ, os.F_OK):
    os.makedirs(FO_TICK_PATH_SEQ, exist_ok=True)
if not os.access(FO_TICK_PATH, os.F_OK):
    os.makedirs(FO_TICK_PATH, exist_ok=True)

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

#
# for writing data with json format to file
#
def save_to_file_json(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
       json.dump(data, make_file, ensure_ascii=False, indent="\t") 
    make_file.close()

#
# for reading data with json format from file
#
def load_json_from_file(file_name, err_msg=1) :
    try :
        with open(file_name,'r',encoding="cp949") as make_file: 
           data=json.load(make_file) 
        make_file.close()
    except  Exception as e : # �Ǵ� except : 
        data = {}
        if err_msg :
            print(e, file_name)
    return data
   
# �Ļ����� ���� �޿��� �ڵ� �ο�
def get_token_websocket():
    PATH = "/oauth2/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    body = {
        "appkey": APP_KEY,
        "appsecretkey": SECRET_KEY,
        "grant_type": "client_credentials",
        "scope": "oob"
    }
    result = requests.post(BASE_URL+PATH, headers=headers, data=body)
    return result

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

# ncnt : tick ����(n tick) 1, 3, 5 ���
# qrycnt : ��û�Ǽ� �ѹ� �Ҹ����� �� �ִ� tick �� max 500
# edate : �ް��� �ϴ� ����
# ctsdate : ���� ��ȸ�� ����
# ctsdate : ���� ��ȸ�� �ð�
def get_n_tick_fo(ticker, ncnt, qrycnt, edate, ctsdate=' ', ctstime=' '):
    block = 't8414InBlock'
    PATH = "/futureoption/chart"
    cont = 'Y'
    if ctsdate == ' ' : # ó������(ctsdate ���� ' '�� �ƴϸ�) ������ȸ 0 ���Ŀ��� 1
        cont = 'N'
    
    headers = {"content-type": "application/json; charset=utf-8", "authorization": "Bearer "+token,
               "tr_cd": "t8414", "tr_cont": cont, "tr_cont_key": "0"}
    body = {
              block: {
                "shcode": ticker,
                "ncnt": 1,
                "qrycnt": qrycnt,
                "nday": '0',
                "sdate": "",
                "stime": "",
                "edate": edate,
                "etime": "",
                "cts_date": ctsdate,
                "cts_time": ctstime,
                "comp_yn": "N"              
                }
            }         

    result = requests.post(BASE_URL+PATH, headers=headers, data=json.dumps(body))
    
    body = result.json()
    if '00000' != body['rsp_cd'] : # ������, ���� �޼��� ��� ����
        print(body['rsp_msg'])
        return None

    return [body['t8414OutBlock1'], body['t8414OutBlock']]

#repeat : merge�� �ִ� seq ��
def merge_fop_data_tick(in_folder, out_foler, dt, ticker, repeat) :
    merged = []
    pre_data = []
    for seq in range(repeat,0,-1) :
        fname = 'seq_' + dt + '_fut_' + ticker + '_tick-1-' + str(seq)+'.csv'
        if seq % 50 == 0:
            print(fname)  
        data = read_csv_to_dict(in_folder+'\\'+fname)
        if len(data) == 0 :
            continue
        # ��¥�� Ʋ�� ��� ����
        if dt != data[0]['date']:
            data = get_tick_data_remove_dif_date(data, dt)
        # �ߺ��� �����ʹ� ����
        data = get_tick_data_after_remove_dup(data, pre_data)
        merged += data
        pre_data = data
    if len(merged) > 0 :
        fname = dt + '_fut' + '_' + ticker+ '_tick-1.csv'
        save_to_file_csv(out_foler+'\\'+fname, merged)

# ��¥�� Ʋ�� �ڷ� ����
def get_tick_data_remove_dif_date(data, dt):
    cnt = 0
    for each in data:
        if each['date'] != dt:
            cnt += 1
        else:
            return data[cnt:]
    print('error get_tick_data_remove_dif_date()')
    return data

# ������ merge�ϹǷ� ū ���ڿ� �ִ� ������ ��Ȯ��. ���� data�� �� �ߺ��Ǵ� �� ����
def get_tick_data_after_remove_dup(data, pre_data):
    if len(pre_data) == 0 : # ������
        return data

    if pre_data[-1]['time'] == data[0]['time']:
        dup = 0
        if 1:
            last = data[0]['time']
            dup = 0
            for each in data:
                if each['time'] == last:
                    dup += 1
                else:
                    return data[dup:]  # �ߺ����� ���� �����͸� ������
    else:
        return data

# tick �������� msec�� ������ ���� �ޱ��� ���� �ɸ��� ��쿡 ebest api ���� ����
#1530028601  1
#1530028601  2
#1530029153  <- �Ʒ��� ���⸦ ã�� �ڵ���
# ������ ���� �ڼ��� ������ �Ʒ� �� ����        
# https://money-expert.tistory.com/97
def get_cts_time(ret):
    pos = 0
    last = ret[0]['time']
    for each in ret :
        if each['time'] == last :
            pos += 1
            last = each['time']
            continue
        else :
            ctstime = ret[pos]['time']
            return ctstime
    print('error get_cts_time() ')
    return ret[0]['time']

# 1�ʿ� �ѹ��� 
# 10�п� 200��.. 200���� �ѱ��� �ʰ� 10���� ��ٷ���
# future ������ ���� ����
def save_fo_tick_data(ticker, n_tick, edate) :
    ctsdate = ' '
    ctstime = ' '
    times = 0 # �� �� �ݺ��ؼ� �Ҹ���������
    
    repeat = 200 # 10�п� 200�������� ����
    query_cnt = 500

    # for test
    if 0:
        repeat = 2
        query_cnt = 6
    # end test

    # ���� ��ȸ���� Ȯ��
    save_status = {}
    st_name = 'future_cont.txt' # download �� ����� ���� �����Ͽ��� ��
    file_path = Path(st_name)
    if file_path.is_file():
        save_status = load_json_from_file(st_name)
        
    if len(save_status) == 0 : # ������ ���ٸ� ����
        save_status = {'ctsdate':' ', 'ctstime':' ', 'end':0, 'times':0, 'normal':0}
        save_to_file_json(st_name, save_status)
    else: 
        if save_status['normal'] == 0 : # ������ ������ �ٽ� ó������
            save_status = {'ctsdate':' ', 'ctstime':' ', 'end':0, 'times':0, 'normal':0}
            save_to_file_json(st_name, save_status)
            
    if save_status['end'] == 0 : # ��� down �޾ƾ� �Ѵ�.
        ctsdate = save_status['ctsdate']
        ctstime = save_status['ctstime']
        times   = save_status['times']
    print(save_status)    
    print('���� tick �ٿ�ε� ����', edate)
    if save_status['times'] == 0:
        print(' 4 - 5�� ���� �ɸ��ϴ�.')
    else:
        print(' 2 - 3�� ���� �ɸ��ϴ�.')
    
    for i in range(0, repeat) : # �ִ� 200��
        ret = get_n_tick_fo(ticker, n_tick, query_cnt, edate, ctsdate=ctsdate, ctstime=ctstime) # 
        if len(ret[0]) == 0 : # tick data �б� ����
            print('tick reading err')
            break

        data = ret[0] # ƽ ������ �������
        end = 0
        
        seq = str(i+1 + times*repeat) # times�� ����� �Ź� ������ sequence ��ȣ�� ���

        # ��¥�� ����Ǿ����� ����
        if ret[1]['cts_date'] != edate :
            end = 1
            save_status['end'] = 1

        # ���� tick ������ ����
        fname = FO_TICK_PATH_SEQ + '\\seq_' + edate + '_fut' + '_' + ticker + '_tick-' + str(n_tick) + '-' + str(seq) + '.csv'        
        save_to_file_csv(fname, data)

        if end :
            info = {'ticker':ticker, 'date':edate, 'max':seq}
            save_to_file_json(FO_TICK_PATH_SEQ+'\\info.txt', info)
            break
        
        time.sleep(1)
            
        ctsdate = ret[1]['cts_date']
        ctstime = get_cts_time(ret[0]) # ������ �о���� tick�� tm. api ������ �־ ������ �����
                        
        save_status['ctsdate'] = ctsdate
        save_status['ctstime'] = ctstime

        # �߰� �߰� ���
        if i % 10 == 0 :
            print(ctsdate, ctstime[0:6])

    # 200�� �̻� ȣ���� �ʿ��ϹǷ�, ���� ȣ��� 201������ �����ϱ� ����
    save_status['times'] += 1

    if save_status['end'] == 1 : # ��� ������        
        os.remove(st_name)
        print('\ntick download ��. �Ʒ� ���� �����Ͽ� merge�ϼ���.')
        print('python tick-merge.py')        
    else:
        print('save status', save_status)
        print('�ѹ� �� �����ϼ���!!')
        save_status['normal'] = 1
        save_to_file_json(st_name, save_status)

# OpenAPI ����� ���� token �����
token = get_token()

# tick ������ �ٿ�ε�
save_fo_tick_data(ticker, n_tick, date)


