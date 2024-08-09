# -*- coding: utf-8 -*-

############################################
# Author: Chad Qin
# update_time: 2024-6-12
# Version: V1.11
############################################

import json
import glob
import socket
import re
import itertools
import time
import logging
import os
import datetime
import math
import sys
import pandas as pd


class PSB4032DeviceProgramming:

    def __init__(self, host, port):
        self.logging_setup()
        self.host = host
        self.port = port
        self.recv_data_list = None
        self.init_info_dict = None
        self.init_info_list = None
        self.temperature = None
        self.command = None
        self.real_time_vlot = None
        self.real_time_curr = None
        self.PSB4032 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PSB4032.settimeout(500)
        try:
            self.PSB4032.connect((self.host, self.port))
        except Exception as e:
            logging.info(e)
            sys.exit()
        self.connect_status = 1
        logging.info("Socket已连接")
        current_path = os.getcwd()
        json_files = glob.glob(os.path.join(current_path, '*.json'))
        if json_files:
            self.json_name = json_files[0]
            with open(self.json_name, 'r', encoding='utf-8') as f:
                self.init_info_dict = json.load(f)
        else:
            logging.info('保存设备初始化信息中')
            dict_ = self.get_init_info()
            dev_num = dict_['设备编号']
            self.json_name = str(dev_num) + '_Init_Info.json'
            with open(self.json_name, 'w', encoding='utf-8') as f:
                json.dump(dict_, f, indent=2, ensure_ascii=False)

    def set_limit(self, Avolt, Svolt, Acurr, Scurr):

        if Avolt > 40 or Svolt < -40:
            return
        if Acurr > 30 or Scurr < -30:
            return

        lim_Avolt_list = []
        lim_Avolt_level = []
        lim_Avolt_diff_key = [key for key in self.init_info_dict if key.startswith('限制正电压')]

        lim_Acurr_list = []
        lim_Acurr_level = []
        lim_Acurr_diff_key = [key for key in self.init_info_dict if key.startswith('限制正电流')]

        lim_Svolt_list = []
        lim_Svolt_level = []
        lim_Svolt_diff_key = [key for key in self.init_info_dict if key.startswith('限制负电压')]

        lim_Scurr_list = []
        lim_Scurr_level = []
        lim_Scurr_diff_key = [key for key in self.init_info_dict if key.startswith('限制负电流')]

        for key in lim_Avolt_diff_key:
            lim_Avolt_list.append(self.init_info_dict[key][0])
            lim_Avolt_level.append(self.init_info_dict[key][1])

        for key in lim_Acurr_diff_key:
            lim_Acurr_list.append(self.init_info_dict[key][0])
            lim_Acurr_level.append(self.init_info_dict[key][1])

        for key in lim_Svolt_diff_key:
            lim_Svolt_list.append(self.init_info_dict[key][0])
            lim_Svolt_level.append(self.init_info_dict[key][1])

        for key in lim_Scurr_diff_key:
            lim_Scurr_list.append(self.init_info_dict[key][0])
            lim_Scurr_level.append(self.init_info_dict[key][1])

        lim_Avolt_list = sorted(lim_Avolt_list)
        lim_Avolt_level = sorted(lim_Avolt_level)

        lim_Acurr_list = sorted(lim_Acurr_list)
        lim_Acurr_level = sorted(lim_Acurr_level)

        lim_Svolt_list = sorted(lim_Avolt_list)
        lim_Svolt_level = sorted(lim_Svolt_level)

        lim_Scurr_list = sorted(lim_Scurr_list)
        lim_Scurr_level = sorted(lim_Scurr_level)

        Avolt_position = self.find_list_position(lim_Avolt_list, Avolt)
        Acurr_position = self.find_list_position(lim_Acurr_list, Acurr)
        Svolt_position = self.find_list_position(lim_Svolt_list, abs(Svolt))
        Scurr_position = self.find_list_position(lim_Scurr_list, abs(Scurr))

        if type(Avolt_position) is int:
            lim_Avolt_level = self.full_hex(4, hex(lim_Avolt_level[Avolt_position])[2:].upper())

        elif type(Avolt_position) is list:
            slope = ((lim_Avolt_level[Avolt_position[1]] - lim_Avolt_level[Avolt_position[0]]) /
                     (lim_Avolt_list[Avolt_position[1]] - lim_Avolt_list[Avolt_position[0]]))
            intercept = lim_Avolt_level[Avolt_position[0]] - slope * lim_Avolt_level[Avolt_position[0]]
            lim_Avolt_level = self.full_hex(4, hex(math.floor(slope * Avolt + intercept))[2:].upper())

        if type(Acurr_position) is int:
            lim_Acurr_level = self.full_hex(4, hex(lim_Acurr_level[Acurr_position])[2:].upper())

        elif type(Acurr_position) is list:
            slope = ((lim_Acurr_level[Acurr_position[1]] - lim_Acurr_level[Acurr_position[0]]) /
                     (lim_Acurr_list[Acurr_position[1]] - lim_Acurr_list[Acurr_position[0]]))
            intercept = lim_Acurr_level[Acurr_position[0]] - slope * lim_Acurr_level[Acurr_position[0]]
            lim_Acurr_level = self.full_hex(4, hex(math.floor(slope * Acurr + intercept))[2:].upper())

        if type(Svolt_position) is int:
            lim_Svolt_level = self.full_hex(4, hex(lim_Svolt_level[Svolt_position])[2:].upper())

        elif type(Svolt_position) is list:
            slope = ((lim_Svolt_level[Svolt_position[1]] - lim_Svolt_level[Svolt_position[0]]) /
                     (lim_Svolt_list[Svolt_position[1]] - lim_Svolt_list[Svolt_position[0]]))
            intercept = lim_Svolt_level[Svolt_position[0]] - slope * lim_Svolt_level[Svolt_position[0]]
            lim_Svolt_level = self.full_hex(4, hex(abs(math.floor(slope * Svolt + intercept)))[2:].upper())

        if type(Scurr_position) is int:
            lim_Scurr_level = self.full_hex(4, hex(lim_Scurr_level[Scurr_position])[2:].upper())

        elif type(Scurr_position) is list:
            slope = ((lim_Scurr_level[Scurr_position[1]] - lim_Scurr_level[Scurr_position[0]]) /
                     (lim_Scurr_list[Scurr_position[1]] - lim_Scurr_list[Scurr_position[0]]))
            intercept = lim_Scurr_level[Scurr_position[0]] - slope * lim_Scurr_level[Scurr_position[0]]
            lim_Scurr_level = self.full_hex(4, hex(abs(math.floor(slope * Scurr + intercept)))[2:].upper())

        command = '<SETL{}{}{}{}>'.format(lim_Avolt_level, lim_Acurr_level, lim_Svolt_level, lim_Scurr_level)
        self.PSB4032.send(command.encode())
        logging.info('设置限制，正电压:{} 负电压:{} 正电流:{} 负电流:{}'.format(Avolt, Svolt, Acurr, Scurr))

    def set_cv_voltage(self, volt):

        """
        volt type: int or float
             range: -40-40(V)
        """
        if volt > 40 or volt < -40:
            return

        volt_list = []
        volt_level = []
        volt_diff_key = [key for key in self.init_info_dict if key.startswith('电压差值')]
        volt_diff_key.sort(key=lambda L: int(re.findall('\d+', L)[0]))

        for key in volt_diff_key:
            volt_list.append(self.init_info_dict[key][0])
            volt_level.append(self.init_info_dict[key][1])

        # volt_list = sorted(volt_list)
        # volt_level = sorted(volt_level)
        #   排序遇到初始化信息错误时可能会导致数据出错

        position = self.find_list_position(volt_list, volt)

        if type(position) is int:
            volt_level = hex(volt_level[position])[2:].upper()
            command = '<VOL1{}>'.format(volt_level)
            self.PSB4032.send(command.encode())
            logging.info('设置恒压输出 CMD: ' + command)
            logging.info('设置恒压输出 电压: ' + str(volt) + 'V')

        elif type(position) is list:
            slope = (volt_level[position[1]] - volt_level[position[0]]) / (
                    volt_list[position[1]] - volt_list[position[0]])
            intercept = volt_level[position[0]] - slope * volt_list[position[0]]
            volt_level_hex = hex(math.floor(slope * volt + intercept))[2:].upper()
            command = '<VOL1{}>'.format(volt_level_hex)
            self.PSB4032.send(command.encode())
            logging.info('设置恒压输出 CMD: ' + command)
            logging.info('设置恒压输出 电压: ' + str(volt) + 'V')

    def set_cc_current(self, curr):

        if curr > 30 or curr < -30:
            return

        curr_list = []
        curr_level = []

        curr_diff_key = [key for key in self.init_info_dict if key.startswith('电流差值')]
        curr_diff_key.sort(key=lambda L: int(re.findall('\d+', L)[0]))

        for key in curr_diff_key:
            curr_list.append(self.init_info_dict[key][0])
            curr_level.append(self.init_info_dict[key][1])

        # curr_list = sorted(curr_list)
        # curr_level = sorted(curr_level)

        position = self.find_list_position(curr_list, curr)

        if type(position) is int:
            curr_level = hex(curr_level[position])[2:].upper()
            command = '<CUR1{}>'.format(curr_level)
            self.PSB4032.send(command.encode())
            logging.info('设置恒流输出 CMD: ' + command)
            logging.info('设置恒流输出 电流: ' + str(curr) + 'A')

        elif type(position) is list:
            slope = (curr_level[position[1]] - curr_level[position[0]]) / (
                    curr_list[position[1]] - curr_list[position[0]])
            intercept = curr_level[position[0]] - slope * curr_list[position[0]]
            curr_level_hex = hex(math.floor(slope * curr + intercept))[2:].upper()
            command = '<CUR1{}>'.format(curr_level_hex)
            self.PSB4032.send(command.encode())
            logging.info('设置恒流输出 CMD: ' + command)
            logging.info('设置恒流输出 电流: ' + str(curr) + 'A')

    def set_linear_wave(self, output_mode, position, StartVolt, EndVolt, Time, TimeUnit, num):

        # 线性波
        """
        position range: 0-63
        StartValue: range: -40-40(V)  ---> Start voltage
        EndValue: range: -40-40(V)    ---> end voltage
        time range: 0-16000000                  ---> generate time
        TimeUnit: {                                 ---> time unit
                'u' : us
                'm' : ms
                's' : s
                }
        num:                                    ---> wave number

        """
        if position < 0 or position > 63 or type(position) is not int:
            return
        if StartVolt < -40 or StartVolt > 40:
            return
        if EndVolt < -40 or EndVolt > 40:
            return
        if Time < 0 or Time > 16000000:
            return
        if TimeUnit.upper() not in ['S', 'M', 'U']:
            return
        if num < 1 or num > 65535 or type(num) is not int:
            return
        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        position_hex = self.full_hex(2, str(self.hex_convert(position)))

        gain = None
        base = None

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']

        start_volt_hex = self.full_hex(4, self.hex_convert(round(StartVolt * gain + base)))
        end_volt_hex = self.full_hex(4, self.hex_convert(round(EndVolt * gain + base)))
        time_hex = self.full_hex(6, str(self.hex_convert(Time)))
        num_hex = self.full_hex(4, str(self.hex_convert(num)))
        command = 'APS{}1{}{}{}{}{}'.format(position_hex, start_volt_hex, end_volt_hex, time_hex, TimeUnit, num_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(command)

        logging.info('设置线性波输出 CMD: ' + command)

        logging.info('设置线性波输出, 组别:{} 起始电压:{}V 结束电压:{}V 运行时间:{}{}s 整波数量:{}'
                     .format(position, StartVolt, EndVolt, Time, TimeUnit, num))

    def set_sin_wave(self, output_mode, position, StartVolt, EndVolt, vpp, FreqMode,
                     StartFreq, EndFreq, Time, TimeUnit, FreqStep):

        # 正弦波
        """
        position    range: 0-63
        StartOffset range: -40-40V
        EndOffset   range: -40-40V
        vpp         range: -40-40V
        freqMode    {
                        0 : fixed
                        1 : logarithm(log)
                        2 : linear
                    }
                    Note: step is xx% when use logarithm freq-step mode. Freq-step <999(99.9%)
        StartFreq   range: 1-3000000= StartFreq*10(MAX:300KHz)
        EndFreq     Ditto
        Time        range: 1-16000000
        TimeUnit    {                                 ---> time unit
                'm' : ms
                's' : s
                }
        FreqStep range 1-65535Hz or 0.1-99% (set by 1-999)


        1.  FreqStep is immutable if FreqMode is fixed
            FreqStep is xxxHz if FreqMode is linear(1-65535Hz)
            FreqStep is xx% if FreqMode is logarithm(0.1-99% -> 1-999)
        2.  EndStep is unnecessary if FreqMode is fixed
        3.  EndOffset is unnecessary if FreqMode is logarithm or linear

        """
        if position < 0 or position > 63 or type(position) is not int:
            return
        if StartVolt < -40 or StartVolt > 40:
            return
        if EndVolt < -40 or EndVolt > 40:
            return
        if vpp < 0 or vpp > 78:
            return
        if FreqMode not in range(0, 3):
            return
        if StartFreq < 0.1 or StartFreq > 300000:
            return
        if EndFreq < 0.1 or EndFreq > 300000:
            return
        if Time < 0.1 or Time > 16000000:
            return
        if TimeUnit.upper() not in ['S', 'M']:
            return
        if TimeUnit.upper() == 'S':
            if 0.1 <= Time <= 16000:
                pass
            else:
                return
        if TimeUnit.upper() == 'M':
            if 100 <= Time <= 16000000:
                pass
            else:
                return
        if FreqMode == 1:
            if FreqStep < 1 or FreqStep > 999:
                return
        if FreqMode == 2:
            if FreqStep < 1 or FreqStep > 65535:
                return
        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        if TimeUnit.upper() == "S":
            total_Time = Time * 1000
        elif TimeUnit.upper() == "M":
            total_Time = Time
        else:
            return

        if total_Time % 100 == 0:
            pass
        else:
            logging.info('设置时间必须为100ms的倍数，已退出!')
            sys.exit()

        position_hex = self.full_hex(2, str(self.hex_convert(position)))

        gain = None
        base = None

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']
        start_volt_hex = self.full_hex(4, self.hex_convert(round(StartVolt * gain + base)))
        end_volt_hex = self.full_hex(4, self.hex_convert(round(EndVolt * gain + base)))
        vpp_hex = self.full_hex(4, self.hex_convert(round(vpp / 2 * gain)))
        start_freq_hex = self.full_hex(6, str(self.hex_convert(int(StartFreq * 10))))
        end_freq_hex = self.full_hex(6, str(self.hex_convert(int(EndFreq * 10))))
        time_hex = self.full_hex(6, str(self.hex_convert(int(total_Time))))

        # if FreqMode == 1:
        #     FreqStep *= 10
        # elif FreqMode == 2:
        #     pass

        freq_step_hex = self.full_hex(4, str(self.hex_convert(FreqStep * 10)))

        command = '<APS{}2{}{}{}{}{}{}{}{}{}>'.format(position_hex, start_volt_hex, end_volt_hex, vpp_hex, FreqMode,
                                                      start_freq_hex, end_freq_hex, time_hex, 'm', freq_step_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(command)

        logging.info('设置正弦波输出 CMD: ' + command)

        if output_mode.upper() == 'CV':
            if FreqMode == 0:
                logging.info('设置CV模式正弦波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 频率:{}Hz 步进方式: 固定 运行时间:{}{}'
                             .format(position, StartVolt, EndVolt, vpp, StartFreq, Time, TimeUnit))
            if FreqMode == 1:
                logging.info('设置CV模式正弦波输出: 组别:{} 起始电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式: 对数 频率步长:{}% 驻留时间:{}{}'
                             .format(position, StartVolt, vpp, StartFreq, EndFreq, FreqStep, Time, TimeUnit))
            if FreqMode == 2:
                logging.info('设置CV模式正弦波输出: 组别:{} 起始电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式: 线性 频率步长:{}Hz 驻留时间:{}{}'
                             .format(position, StartVolt, vpp, StartFreq, EndFreq, FreqStep, Time, TimeUnit))

        if output_mode.upper() == 'CC':
            if FreqMode == 0:
                logging.info('设置CC模式正弦波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 频率:{}Hz 步进方式: 固定 运行时间:{}{}'
                             .format(position, StartVolt, EndVolt, vpp, StartFreq, Time, TimeUnit))
            if FreqMode == 1:
                logging.info('设置CC模式正弦波输出: 组别:{} 起始电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式: 对数 频率步长:{}% 驻留时间:{}{}'
                             .format(position, StartVolt, vpp, StartFreq, EndFreq, FreqStep, Time, TimeUnit))
            if FreqMode == 2:
                logging.info('设置CC模式正弦波输出: 组别:{} 起始电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式: 线性 频率步长:{}Hz 驻留时间:{}{}'
                             .format(position, StartVolt, vpp, StartFreq, EndFreq, FreqStep, Time, TimeUnit))

    def set_triangular_wave(self, output_mode, position, StartVolt, EndVolt, vpp, FreqMode,
                            StartFreq, EndFreq, Time, TimeUnit, FreqStep):

        # 三角波

        """

        Same as Sin-wave set

        """

        if position < 0 or position > 63 or type(position) is not int:
            return
        if StartVolt < -40 or StartVolt > 40:
            return
        if EndVolt < -40 or EndVolt > 40:
            return
        if vpp < 0 or vpp > 78:
            return
        if FreqMode not in range(0, 3):
            return
        if StartFreq < 0.1 or StartFreq > 99999:
            return
        if EndFreq < 0.1 or EndFreq > 99999:
            return
        if TimeUnit.upper() == 'S':
            if 0.1 <= Time <= 16000:
                pass
            else:
                return
        if TimeUnit.upper() == 'M':
            if 100 <= Time <= 16000000:
                pass
            else:
                return
        if FreqMode == 1:
            if FreqStep < 1 or FreqStep > 999:
                return
        if TimeUnit.upper() not in ['S', 'M', 'U']:
            return
        if FreqMode == 2:
            if FreqStep < 1 or FreqStep > 65535:
                return

        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        if TimeUnit.upper() == "S":
            total_Time = Time * 1000
        elif TimeUnit.upper() == "M":
            total_Time = Time
        else:
            return

        if total_Time % 100 == 0:
            pass
        else:
            logging.info('设置时间必须为100ms的倍数，已退出!')
            sys.exit()

        position_hex = self.full_hex(2, str(self.hex_convert(position)))

        gain = None
        base = None

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']

        start_volt_hex = self.full_hex(4, self.hex_convert(round(StartVolt * gain + base)))
        end_volt_hex = self.full_hex(4, self.hex_convert(round(EndVolt * gain + base)))
        vpp_hex = self.full_hex(4, self.hex_convert(round(vpp / 2 * gain)))
        start_freq_hex = self.full_hex(6, str(self.hex_convert(int(StartFreq * 10))))
        end_freq_hex = self.full_hex(6, str(self.hex_convert(int(EndFreq * 10))))
        time_hex = self.full_hex(6, str(self.hex_convert(int(total_Time))))
        freq_step_hex = self.full_hex(4, str(self.hex_convert(FreqStep * 10)))

        command = '<APS{}3{}{}{}{}{}{}{}{}{}>'.format(position_hex, start_volt_hex, end_volt_hex, vpp_hex, FreqMode,
                                                      start_freq_hex, end_freq_hex, time_hex, 'm', freq_step_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(command)

        logging.info('设置三角波输出 CMD: ' + command)

        if output_mode.upper() == 'CV':
            if FreqMode == 0:
                logging.info('设置CV模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 频率:{}Hz 步进方式:固定 运行时间:{}{}s'
                             .format(position, StartVolt, EndVolt, vpp, StartFreq, Time, TimeUnit))
            if FreqMode == 1:
                logging.info('设置CV模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式:对数 频率步长:{}% '
                             '驻留时间:{}{}'.format(position, StartVolt, EndVolt, vpp, StartFreq,
                                                    EndFreq, FreqStep, Time, TimeUnit))
            if FreqMode == 2:
                logging.info('设置CV模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式:线性 频率步长:{}Hz '
                             '驻留时间:{}{}'.format(position, StartVolt, EndVolt, vpp, StartFreq,
                                                    EndFreq, FreqStep, Time, TimeUnit))

        if output_mode.upper() == 'CC':
            if FreqMode == 0:
                logging.info('设置CC模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 频率:{}Hz 步进方式:固定 运行时间:{}{}s'
                             .format(position, StartVolt, EndVolt, vpp, StartFreq, Time, TimeUnit))
            if FreqMode == 1:
                logging.info('设置CC模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式:对数 频率步长:{}% '
                             '驻留时间:{}{}s'.format(position, StartVolt, EndVolt, vpp,
                                                     StartFreq, EndFreq, FreqStep, Time, TimeUnit))
            if FreqMode == 2:
                logging.info(
                    '设置CC模式三角波输出: 组别:{} 起始电压:{}V 结束电压:{}V 峰峰值:{}V 起始频率:{}Hz 结束频率:{}Hz 步进方式:线性 频率步长:{}Hz 驻留时间:{}{}'
                    .format(position, StartVolt, EndVolt, vpp, StartFreq, EndFreq, FreqStep, Time, TimeUnit))

    def set_exponential_wave(self, output_mode, position, StartVolt, EndVolt, Time, TimeUnit, Num):

        # 指数波(升、降)

        """

        """

        if position < 0 or position > 63 or type(position) is not int:
            return
        if StartVolt < -40 or StartVolt > 40:
            return
        if EndVolt < -40 or EndVolt > 40:
            return
        if Time < 1 or Time > 16000000:
            return
        if TimeUnit.upper() not in ['S', 'M', 'U']:
            return
        if Num < 1 or Num > 65535 or type(Num) is not int:
            return
        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        gain = None
        base = None

        position_hex = self.full_hex(2, str(self.hex_convert(position)))

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']

        start_volt_hex = self.full_hex(4, self.hex_convert(round(StartVolt * gain + base)))
        end_volt_hex = self.full_hex(4, self.hex_convert(round(EndVolt * gain + base)))
        time_hex = self.full_hex(4, str(self.hex_convert(Time)))
        num_hex = self.full_hex(4, str(self.hex_convert(Num)))

        if EndVolt > StartVolt:
            self.command = '<APS{}4{}{}{}{}{}>'.format(position_hex, start_volt_hex, end_volt_hex,
                                                       time_hex, TimeUnit.lower(), num_hex)
        elif EndVolt < StartVolt:
            self.command = '<APS{}5{}{}{}{}{}>'.format(position_hex, start_volt_hex, end_volt_hex,
                                                       time_hex, TimeUnit.lower(), num_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(self.command)

        logging.info('设置指数波输出 CMD: ' + self.command)

        if output_mode.upper() == 'CV':
            logging.info('设置CV模式指数波输出: 组别:{} 起始电压:{}V 结束电压:{}V 运行时间:{}{}s 整波数量:{}'
                         .format(position, StartVolt, EndVolt, Time, TimeUnit, Num))
        if output_mode.upper() == 'CC':
            logging.info('设置CC模式指数波输出: 组别:{} 起始电压:{}V 结束电压:{}V 运行时间:{}{}s 整波数量:{}'
                         .format(position, StartVolt, EndVolt, Time, TimeUnit, Num))

    def set_square_wave(self, output_mode, position, Volt1, Volt2, Time1, Time1Unit, Time2, Time2Unit, Num):

        """
        Volt1   range: -40~40V
        Volt2   range: -40~40V
        Time1   type: int(>0)                       ---> Volt1's time
        Time2   type: int(>0)                       ---> Volt2's time
        TimeUnit1/2: {                                 ---> time unit
                'u' : us
                'm' : ms
                's' : s
                }
        num:                                    ---> wave number
        """

        if position < 0 or position > 63 or type(position) is not int:
            return
        if Volt1 < -40 or Volt1 > 40:
            return
        if Volt2 < -40 or Volt2 > 40:
            return
        if Time1 < 1 or Time1 > 16000000:
            return
        if Time2 < 1 or Time2 > 16000000:
            return
        if Time1Unit.upper() not in ['S', 'M', 'U']:
            return
        if Time2Unit.upper() not in ['S', 'M', 'U']:
            return
        if Num < 1 or Num > 65535 or type(Num) is not int:
            return
        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        position_hex = self.full_hex(2, str(self.hex_convert(position)))

        gain = None
        base = None

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']

        Volt1_hex = self.full_hex(4, self.hex_convert(round(Volt1 * gain + base)))
        Volt2_hex = self.full_hex(4, self.hex_convert(round(Volt2 * gain + base)))
        time1_hex = self.full_hex(4, str(self.hex_convert(Time1)))
        time2_hex = self.full_hex(4, str(self.hex_convert(Time2)))
        num_hex = self.full_hex(4, str(self.hex_convert(Num)))

        command = '<APS{}6{}{}{}{}{}{}{}>'.format(position_hex, Volt1_hex, Volt2_hex,
                                                  time1_hex, Time1Unit, time2_hex, Time2Unit, num_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(command)

        logging.info('设置方波输出 CMD: ' + command)

        if output_mode.upper() == 'CV':
            logging.info('设置CV模式指数波输出: 组别:{} 电平1:{}V 运行时间1:{}{}s 电平2:{}V 运行时间2:{}{}s 整波数量:{}'
                         .format(position, Volt1, Time1, Time1Unit, Volt2, Time2, Time2Unit, Num))
        if output_mode.upper() == 'CC':
            logging.info('设置CC模式指数波输出: 组别:{} 电平1:{}A 运行时间1:{}{}s 电平2:{}A 运行时间2:{}{}s 整波数量:{}'
                         .format(position, Volt1, Time1, Time1Unit, Volt2, Time2, Time2Unit, Num))

    def set_attenuation_wave(self, output_mode, position, VoltOffset, vpp, freq, Time, coefficient, num):

        """

        VoltOffset  range: -40~40V
        vpp         range: 0~80V
        freq        range: 0~100kHz
        time        It's D1-D4 when time is 1-4(int)
        coefficient Second peak/first peak = coefficient(1-99%)
        num         number of wave

        """

        if position < 0 or position > 63 or type(position) is not int:
            return
        if VoltOffset < -40 or VoltOffset > 40:
            return
        if vpp < 0 or vpp > 80:
            return
        if freq < 1 or freq > 100000:
            return
        if Time < 1 or Time > 16000000:
            return
        if coefficient < 1 or coefficient > 99:
            return
        if num < 1 or num > 65535 or type(num) is not int:
            return
        if output_mode.upper() == 'CC' or output_mode.upper() == 'CV':
            pass
        else:
            sys.exit()

        gain = None
        base = None

        if output_mode.upper() == 'CV':
            gain = round(self.init_info_dict['电压增益'])
            base = self.init_info_dict['电压基准']
        elif output_mode.upper() == 'CC':
            gain = round(self.init_info_dict['电流增益'])
            base = self.init_info_dict['电流基准']

        position_hex = self.full_hex(2, str(self.hex_convert(position)))
        start_volt_hex = self.full_hex(4, self.hex_convert(round(VoltOffset * gain + base)))
        vpp_hex = self.full_hex(4, self.hex_convert(round(vpp / 2 * gain)))
        freq_hex = self.full_hex(6, str(self.hex_convert(freq * 10)))
        time_hex = self.full_hex(6, str(self.hex_convert(int(Time / 10))))
        attenuation = self.full_hex(2, str(self.hex_convert(coefficient)))
        num_hex = self.full_hex(4, str(self.hex_convert(num)))

        command = '<APS{}7{}0000{}0{}000000{}{}{}>'.format(position_hex, start_volt_hex, vpp_hex,
                                                           freq_hex, time_hex, attenuation, num_hex)

        self.reset_group_wave()

        if output_mode.upper() == 'CV':
            self.write_data('VOL18000')
        elif output_mode.upper() == 'CC':
            self.write_data('CUR18000')

        self.write_data(command)

        logging.info('设置衰减波输出 CMD: ' + command)

        if output_mode.upper() == 'CV':
            logging.info('设置CV模式指数波输出: 组别:{} 偏置电压:{}V 峰峰值:{}V 频率:{}Hz 衰减系数:{} 间隔时间:{}s 整波数量:{}'
                         .format(position, VoltOffset, vpp, freq, coefficient, Time, num))
        if output_mode.upper() == 'CC':
            logging.info('设置CV模式指数波输出: 组别:{} 偏置电压:{}A 峰峰值:{}A 频率:{}Hz 衰减系数:{} 间隔时间:{}s 整波数量:{}'
                         .format(position, VoltOffset, vpp, freq, coefficient, Time, num))

    def run_group_wave(self, WaveSum, num):

        wave_sum_hex = self.full_hex(2, str(self.hex_convert(WaveSum)))
        num_hex = self.full_hex(4, str(self.hex_convert(num)))
        self.write_data('CNT{}{}'.format(wave_sum_hex, num_hex))
        self.write_data('RUNC')
        # self.write_data('STO')
        logging.info('组合波发送波形数量{}, 循环次数{}'.format(WaveSum, num))

    def set_power_res(self, res):

        if res < 0 or res > 500:
            return
        if res is not int:
            return
        res_hex = self.full_hex(4, self.hex_convert(res * 10))
        self.write_data('SETR{}'.format(res_hex))
        logging.info('设置电源内阻{}mΩ CMD: '.format(res) + 'SETR{}'.format(res_hex))

    def read_temp(self):
        # global temperature

        temp = 0
        flag = 1
        logging.info('读取温度开始:')
        while flag:
            recv_data = self.PSB4032.recv(4096)
            # noinspection PyBroadException
            try:
                info = recv_data.decode("utf-8")
                if 'TEM' in info:
                    temp += 1
                    temp_data = info
                    self.temperature = int(temp_data.split('M')[1].split('>')[0])
                    self.temperature = (
                            str(round((3950 / (math.log((40950 / (4095 - self.temperature) - 10) / 10)
                                               + (3950 / 298.15)) - 273.15), 3)) + '℃')
                    logging.info('当前温度:' + str(self.temperature))
                if temp == 1:
                    flag = 0
            except Exception:
                pass

    def read_real_time_VoltCurr(self, read_time):

        flag = 1
        while flag:
            recv_datas = 0
            real_time_data = 0
            try:
                recv_datas = self.receive_real_time_data()
            except ConnectionResetError:
                pass

            for recv_data in recv_datas:
                if 'SENDVOL' in recv_data:
                    flag = 0
                real_time_data = recv_data

            # print('电压电流数据: ' + real_time_data)

            self.real_time_vlot = real_time_data.split('SENDVOL')[1].split('>')[0]
            self.real_time_curr = real_time_data.split('SENDCUR')[1].split('>')[0]

            # print(self.real_time_vlot, self.real_time_curr)

            if not -40 < float(int(self.real_time_vlot, 16) / 100) < 40:
                self.real_time_vlot = self.complement(self.real_time_vlot) / 100
            else:
                self.real_time_vlot = int(self.real_time_vlot, 16) / 100

            if not -30 < float(int(self.real_time_curr, 16) / 100) < 30:
                self.real_time_curr = self.complement(self.real_time_curr) / 100
            else:
                self.real_time_curr = int(self.real_time_curr, 16) / 100

            logging.info(
                '当前电压:{}V\t'.format(str(self.real_time_vlot)) + '当前电流:{}A'.format(str(self.real_time_curr)))

            time.sleep(read_time)

        return self.real_time_vlot, self.real_time_curr

    def write_data(self, send_command):
        command = "<{}>".format(send_command)
        self.PSB4032.sendall(command.encode())
        logging.info('CMD: ' + command)

    def read_data(self):

        recv_data = self.PSB4032.recv(4096)
        recv_data = recv_data.decode()
        return recv_data

    def receive_data(self):

        recv_data_list = []
        temp = 0
        flag = 1
        while flag:
            recv_data = self.PSB4032.recv(4096)
            # noinspection PyBroadException
            try:
                info = recv_data.decode("utf-8")
                if 'TEM' in info:
                    temp += 1
                if temp == 3:
                    flag = 0
                recv_data_list.append(recv_data.decode())
            except Exception:
                continue

        return recv_data_list

    def receive_real_time_data(self):

        recv_data_list = []
        temp = 0
        flag = 1
        while flag:
            recv_data = self.PSB4032.recv(4096)
            # noinspection PyBroadException
            try:
                info = recv_data.decode("utf-8")
                if 'SENDVOL' in info:
                    temp += 1
                if temp == 1:
                    flag = 0
                recv_data_list.append(recv_data.decode())
            except Exception:
                continue

        return recv_data_list

    def get_init_info(self):

        self.init_info_list = []

        while True:
            self.recv_data_list = self.receive_data()
            self.init_info_dict = {}
            for recv in self.recv_data_list:
                if '<' in recv:
                    init_info = re.findall(r'<(.*?)>', recv)
                    self.init_info_list.append(init_info)
                else:
                    pass

            self.init_info_list = list(itertools.chain.from_iterable(self.init_info_list))

            for info in self.init_info_list:
                if "NUMBER" in info:
                    info = info.split('R')[1]
                    info = int(info, 16)
                    self.init_info_dict['设备编号'] = info

                elif "GAINVOL" in info:
                    if "SHOW" not in info:
                        info = info.split('L')[1]
                        info = int(info, 16) / 100
                        self.init_info_dict['电压增益'] = info

                elif "GAINCUR" in info:
                    if "SHOW" not in info:
                        info = info.split('R')[1]
                        info = int(info, 16) / 100
                        self.init_info_dict['电流增益'] = info

                elif "MIDVOL" in info:
                    if "SHOW" not in info:
                        info = info.split('L')[1]
                        info = int(info, 16)
                        self.init_info_dict['电压基准'] = info

                elif "MIDCUR" in info:
                    if "SHOW" not in info:
                        info = info.split('R')[1]
                        info = int(info, 16)
                        self.init_info_dict['电流基准'] = info

                elif "MAXVOL" in info:
                    info = info.split('L')[1]
                    info = int(info, 16) / 100
                    self.init_info_dict['最大电压'] = info

                elif "MAXCUR" in info:
                    info = info.split('R')[1]
                    info = int(info, 16) / 100
                    self.init_info_dict['最大电流'] = info

                elif "MINVOL" in info:
                    info = info.split('L')[1]
                    info = self.complement(info) / 100
                    self.init_info_dict['最小电压'] = info

                elif "MINCUR" in info:
                    info = info.split('R')[1]
                    info = self.complement(info) / 100
                    self.init_info_dict['最小电流'] = info

                elif "CURDI" in info:
                    current_list = []
                    cur_diff_group = info[5:7]
                    cur_diff_group = int(cur_diff_group, 16)
                    current = info[7:11]
                    current_act = info[11:15]
                    current_act = int(current_act, 16)

                    if current[0] == 'F':
                        current = int(self.complement(current)) / 100
                    else:
                        current = int(current, 16) / 100

                    current_list.append(current)
                    current_list.append(current_act)

                    self.init_info_dict['电流差值{}组(电流值,实际值)'.format(cur_diff_group)] = current_list

                elif "VOLDI" in info:
                    volt_list = []
                    vol_diff_group = info[5:7]
                    vol_diff_group = int(vol_diff_group, 16)
                    volt = info[7:11]
                    volt_act = info[11:15]
                    volt_act = int(volt_act, 16)

                    if volt[0] == 'F':
                        volt = int(self.complement(volt)) / 100
                    else:
                        volt = int(volt, 16) / 100

                    volt_list.append(volt)
                    volt_list.append(volt_act)

                    self.init_info_dict['电压差值{}组(电压值,实际值)'.format(vol_diff_group)] = volt_list

                elif "AVOL" in info:

                    lim_volt_list = []
                    lim_vol_diff_group = info[4:6]
                    vol_diff_group = int(lim_vol_diff_group, 16)
                    lim_volt = info[6:10]
                    lim_volt_act = info[10:14]
                    lim_volt_act = int(lim_volt_act, 16)

                    if lim_volt[0] == 'F':
                        lim_volt = int(self.complement(lim_volt)) / 100
                    else:
                        lim_volt = int(lim_volt, 16) / 100

                    lim_volt_list.append(lim_volt)
                    lim_volt_list.append(lim_volt_act)

                    self.init_info_dict['限制正电压差值{}组(电压值,实际值)'.format(vol_diff_group)] = lim_volt_list

                elif "SVOL" in info:

                    lim_volt_list = []
                    lim_vol_diff_group = info[4:6]
                    vol_diff_group = int(lim_vol_diff_group, 16)
                    lim_volt = info[6:10]
                    lim_volt_act = info[10:14]
                    lim_volt_act = int(lim_volt_act, 16)

                    if lim_volt[0] == 'F':
                        lim_volt = int(self.complement(lim_volt)) / 100
                    else:
                        lim_volt = int(lim_volt, 16) / 100

                    lim_volt_list.append(lim_volt)
                    lim_volt_list.append(lim_volt_act)

                    self.init_info_dict['限制负电压差值{}组(电压值,实际值)'.format(vol_diff_group)] = lim_volt_list

                elif "ACUR" in info:

                    lim_curr_list = []
                    lim_curr_diff_group = info[4:6]
                    curr_diff_group = int(lim_curr_diff_group, 16)
                    lim_curr = info[6:10]
                    lim_curr_act = info[10:14]
                    lim_curr_act = int(lim_curr_act, 16)

                    if lim_curr[0] == 'F':
                        lim_curr = int(self.complement(lim_curr)) / 100
                    else:
                        lim_curr = int(lim_curr, 16) / 100

                    lim_curr_list.append(lim_curr)
                    lim_curr_list.append(lim_curr_act)

                    self.init_info_dict['限制正电流差值{}组(电流值,实际值)'.format(curr_diff_group)] = lim_curr_list

                elif "SCUR" in info:

                    lim_curr_list = []
                    lim_curr_diff_group = info[4:6]
                    curr_diff_group = int(lim_curr_diff_group, 16)
                    lim_curr = info[6:10]
                    lim_curr_act = info[10:14]
                    lim_curr_act = int(lim_curr_act, 16)

                    if lim_curr[0] == 'F':
                        lim_curr = int(self.complement(lim_curr)) / 100
                    else:
                        lim_curr = int(lim_curr, 16) / 100

                    lim_curr_list.append(lim_curr)
                    lim_curr_list.append(lim_curr_act)

                    self.init_info_dict['限制负电流差值{}组(电流值,实际值)'.format(curr_diff_group)] = lim_curr_list

                # elif "SENDVOL" in info:
                #     info = info.split('L')[1]
                #     info = int(info, 16)/100
                #     self.init_info_dict['目前电压值'] = info
                #
                # elif "SENDCUR" in info:
                #     info = info.split('R')[1]
                #     info = int(info, 16) / 100
                #     self.init_info_dict['目前电流值'] = info

            if len(self.init_info_dict) == 49:
                pd.set_option('display.float_format', lambda x: '%.f' % x)
                df = pd.DataFrame(self.init_info_dict)
                df = df.T.head(49)
                df_1 = df[0:8]
                df_2 = df[9:49]
                df_1 = df_1.drop(labels=[1], axis=1)
                str_df1 = df_1.to_string()
                str_df2 = df_2.to_string()
                str_df = str_df1 + str_df2
                logging.info('初始化信息: \n' + str_df)
                break
            else:
                # logging.info('初始化信息获取失败，重新获取...')
                self.rj45_disconnect()
                time.sleep(0.01)
                self.reset_init()
        return self.init_info_dict

    def reset_group_wave(self):

        self.write_data('STO')
        logging.info('初始化组合波')

    def reset_volt_output(self):

        self.write_data('VOL18000')
        logging.info('恒压输出归零')

    def reset_curr_output(self):
        self.write_data('CUR18000')
        logging.info('恒流输出归零')

    def reset_init(self):

        self.PSB4032 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PSB4032.connect((self.host, self.port))

    def rj45_disconnect(self):

        self.PSB4032.close()

    @staticmethod
    def hex_convert(dec):

        hex_data = hex(dec)[2:]
        return hex_data.upper()

    @staticmethod
    def complement(data):

        a = int(data, 16) - 1
        a = bin(a)
        bin_code = list(a)
        bin_code = list(bin_code)
        negation_bin_code = []
        for i in range(2, 18):
            if bin_code[i] == '0':
                negation_bin_code.append('1')
            elif bin_code[i] == '1':
                negation_bin_code.append('0')
        negation_bin_code = ''.join(negation_bin_code)
        negation_bin_code = '0b' + negation_bin_code
        oct_code = -int(negation_bin_code, 2)
        return oct_code

    @staticmethod
    def full_hex(LenthHex, HexData):

        if LenthHex - len(HexData) > 0:
            full_hex_data = ('0' * (LenthHex - len(HexData)) + HexData).upper()
        else:
            full_hex_data = HexData
        return full_hex_data

    @staticmethod
    def find_list_position(List, number):

        if number < List[0] or number > List[-1]:
            print('超出输出范围')
        else:
            flag = 1
            i = 0
            while flag:
                if number == List[i]:
                    return i
                elif List[i + 1] > number > List[i]:
                    return [i, i + 1]
                else:
                    i += 1

    @staticmethod
    def logging_setup():
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
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        fileinfo.setFormatter(formatter)
        controlshow.setFormatter(formatter)

        logger.addHandler(fileinfo)
        logger.addHandler(controlshow)
