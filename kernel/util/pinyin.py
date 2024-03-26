
from pypinyin import pinyin, Style

# import xml.etree.ElementTree as etree
class Str():

    def __init__(self, args):
        pass

    def to_pinyin(self, chinese):
        pinyin_list = pinyin(chinese, style=Style.NORMAL)
        pinyin_list = self.list_2d_to_1d_if_possible(pinyin_list)
        pinyin_text = ''.join(pinyin_list)
        return pinyin_text

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
