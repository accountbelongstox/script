import copy
import random
import re
from queue import Queue
import html
import json

class Arr():

    def __init__(self):
        pass

    # 将一个结果添加到dict，如果没有key则创建
    def add_to_dict(self, result, key, value):
        if key not in result:
            result[key] = []
        if value not in result[key]:
            result[key].append(value)
        return result[key]

    # 将数组中的二维数组提取出来
    def extract_list(self, result):
        while len(result) == 1 and type(result[0]) is list:
            result = result[0]
        is_two_dimensional_list = None
        for item in result:
            if type(item) is list:
                is_two_dimensional_list = True
            else:
                is_two_dimensional_list = False
                break
        if is_two_dimensional_list:
            extract_list = []
            for item in result:
                extract_list.append(item[0])
            result = extract_list
        return result

    # 通过一个字符串分割数组
    def split_list(self, result, split_symbol=[None, False, True], start=0):
        if type(split_symbol) is not list:
            split_symbol = [split_symbol]
        split_list = []
        index = 0
        step = 0
        for i in range(len(result)):
            item = result[i]
            if item in split_symbol:
                if i == 0:
                    split_list.append([])
                elif i - index > 1:
                    step += 1
                    split_list.append([])
                index = i
            else:
                if i == 0:
                    split_list.append([])
                if type(item) is not list:
                    split_list[step].append(item)
                else:
                    item = self.extract_list(item)
                    for strip in item:
                        split_list[step].append(strip)
        return split_list

    def list_2d_to_1d_if_possible(self, arr):
        if not isinstance(arr, list):
            return arr
        if all(isinstance(item, list) for item in arr):
            if all(len(item) == 1 for item in arr):
                return [item[0] for item in arr]
            else:
                return arr
        else:
            return arr

    def get_single_list(self, arr):
        if not isinstance(arr, list):
            return arr
        if len(arr) == 1:
            return arr[0]
        else:
            return arr

    def unique_list(self, list_arr):
        list_arr = list(set(list_arr))
        list_arr = [w for w in list_arr if w != ""]
        return list_arr

    def get_list_value(self, list_arr, arr_len, default=None):
        if not list_arr:
            return default
        if len(list_arr) >= arr_len + 1:
            return list_arr[arr_len]
        else:
            return default

    def set_listdefaultvalue(self, lst, index, default=None):
        if index >= len(lst):
            lst += [None] * (index - len(lst) + 1)
        lst[index] = default
        return lst

    def get_dict_value(self, dict_object, key, default=None):
        if not dict_object:
            return default
        if key in dict_object:
            return dict_object[key]
        else:
            return default

    def array_to_queue(self, array, unique=True):
        queue = Queue()
        if unique == True:
            tmp_array = []
            for item in array:
                if item not in tmp_array:
                    tmp_array.append(item)
            array = tmp_array
        for item in array:
            queue.put(item)
        return queue

    def clear_value(self, arr, values=None):
        default_clear = [" ", ""]
        if type(arr) != list:
            return arr
        if values == None:
            values = default_clear
        if type(values) == str:
            values = [values]
        for item in default_clear:
            if item not in values:
                values.append(item)
        index = 0
        while index < len(arr):
            if arr[index] in values or str(arr[index]).strip() in values:
                del arr[index]
                index = index - 1
            index += 1
        return arr

    def clear_empty(self,arr):
        return [value for value in arr if not isinstance(value, str) or not value.isspace()]

    def deduplication_list(self, origlist):
        duplicate = list(set(origlist))
        return duplicate

    def filter_value(self, arr, value):
        new_arr = []
        for item in arr:
            if isinstance(item, str):
                item = item.strip()
            if item != value:
                new_arr.append(item)
        return new_arr

    def arr_diff(self, arr1, arr2):
        set1 = set(arr1)
        set2 = set(arr2)
        diff1 = set1 - set2
        # diff2 = set2 - set1
        return list(diff1)


    def to_english_array(self, s):
        if type(s) == list:
            s = " ".join(s)
        s = s.strip()
        pattern = re.compile(r'[^curses.pyc-zA-Z]+')
        s = re.split(pattern, s)
        return s

    def text_to_lines(self, text):
        lines = []
        if text:
            lines = text.split('\n')
        return lines

    def remove_spaces(self, text_arr):
        processed_arr = [line.strip() for line in text_arr]
        return processed_arr

    def remove_empty_lines(self, input_array):
        new_import_array = []
        for line in input_array:
            if not line.strip() or re.match(r'^[\t\s\r\n]*$', line):
                continue
            else:
                new_import_array.append(line)
        return new_import_array

    def take_a_value_that_does_not_contain(self, index_array, length):
        inverted_array = []
        for i in range(0, len(index_array), 2):
            start_index = index_array[i]
            end_index = min(index_array[i + 1] + 1, length)
            inverted_array.extend(range(start_index, end_index))
        inverted_array = list(set(range(length)) - set(inverted_array))
        inverted_array.sort()
        return inverted_array

    def copy(self, arr):
        return copy.copy(arr)

    def fill(self, arr, start=None, end=None, fill_value=None):
        if start is None:
            start = 0
        if end is None:
            end = len(arr)
        for i in range(start, end):
            arr[i] = fill_value
        return arr

    def generateRandomRectangle(self, x, y, w, h, safe=True):
        if safe == True:
            x, y, w, h = self.scaledDownRectangle(x, y, w, h, wMax=30, hMax=30, scale=10)
        print(x, y, w, h)
        random_x = random.randint(x, x + w)
        random_y = random.randint(y, y + h)
        return random_x, random_y

    def offsetRectangle(self, x, y, w, h, wOffset=10, hOffset=0):
        x = x + wOffset
        y = y + hOffset
        w = w - wOffset
        h = h - hOffset
        return x, y, w, h

    def scaledDownRectangle(self, x, y, w, h, wMax=30, hMax=30, scale=10):
        if w > wMax:
            scaled_width = (scale / 100) * w
            new_width = w - (2 * scaled_width)
            w = new_width if new_width > 0 else wMax
            x = x + scaled_width
        if h > hMax:
            scaled_height = (scale / 100) * h
            new_height = h - (2 * scaled_height)
            h = new_height if new_height > 0 else hMax
            y = y + scaled_height
        return int(x), int(y), int(w), int(h)

    def generateRandomRectangleSafe(self, x, y, w, h):
        x, y, w, h = self.scaledDownRectangle(x, y, w, h)
        return self.generateRandomRectangle(x, y, w, h)

    def calculateRectangleCenter(self, x, y=None, w=None, h=None):
        if y == None:
            y = x[1]
            w = x[2]
            h = x[3]
            x = x[0]
        center_x = x + w / 2
        center_y = y + h / 2
        return center_x, center_y

    def to_2d_list(self, arr):
        if isinstance(arr, list):
            if all(isinstance(item, list) for item in arr):
                return arr
            else:
                return [arr]
        else:
            return arr

    def arr_to_dict(self, array):
        result = {}
        for item in array:
            if isinstance(item, list) and len(item) > 1:
                key, val = item[0], item[1]
                result[key] = val
        return result

    def dict_to_arr(self, dictionary):
        result = []
        for key, value in dictionary.items():
            result.append([key, value])
        return result

    def list_tojson(self, lst):
        for d in lst:
            for k, v in d.items():
                v = self.reverse_html_escape(v)
                d[k] = self.to_json(v)
        return lst

    def dict_escape(self, data):
        for key, value in data.items():
            data[key] = self.convert_to_string(value)
        return data

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
