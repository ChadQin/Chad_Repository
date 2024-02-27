import time
import pyvisa,serial

#########################
# update time: 2024-02-22

class KS34465A:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.K34465A = self.rm.open_resource(self.rm_address[int(input('选择串口:\n'))])


#设置为DC 电流档

    def conf_curr_dc(self):
        self.K34465A.write('CONF:CURR:DC')

#设置为AC 电流档

    def conf_curr_ac(self):
        self.K34465A.write('CONF:CURR:AC')

#设置为DC 电压档

    def conf_volt_dc(self):
        self.K34465A.write('CONF:VOLT:DC')

#设置为AC 电压档

    def conf_volt_ac(self):
        self.K34465A.write('CONF:VOLT:AC')

#获取DC 电压档电压值

    def get_volt_dc(self):
        volt=self.K34465A.query('MEAS:VOLT:DC?')
        return(float(volt))

#获取AC 电压档电压值

    def get_volt_ac(self):
        volt=self.K34465A.query('MEAS:VOLT:AC?')
        return(float(volt))

#获取DC 电流档电流值

    def get_curr_dc(self):
        curr=self.K34465A.query('MEAS:CURR:DC?')
        return(float(curr))

#获取AC 电流档电流值

    def get_curr_ac(self):
        curr=self.K34465A.query('MEAS:CURR:AC?')
        return(float(curr))


class IT8812B:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.IT8812B = self.rm.open_resource(self.rm_address[int(input('选择串口:\n'))])

    def function(self):
        #询问模式
        function = self.IT8812B.query('FUNCtion?')
        print(function)
        return function

    def function_res(self):
        #切换到CR模式
        self.IT8812B.write('FUNC RES')

    def function_volt(self):
        # 切换到CV模式
        self.IT8812B.write('FUNC VOLTage')

    def function_curr(self):
        # 切换到CC模式
        self.IT8812B.write('FUNC CURRent')

    def function_pow(self):
        # 切换到CP模式
        self.IT8812B.write('FUNC POWer')

    def read_volt(self):
        # 读取电压输入值
        volt = self.IT8812B.query('MEAS:VOLT?')
        volt = round(float(volt),3)
        return volt

    def read_curr(self):
        # 读取电流输入值
        curr = self.IT8812B.query('MEAS:CURR?')
        curr = round(float(curr),3)
        return curr

    def CC_read_curr_range(self):
        # 读取设定电流范围
        range = self.IT8812B.query('CURRent:RANGe?')
        return range

    def CC_setup_range(self,curr):
        # 设定电流范围:
        # 0-3A 0.1mA分辨率
        # 0-15A 1mA分辨率
        if curr == 'low':
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(3))
        elif curr == 'high':
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(15))
        else:
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(str(curr)))

    def CC_setup_curr(self,curr):
        # CC模式下，调节电流大小(A)
        self.IT8812B.write('CURR {}'.format(curr))

    def CC_setup_curr_read(self):
        # CC模式下，读取设定电流大小(A)
        curr = self.IT8812B.query('CURRent?')
        curr = round(float(curr), 3)
        return curr

    def CV_setup_volt(self,volt):
        # CV模式下，调节电压大小(V)
        self.IT8812B.write('VOLT {}'.format(volt))

    def CV_setup_volt_read(self):
        # CV模式下，读取设定电压大小(V)
        volt = self.IT8812B.query('VOLTage?')
        volt = round(float(volt), 3)
        return volt

    def CR_setup_res(self,res):
        # CR模式下，调节电阻大小(Ω)
        self.IT8812B.write('RES {}'.format(res))

    def CR_setup_res_read(self):
        # CR模式下，读取调节电阻大小(Ω)
        res = self.IT8812B.query('RESistance?')
        res = round(float(res), 3)
        return res

    def local_control(self):
        # 锁定设备实体按键控制
        self.IT8812B.write('SYST:LOC')

    def status(self,status):
        # 输入状态设定
        if status == 'on':
            self.IT8812B.write('INP 1')
        elif status == 'off':
            self.IT8812B.write('INP 0')
        else:
            print("输入错误，请输入'on'或者'off'")

    def clear_error_status(self):
        # 清除错误状态
        self.IT8812B.write('SYST:CLE')

    def close_dev(self):
        # 关闭设备连接
        self.IT8812B.close()


class Tek_osc():
    def __init__(self,baud_rate):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.tek_osc = self.rm.open_resource(self.rm_address[int(input('选择示波器串口:\n'))])
        self.tek_osc.baud_rate = baud_rate

    def as_num(self,x):
        y = '{:.6f}'.format(x)  # .10f 保留10位小数
        return y

    def single_sequence(self,state):
        #单次触发: SEQuence
        #多次触发:  RUNSTop
        self.tek_osc.write('ACQuire:STOPAfter {}\n'.format(state))
        if state == 'SEQuence':
            self.tek_osc.write('ACQuire:STATE ON\n')
        else:
            pass

    def meas_read(self,type):
        #{
        #   频率: FREQuency
        #   均方根: RMS
        #
        #
        # }
        self.tek_osc.write('MEASUrement:IMMed:TYPe {}\n'.format(type))
        data = float(self.tek_osc.query('MEASUrement:IMMed:VALue?\n'))
        data = self.as_num(data)
        return data

    def close_dev(self):
        # 关闭设备连接
        self.tek_osc.close()

    def autoset(self):
        self.tek_osc.write('AUTOSET EXECUTE\n')
        # self.tek_osc.write('DISplay:INTENSITy:WAVEform 75\n')


class CYHR_SignalSource:
    def __init__(self,portx, bps, timeout):
            # 打开串口，并得到串口对象
            self.ser = serial.Serial(portx, bps, timeout=timeout)

    def write_data(self, msg):
        print('CMD: {}'.format(msg))
        self.ser.write('{}\n'.format(msg).encode('utf-8'))

    def read_data(self):
        self.data = self.ser.readline()
        self.data = self.data.decode('utf-8')
        print('return info: {}\n'.format(self.data))
        return self.data

    def hex_convert(self,dec):
        self.hex_data = hex(dec)[2:]
        return self.hex_data.upper()

    def full_8byte_hex(self,hex_data):
        if 8 - len(hex_data) > 0:
            self.hex_data = '0' * (8 - len(hex_data)) + hex_data
        return self.hex_data.upper()

    def confirm_connect(self):
        self.write_data('<REA>')
        self.read_data()

    def single_output(self,freq,pow,level):
        freq = self.full_8byte_hex(self.hex_convert(freq))
        self.write_data('<FRQ{}>'.format(freq))
        pow = self.hex_convert(pow)
        self.write_data('<POW{}{}>'.format(level,pow))

    def STOP(self):
        self.write_data('<STO>')

    def close_dev(self):
        self.ser.close()