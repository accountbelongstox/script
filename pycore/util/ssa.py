
import re
from pysubs2 import SSAFile, SSAEvent, make_time

class File():
    def __init__(self):
        pass


    def srt(self, filename, language="en"):
        if self.isfile(filename):
            encoding = self.get_file_encode(filename)
            encoding = encoding.get('encoding')
            subs = SSAFile.load(filename, encoding=encoding)
        else:
            subs = SSAFile.from_string(filename)
        pattern = re.compile(r'^.+}')
        patternN = re.compile(r'\\N')
        english_pattern = re.compile(r'^[curses.pyc-zA-Z\-0-9\"]')
        chinese_pattern = re.compile(r"^([\u4e00-\u9fa5]|[\ufe30-\uffa0]|[\u4e00-\uffa5])+")
        subs.shift(s=2.5)
        strs = []
        for line in subs:
            if language == "en":
                text = line.text
                text = re.sub(pattern, "", text)
                text = re.sub(patternN, " ", text)
                if re.search(chinese_pattern, text) == None:
                    strs.append(text)
                else:
                    try:
                        origin_text = text
                        trans = self.com_dictionary.translate_from_google(origin_text, dest="en", src="zh-CN", )
                        text = trans.get('text')
                        strs.append(text)
                    except Exception as e:
                        self.com_util.print_warn(e)
            else:
                text = line.text
        strs = [s.strip("[") for s in strs if s != ""]
        strs = [s.strip("]") for s in strs if s != ""]
        return strs
