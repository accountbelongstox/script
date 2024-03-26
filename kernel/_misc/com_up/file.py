from kernel.base.base import *
import os
import zipfile
import shutil
import time
import base64
import time
# google 文字识别引擎
import pytesseract
from PIL import Image
import re
# from paddleocr import PaddleOCR, draw_ocr
# from urllib.parse import urlparse
import filetype
from pysubs2 import SSAFile, SSAEvent, make_time
# import pysubs2
import tempfile
import chardet
import datetime


class File(Base):
    file_codings = [
        "utf-8",
        "utf-16",
        "utf-16le",
        "utf-16BE",
        "gbk",
        "gb2312",
        "us-ascii",
        "ascii",
        "IBM037",
        "IBM437",
        "IBM500",
        "ASMO-708",
        "DOS-720",
        "ibm737",
        "ibm775",
        "ibm850",
        "ibm852",
        "IBM855",
        "ibm857",
        "IBM00858",
        "IBM860",
        "ibm861",
        "DOS-862",
        "IBM863",
        "IBM864",
        "IBM865",
        "cp866",
        "ibm869",
        "IBM870",
        "windows-874",
        "cp875",
        "shift_jis",
        "ks_c_5601-1987",
        "big5",
        "IBM1026",
        "IBM01047",
        "IBM01140",
        "IBM01141",
        "IBM01142",
        "IBM01143",
        "IBM01144",
        "IBM01145",
        "IBM01146",
        "IBM01147",
        "IBM01148",
        "IBM01149",
        "windows-1250",
        "windows-1251",
        "Windows-1252",
        "windows-1253",
        "windows-1254",
        "windows-1255",
        "windows-1256",
        "windows-1257",
        "windows-1258",
        "Johab",
        "macintosh",
        "x-mac-japanese",
        "x-mac-chinesetrad",
        "x-mac-korean",
        "x-mac-arabic",
        "x-mac-hebrew",
        "x-mac-greek",
        "x-mac-cyrillic",
        "x-mac-chinesesimp",
        "x-mac-romanian",
        "x-mac-ukrainian",
        "x-mac-thai",
        "x-mac-ce",
        "x-mac-icelandic",
        "x-mac-turkish",
        "x-mac-croatian",
        "utf-32",
        "utf-32BE",
        "x-Chinese-CNS",
        "x-cp20001",
        "x-Chinese-Eten",
        "x-cp20003",
        "x-cp20004",
        "x-cp20005",
        "x-IA5",
        "x-IA5-German",
        "x-IA5-Swedish",
        "x-IA5-Norwegian",
        "x-cp20261",
        "x-cp20269",
        "IBM273",
        "IBM277",
        "IBM278",
        "IBM280",
        "IBM284",
        "IBM285",
        "IBM290",
        "IBM297",
        "IBM420",
        "IBM423",
        "IBM424",
        "x-EBCDIC-KoreanExtended",
        "IBM-Thai",
        "koi8-r",
        "IBM871",
        "IBM880",
        "IBM905",
        "IBM00924",
        "EUC-JP",
        "x-cp20936",
        "x-cp20949",
        "cp1025",
        "koi8-u",
        "iso-8859-1",
        "iso-8859-2",
        "iso-8859-3",
        "iso-8859-4",
        "iso-8859-5",
        "iso-8859-6",
        "iso-8859-7",
        "iso-8859-8",
        "iso-8859-9",
        "iso-8859-13",
        "iso-8859-15",
        "x-Europa",
        "iso-8859-8-i",
        "iso-2022-jp",
        "csISO2022JP",
        "iso-2022-jp",
        "iso-2022-kr",
        "x-cp50227",
        "euc-jp",
        "EUC-CN",
        "euc-kr",
        "hz-gb-2312",
        "GB18030",
        "x-iscii-de",
        "x-iscii-be",
        "x-iscii-ta",
        "x-iscii-te",
        "x-iscii-as",
        "x-iscii-or",
        "x-iscii-ka",
        "x-iscii-ma",
        "x-iscii-gu",
        "x-iscii-pa",
        "utf-7",
    ]
    def __init__(self, args):
        pass

    def b64encode(self, data_file):
        if self.isfile(data_file):
            extent_file = os.path.splitext(data_file)[1]
            extent_file = extent_file.replace(".", "")
            suffix = "data:image/{};base64,".format(extent_file)
            data = self.open(data_file, 'b')
        else:
            suffix = ""
            data = data_file
        data = base64.b64encode(data)
        data = self.com_string.byte_to_str(data)
        data = suffix + data
        return data

    def image_to_str(self, image_url, lang):
        im = Image.open(image_url)
        im = im.convert('L')
        im_str = pytesseract.image_to_string(im, lang=lang)
        return im_str

    def image_to_str_from_paddleorc(self, img_path, lang="chi_sim"):  # lang='chi_sim'# lang eng
        # unbuntu
        # sudo apt-get install tesseract-ocr
        # export PATH=$PATH:/usr/local/bin/tesseract
        image_path = os.path.join(os.getcwd(), img_path)
        text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
        return text

    def rename_remove_space(self, filename):
        space_pattern = re.compile(r"\s+")
        file_space = re.findall(space_pattern, filename)
        if (len(file_space) > 0):
            new_file_name = os.path.basename(filename)
            new_file_name = re.sub(space_pattern, "", new_file_name)
            file_basedir = os.path.dirname(filename)
            new_file = os.path.join(file_basedir, new_file_name)
            self.cut(filename, new_file)
            filename = new_file
        return filename

    def read_file(self, file_name, encoding="utf-8", info=False):
        return self.load_file(file_name, encoding, info=info)

    def read_lines(self, file_path, encoding="utf-8", ):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = self.remove_empty_lines(lines)
            if len(lines) == 0:
                return None
            else:
                return lines

    def load_file(self, file_name, encoding="utf-8", info=False):
        file_name = self.get_path(file_name)
        if not self.isfile(file_name):
            return ""
        file_object = self.try_file_encode(file_name, encoding=encoding, info=info)
        content = None
        if file_object != None:
            content = file_object.get("content")
        return content

    def try_file_encode(self, file_name, encoding=None, info=False):
        if encoding != None:
            codings = [encoding] + self.file_codings
        else:
            codings = self.file_codings
        index = 0
        while index < len(codings):
            encoding = codings[index]
            try:
                f = open(file_name, f"r+", encoding=encoding)
                content = f.read()
                lines = f.readlines()
                if info == True:
                    print(f"Successfully mode {encoding} to {file_name}")
                f.close()
                result = {
                    "encoding": encoding,
                    "content": content,
                    "lines": lines,
                }
                return result
            except Exception as e:
                print(f"file open error, {file_name}")
                print(e)
                index += 1
        return None

    def check_encode(self, file):
        with open(file, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']
            return encoding

    def open(self, file_name, encoding="utf-8"):
        content = self.load_file(file_name, encoding=encoding)
        return content

    def read(self, file_name, encoding="utf-8"):
        content = self.load_file(file_name, encoding=encoding)
        return content

    def load_js(self, file_name, encoding="utf-8"):
        template_dir = self.com_config.get_js_dir()
        file_path = os.path.join(template_dir, file_name)
        content = self.load_file(file_path, encoding)
        return content

    def load_html(self, file_name, encoding="utf-8"):
        template_dir = self.com_config.get_template_dir()
        file_path = os.path.join(template_dir, file_name)
        content = self.load_file(file_path, encoding)
        return content

    def get_default_save_dir(self):
        save_dir = self.com_config.get_public("save_dir")
        return save_dir

    def save(self, file_name=None, content=None, encoding=None, overwrite=False):
        return self.save_file(file_name, content, encoding=encoding, overwrite=overwrite)

    def create_file_name(self, prefix='', suffix=""):
        filename = self.com_string.random_string(16)
        save_time = self.save_time()
        if prefix != '':
            prefix = f"{prefix}_"
        filename = f"{prefix}{save_time}_{filename}{suffix}"
        filedir = self.com_config.get_public("save_dir")
        filesavedir = os.path.join(filedir, filename)
        return filesavedir

    def save_time(self, ):
        t = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        return t

    def save_file(self, file_name=None, content=None, encoding=None, overwrite=False):
        if file_name == None:
            return None
        if content == None:
            content = file_name
            file_name = self.create_file_name()
        basename = os.path.dirname(file_name)
        if basename == "":
            basename = self.get_default_save_dir()
            file_name = os.path.join(basename, file_name)
        if os.path.exists(basename) is not True and os.path.isdir(basename) is not True:
            self.mkdir(basename)
        if not self.isfile(file_name):
            overwrite = True

        if encoding == None and type(content) == str:
            encoding = "utf-8"
        if overwrite == True:
            m = "w"
        else:
            m = "curses.pyc"

        print(f"save file ({encoding}) to \"{file_name}\"")
        if encoding == None or encoding == "binary":
            f = open(file_name, f"{m}b+")
            content = content.encode(encoding)
        else:
            f = open(file_name, f"{m}+", encoding=encoding)
        try:
            # print(f"savefile_encoding {encoding}")
            f.write(content)
        except:
            f.close()
            content = self.com_string.byte_to_str(content)
            f = open(file_name, f"{m}+", encoding="utf-8")
            f.write(content)
        f.close()
        return file_name

    def read_file_bytes(self, file_name):
        file_name = self.get_path(file_name)
        if self.isfile(file_name):
            with open(file_name, "rb") as f:
                data = f.read()
            return data
        else:
            return None

    def zip_extract(self, file, member, o=None):
        if o == None:
            o = os.path.dirname(file)
        with zipfile(file) as f:
            f.extract(member, o)

    def zip_extractall(self, file, odir=None, member=None):
        if odir == None:
            odir = os.path.dirname(file)
        with zipfile.ZipFile(file) as f:
            f.extractall(odir, member)
        return odir

    def file_extract(self, filename):
        """
        #输助函数,将最后下载的文件解压和删除。
        :param filename:
        :return:
        """
        extract_dir = os.path.dirname(filename)
        return self.zip_extractall(filename, extract_dir)

    def remove(self, top_path):
        print("delete : ", top_path)
        for root, dirs, files in os.walk(top_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.isdir(top_path):
            os.rmdir(top_path)
        elif os.path.isfile(top_path):
            os.remove(top_path)

    def mkdir(self, dir):
        if os.path.exists(dir):
            return False
        else:
            os.makedirs(dir, exist_ok=True)
            return True

    def isFile(self, path):
        return self.isfile(path)

    def is_file(self, path):
        if not isinstance(path,str):
            return False
        return self.isfile(path)

    def isfile(self, path):
        if type(path) is not str:
            return False
        path = self.get_path(path)
        if os.path.exists(path) and os.path.isfile(path) and os.path.getsize(path) > 0:
            return True
        else:
            return False

    def get_path(self, path):
        if os.path.exists(path) and os.path.isfile(path):
            return path
        public_dir = self.com_config.get_public(path)
        if os.path.exists(public_dir) and os.path.isfile(public_dir):
            return public_dir
        path = os.path.join(self.getcwd(), path)
        if os.path.exists(path) and os.path.isfile(path):
            return path
        else:
            return path

    def is_dir(self, path):
        return self.isdir(path)

    def isdir(self, path):
        if type(path) is not str:
            return False
        if os.path.exists(path) and os.path.isdir(path):
            return True
        else:
            return False

    def copy(self, src, dst):
        return shutil.copyfile(src, dst)

    def cut(self, src, dst):
        if self.is_file(src) and self.is_file(dst):
            # print(f"file cut error: file exists {dst}")
            os.remove(src)
            # os.remove(dst)
            return
        if self.is_file(src):
            dst_basedir = os.path.dirname(dst)
            self.mkdir(dst_basedir)
            shutil.copyfile(src, dst)
            os.remove(src)
        else:
            print(f"file cut error(src no exists):\n src:{src}\n dst:{dst}")

    def wait_cut(self, src, dst, wait=0):
        if wait > 30:
            print(f"down file {src} fail, file cut.")
        else:
            wait += 1
            if not self.is_file(src):
                time.sleep(1)
                return self.wait_cut(src, dst, wait)
            else:
                print(f"down cut success: {src}")
                dst_basedir = os.path.dirname(dst)
                self.mkdir(dst_basedir)
                shutil.copyfile(src, dst)
                os.remove(src)

    def rmtree(self, dir):
        shutil.rmtree(dir)

    def dir_to_localurl(self, filename):
        control_name = self.load_module.get_control_name()
        filename = filename.split(control_name)[-1]
        filename = self.dir_normal(filename, linux=True)
        filename = filename.lstrip('/')
        return filename

    def dir_normal(self, filename, linux=False):
        filename = re.sub(re.compile(r"[\\\/]+"), "/", filename)
        if self.load_module.is_windows() and linux == False:
            # pattern = re.compile(r"[\/]+")
            filename = filename.replace("//", "/")
            filename = filename.replace("/", "\\")
        else:
            filename = filename.replace("//", "/")
        return filename

    def file_type(self, filename):
        if self.isfile(filename) == False:
            return ""
        kind = filetype.guess(filename)
        if kind is not None:
            if kind.extension != None:
                return kind.extension
        return None

    def file_to(self, filename, encoding="utf-8"):
        file_object = self.try_file_encode(filename)
        if file_object == None:
            return False
        file_encode = file_object.get('encoding')
        if file_encode != encoding:
            content = self.read_file(filename)
            # content = content.encode(encoding)
            os.remove(filename)
            self.save(filename, content, encoding=encoding)
        return True

    def dir_to(self, filedir, encoding="utf-8"):
        files = os.listdir(filedir)
        for file in files:
            file = os.path.join(filedir, file)
            self.file_to(file, encoding)

    def srt(self, filename, language="en"):
        if self.isfile(filename):
            encoding = self.try_file_encode(filename)
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
                        print(e)
            else:
                text = line.text
        strs = [s.strip("[") for s in strs if s != ""]
        strs = [s.strip("]") for s in strs if s != ""]
        return strs

    def file_suffix(self, file_path, suffix):
        file_path = file_path.split('.')[0:-1]
        suffix = suffix.replace('.', "")
        file_path.append(suffix)
        file_path = ".".join(file_path)
        return file_path

    def get_suffix(self, file_path):
        file_type = os.path.splitext(file_path)[-1]
        suffix = file_type.replace('.', "")
        return suffix

    def get_template_dir(self, filename=None, fulllink=False, absolute=True):
        control_dir = self.load_module.get_control_dir()
        if filename == None:
            filename = ""
        elif filename and fulllink == True:
            top_symbol = re.compile(r'^\/')
            filename = re.sub(top_symbol, '', filename)
        template_folder = self.com_config.get_global("flask_template_folder")
        template_folder = os.path.join(control_dir, template_folder)
        template_folder = self.dir_normal(template_folder)
        filename = os.path.join(template_folder, filename)
        filename = self.dir_normal(filename)
        if absolute == False:
            filename = filename.replace(template_folder, "")
        return filename

    def get_static_dir(self, filename=None, fulllink=False, absolute=True):
        control_dir = self.load_module.get_control_dir()
        if filename == None:
            filename = ""
        elif filename and fulllink == True:
            top_symbol = re.compile(r'^\/')
            filename = re.sub(top_symbol, '', filename)
        template_folder = self.com_config.get_global("flask_static_folder")
        template_folder = os.path.join(control_dir, template_folder)
        template_folder = self.dir_normal(template_folder)
        filename = os.path.join(template_folder, filename)
        filename = self.dir_normal(filename)
        if absolute == False:
            filename = filename.replace(template_folder, "")
        return filename

    def ext(self, file, ext=None):
        file_ext = os.path.splitext(file)[1]
        if ext != None:
            return ext == file_ext
        else:
            return file_ext

    def change_ext(self, file, ext=None):
        if ext == None:
            return file
        else:
            if ext.startswith(".") == False:
                ext = "." + ext
            filedir = str(os.path.splitext(file)[0])
            file = filedir + ext
            return file

    def copy_totmp(self, src_path):
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        shutil.copy(src_path, temp_file.name)
        return temp_file

    def delete_tmp(self, temp_file):
        file_path = temp_file.name
        temp_file.close()
        os.remove(file_path)

    def remove_old_subdirs(self, dir_path, pre_fix="", out_time=None, not_include=None, include=None):
        # 获取当前时间
        now = datetime.datetime.now()
        # 遍历该目录下的所有子目录
        for subdir in os.listdir(dir_path):
            # 判断是否为目录，是否以"downfile_"开头，以及创建时间是否超过1分钟
            subdir_fullname = os.path.join(dir_path, subdir)
            if pre_fix != None:
                if subdir.startswith(pre_fix) == False:
                    continue
            if out_time != None:
                create_time = os.path.getctime(subdir_fullname)
                create_time = datetime.datetime.fromtimestamp(create_time).seconds
                diff_time = now - create_time
                if diff_time < out_time:
                    continue
            if not_include != None:
                not_include = str(not_include)
                if subdir.find(not_include) != -1:
                    continue
            if include != None:
                include = str(include)
                if subdir.find(include) == -1:
                    continue
            try:
                shutil.rmtree(subdir_fullname)
            except Exception as e:
                print(f"remove_old_subdirs {e}")

    def search_file(self, start_path, target_file_name):
        for dirpath, dirnames, filenames in os.walk(start_path):
            for filename in filenames:
                if filename == target_file_name:
                    return os.path.join(dirpath, filename)
        return None

    def is_absolute_path(self, file_path):
        return os.path.isabs(file_path)

    def merge_paths(self, base_path, sub_path):
        return os.path.relpath(sub_path, base_path)

    def dir_include(self, dir, prefix):
        file_names = os.listdir(dir)
        # 判断每个文件名是否以指定字符前缀开头
        for file_name in file_names:
            if file_name.startswith(prefix):
                return True
        return False

    def dir_find(self, dir, prefix):
        file_names = os.listdir(dir)
        # 判断每个文件名是否以指定字符前缀开头
        for file_name in file_names:
            if file_name.startswith(prefix):
                return file_name
        return None
    def sanitize_filename(self,filename):
        filename = self.com_string.decode(filename)
        pattern = r'[^curses.pyc-zA-Z0-9_\.]+'
        replaced_string = re.sub(pattern, '_', filename)
        return replaced_string

    def get_ext(self,filename):
        _, ext = os.path.splitext(filename)
        return ext if ext else ''

    def url_tofile(self,url):
        file_name = url.split('/')[-1]
        sanitize_filename = self.sanitize_filename(file_name)
        return sanitize_filename