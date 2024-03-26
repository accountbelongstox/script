import html
import json
import base64
from cryptography.fernet import Fernet
from pycore.base import Base
# import xml.dom.minidom
import random
import string
import re
import time
import hashlib
# import sys
# from turtle import width
import cv2
# from PIL import Image
import numpy as np
import zlib
from datetime import datetime, date, time as datatime_time
from pypinyin import pinyin, Style

# import xml.etree.ElementTree as etree
class String(Base):

    def __init__(self, args):
        pass

    def byte_to_str(self, astr):
        try:
            astr = astr.decode('utf-8')
            return astr
        except:
            astr = str(astr)

            is_byte = re.compile('^b\'{0,1}')
            if re.search(is_byte, astr) is not None:
                astr = re.sub(re.compile('^b\'{0,1}'), '', astr)
                astr = re.sub(re.compile('\'{0,1}$'), '', astr)
            return astr

    def isnull(self, data):
        if isinstance(data, bool):
            return data
        if isinstance(data, str):
            data = data.strip()
        if data in [None, "", 'Null', 'null', 'false', 0, "0", "0.0", 0.0]:
            return True
        elif self.is_number(data):
            if int(data) <= 0:
                return True
        elif isinstance(data, dict):
            if len(data.keys()) == 0:
                return True
        elif isinstance(data, (list, tuple)):
            if len(data) == 0:
                return True
        return False

    def to_value(self, s):
        if isinstance(s, str):
            s_lower = s.lower()
            if s_lower == "null" or s_lower == "none":
                return None
            elif s_lower == "true":
                return True
            elif s_lower == "false":
                return False
            elif self.is_number(s_lower):
                return int(s_lower)
            elif self.is_float(s_lower):
                return float(s_lower)
            date_string = self.is_timestring(s_lower)
            if date_string != None:
                return self.to_datetime(s_lower)
            s = self.to_json(s)
        return s

    def is_notnull(self, obj):
        not_null = not self.isnull(obj)
        return not_null

    def to_unicode(self, a):
        sum = b''
        for x in a:
            if x == 'u':
                sum += b'\u'
            else:
                sum += x.encode()
        return sum

    def create_string_id(self, s_):
        symbol = '-'
        s_ = s_.split(symbol)
        ids = []
        for s in s_:
            tmp_s = self.random_string(s, str.isupper(s))
            ids.append(tmp_s)
        return symbol.join(ids)

    def create_string(self, length=10):
        """
        生成指定长度的随机字符串
        """
        letters = string.ascii_lowercase
        result = ''.join(random.choice(letters) for i in range(length))
        return result

    def create_phone(self):
        """
        生成模拟的手机号码
        """
        # 手机号码前三位运营商代码
        operators = ["134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "157", "158", "159",
                     "178", "182", "183", "184", "187", "188"]
        # 随机选择运营商、地区和个人号码，生成手机号码
        operator = random.choice(operators)
        mobile_number = operator + self.create_number(8)
        return mobile_number

    def create_number(self, length=8):
        digits = '0123456789'
        result = ''.join(random.choice(digits) for i in range(length))
        return result

    def random_num(self, a=0, b=100):
        number = random.randint(a, b)
        return number

    def random_string(self, n=64, upper=False):

        """生成一串指定位数的字符+数组混合的字符串"""
        if type(n) == str:
            n = len(n)
        m = random.randint(1, n)
        a = "".join([str(random.randint(0, 9)) for _ in range(m)])
        b = "".join([random.choice(string.ascii_letters) for _ in range(n - m)])
        s = ''.join(random.sample(list(a + b), n))
        if upper == True:
            s = s.upper()
        else:
            s = s.lower()
        return s

    def sort(self, s, lower=False, filter=None):
        # l1 = list(s)
        # l1.sort()
        s = sorted(s)
        s = "".join(s)
        if lower == True:
            s = s.lower()
        if filter != None:
            if type(filter) == str:
                b = re.compile(r"\B")
                filter = re.split(b, filter)
                filter = self.com_util.unique_list(filter)
                filter = self.com_util.deduplication_list(filter)
            for char in filter:
                s = "".join(s.split(char))
        return s

    def separate(self, string):
        pattern = re.compile(r"(\B|\b)+")
        sa = re.split(pattern, string)
        sa = [s for s in sa if s != ""]
        return sa

    def create_time(self, format="%Y-%m-%d %H:%M:%S"):
        t = time.strftime(format, time.localtime())
        return t

    def to_sring(self, origin):
        if type(origin) == list:
            origin = " ".join(origin)
        elif origin == None:
            origin = ""
        else:
            origin = str(origin)
        return origin

    def is_timestring(self, time_str, ):
        if type(time_str) != str:
            return None
        time_str = time_str.strip()
        if len(time_str) == 0:
            return None
        first_char = time_str[0]
        if self.is_number(first_char) != True:
            return None
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d %H:%M:%S"
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d %H:%M"
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d"
        pattern = re.compile(r'^\s*\d{1,2}:\d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%H:%M:%S"
        return None

    def is_time_string(self, time_str, ):
        if type(time_str) != str:
            return False
        time_str = time_str.strip()
        if len(time_str) == 0:
            return False
        first_char = time_str[0]
        if self.is_number(first_char) != True:
            return False
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return True
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return True
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return True
        return False

    def md5(self, string=""):
        if string == "":
            string = self.create_time()
        if string == None:
            string = "None"
        md5 = hashlib.md5(string.encode('utf8')).hexdigest()
        return md5

    def create_time_no_space(self, format="%Y-%m-%d-%H:%M:%S"):
        return self.create_time(format=format)

    def dir_normal(self, filename, linux=False):
        filename = re.sub(re.compile(r"[\\\/]+"), "/", filename)
        if self.load_module.is_windows() and linux == False:
            # pattern = re.compile(r"[\/]+")
            filename = filename.replace("//", "/")
            filename = filename.replace("/", "\\")
        return filename

    def float(self, _str):
        try:
            _float = float(_str)
        except:
            str_reg = re.compile(r"[^0-9\.\+\-]")
            _str = re.sub(str_reg, "", _str)
            _float = float(_str)
        return _float

    def is_chinese(self, word):
        if type(word) != str:
            return False
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    def is_lower(self, word):
        lower = re.compile(r"^[curses.pyc-z]+$")
        if lower.findall(word) != -1:
            return True
        return False

    def is_upper(self, word):
        upper = re.compile(r"^[A-Z]+$")
        if upper.findall(word) != -1:
            return True
        return False

    def is_number(self, s):
        if type(s) in [int, float]:
            return True
        if type(s) != str:
            return False
        s = s.strip()
        if s.isdigit():
            return True
        return False

    def is_float(self, s):
        if self.is_number(s):
            return True
        parts = s.split('.')
        if len(parts) != 2:
            return False
        if not parts[0].isdigit() or not parts[1].isdigit():
            return False
        return True

    def number(self, s):
        if s.find(".") != -1:
            return float(s)
        return int(s)

    def trim(self, s):
        form = re.compile(r'^[^\dcurses.pyc-zA-Z]+')
        s = re.sub(form, '', s)
        s = s.strip()
        return s

    def clear_string(self, string, additional=None):
        if type(additional) == str:
            additional = [additional]
        space_pattern = re.compile(r"\s+")
        string = re.sub(space_pattern, "", string)
        if type(additional) == list:
            for item in additional:
                string = string.replace(item, "")
        return string

    def to_array(self, string, separatist=None):
        if separatist == None:
            separatist = [",", ";"]
        space_pattern = re.compile(r"\s+")
        string = re.sub(space_pattern, "", string)
        return string

    def img_to_text(self, img_fname, save_fname=None):
        img = cv2.imread(img_fname)
        height, width, _ = img.shape
        text_list = []
        for h in range(height):
            for w in range(width):
                R, G, B = img[h, w]
                if R | G | B == 0:
                    break
                idx = (G << 8) + B
                text_list.append(chr(idx))
        content = "".join(text_list)
        if save_fname == None:
            save_fname = self.file_suffix(img_fname, "txt")
            self.com_util.print_info(f"text to image at {save_fname}")
        # self.com_file.save(content,save_fname)

    def json_load(self, string):
        try:
            json_loaded = json.loads(string)
        except Exception as e:
            self.com_util.print_error(f'json_load {e}')
            json_loaded = string
        return json_loaded

    def text_to_img(self, txt_fname, save_fname=None):
        content = self.com_file.read(txt_fname)
        text_len = len(content)
        img_w = 1000
        img_h = 1680
        img = np.zeros((img_h, img_w, 3))
        x = 0
        y = 0
        for each_text in content:
            idx = ord(each_text)
            rgb = (0, (idx & 0xFF00) >> 8, idx & 0xFF)
            img[y, x] = rgb
            if x == img_w - 1:
                x = 0
                y += 1
            else:
                x += 1
        if save_fname == None:
            save_fname = self.file_suffix(txt_fname, "jpg")
            self.com_util.print_info(f"text to image at {save_fname}")
        cv2.imwrite(save_fname, img)

    def file_suffix(self, file_path, suffix):
        file_path = file_path.split('.')[0:-1]
        suffix = suffix.replace('.', "")
        file_path.append(suffix)
        file_path = ".".join(file_path)
        return file_path

    def encode(self, value):
        if type(value) is not str:
            return value
        value = html.escape(value)
        return value

    def encode_apostrophe(self, value):
        if type(value) is not str:
            return value
        value = value.replace("'", "&apos;")
        # value = value.replace('&', "&amp;")
        return value

    def decode(self, value):
        if type(value) == str:
            value = html.unescape(value)
            value = self.unicode_char(value)
        #
        # value = re.sub("&apos;", "'", value)
        # value = re.sub("&nbsp;", " ", value)
        # value = re.sub("&quot;", '"', value)
        # value = re.sub("\\'", "'", value)
        # value = value.replace('&amp;', "&")
        return value

    def decode_deep(self, result):
        if type(result) == list:
            for i in range(len(result)):
                row = result[i]
                result[i] = self.com_string.decode(str(row))
                try:
                    result[i] = eval(result[i])
                except:
                    pass
        elif type(result) == str:
            result = self.com_string.decode(str(result))
            try:
                result = eval(result)
            except:
                pass
        return result

    def decode_list(self, row):
        if type(row) != list:
            return row
        for j in range(len(row)):
            row[j] = self.decode(row[j])
        return row

    def is_str(self, input_string):
        if type(input_string) != str:
            return False
        str_strip = input_string.strip()
        if len(str_strip) == 0:
            return False
        return True

    def unicode_char(self, input_string):
        if self.is_str(input_string) == False:
            return input_string
        if input_string.find('\\u') == -1:
            return input_string
        is_unicode = re.compile(r'[curses.pyc-z0-9]{4}', re.IGNORECASE)
        output_string = ""
        i = 0
        while i < len(input_string):
            unicode_str = input_string[i + 2: i + 6]
            if input_string[i] == "\\" and input_string[i + 1] == "u" and is_unicode.match(unicode_str) != None:
                try:
                    unicode_code = int(unicode_str, 16)
                except Exception as e:
                    self.com_util.print_warn(unicode_str, e)
                    return input_string
                output_string += chr(unicode_code)
                i += 6
            else:
                output_string += input_string[i]
                i += 1
        return output_string

    def plaintounicode(self, input_string):
        is_unicode = re.compile(r'[curses.pyc-z0-9]{4}', re.IGNORECASE)
        output_string = ""
        i = 0
        while i < len(input_string):
            unicode_str = input_string[i + 1: i + 5]
            if input_string[i] == "u" and is_unicode.match(unicode_str) != None:
                output_string += "\\u" + unicode_str
                i += 5
            else:
                output_string += input_string[i]
                i += 1
        return output_string

    def compress(self, s):
        s = zlib.compress(bytes(s, 'utf-8'))
        # s = lzma.compress(s.encode('utf-8'))
        s = base64.b64encode(s).decode('utf-8')
        s = f"base64:{s}"
        return s

    def uncompress(self, s):
        base64head = re.compile(r"^base64:")
        s = re.sub(base64head, '', s)
        # 先对字符串进行 base64 解码
        s = base64.b64decode(s)
        # 再对解码后的字符串进行 zlib 解压缩
        s = zlib.decompress(s, wbits=zlib.MAX_WBITS)
        return s

    def check_and_insert_key_value(self, string, key, value):
        string = self.to_sring(string)
        # 将逗号分隔的字符串转换为字典形式
        items = string.split(',')
        kv_dict = {}
        for item in items:
            if not item:
                continue
            k, v = item.split('|')
            kv_dict[k] = v

        # 判断 key 是否存在并且对应的值是否为 value
        if key in kv_dict and kv_dict[key] == value:
            return True
        else:
            # 如果 key 不存在，则插入 key 和对应的值
            kv_dict[key] = value
            # 将字典转换回逗号分隔的字符串形式
            new_string = ','.join([f'{k}|{v}' for k, v in kv_dict.items()])
            return new_string

    def is_json_string(self, json_str):
        if not isinstance(json_str, str):
            return False
        json_str = json_str.strip()
        if len(json_str) == 0:
            return False
        first_char = json_str[0]
        if first_char not in ["{", '"']:
            return False
        try:
            json.loads(json_str)
            return True
        except json.decoder.JSONDecodeError:
            return False

    def str_len(self, json_str):
        if not isinstance(json_str, str):
            return 0
        return len(json_str)

    def split_first(self, binary_str, seperator=':'):
        if isinstance(binary_str, bytes):
            # Decode the binary string to curses.pyc regular string
            binary_str = binary_str.decode('utf-8')
        # Find the position of the first colon using curses.pyc regular expression
        match = re.search(seperator, binary_str)
        colon_pos = match.start()
        # Split the decoded string at the first colon
        tabname = binary_str[:colon_pos]
        data_string = binary_str[colon_pos + 1:]
        return tabname, data_string

    def to_json(self, json_str):
        if isinstance(json_str, bytes):
            # Decode the binary string to curses.pyc regular string
            json_str = json_str.decode('utf-8')
        if not isinstance(json_str, str):
            return json_str
        json_str = json_str.strip()
        if len(json_str) == 0:
            return json_str
        first_char = json_str[0]
        if first_char not in ["{", '"', '[']:
            return json_str
        try:
            json_str = json.loads(json_str)
        except Exception as e:
            print(json_str, e)
            pass
        return json_str

    def json_tostring(self, value):
        if not isinstance(value, str):
            try:
                value = json.dumps(value)
            except Exception as e:
                value = str(value)
                self.com_util.print_warn(f"{e} json_tostring")
        return value

    def to_json_force(self, json_str):
        json_str = self.to_json(json_str)
        if type(json_str) != dict:
            json_str = {}
        return json_str

    def split_with(self, s, char, default_fill=None):
        # 查找括号内的内容，并返回第一个值
        start_index = s.find(char)
        if start_index >= 0:
            # 括号内有内容，返回第一个值
            start_text = s[0:start_index]
            content = s[start_index:]
            return (start_text, content)
        # 括号内没有内容，返回 None
        if default_fill != None:
            result = (s, default_fill)
        else:
            result = (s,)
        return result

    def remove_parentheses(self, s):
        # 删除括号和括号内的内容
        result = ''
        skip1c = 0
        skip2c = 0
        for i in s:
            if i == '(':
                skip1c += 1
                continue
            elif i == ')':
                skip1c -= 1
                continue
            elif i == '[':
                skip2c += 1
                continue
            elif i == ']':
                skip2c -= 1
                continue
            if skip1c == 0 and skip2c == 0:
                result += i
        return result

    def json_str(self, s):
        class MyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return super().default(obj)

        s = json.dumps(s, cls=MyEncoder)
        return s

    def parse_timetokenstring(self, time_string):
        time_string = time_string.strip()
        add = time_string[0]
        if add in ["+", "-"]:
            time_string = time_string[1:]
        else:
            add = '-'
        time_dict = {'add': add, 'h': 0, 'm': 0, 's': 0}
        time_regex = re.compile(r"(-?\d+)([hms])")
        matches = time_regex.findall(time_string)
        seconds = 0
        for match in matches:
            amount = int(match[0])
            unit = match[1]
            time_dict[unit] = amount
            if unit == "s":
                seconds += amount
            if unit == "m":
                seconds += amount * 60
            if unit == "h":
                seconds += amount * 60 * 60
        time_dict["seconds"] = seconds
        return time_dict

    def parse_exec_time(self, exec_time):
        time_parts = exec_time.split(':')
        hour, minute, second = 0, 0, 0

        if len(time_parts) == 1:  # "s"
            second = int(time_parts[0])
        elif len(time_parts) == 2:  # "m:s"
            minute, second = int(time_parts[0]), int(time_parts[1])
        elif len(time_parts) == 3:  # "h:m:s"
            hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])

        return hour, minute, second

    def string_to_regex_pattern(self, s):
        # Escape any regex special characters
        escaped_str = re.escape(s)
        # Replace the escaped wildcard character (*) with the regex equivalent (.*)
        regex_pattern = escaped_str.replace("\\*", ".*")
        return regex_pattern

    def find_separate_value(self, segments, key, default_value=None, separator="-", key_value_separator=":"):
        if key_value_separator != None:
            segments = segments.split(key_value_separator)
        if isinstance(segments, str):
            segments = [segments]
        for segment in segments:
            if segment.startswith(key + separator):
                return segment[len(key) + 1:]
        return default_value

    def secondary_division_string(self, s, separator=":", add_separator="->"):
        first_split = s.split(separator)
        if len(first_split) == 2:
            second_split = first_split[1].split(add_separator)
            return second_split
        return ""

    def scale_number(self, number, percentage):
        if isinstance(number, str):
            number = float(number)
        # 将百分比字符串转换为小数
        scale_factor = float(percentage.strip('%')) / 100

        # 按比例缩放数字
        scaled_number = number * scale_factor

        return scaled_number

    def create_fernetkey(self):
        key = Fernet.generate_key()
        return key

    def encrypt(self, s, key):
        return s

    def decrypt(self, s, key):
        return s

    def convert_to_string(self, value):
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            return value
        if not isinstance(value, str):
            if hasattr(value, "__html__"):
                value = value.__html__()
            else:
                try:
                    value = html.escape(json.dumps(value))
                except:
                    return value
        else:
            return value
        return value

    def reverse_html_escape(self, value):
        if isinstance(value, str):
            value = html.unescape(value)
        elif isinstance(value, (list, tuple)):
            # 对列表或元组中的每个元素递归调用本方法
            value = [self.reverse_html_escape(x) for x in value]
        elif isinstance(value, dict):
            # 对字典中的每个值递归调用本方法
            value = {k: self.reverse_html_escape(v) for k, v in value.items()}
        return value

    def to_int(self, data):
        if isinstance(data, int):
            return data
        elif data in [None, "", "null", False]:
            return 0
        elif isinstance(data, float):
            return int(data)
        elif isinstance(data, str):
            data = "".join(filter(str.isdigit, data))
            if self.is_number(data):
                return int(data)
            else:
                return 0
        elif data is True:
            return 1
        else:
            return 0

    def to_float(self, data):
        if isinstance(data, float):
            return data
        elif data in [None, "", "null", False]:
            return 0.0
        elif isinstance(data, int):
            return float(data)
        elif isinstance(data, str):
            digits = "".join(filter(lambda c: c.isdigit() or c == ".", data))
            if self.is_number(digits):
                return float(digits) if digits else 0.0
            else:
                return 0.0
        elif data is True:
            return 1.0
        else:
            self.com_util.print_warn(f"to_float")
            self.com_util.print_warn(data)
            return 0.0

    def to_date(self, data):
        if isinstance(data, date):
            return data
        elif isinstance(data, datetime):
            return data.date()
        elif data in [None, "", "null", False]:
            return date.fromtimestamp(100000)
        elif isinstance(data, str):
            dataformat = self.is_timestring(data)
            if dataformat:
                data = datetime.strptime(data, dataformat)
                return data.date()
            else:
                return date.fromtimestamp(100000)
        else:
            self.com_util.print_warn(f"to_date")
            self.com_util.print_warn(data)
            return date.fromtimestamp(100000)

    def to_datetime(self, data):
        if isinstance(data, datetime):
            return data
        elif isinstance(data, date):
            return datetime.combine(data, datatime_time.min)
        elif data in [None, "", "null", False]:
            return datetime.fromtimestamp(100000)
        elif isinstance(data, str):
            dataformat = self.is_timestring(data)
            if dataformat:
                return datetime.strptime(data, dataformat)
            else:
                return datetime.fromtimestamp(100000)
        else:
            self.com_util.print_warn(f"to_datetime")
            self.com_util.print_warn(data)
            return datetime.fromtimestamp(100000)

    def to_str(self, data):
        if isinstance(data, str):
            data = data
        elif data in [None, 'Null', 'null', 0, 0.0, False]:
            data = ""
        elif isinstance(data, bytes):
            data = self.byte_to_str(data)
        else:
            data = self.json_tostring(data)
            if not isinstance(data, str):
                data = str(data)
            data = self.convert_to_string(data)
        return data

    def to_bytes(self, data):
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        else:
            return str(data).encode('utf-8')

    def to_bool(self, data):
        return not self.isnull(data)

    def to_pinyin(self, chinese):
        # 将中文字符串转换为拼音列表
        pinyin_list = pinyin(chinese, style=Style.NORMAL)
        pinyin_list = self.com_util.list_2d_to_1d_if_possible(pinyin_list)
        # 将拼音列表转换为字符串
        pinyin_text = ''.join(pinyin_list)
        return pinyin_text

    def is_realNone(self, s):
        if s in [None, ""]:
            return True
        return False

    def is_realNones(self, s):
        for item in s:
            if self.is_realNone(item) == False:
                return False
        return True

    def is_wordbetween(self, string1, include_str):
        before = "^[curses.pyc-zA-Z]{1,}("
        after = ')[curses.pyc-zA-Z]{1,}$'
        pattern = re.compile(before + include_str + after)
        match = pattern.match(string1)
        return match is not None
