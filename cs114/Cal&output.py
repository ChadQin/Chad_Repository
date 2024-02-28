
import serial,time
import pyvisa as visa
from device import device_programming

#   update_time = 2024.02.28

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


def read_data(ser):
    data = ser.readline()
    data = data.decode('utf-8')
    print('return info: {}\n'.format(data))

    return data

def hex_convert(dec):
    hex_data = hex(dec)[2:]
    return hex_data.upper()

def full_8byte_hex(hex_data):
    if 8-len(hex_data) > 0:
        hex_data = '0'*(8-len(hex_data)) + hex_data
    return hex_data.upper()

def osc_get_data():
    osc.single_sequence()
    RMS = osc.meas_read('RMS')
    print('均方根:', str(round(float(RMS), 3)) + 'V')
    FREQ = osc.meas_read('FREQuency')
    print('频率:', str(float(FREQ) / 1000000) + 'MHz')

def output(freq_pow_dic):
    # freq_pow_dic = {
    #     250: 4000,
    #     260: 5788,
    #     270: 5950,
    #     280: 6180,
    #     290: 6200,
    #     300: 6344,
    #     310: 7030,
    #     320: 7520,
    #     330: 8250,
    #     340: 9255,
    #     350: 10440,
    #     360: 11555,
    #     370: 12288,
    #     380: 12715,
    #     390: 13200,
    #     400: 13720
    # }

    # freq_pow_dic = {100:4000}

    for freq, pow in freq_pow_dic.items():
        SIGNAL.single_output(freq * 1000000, pow, '1F')
        meas_freq = osc.meas_read('FREQuency')
        if float(meas_freq) > 1 / 5 * freq * 1000000:
            osc.auto_set()
        elif float(meas_freq) < freq * 1000000 / 1.5:
            osc.auto_set()
        meas_freq = osc.meas_read('FREQuency')
        print('频率:', str(float(meas_freq) / 1000000) + 'MHz')
        RMS = osc.meas_read('RMS')
        print('均方根:', str(RMS) + 'V')
        time.sleep(2)
        print('\n')


def cal(set_freq,set_pow,limit_level):

    cal_level = []

    for base_freq in set_freq:
        print(base_freq)
        base_freq = base_freq * 1000000
        pow_level = 2000
        SIGNAL.single_output(base_freq, 2000, '1F')
        while True:
            if pow_level > limit_level:
                print('输入过大！！！')
                break
            read_pow = osc.meas_read('RMS')

            if abs(float(read_pow) - float(set_pow)) < 0.002:
                time.sleep(0.1)
                read_pow = osc.meas_read('RMS')
                if abs(float(read_pow) - float(set_pow)) < 0.002:
                    time.sleep(0.1)
                    read_pow = osc.meas_read('RMS')
                    if abs(float(read_pow) - float(set_pow)) < 0.002:
                        cal_level.append(pow_level)
                        break

            elif abs(float(read_pow) - float(set_pow)) > 0.5:
                if float(read_pow) > float(set_pow):
                    pow_level = pow_level - 1500
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    osc.auto_set()
                    print('RMS:', read_pow+'V\n')
                elif float(read_pow) < float(set_pow):
                    pow_level = pow_level + 1500
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    osc.auto_set()
                    print('RMS:', read_pow+'V\n')

            elif abs(float(read_pow) - float(set_pow)) > 0.1:
                if float(read_pow) > float(set_pow):
                    pow_level = pow_level - 500
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    osc.auto_set()
                    print('RMS:', read_pow+'V\n')
                elif float(read_pow) < float(set_pow):
                    pow_level = pow_level + 500
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    osc.auto_set()
                    print('RMS:', read_pow+'V\n')

            elif abs(float(read_pow) - float(set_pow)) > 0.05:
                if float(read_pow) > float(set_pow):
                    pow_level = pow_level - 150
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    print('RMS:', read_pow+'V\n')
                elif float(read_pow) < float(set_pow):
                    pow_level = pow_level + 150
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    print('RMS:', read_pow+'V\n')


            else:
                if float(read_pow) > float(set_pow):
                    pow_level = pow_level - 10
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    print('RMS:', read_pow+'V\n')
                elif float(read_pow) < float(set_pow):
                    pow_level = pow_level + 10
                    SIGNAL.single_output(base_freq, pow_level, '1F')
                    print('RMS:', read_pow+'V\n')

    return cal_level



if __name__ == '__main__':

    osc = device_programming._TekOsc(38400)
    SIGNAL = device_programming._CYHRSignalSource('COM13', 19200, 0.01)

    freq_list = [250,280,300,330,350,380,400]

    level_list = cal(freq_list,1,15000)

    freq_pow_dic = dict(zip(freq_list,level_list))
    print(freq_pow_dic)
    SIGNAL.stop()
    time.sleep(5)
    output(freq_pow_dic)
    time.sleep(5)
    SIGNAL.stop()

    osc.close_dev()
    SIGNAL.close_dev()
