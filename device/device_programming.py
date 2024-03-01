import time,logging,datetime,os
import pyvisa
import serial


#########################
# update time: 2024-02-27


def Logging_setup():
    folder = "log"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 设置将日志输出到文件中，并且定义文件内容
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if os.path.isdir(f"{folder}"):
        pass
    else:
        try:
            os.makedirs(folder)
        except OSError as e:
            print("无法创建文件夹：", str(e))

    fileinfo = logging.FileHandler(os.getcwd() + f"\\{folder}\\Test_log_{now}.log")
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


class KS34465A:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.K34465A = self.rm.open_resource(self.rm_address[int(input('选择串口:\n'))])

    def conf_curr_dc(self):
        #   设置为DC 电流档
        self.K34465A.write('CONF:CURR:DC')

    def conf_curr_ac(self):
        #   设置为AC电流档
        self.K34465A.write('CONF:CURR:AC')

    def conf_volt_dc(self):
        #   设置为DC电压档
        self.K34465A.write('CONF:VOLT:DC')

    def conf_volt_ac(self):
        #   设置为AC电压档
        self.K34465A.write('CONF:VOLT:AC')

    def get_volt_dc(self):
        #   获取DC电压档电压值
        volt = self.K34465A.query('MEAS:VOLT:DC?')

        return float(volt)

    def get_volt_ac(self):
        #   获取AC电压档电压值
        volt = self.K34465A.query('MEAS:VOLT:AC?')
        return float(volt)

    def get_curr_dc(self):
        #   获取DC电流档电流值
        curr = self.K34465A.query('MEAS:CURR:DC?')
        return float(curr)

    def get_curr_ac(self):
        #   获取AC电流档电流值
        curr = self.K34465A.query('MEAS:CURR:AC?')
        return float(curr)

    def measurement(self,function):
        if function=='DCV':
            Meas=self.K34465A.query('MEASUre:VOLTage:DC?')
        if function=='DCI':
            Meas = self.K34465A.query('MEASUre:CURRent:DC?')
        if function == 'ACV':
            Meas = self.K34465A.query('MEASUre:VOLTage:AC?')
        if function == 'ACI':
            Meas = self.K34465A.query('MEASUre:CURRent:AC?')
        if function=='Res':
            Meas=self.K34465A.query('MEASUre:RESistance?')
        Meas_Result = float(Meas)
        return Meas_Result

    def local(self):
        self.K34465A.write('SYST:LOC')

    def text_function(self,cmd):
        if '?' in cmd:
            read = self.K34465A.query(cmd)
            return read
        else:
            self.K34465A.write(cmd)

class IT8812B:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.IT8812B = self.rm.open_resource(self.rm_address[int(input('选择串口:\n'))])

    def function(self):
        #   询问模式
        function = self.IT8812B.query('FUNCtion?')
        print(function)
        return function

    def function_res(self):
        #   切换到CR模式
        self.IT8812B.write('FUNC RES')

    def function_volt(self):
        #   切换到CV模式
        self.IT8812B.write('FUNC VOLTage')

    def function_curr(self):
        #   切换到CC模式
        self.IT8812B.write('FUNC CURRent')

    def function_pow(self):
        #   切换到CP模式
        self.IT8812B.write('FUNC POWer')

    def read_volt(self):
        #   读取电压输入值
        volt = self.IT8812B.query('MEAS:VOLT?')
        volt = round(float(volt), 3)
        return volt

    def read_curr(self):
        #   读取电流输入值
        curr = self.IT8812B.query('MEAS:CURR?')
        curr = round(float(curr), 3)
        return curr

    def cc_read_curr_range(self):
        #   读取设定电流范围
        cc_range = self.IT8812B.query('CURRent:RANGe?')
        return cc_range

    def cc_setup_range(self, curr):
        #   设定电流范围:
        #   0-3A 0.1mA分辨率
        #   0-15A 1mA分辨率
        if curr == 'low':
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(3))
        elif curr == 'high':
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(15))
        else:
            self.IT8812B.write('SOUR:CURR:RANGE {}'.format(str(curr)))

    def cc_setup_curr(self, curr):
        #   CC模式下，调节电流大小(A)
        self.IT8812B.write('CURR {}'.format(curr))

    def cc_setup_curr_read(self):
        #   CC模式下，读取设定电流大小(A)
        curr = self.IT8812B.query('CURRent?')
        curr = round(float(curr), 3)
        return curr

    def cv_setup_volt(self, volt):
        #   CV模式下，调节电压大小(V)
        self.IT8812B.write('VOLT {}'.format(volt))

    def cv_setup_volt_read(self):
        #   CV模式下，读取设定电压大小(V)
        volt = self.IT8812B.query('VOLTage?')
        volt = round(float(volt), 3)
        return volt

    def cr_setup_res(self, res):
        #   CR模式下，调节电阻大小(Ω)
        self.IT8812B.write('RES {}'.format(res))

    def cr_setup_res_read(self):
        #   CR模式下，读取调节电阻大小(Ω)
        res = self.IT8812B.query('RESistance?')
        res = round(float(res), 3)
        return res

    def local_control(self):
        #   锁定设备实体按键控制
        self.IT8812B.write('SYST:LOC')

    def status(self, status):
        #   输入状态设定
        if status == 'on':
            self.IT8812B.write('INP 1')
        elif status == 'off':
            self.IT8812B.write('INP 0')
        else:
            print("输入错误，请输入'on'或者'off'")

    def clear_error_status(self):
        #   清除错误状态
        self.IT8812B.write('SYST:CLE')

    def close_dev(self):
        #   关闭设备连接
        self.IT8812B.close()


