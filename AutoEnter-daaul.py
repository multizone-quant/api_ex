# pip install pyautogui

import pyautogui
import time

start_x = 1043
start_y = 521

qty_x = 1050
qty_y = 463
press_1_x = 920
press_1_y = 640

press_00_x = 990
press_00_y = 840

price_x = 1050
price_y = 512
press_3_x = 1052
press_3_y = 646
press_4_x = 920
press_4_y = 710
press_0_x = 920
press_0_y = 850

press_ok_x  = 1070
press_ok_y  = 925


buy_x  = 1050
buy_y  = 840

buy_confirm_x  = 1025
buy_confirm_y  = 745

# 우선 시작을 알리고, 키보드 입력을 받는다.
print('자동매매 시작 press enter')
input()

while(1) :
    # 주문 시작
    pyautogui.moveTo(start_x, start_y)
    pyautogui.click()
    time.sleep(3)
    # 수량 입력 시작
    pyautogui.moveTo(qty_x, qty_y)
    pyautogui.click()
    time.sleep(1)
    # 100 입력인 경우
    # press 1
    pyautogui.moveTo(press_1_x, press_1_y)
    pyautogui.click()
    # press 00
    pyautogui.moveTo(press_00_x, press_00_y)
    pyautogui.click()
    # 약간 시간이 필요함

    # 가격 입력 시작
    pyautogui.moveTo(price_x, price_y)
    time.sleep(1)    
    pyautogui.click()

    # 34410 입력인 경우
    # press 3
    pyautogui.moveTo(press_3_x, press_3_y)
    pyautogui.click()
    time.sleep(1)
    # press 4
    pyautogui.moveTo(press_4_x, press_4_y)
    pyautogui.click()
    time.sleep(1)
    # press 4
    pyautogui.moveTo(press_4_x, press_4_y)
    pyautogui.click()
    time.sleep(1)
    # press 1
    pyautogui.moveTo(press_1_x, press_1_y)
    pyautogui.click()
    time.sleep(1)
    # press 0
    pyautogui.moveTo(press_0_x, press_0_y)
    pyautogui.click()
    time.sleep(1)

    pyautogui.moveTo(press_ok_x, press_ok_y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(2)

    print('ready to buy')
    
    pyautogui.moveTo(buy_x, buy_y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)

    pyautogui.moveTo(buy_confirm_x, buy_confirm_y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    print('done press any key')
    input()
