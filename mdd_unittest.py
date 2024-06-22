# -*- encoding: cp949 -*-
import unittest

# 고/저  신고/저
candles = [
        {'date':'2024-01-01', 'close':2},
        {'date':'2024-01-02', 'close':12},
        {'date':'2024-01-03', 'close':14}, # 고
        {'date':'2024-01-04', 'close':12},
        {'date':'2024-01-05', 'close':9},
        {'date':'2024-01-06', 'close':8},  # 저  answer
        {'date':'2024-01-07', 'close':15}, # 신고
        {'date':'2024-01-08', 'close':12},
        {'date':'2024-01-09', 'close':10}, # 저        
    ]

# 고/저  신고,저
candles2 = [
        {'date':'2024-01-01', 'close':10},
        {'date':'2024-01-02', 'close':12},
        {'date':'2024-01-03', 'close':14}, # 고  6
        {'date':'2024-01-04', 'close':12},
        {'date':'2024-01-05', 'close':9},
        {'date':'2024-01-06', 'close':8},  # 저
        {'date':'2024-01-07', 'close':15}, # 신고
        {'date':'2024-01-08', 'close':12},
        {'date':'2024-01-09', 'close':7}, #  저    8  answer
    ]

# 고/저  신고,저
candles3 = [
        {'date':'2024-01-01', 'close':10},
        {'date':'2024-01-02', 'close':12},
        {'date':'2024-01-03', 'close':14}, # 고  
        {'date':'2024-01-04', 'close':12},
        {'date':'2024-01-05', 'close':9},
        {'date':'2024-01-06', 'close':8},  # 저 8  answer
        {'date':'2024-01-07', 'close':13}, # 신고
        {'date':'2024-01-08', 'close':9},
        {'date':'2024-01-09', 'close':12}, # 저    
        {'date':'2024-01-10', 'close':9},
    ]

# 고/저  신고/저 신고/저
candles4 = [
        {'date':'2024-01-01', 'close':10},
        {'date':'2024-01-02', 'close':12},
        {'date':'2024-01-03', 'close':14}, # 고  
        {'date':'2024-01-04', 'close':12},
        {'date':'2024-01-05', 'close':9},
        {'date':'2024-01-06', 'close':8},  # 저 
        {'date':'2024-01-07', 'close':15}, # 신고
        {'date':'2024-01-08', 'close':7},  # 저  answer
        {'date':'2024-01-09', 'close':16}, # 고    
        {'date':'2024-01-10', 'close':9},  # 저
    ]

# dd = (최저 - 최고)/최대
def cal_dd(low, high) :
    # dd 계산
    return (low - high) / high

# data : 시뮬 결과가 저장된 dict의 list
# key :   mdd 계산시 사용할 key값
# display : 중간과정 출력 여부(debugging용)
def get_mdd(data, key, display=0):
    dds = []      # dd계산한 구간 정보 
    mdd = 0       # mdd 값
    mdd_pos = -1  # mdd가 있는 곳의 위치
    high = data[0]
    low  = data[0]
    
    for each in data:        
        if high[key] < each[key] : # 신고 
            # 첫 시작인지 확인
            if high[key] == low[key] : # 처음 시작 중인데 계속 올라가는 중 low도 update
                high = each
                low  = each
                continue
            if display :
                print('신고 ', each)
            dds.append([low, high])
            # dd 계산
            new_dd = cal_dd(low[key], high[key])
            
            if mdd > new_dd :
                mdd = new_dd
                mdd_pos = len(dds) - 1 # 최근 append한 pair가 mdd 위치임
                if display :
                    print('new mdd', high[key], low[key], mdd, mdd_pos)
            # low 값을 신고지점으로 이동
            high = each    
            low  = each            
            continue
        
        if low[key] > each[key] : # 신저 
           if display :
               print('신저 ', each)
           low = each 

    # 종료시점이 dd 최저인지 한번 더 확인
    new_dd = cal_dd(low[key], high[key])
    if mdd > new_dd :
        dds.append([low, high])
        mdd = new_dd
        mdd_pos = len(dds) - 1 # 최근 append한 pair가 mdd 위치임
        if display :
           print('new mdd', high[key], low[key], mdd, mdd_pos)

    # 마지막 것 추가
    dds.append([low, high])    
    return dds, mdd, mdd_pos

class CustomTests(unittest.TestCase): 
    def setUp(self):    # 
        pass
    def tearDown(self): # 
        pass
    def test_process_statement(self) :
        cnt = 1
        display = 0
        key = 'close'
        dds, mdd, mdd_pos = get_mdd(candles, key, display)
        if 0:
            print('dds')
            for each in dds:
                print(each)
        print('next---', cnt)
        self.assertEqual(mdd, (8-14)/14)
        self.assertEqual(dds[mdd_pos][0]['date'], '2024-01-06')
        self.assertEqual(dds[mdd_pos][1]['date'], '2024-01-03')

        cnt += 1
        print('next---', cnt)
        dds, mdd, mdd_pos = get_mdd(candles2, key, display)
        self.assertEqual(mdd, (7-15)/15)
        self.assertEqual(dds[mdd_pos][0]['date'], '2024-01-09')
        self.assertEqual(dds[mdd_pos][1]['date'], '2024-01-07')

        cnt += 1
        print('next---', cnt)
        dds, mdd, mdd_pos = get_mdd(candles3, key, display)
        self.assertEqual(dds[mdd_pos][0]['date'], '2024-01-06')
        self.assertEqual(dds[mdd_pos][1]['date'], '2024-01-03')
        self.assertEqual(mdd, (8-14)/14)

        cnt += 1
        print('next---', cnt)
        dds, mdd, mdd_pos = get_mdd(candles4, key, display)
        self.assertEqual(mdd, (7-15)/15)
        self.assertEqual(dds[mdd_pos][0]['date'], '2024-01-08')
        self.assertEqual(dds[mdd_pos][1]['date'], '2024-01-07')
      
unittest.main()