class _TekOsc:
    def __init__(self, baud_rate):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        self.tek_osc = self.rm.open_resource(self.rm_address[int(input('选择示波器串口:\n'))])
        self.tek_osc.baud_rate = baud_rate

    def as_num(self, x):
        y = '{:.6f}'.format(x)  # .10f 保留10位小数
        return y

    def single_sequence(self, state_trig):
        #   单次触发: SEQuence
        #   多次触发:  RUNSTop
        self.tek_osc.write('ACQuire:STOPAfter {}\n'.format(state_trig))
        if state_trig == 'SEQuence':
            self.tek_osc.write('ACQuire:STATE ON\n')
        else:
            pass

    def meas_read(self, meas_type):
        #   {
        #       频率: FREQuency
        #       均方根: RMS
        #
        #
        #   }
        self.tek_osc.write('MEASUrement:IMMed:TYPe {}\n'.format(meas_type))
        data = float(self.tek_osc.query('MEASUrement:IMMed:VALue?\n'))
        data = self.as_num(data)
        return data

    def close_dev(self):
        #   关闭设备连接
        self.tek_osc.close()

    def auto_set(self):
        self.tek_osc.write('AUTOSET EXECUTE\n')
#       self.tek_osc.write('DISplay:INTENSITy:WAVEform 75\n')

    def text_function(self,cmd):
        self.tek_osc.write(cmd)



class _CYHRSignalSource:
    def __init__(self, portx, bps, timeout):
        #   打开串口，并得到串口对象
        self.ser = serial.Serial(portx, bps, timeout=timeout)

    def write_data(self, msg):
        logging.info('CMD: {}'.format(msg))
        self.ser.write('{}\n'.format(msg).encode('utf-8'))

    def read_data(self):
        self.data = self.ser.readline()
        self.data = self.data.decode('utf-8')
        print('return info: {}\n'.format(self.data))
        return self.data

    def hex_convert(self, dec):
        self.hex_data = hex(dec)[2:]
        return self.hex_data.upper()

    def full_byte_hex(self, len_byte, hex_data):
        if 8 - len(hex_data) > 0:
            self.hex_data = '0' * (len_byte - len(hex_data)) + hex_data
        return self.hex_data.upper()

    def confirm_connect(self):
        self.write_data('<REA>')
        self.read_data()

    def single_output(self, freq, pow_input, level):
        wave_freq = self.full_byte_hex(8, self.hex_convert(freq))
        self.write_data('<FRQ{}>'.format(wave_freq))
        wave_pow = self.full_byte_hex(4, self.hex_convert(pow_input))
        self.write_data('<POW{}{}>'.format(level, wave_pow))

    def stop(self):
        self.write_data('<STO>')

    def close_dev(self):
        self.ser.close()
