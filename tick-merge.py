# -*- coding: utf-8 -*-
import json
import os
import csv

# download ������ �ʿ��� folder.
# �ʿ��� dir�� �ִ��� Ȯ��, ������ �����.
FO_TICK_PATH_SEQ = '.\\future_tick_seq'

# download�� ����� ������ folder.
# �ٸ� �̸��� ���Ѵٸ� �Ʒ� �̸��� �ٲ۴�
FO_TICK_PATH = '.\\future_tick'

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
        fname = out_foler+'\\'+dt + '_fut' + '_' + ticker+ '_tick-1.csv'
        save_to_file_csv(fname, merged)
        print('\n', fname)

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

# merge�� ������ FO_TICK_PATH_SEQ+'\\info.txt' �� �ִ�
info = load_json_from_file(FO_TICK_PATH_SEQ+'\\info.txt')
merge_fop_data_tick(FO_TICK_PATH_SEQ, FO_TICK_PATH, info['date'], info['ticker'], info['max']) 

print('\ndone')
