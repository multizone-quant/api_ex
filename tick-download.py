# -*- coding: euc-kr -*-
import requests
import json
import time
import os
import csv
from pathlib import Path

import websockets

# OpenAPI 문서
# https://openapi.ebestsec.co.kr/intro

# 절차
# 1. pip install websockets
# 2. 본인의 KEY 정보 추가
# 3. down하고자 하는 일자
# 4. down하고자 하는 ticker
# 5. tick-download.py 실행
#    한번 더 실행하라고 하면 위 화살표 눌러서 한번 더 실행
# 6. download 끝났으면 tick-merge.py 실행
# 7. down 받은 tick data는 future_tick folder에 있음

APP_KEY = "본인의 key"
SECRET_KEY = "본인의 sec key"

date   = '20240125'
ticker = '101V3000'


# 이하 수정할 필요없는 부분
BASE_URL = "https://openapi.ebestsec.co.kr:8080"

n_tick = 1 # 저장하고하는 틱 단위

# download 과정에 필요한 folder.
# 필요한 dir가 있는지 확인, 없으면 만든다.
FO_TICK_PATH_SEQ = '.\\future_tick_seq'

# download한 결과를 저장할 folder.
# 다른 이름을 원한다면 아래 이름을 바꾼다
FO_TICK_PATH = '.\\future_tick'

# 이하 수정할 필요없는 부분 끝


if not os.access(FO_TICK_PATH_SEQ, os.F_OK):
    os.makedirs(FO_TICK_PATH_SEQ, exist_ok=True)
if not os.access(FO_TICK_PATH, os.F_OK):
    os.makedirs(FO_TICK_PATH, exist_ok=True)

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
    except  Exception as e : # 또는 except : 
        data = {}
        if err_msg :
            print(e, file_name)
    return data
   
# 파생인의 쉼터 꿈에님 코드 인용
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

# ncnt : tick 단위(n tick) 1, 3, 5 등등
# qrycnt : 요청건수 한번 불리어질 때 최대 tick 수 max 500
# edate : 받고자 하는 일자
# ctsdate : 연속 조회시 일자
# ctsdate : 연속 조회시 시간
def get_n_tick_fo(ticker, ncnt, qrycnt, edate, ctsdate=' ', ctstime=' '):
    block = 't8414InBlock'
    PATH = "/futureoption/chart"
    cont = 'Y'
    if ctsdate == ' ' : # 처음에는(ctsdate 값이 ' '가 아니면) 연속조회 0 이후에는 1
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
    if '00000' != body['rsp_cd'] : # 오류임, 오류 메세지 찍고 종료
        print(body['rsp_msg'])
        return None

    return [body['t8414OutBlock1'], body['t8414OutBlock']]

# tick 데이터의 msec이 같은데 연속 받기의 끝에 걸리는 경우에 ebest api 오류 있음
#1530028601  1
#1530028601  2
#1530029153  <- 아래는 여기를 찾는 코드임
# 오류에 대한 자세한 사항은 아래 글 참고        
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

# 1초에 한번씩 
# 10분에 200건.. 200건이 넘기지 않고 10분은 기다려야
# future 데이터 저장 연속
def save_fo_tick_data(ticker, n_tick, edate) :
    ctsdate = ' '
    ctstime = ' '
    times = 0 # 몇 번 반복해서 불리어졌는지
    
    repeat = 200 # 10분에 200번까지만 가능
    query_cnt = 500

    # for test
    if 0:
        repeat = 2
        query_cnt = 6
    # end test

    # 연속 조회인지 확인
    save_status = {}
    st_name = 'future_cont.txt' # download 중 사용할 파일 무시하여도 됨
    file_path = Path(st_name)
    if file_path.is_file():
        save_status = load_json_from_file(st_name)
        
    if len(save_status) == 0 : # 파일이 없다면 생성
        save_status = {'ctsdate':' ', 'ctstime':' ', 'end':0, 'times':0, 'normal':0}
        save_to_file_json(st_name, save_status)
    else: 
        if save_status['normal'] == 0 : # 비정상 종료임 다시 처음부터
            save_status = {'ctsdate':' ', 'ctstime':' ', 'end':0, 'times':0, 'normal':0}
            save_to_file_json(st_name, save_status)
            
    if save_status['end'] == 0 : # 계속 down 받아야 한다.
        ctsdate = save_status['ctsdate']
        ctstime = save_status['ctstime']
        times   = save_status['times']
    print(save_status)    
    print('선물 tick 다운로드 시작', edate)
    if save_status['times'] == 0:
        print(' 4 - 5분 정도 걸립니다.')
    else:
        print(' 2 - 3분 정도 걸립니다.')
    
    for i in range(0, repeat) : # 최대 200번
        ret = get_n_tick_fo(ticker, n_tick, query_cnt, edate, ctsdate=ctsdate, ctstime=ctstime) # 
        if len(ret[0]) == 0 : # tick data 읽기 오류
            print('tick reading err')
            break

        data = ret[0] # 틱 정보가 들어있음
        end = 0
        
        seq = str(i+1 + times*repeat) # times의 배수로 매번 저장할 sequence 번호를 계산

        # 날짜가 변경되었으면 종료
        if ret[1]['cts_date'] != edate :
            end = 1
            save_status['end'] = 1

        # 받은 tick 데이터 저장
        fname = FO_TICK_PATH_SEQ + '\\seq_' + edate + '_fut' + '_' + ticker + '_tick-' + str(n_tick) + '-' + str(seq) + '.csv'        
        save_to_file_csv(fname, data)

        if end :
            info = {'ticker':ticker, 'date':edate, 'max':seq}
            save_to_file_json(FO_TICK_PATH_SEQ+'\\info.txt', info)
            break
        
        time.sleep(1)
            
        ctsdate = ret[1]['cts_date']
        ctstime = get_cts_time(ret[0]) # 다음에 읽어야할 tick의 tm. api 오류가 있어서 별도로 계산함
                        
        save_status['ctsdate'] = ctsdate
        save_status['ctstime'] = ctstime

        # 중간 중간 출력
        if i % 10 == 0 :
            print(ctsdate, ctstime[0:6])

    # 200번 이상 호출이 필요하므로, 다음 호출시 201번부터 저장하기 위함
    save_status['times'] += 1

    if save_status['end'] == 1 : # 모두 저장함        
        os.remove(st_name)
        print('\ntick download 끝. 아래 파일 실행하여 merge하세요.')
        print('python tick-merge.py')        
    else:
        print('save status', save_status)
        print('한번 더 실행하세요!!')
        save_status['normal'] = 1
        save_to_file_json(st_name, save_status)

# OpenAPI 사용을 위한 token 만들기
token = get_token()

# tick 데이터 다운로드
save_fo_tick_data(ticker, n_tick, date)


