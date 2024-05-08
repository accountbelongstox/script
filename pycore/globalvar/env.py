import os
from pycore.base.base import Base
from pycore.globalvar.gdir import gdir
import sys
import tempfile
import re

class Env(Base):
    main_env_file = None
    local_env_file = None
    root_dir = ""
    annotation_symbol = "#"
    example_env_file = ""
    command_line_args = sys.argv[1:]
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

    def __init__(self, root_dir=None, env_name=".env", delimiter="="):
        if root_dir == None:
            root_dir = self.get_root_dir()
        else:
            root_dir = self.resolve_path(root_dir)
        self.set_root_dir(root_dir, env_name, delimiter=delimiter)

    def get_root_dir(self):
        main_file_path = os.path.abspath(sys.argv[0])
        root_path = os.path.dirname(main_file_path)
        return root_path

    def resolve_path(self, path, relative_path=None, resolve=True):
        if resolve == False:
            return path
        if not os.path.isabs(path):
            if os.path.exists(path):
                return os.path.abspath(path)
            root_path = self.get_root_dir()
            if relative_path != None:
                root_path = os.path.join(root_path, relative_path)
            path = os.path.join(root_path, path)
        return path
    def set_delimiter(self, delimiter="="):
        self.delimiter = delimiter

    def example_to(self, example_path):
        env_file = example_path.replace("-example", "")
        env_file = env_file.replace("_example", "")
        env_file = env_file.replace(".example", "")
        self.merge_env(env_file, example_path)

    def is_file(self, path):
        if not isinstance(path, str):
            return False
        return self.isfile(path)

    def isfile(self, path):
        if type(path) is not str:
            return False
        path = self.resolve_path(path)
        if os.path.exists(path) and os.path.isfile(path):
            return True
        else:
            return False

    def is_absolute_path(self, file_path):
        return os.path.isabs(file_path)

    def mkdir(self, dir):
        if os.path.exists(dir) and os.path.isdir(dir):
            return False
        else:
            try:
                os.makedirs(dir, exist_ok=True)
            except Exception as e:
                self.warn(e)
            return True

    def mkbasedir(self, dir):
        dir = os.path.dirname(dir)
        return self.mkdir(dir)

    def save(self, file_name=None, content=None, encoding="utf-8", overwrite=False):
        if file_name is None:
            file_name = self.create_file_name()
        if content is None:
            return None
        if isinstance(content, list):
            content = "\n".join(content)
        if not self.is_absolute_path(file_name) and not self.is_file(file_name):
            tmp_dir = tempfile.gettempdir()
            file_name = os.path.join(tmp_dir, file_name)
        self.mkbasedir(file_name)
        if overwrite:
            mode = "wb"
        else:
            mode = "ab"
        try:
            with open(file_name, mode) as f:
                if encoding == "binary":
                    if isinstance(content, bytes):
                        f.write(content)
                    else:
                        f.write(content.encode('utf-8'))
                else:
                    f.write(content.encode(encoding))
        except Exception as e:
            self.warn(f"save: {e}")
            return None
        return file_name

    def save_key_to_tmp(self, key, val):
        tmp_dir = gdir.getTempDir()
        filename = gdir.getTempDir(key)


    def set_root_dir(self, root_dir, env_name=".env", delimiter="="):
        self.set_delimiter(delimiter)
        self.root_dir = root_dir
        self.local_env_file = os.path.join(self.root_dir, env_name)
        example_env_file = os.path.join(self.root_dir, env_name + '_example')
        if not self.is_file(example_env_file):
            example_env_file = os.path.join(self.root_dir, env_name + '-example')
        if not self.is_file(example_env_file):
            example_env_file = os.path.join(self.root_dir, env_name + '.example')
        self.example_env_file = example_env_file
        self.get_local_env_file()

    def load(self, root_dir, env_name=".env", delimiter="="):
        return Env(root_dir=root_dir, env_name=env_name, delimiter=delimiter)

    def get_local_env_file(self):
        if not self.is_file(self.local_env_file):
            self.save(self.local_env_file, "")
        self.merge_env(self.local_env_file, self.example_env_file)
        return self.local_env_file

    def get_env_file(self):
        return self.local_env_file

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

    def merge_env(self, env_file, example_env_file):
        if self.is_file(example_env_file) == False:
            return
        example_arr = self.read_env(example_env_file)
        local_arr = self.read_env(env_file)
        added_keys = []
        example_dict = self.arr_to_dict(example_arr)
        local_dict = self.arr_to_dict(local_arr)
        for key, value in example_dict.items():
            if key not in local_dict:
                local_dict[key] = value
                added_keys.append(key)
        if len(added_keys) > 0:
            self.success(f"Env-Update env: {env_file}")
            local_arr = self.dict_to_arr(local_dict)
            self.save_env(local_arr, env_file)
        for added_key in added_keys:
            self.success(f"Env-Added key: {added_key}")

    def read_key(self, key):
        with open(self.main_env_file, 'r') as file:
            for line in file:
                k, v = line.partition(self.delimiter)[::2]
                if k.strip() == key:
                    return v.strip()
        return None

    def replace_or_add_key(self, key, val):
        updated = False
        lines = []
        with open(self.main_env_file, 'r') as file:
            for line in file:
                k, v = line.partition(self.delimiter)[::2]
                if k.strip() == key:
                    line = f"{key}{self.delimiter}{val}\n"
                    updated = True
                lines.append(line)

        if not updated:
            lines.append(f"{key}{self.delimiter}{val}\n")
        content = "\n".join(lines)
        self.save(self.main_env_file, content, overwrite=True)

    def read(self, file_name, encoding="utf-8", info=False, readLine=False):
        file_name = self.resolve_path(file_name)
        if not self.isfile(file_name):
            self.warn(f"File '{file_name}' does not exist.")
            return None
        file_object = self.try_file_encode(file_name, encoding=encoding, info=info, readLines=readLine)
        if file_object == None:
            self.warn(f"Unable to read file '{file_name}' with {encoding} encoding.")
        return file_object

    def try_file_encode(self, file_name, encoding=None, info=False, readLines=False):
        if encoding != None:
            codings = [encoding] + self.file_codings
        else:
            codings = self.file_codings
        index = 0
        while index < len(codings):
            encoding = codings[index]
            try:
                f = open(file_name, f"r+", encoding=encoding)
                if readLines == False:
                    content = f.read()
                else:
                    content = f.readlines()
                if info == True:
                    self.success(f"Successfully mode {encoding} to {file_name}")
                f.close()
                result = {
                    "encoding": encoding,
                    "content": content,
                }
                return result
            except Exception as e:
                self.error(e, file_name)
                index += 1
        return None

    def read_lines(self, file_name, encoding="utf-8", info=False):
        file_object = self.read(file_name, encoding=encoding, info=info, readLine=True)
        lines = None
        if file_object != None:
            lines = file_object.get("content")
        return lines

    def read_env(self, file_path=None):
        if file_path is None:
            file_path = self.local_env_file
        result = []
        lines = self.read_lines(file_path)
        for line in lines:
            line_values = [value.strip() for value in line.split(self.delimiter)]
            result.append(line_values)
        return result

    def get_envs(self, file_path=None):
        return self.read_env(file_path=file_path)

    def save_env(self, env_arr, file_path=None):
        if file_path == None:
            file_path = self.local_env_file
        filtered_env_arr = [subarr for subarr in env_arr if len(subarr) == 2]
        formatted_lines = [f'{subarr[0]}{self.delimiter}{subarr[1]}' for subarr in filtered_env_arr]
        result_string = '\n'.join(formatted_lines)
        self.save(file_path, result_string, overwrite=True)

    def set_env(self, key, value, file_path=None):
        if file_path is None:
            file_path = self.local_env_file
        env_arr = self.read_env(file_path=file_path)
        key_exists = False
        for subarr in env_arr:
            if subarr[0] == key:
                subarr[1] = value
                key_exists = True
                break
        if not key_exists:
            env_arr.append([key, value])
        self.save_env(env_arr, file_path)

    def get_arg(self, name):
        if isinstance(name, int):
            name = name + 1
            if len(sys.argv) > name:
                return sys.argv[name]
            else:
                return None
        for i, arg in enumerate(self.command_line_args):
            if re.match(r"^[\-]*" + re.escape(name) + r"($|=|-|:)", arg):
                if f"{name}:" in arg:
                    return arg.split(":")[1]
                elif arg == f"--{name}" or arg == f"-{name}" or re.match(r"^-{0,1}\*{1}" + re.escape(name), arg):
                    if i + 1 < len(self.command_line_args):
                        return self.command_line_args[i + 1]
                    else:
                        return None
                elif arg == name:
                    if i + 1 < len(self.command_line_args) and not self.command_line_args[i + 1].startswith("-"):
                        return self.command_line_args[i + 1]
                    else:
                        return ""
        return None

    def is_arg(self, name):
        return self.get_arg(name) != None


    def is_env(self, key, file_path=None):
        is_arg = self.is_arg("is_env")
        val = self.get_env(key=key, file_path=file_path)
        if val == "":
            if is_arg == True:
                print("False")
            return False
        if is_arg == True:
            print("True")
        return True

    def get_env(self, key, file_path=None):
        # is_arg = self.is_arg("get_env")
        if file_path is None:
            file_path = self.local_env_file
        env_arr = self.read_env(file_path=file_path)
        for subarr in env_arr:
            if subarr[0] == key:
                return subarr[1]
        return ""

    def get_args(self):
        return self.command_line_args
