import pyvisa

class KS34465A:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.rm_address = self.rm.list_resources()
        for i, device in enumerate(self.rm_address):
            print(f"{i}:{device}")
        # self.ser_num = int(input('选择串口:\n'))
        self.K34465A = self.rm.open_resource(self.rm_address[int(input('选择串口:\n'))])
        # self.resource_str = 'TCPIP0::A-34461A-xxxx.local::inst0::INSTR'
        # self.device = self.rm.open_resource(self.resource_str)

#设置为DC 电流档

    def conf_curr_dc(self):
        self.device.write('CONF:CURR:DC')

#设置为AC 电流档

    def conf_curr_ac(self):
        self.device.write('CONF:CURR:AC')

#设置为DC 电压档

    def conf_volt_dc(self):
        self.device.write('CONF:VOLT:DC')

#设置为AC 电压档

    def conf_volt_ac(self):
        self.device.write('CONF:VOLT:AC')

#获取DC 电压档电压值

    def get_volt_dc(self):
        volt=self.device.query('MEAS:VOLT:DC?')
        return(float(volt))

#获取AC 电压档电压值

    def getvolt_ac(self):
        volt=self.device.query('MEAS:VOLT:AC?')
        return(float(volt))

#获取DC 电流档电流值

    def get_curr_dc(self):
        curr=self.device.query('MEAS:CURR:DC?')
        return(float(curr))

#获取AC 电流档电流值

    def get_curr_ac(self):
        curr=self.device.query('MEAS:CURR:AC?')
        return(float(curr))