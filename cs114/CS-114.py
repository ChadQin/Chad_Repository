import serial
import logging
import re
import csv
from colorama import Fore, Back, Style
from time import sleep
from serial.tools import list_ports

def DOpenPort(portx, bps, timeout):
    try:
        # 打开串口，并得到串口对象
        ser = serial.Serial(portx, bps, timeout=timeout)
        # 判断是否打开成功
        if(False == ser.is_open):
           ser = -1
    except Exception as e:
        print("---异常---：", e)

    return ser

def write_data(ser,msg):
    print('CMD: {}'.format(msg))
    ser.write('{}\n'.format(msg).encode('utf-8'))
    # logging.info(ser)
    # logging.info(msg)

def read_data(ser):
    data = ser.readline()
    data = data.decode('utf-8')
    logging.info(data)
    print('return info: {}\n'.format(data))

    return data

def write_source(inflection_point):

    step_nums = str(inflection_point)
    write_data(ser,'<CNT0{}0{}>'.format(str(int(inflection_point)-1),str(int(step_nums)-2)))
    read_data(ser)
    print('<CNT0{}0{}>'.format(str(int(inflection_point)-1),str(int(step_nums)-2)))

    for freq_num in range(inflection_point):
        freq = float(input('输入第{}个频率点的频率(MHz):\n'.format(int(freq_num)+1)))*1000000
        freq = hex(int(freq))[2:].zfill(8)
        power = float(input('输入第{}个频率点的功率(dBm):\n'.format(int(freq_num)+1)))*10
        power = int(power)
        if power >= 0:
            hex_power = format(power,'04x')
            print('0x' + hex_power)
        else:
            hex_power = hex(power&0xffff)[2:]
            print(hex(power&0xffff))
        FOD_CMD = ('<FDD0{}{}{}>'.format(freq_num,freq,hex_power)).upper()
        write_data(ser,FOD_CMD)
        read_data(ser)
        print(FOD_CMD)
        sleep(0.5)

    for step_num in range(int(step_nums)-1):
        freq_start = float(input('输入起点频率(MHz):\n'))*1000000
        freq_start = hex(int(freq_start))[2:].zfill(8)
        freq_finish = float(input('输入终点频率(MHz):\n'))*1000000
        freq_finish = hex(int(freq_finish))[2:].zfill(8)
        step = float(input('输入步长频率(MHz):\n'))*1000000
        step = hex(int(step))[2:].zfill(8)
        SBS_CMD = ('<SBS0{}{}{}1{}>'.format(step_num,freq_start, freq_finish, step)).upper()
        write_data(ser,SBS_CMD)
        read_data(ser)
        print(SBS_CMD)
        sleep(0.5)
    write_data(ser,'<RUN>')
    print('<RUN>')

def write_csv(content):
    with open('./data.csv','a+',encoding='UTF8',newline="") as f:
        writer = csv.writer(f)
        writer.writerow(content)


def complement(DATA):
    a = int(DATA, 16) - 1
    a = bin(a)
    bin_code = list(a)
    bin_code = list(bin_code)
    negation_bin_code= []
    for i in range(2,18):
        if bin_code[i] == '0':
            negation_bin_code.append('1')
        elif bin_code[i] == '1':
            negation_bin_code.append('0')
    negation_bin_code = ''.join(negation_bin_code)
    negation_bin_code = '0b' + negation_bin_code
    oct_code = -int(negation_bin_code,2)/10
    return oct_code

ser = DOpenPort('COM13', 19200, 0.01)
write_source(2)

if __name__ == '__main__':

    header = ['freq(MHz)','power(dBm)', 'Gear' ,'level']
    write_csv(header)


    text = open('data.txt','r',encoding='utf-8')
    datas = []
    for line in text:
        p1 = re.compile(r'[<](.*?)[>]', re.S)
        datas = datas + (re.findall(p1,line))
    print(datas)
    for data in datas:
        print(data)
        if 'SED' in data:
            data.replace('\'', '').replace('<', '').replace('>', '')
            freq = data[3:11]
            freq = int(freq, 16)
            power = data[11:15]
            Gear = data[15:17]
            level = data[17:21]
            if int(power, 16) > 32768:
                power_dbm = complement(power)
            else:
                power_dbm = int(power, 16) / 10
            print(Fore.LIGHTMAGENTA_EX + '频率点:' + str(freq / 1000000) + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + '功率值:' + str(power_dbm) + Style.RESET_ALL)
            print(Fore.LIGHTBLUE_EX + '功率等级:' + str(int(level, 16)) + Style.RESET_ALL)
            print(Fore.LIGHTBLUE_EX + '档位:' + str(Gear) + Style.RESET_ALL + '\n')
            content = []
            content.append(str((freq / 1000000)).strip())
            content.append(str(power_dbm).strip())
            content.append(str(Gear).strip())
            content.append(str(int(level, 16)).strip())
            write_csv(content)
        else:
           pass

    print("Press enter to close")
    input()


