import json
import pprint
import re
import shutil
import time
# import socket
from queue import Queue
from pycore.base import *
import datetime
from time import strftime
from time import gmtime
# import xml.etree.ElementTree as etree
from urllib.parse import *
import inspect
import operator
import psutil
import subprocess
from decimal import Decimal
import pandas
import random
import platform

class Util(Base):
    RED = '\033[31;1m'
    GREEN = '\033[32;1m'
    YELLOW = '\033[33;1m'
    BLUE = '\033[34;1m'
    MAGENTA = '\033[35;1m'
    CYAN = '\033[36;1m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

    def __init__(self, args):
        pass

    def print_success(self, message, time=False):
        if time: message = f"{message} : {self.com_string.create_time()}"
        print(f"\033[0;37;42m{message}\033[0m")
        return self.print_result(message, -1)

    def print_danger(self, message, time=False):
        if time: message = f"{message} : {self.com_string.create_time()}"
        print(f"{self.RED}{message}\033[0m")
        return self.print_result(message, -1)

    def print_warn(self, message, time=False):
        if time: message = f"{message} : {self.com_string.create_time()}"
        print(f"{self.MAGENTA}{message}\033[0m")
        return self.print_result(message, -1)

    def print_info(self, message, time=False):
        if time: message = f"{message} : {self.com_string.create_time()}"
        print(f"\033[0;32;40m{message}\033[0m")
        return self.print_result(message, -1)

    def print_data(self, data):
        return self.result(data)

    def print_result(self, data, code=0):
        if data or data == None:
            if data == None:
                message = self.print_message("Sql request execute succeeded.", code)
            else:
                message = self.print_message("Data acquisition succeeded.", code)
            if type(data) == str:
                if data.startswith("base64:"):
                    show_message = "DataStringify acquisition succeeded"
                else:
                    show_message = data
                message = self.print_message(show_message, code)
            if type(data) != list:
                data = [data]
            length = len(data)
        else:
            message = self.print_message("Data acquisition failed.", -1)
            length = 0
        message["length"] = length
        message["data"] = data
        return message

    def print_message(self, msg, code=0):
        message = {
            "message": msg,
            "code": code
        }
        return message

    def pprint(self, data):
        pprint.pprint(data)

    def deduplication(self, data):
        try:
            data = list(
                set(data)
            )
        except Exception as e:
            print("deduplication_info", e)
            try:
                data = [list(t) for t in set([tuple(d) for d in data])]
            except Exception as e:
                print("deduplication_info", e)
                try:
                    data = set([str(item) for item in data])
                    data = [eval(i) for i in data]
                except Exception as e:
                    print("deduplication_info", e)
        return data

    def get_parameter(self, method, info=True):
        parameter_names = inspect.getfullargspec(method)
        parameter_names = parameter_names.args
        if info: self.print_info(f"parameter: [{', '.join(parameter_names)}]", )
        return parameter_names

    def create_time(self, format="%Y-%m-%d %H:%M:%S"):
        t = time.strftime(format, time.localtime())
        return t

    def create_timepoint(self):
        return float(time.strftime("%H.%M", time.localtime()))

    def format_timestamp(self, timestamp):
        if type(timestamp) == str:
            timestamp = int(timestamp)
        if timestamp > (1000000000000 - 1):
            timestamp = timestamp / 1000
        return timestamp

    def timestamp_todate(self, timestamp):
        timestamp = self.format_timestamp(timestamp)
        return datetime.datetime.fromtimestamp(timestamp)

    def timer(self, starttime, format="%Y-%m-%d %H:%M:%S"):
        if type(starttime) == str:
            starttime = datetime.datetime.strptime(starttime, format)
        endtime = datetime.datetime.now()
        time_difference = (endtime - starttime).seconds
        time_statistics = strftime("%H:%M:%S", gmtime(time_difference))
        return time_statistics

    def equal_time(self, starttime, endtime, format="%Y-%m-%d %H:%M:%S"):
        if type(starttime) == str:
            starttime = datetime.datetime.strptime(starttime, format)
        if type(endtime) == str:
            endtime = datetime.datetime.strptime(endtime, format)
        time_difference = endtime > starttime
        # time_statistics = strftime("%H:%M:%S", gmtime(time_difference))
        return time_difference

    def format_time(self, timestr, ):
        if timestr in [None, ''] or timestr.startswith("1970"):
            timestr = "1970-02-01 08:00:00"
        return timestr

    def create_time_now(self):
        now = datetime.datetime.now()
        return now

    def create_timestamp(self, length=10):
        now = int(round(time.time()))
        if length == 13:
            now = now * 1000
        return now

    def date_totimestamp(self, length=10):
        now = int(round(time.time()))
        if length == 13:
            now = now * 1000
        return now

    def totimestamp(self, timestr):
        from datetime import datetime
        timestr = self.format_time(timestr)
        format = self.com_string.is_timestring(timestr)
        date_object = datetime.strptime(timestr, format)
        try:
            timestamp = date_object.timestamp()
        except:
            timestamp = 0
        return int(timestamp)

    def timetoformat(self, timestamp):
        if type(timestamp) == str:
            timestamp = self.totimestamp(timestamp)
        timestamp = self.format_timestamp(timestamp)
        dt = datetime.datetime.fromtimestamp(timestamp)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        return time_str

    def proportion(self, x, rate=0):
        if rate == 0:
            return x
        rate_value = rate / 100
        if rate > 0:
            x = x + (x * rate_value)
        else:
            x = x - (x * rate_value)
        return x

    def to_json(self, data):
        try:
            data_json = json.loads(data)
        except Exception as e:
            data_json = data
            self.print_warn(e)
        return data_json

    def urljoin(self, url, sub_url):
        url = urljoin(url, sub_url)
        return url

    def get_module_name(self, module):
        name = module.__class__.__name__
        return name

    def eq(self, initial, compare):
        if (len(initial) != len(compare)):
            return False
        initial.sort(key=lambda x: str(x))
        compare.sort(key=lambda x: str(x))
        for index in range(len(initial)):
            initial_item = initial[index]
            compare_item = compare[index]
            if initial_item != compare_item:
                return False
        return True


    def cmd(self, demand, info=False):
        outs = os.popen(demand, 'r')
        out = outs.read()
        if info == True:
            print("info:", info)
        return out

    def ping_ips(self, ips):
        queue = self.array_to_queue(ips, unique=True)
        results = []
        while queue.qsize() > 0:
            ip = queue.get()
            result = self.ping_ip(ip)
            results.append(result)
        results.sort(key=lambda x: x['timeout'])
        return results

    def ping_ip(self, ip):
        cmd = f"ping {ip}"
        self.print_info(cmd)
        outs = os.popen(cmd, 'r')
        out = outs.read()
        get_time = re.compile(r"time\=(\d+)")
        time_group = re.findall(get_time, out)
        time_outs = re.compile(r"request\s+timed\s+out", re.I)
        time_outs_group = re.findall(time_outs, out)
        time_group = [int(t) for t in time_group]
        # 如果有 Request time out
        time_outs_group = [1000 for t in time_outs_group]
        # 合并所有延迟,并计算最终值.
        time_group = time_group + time_outs_group
        timeout = 0
        for t in time_group:
            timeout += t
        divint = len(time_group)
        is_NotFound_mianhost = False
        if divint == 0:
            is_NotFound_mianhost = True
            divint = 1
        timeout = timeout // divint
        if is_NotFound_mianhost:
            print("Error:", outs)

        self.print_info(f"ip: {ip} \n\ttimeout: {timeout}ms\n")
        result = {
            "ip": ip,
            "timeout": timeout
        }
        return result

    def set_hosts_file(self, domain, ipAddress):
        file = "C:/Windows/System32/drivers/etc/HOSTS"
        # file = self.load_module.get_control_dir('HOSTS')
        # format hosts_file
        print(f"\n update hosts:({domain} with {ipAddress} in {file}")
        local_text = self.com_file.open(file)
        local_text = local_text.strip()
        local_text = re.split('[\n\r]+', local_text)

        exists_domain = f' {domain}'
        update_ip = f"{ipAddress} {domain}"
        is_add = None
        for index in range(0, len(local_text)):
            item = local_text[index].strip()
            if item.endswith(exists_domain):
                if is_add == True:
                    local_text[index] = ""
                else:
                    is_add = True
                    local_text[index] = update_ip

        # 未添加过
        if is_add == None:
            local_text.append(update_ip)

        local_text = [t.strip() for t in local_text if t != ""]
        local_text = '\n'.join(local_text) + '\n'
        self.com_file.save(file, local_text, overwrite=True)

        for i in range(10):
            self.flushdns()
            time.sleep(1)

    def flushdns(self):
        cmd = "ipconfig /flushdns"
        self.print_info(f'flushdns')
        self.cmd(cmd)

    def equal(self, origin, other):
        result = operator.eq(origin, other)
        return result

    def default_value(self, value, default=None):
        if value != None:
            return value
        else:
            return default


    def rmtree(self, dir):
        try:
            shutil.rmtree(dir, ignore_errors=False, onerror=None)
        except Exception as e:
            self.print_warn(e)

    def get_keycode(self, keycode):
        win32api = self.import_win32()
        GetKeyboardLayoutName = win32api.GetKeyboardLayoutList()
        print("GetKeyboardLayoutName", GetKeyboardLayoutName)
        if isinstance(keycode, int):
            return keycode
        keymap = {
            "0": 49, "1": 50, "2": 51, "3": 52, "4": 53, "5": 54, "6": 55, "7": 56, "8": 57, "9": 58,
            'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117, 'F7': 118, 'F8': 119,
            'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123, 'F13': 124, 'F14': 125, 'F15': 126, 'F16': 127,
            "A": 65, "B": 66, "C": 67, "D": 68, "E": 69, "F": 70, "G": 71, "H": 72, "I": 73, "J": 74,
            "K": 75, "L": 76, "M": 77, "N": 78, "O": 79, "P": 80, "Q": 81, "R": 82, "S": 83, "T": 84,
            "U": 85, "V": 86, "W": 87, "X": 88, "Y": 89, "Z": 90,
            'BACKSPACE': 8, 'TAB': 9, 'TABLE': 9, 'CLEAR': 12,
            'ENTER': 13, 'SHIFT': 16, 'CTRL': 17,
            'CONTROL': 17, 'ALT': 18, 'ALTER': 18, 'PAUSE': 19, 'BREAK': 19, 'CAPSLK': 20, 'CAPSLOCK': 20, 'ESC': 27,
            'SPACE': 32, 'SPACEBAR': 32, 'PGUP': 33, 'PAGEUP': 33, 'PGDN': 34, 'PAGEDOWN': 34, 'END': 35, 'HOME': 36,
            'LEFT': 37, 'UP': 38, 'RIGHT': 39, 'DOWN': 40, 'SELECT': 41, 'PRTSC': 42, 'PRINTSCREEN': 42, 'SYSRQ': 42,
            'SYSTEMREQUEST': 42, 'EXECUTE': 43, 'SNAPSHOT': 44, 'INSERT': 45, 'DELETE': 46, 'HELP': 47, 'WIN': 91,
            'WINDOWS': 91, 'NMLK': 144,
            'NUMLK': 144, 'NUMLOCK': 144, 'SCRLK': 145}
        key_upper = keycode.upper()
        if key_upper in keymap:
            return keymap[key_upper]
        return keycode

    def is_special_key(self, key):
        if key in ["@", "!", "~"]:
            return True
        return False

    def combine_key(self, key_code):
        if key_code == "@":
            self.down_key("SHIFT")
            self.press_key("2")
            self.release_key("SHIFT")

    def import_win32(self):
        import win32api
        return win32api

    def import_win32con(self):
        import win32con
        return win32con

    def get_mouse(self):
        try:
            from pymouse import PyMouse  # 模拟鼠标
            pyMouse = PyMouse()
            return pyMouse
        except:
            self.import_win32()
            return self.get_mouse()

    def get_keyboard(self):
        try:
            from pykeyboard import PyKeyboard  # 模拟键盘
            pyKeyboard = PyKeyboard()
            return pyKeyboard
        except:
            self.import_win32()
            return self.get_keyboard()

    def type_string(self, string):
        pyKeyboard = self.get_keyboard()
        pyKeyboard.type_string(string)

    def release_key(self, key_code):
        win32api = self.import_win32()
        win32con = self.import_win32con()
        key_code = self.get_keycode(key_code)
        win32api.keybd_event(key_code, win32api.MapVirtualKey(key_code, 0), win32con.KEYEVENTF_KEYUP, 0)

    def down_key(self, key_code):
        win32api = self.import_win32()
        key_code = self.get_keycode(key_code)
        win32api.keybd_event(key_code, win32api.MapVirtualKey(key_code, 0), 0, 0)

    def press_and_release_key(self, key_code):
        self.down_key(key_code)
        self.release_key(key_code)

    def press_key(self, key):
        key = self.get_keycode(key)
        if self.is_special_key(key) == True:
            self.combine_key(key)
        else:
            self.press_and_release_key(key)

    def get_system_metrics(self):
        import win32api
        import win32con
        result = {}
        result["x"] = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        result["y"] = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return result

    def copy_object(self, original, exclude=None):
        if exclude == None:
            exclude = []
        elif type(exclude) == str:
            exclude = [exclude]
        target = {}
        for key, val in original.items():
            if key not in exclude:
                target[key] = val
        return target

    def copylistandexclude(self, arr, exclude=None):
        return [val for val in arr if val not in exclude]

    def kill_process(self, process_name):
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                proc.kill()
                print(f"Process '{process_name}' killed.")
                return

    def compress_list(self, l):
        for i in range(len(l)):
            item = l[i]
            if type(item) == str and len(item) > 1000:
                l[i] = self.com_string.compress(item)
            elif type(item) == dict:
                l[i] = self.compress_dict(item)
            elif type(item) == list:
                l[i] = self.compress_list(item)
        return l

    def compress(self, item):
        if type(item) == str and len(item) > 1000:
            item = self.com_string.compress(item)
        elif type(item) == dict:
            item = self.compress_dict(item)
        elif type(item) == list:
            item = self.compress_list(item)
        return item

    def compress_dict(self, l):
        for i, item in l.items():
            if type(item) == str and len(item) > 1000:
                l[i] = self.com_string.compress(item)
            elif type(item) == dict:
                l[i] = self.compress_dict(item)
            elif type(item) == list:
                l[i] = self.compress_list(item)
        return l

    def uncompress(self, item):
        if type(item) == str and len(item) > 1000:
            item = self.com_string.uncompress(item)
        elif type(item) == dict:
            item = self.uncompress_dict(item)
        elif type(item) == list:
            item = self.uncompress_list(item)
        return item

    def uncompress_dict(self, l):
        for i, item in l.items():
            if type(item) == str and len(item) > 1000:
                l[i] = self.com_string.uncompress(item)
            elif type(item) == dict:
                l[i] = self.uncompress_dict(item)
            elif type(item) == list:
                l[i] = self.uncompress_list(item)
        return l

    def uncompress_list(self, l):
        for i in range(len(l)):
            item = l[i]
            if type(item) == str and len(item) > 1000:
                l[i] = self.com_string.uncompress(item)
            elif type(item) == dict:
                l[i] = self.uncompress_dict(item)
            elif type(item) == list:
                l[i] = self.uncompress_list(item)
        return l

    def compress_json(self, my_dict):
        my_dict = self.com_string.json_str(my_dict)
        my_dict = self.com_string.compress(my_dict)
        return my_dict

    def mapstrtolist(self, result):
        def resolve(arr):
            if arr.find('|') != -1:
                arr = arr.split('|')
                for i in range(len(arr)):
                    arr[i] = int(arr[i])
            else:
                arr = int(arr)
            return arr

        is_str = type(result)
        while is_str == list:
            result = result[0]
            is_str = type(result)
        result = result.split(",")
        result = [resolve(i) for i in result if i != '']
        return result

    def fill_string(self, n, fill_char="0"):
        s = ''
        while len(s) < n:
            s += fill_char

    def fill_list(self, n, fill_value="0"):
        arr = []
        while len(arr) < n:
            arr.append(fill_value)
        return arr

    def get_limit(self, flask_limit, max=100):
        if type(flask_limit) != str:
            limit = self.com_flask.get_request(flask_limit, 'limit', (0, max))
        else:
            limit = flask_limit

        if type(limit) == str:
            if limit.find(',') != -1:
                limit = limit.split(',')
                limit_start = limit[0]
                limit_end = limit[1]
            else:
                limit_start = int(limit)
                limit_end = limit_start + max
        else:
            if len(limit) > 1:
                limit_start = limit[0]
                limit_end = limit[1]
            else:
                limit_start = int(limit[0])
                limit_end = limit_start + max
        return (int(limit_start), int(limit_end))

    def circular_slice(self, arr, a, b):
        """
        从数组中循环截取从a到b的长度
        如果a或b大于数组长度,则从头截取

        :param arr: 要截取的数组
        :param a: 起始位置
        :param b: 结束位置
        :return: 截取后的子数组
        """
        # 如果a或b大于数组长度，则将它们限制在数组长度内
        a = a % len(arr)
        b = b % len(arr)
        if b >= a:
            return arr[a:b + 1]
        else:
            return arr[a:] + arr[:b + 1]

    def find_adjacent_versions(self, versions, target):
        # 将版本号列表按照 '.' 进行分割并转换为二维列表
        version_list = [list(map(int, version.split('.'))) for version in versions]
        target_list = list(map(int, target.split('.')))

        adjacent_versions = []

        # 查找是否有与目标版本号相同的版本号
        if target_list in version_list:
            adjacent_versions.append(target)
        else:
            # 如果不存在相同版本号，则查找相邻的版本号
            for version in version_list:
                # 如果当前版本号比目标版本号小，则继续查找下一个版本号
                if version < target_list:
                    continue

                # 如果当前版本号比目标版本号大，则将其作为相邻版本号之一，并退出循环
                if version > target_list:
                    adjacent_versions.append('.'.join(map(str, version)))
                    break

            # 如果不存在比目标版本号大的版本号，则返回空列表
            if len(adjacent_versions) == 0:
                return []

            # 继续查找是否存在比目标版本号大的版本号
            for version in reversed(version_list):
                # 如果当前版本号比目标版本号大，则继续查找下一个版本号
                if version > target_list:
                    continue

                # 如果当前版本号比目标版本号小，则将其作为相邻版本号之一，并退出循环
                if version < target_list:
                    adjacent_versions.insert(0, '.'.join(map(str, version)))
                    break
        return adjacent_versions

    def get_likeversion(self, supported_version, version):
        likeversion = self.find_adjacent_versions(supported_version, version)
        if len(likeversion) > 0:
            return likeversion[0]
        else:
            return None

    def exec(self, cmd):
        # 定义要执行的Shell脚本
        script = """
        cd /tmp && wget http://www.zlib.net/fossils/zlib-1.2.9.tar.gz
        tar -xvf zlib-1.2.9.tar.gz && cd zlib-1.2.9
        ./configure && make && make install
        ln -s -f /usr/local/lib/libz.so.1.2.9  /lib64/libz.so.1.2.9

        cp /www/wwwroot/project-name/pycore/libs/libstdc++.so.6.0.24 /usr/lib64/
        rm -rf /usr/lib64/libstdc++.so.6
        ln -s /usr/lib64/libstdc++.so.6.0.24 /usr/lib64/libstdc++.so.6
        strings /usr/lib64/libstdc++.so.6 | grep GLIBCXX
        """

        # 执行Shell脚本
        subprocess.run(script, shell=True, check=True)

    def insert_list(self, my_list, value, max):
        my_list.append(value)
        if len(my_list) > max:
            superflous = my_list.pop(0)
            return superflous
        return None

    def diff_time(self, time_string, now_timestamp_time):
        now_timestamp_time = int(now_timestamp_time)
        diff_time = self.get_time_delta(time_string)
        print("now_timestamp_time", now_timestamp_time, "diff_time", diff_time)
        diff_time = now_timestamp_time - (diff_time)
        return diff_time / 1000

    def before_timestamp_diff(self, time_string, banchmark_timestamp, ):
        time_diff = self.before_timestamp(time_string, banchmark_timestamp)
        return banchmark_timestamp - time_diff

    def before_timestamp(self, time_string, banchmark_timestamp, ):
        time_dict = self.com_string.parse_timetokenstring(time_string)
        if time_dict.get("add") == "+":
            banchmark_timestamp += time_dict.get("seconds")
        else:
            banchmark_timestamp -= time_dict.get("seconds")
        return banchmark_timestamp

    def get_time_delta(self, time_string, format=False, len=13):
        time_diff = datetime.timedelta()
        time_dict = self.com_string.parse_timetokenstring(time_string)
        diff_timecalculate = datetime.timedelta(hours=time_dict.get("h"), minutes=time_dict.get("m"),
                                                seconds=time_dict.get("s"))
        if time_dict.get("add") == "+":
            time_diff += diff_timecalculate
        else:
            time_diff -= diff_timecalculate
        timestamp = (datetime.datetime.now() + time_diff).timestamp()
        if len == 13:
            if timestamp < 10000000000:
                timestamp = timestamp * 1000
        if format:
            timestamp = self.timetoformat(timestamp)
        return timestamp

    def calculate_percentage(self, num1, num2):
        ratio = Decimal(num1) / Decimal(num2)
        percentage = ratio * 100
        return percentage

    def count_zeroes_and_cut(self, decimal, cut=2):
        str_decimal = str(decimal)
        zero_count = 0
        decimal_part = str_decimal.split('.')[1]

        for digit in decimal_part:
            if digit == '0':
                zero_count += 1
            else:
                break

        cut_decimal = float(str_decimal[:zero_count + cut])
        return cut_decimal

    def analyze_downorraise(self, data):
        df = pandas.DataFrame(data, columns=['value'])
        # 计算移动平均值
        rolling_mean = df['value'].rolling(window=3).mean()
        # 判断数据趋势
        if rolling_mean[-1] > rolling_mean[0]:
            return True
            print("数据呈上涨趋势")
        else:
            print("数据呈下跌趋势")
            return None

    def turnOverAnalyze(self):
        # (17832599.7597 / 24 / 60 /60 ) * 30 * 0.00233
        pass

    def list_tojson(self, lst):
        for d in lst:
            for k, v in d.items():
                v = self.com_string.reverse_html_escape(v)
                d[k] = self.com_string.to_json(v)
        return lst

    def list_toint(self, l, force=False):
        l = [int(w) if (isinstance(w, str) and not self.com_string.isnull(w)) else w for w in l]
        return l

    def list_escape(self, data):
        for index in range(len(data)):
            value = data[index]
            data[index] = self.dict_escape(value)
        return data

    def dict_escape(self, data):
        for key, value in data.items():
            data[key] = self.com_string.convert_to_string(value)
        return data

    def shuffle_list(self, arr):
        random.shuffle(arr)
        return arr

    def arr_diff(self, arr1, arr2):
        set1 = set(arr1)
        set2 = set(arr2)
        diff1 = set1 - set2
        # diff2 = set2 - set1
        return list(diff1)

    def is_intersect(self,list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        if set1 & set2:
            return True
        else:
            return False

    def get_intersect(self,list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        intersection = set1 & set2
        return list(intersection)

    # 差集运算
    def get_disjoint(self,list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        disjoint = set1 - set2
        return list(disjoint)

    def is_time_between(self,start_time_str, end_time_str):
        current_time = datetime.datetime.now().time()
        start_time = datetime.datetime.strptime(start_time_str, '%H').time()
        end_time = datetime.datetime.strptime(end_time_str, '%H').time()
        if start_time <= current_time <= end_time:
            return True
        else:
            return False

    def is_windows(self):
        sysstr = platform.system()
        windows = "windows"
        if (sysstr.lower() == windows):
            return True
        else:
            return False

    def is_linux(self):
        return not self.is_windows()
