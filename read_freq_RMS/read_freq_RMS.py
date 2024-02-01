import sys

import pyvisa as visa
import time,datetime,os
import keyboard
import threading
import logging
import csv
from colorama import Fore,Back,Style


def as_num(x):
    y = '{:.9f}'.format(x)  # .10f 保留10位小数
    return y

def write_csv(content):
    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)
    with open('{}/freq&RMS.csv'.format(path),'a',encoding='UTF8',newline="") as f:
        writer = csv.writer(f)
        writer.writerow(content)
def read_measu():
    while True:
        data = []
        osc.write("MEASUREMENT:IMMED:TYPE FREQUENCY\n")
        freq = osc.query("MEASUrement:IMMed:VALue?\n")
        scale = osc.query("HORizontal:MAIn:SCAle?\n")
        a = as_num(4*float(freq))
        if 15*float(freq) > 1/float(scale):
            osc.write("HORizontal:MAIn:SCAle {}\n".format(2*1/float(a)))
        else:
            pass
        osc.write("MEASUREMENT:IMMED:TYPE RMS\n")
        RMS = osc.query("MEASUrement:IMMed:VALue?\n")
        logging.info('频率(MHz): ' + str(float(freq)/1000000))
        logging.info('RMS(V): ' + str(float(RMS)) + '\n')
        data.append(str(float(freq)/1000000))
        data.append(str(float(RMS)))
        write_csv(data)
        time.sleep(float(sleep_time)-0.13)

def Logging_setup():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 设置将日志输出到文件中，并且定义文件内容
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fileinfo = logging.FileHandler(f"{path}/Test_log_{now}.log")
    fileinfo.setLevel(logging.INFO)
    # 设置将日志输出到控制台
    controlshow = logging.StreamHandler()
    controlshow.setLevel(logging.INFO)
    # 设置日志的格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    fileinfo.setFormatter(formatter)
    controlshow.setFormatter(formatter)

    logger.addHandler(fileinfo)
    logger.addHandler(controlshow)

if __name__ == '__main__':


    path = "./log"
    title = ['频率(MHz)', 'RMS(V)']
    write_csv(title)
    Logging_setup()

    print(Fore.LIGHTRED_EX + 'NOTE：输入驻留时间后会一直运行，生成表格和运行log，如果需要停止运行用键盘按下"esc"')
    print("Press enter to continue" + Style.RESET_ALL)
    input()

    rm = visa.ResourceManager()
    rm_address = rm.list_resources()
    for i, device in enumerate(rm_address):
        print(f"{i}:{device}")
    ser_num = int(input('选择串口:\n'))
    osc = rm.open_resource(rm_address[int(input('选择串口:\n'))])

    osc.baud_rate = 38400

    try:
        IDN = osc.query("*IDN?\n")
        logging.info('示波器型号:\t' + IDN)
    except:
        logging.warning('串口异常！！！')
        print("Press enter to close")
        input()
        sys.exit()

    osc.write("HORizontal:MAIn:SCAle {}\n".format(1.0e-4))
    time.sleep(1)
    sleep_time = input('驻留时间?(S)\n')
    logging.info('驻留等待(S):' + str(float(sleep_time)) + '\n')
    osc.write("HORizontal:MAIn:SCAle {}\n".format(1.0e-4))
    t = threading.Thread(target=read_measu, daemon=True)
    t.start()
    keyboard.wait('esc')
    osc.close()










