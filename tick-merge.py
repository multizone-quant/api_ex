# -*- coding: utf-8 -*-
import json
import os
import csv

# download 과정에 필요한 folder.
# 필요한 dir가 있는지 확인, 없으면 만든다.
FO_TICK_PATH_SEQ = '.\\future_tick_seq'

# download한 결과를 저장할 folder.
# 다른 이름을 원한다면 아래 이름을 바꾼다
FO_TICK_PATH = '.\\future_tick'

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

#repeat : merge할 최대 seq 값
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
        # 날짜가 틀린 경우 제거
        if dt != data[0]['date']:
            data = get_tick_data_remove_dif_date(data, dt)
        # 중복된 데이터는 제거
        data = get_tick_data_after_remove_dup(data, pre_data)
        merged += data
        pre_data = data
    if len(merged) > 0 :
        fname = out_foler+'\\'+dt + '_fut' + '_' + ticker+ '_tick-1.csv'
        save_to_file_csv(fname, merged)
        print('\n', fname)

# 날짜가 틀린 자료 삭제
def get_tick_data_remove_dif_date(data, dt):
    cnt = 0
    for each in data:
        if each['date'] != dt:
            cnt += 1
        else:
            return data[cnt:]
    print('error get_tick_data_remove_dif_date()')
    return data

# 역으로 merge하므로 큰 숫자에 있는 정보가 정확함. 현재 data값 중 중복되는 것 삭제
def get_tick_data_after_remove_dup(data, pre_data):
    if len(pre_data) == 0 : # 최초임
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
                    return data[dup:]  # 중복되지 않은 데이터만 돌려줌
    else:
        return data

# merge할 정보는 FO_TICK_PATH_SEQ+'\\info.txt' 에 있다
info = load_json_from_file(FO_TICK_PATH_SEQ+'\\info.txt')
merge_fop_data_tick(FO_TICK_PATH_SEQ, FO_TICK_PATH, info['date'], info['ticker'], info['max']) 

print('\ndone')
