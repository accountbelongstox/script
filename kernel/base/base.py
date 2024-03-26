import os
from pprint import pprint
# from pprint import PrettyPrinter
# import datetime
import sys
from pycore._base.log import Log
# from glob import glob
global_modes = {}

class Base(Log):

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __set__(self, instance, value):
        self.__dict__[instance] = value

    def __get__(self, item):
        return self.__dict__.get(item)

    def __getattr__(self, key):
        global global_modes
        if key in global_modes:
            return global_modes[key]
        elif '_' in key:
            mode, method_name = key.split('_', 1)
            if mode in global_modes and method_name in global_modes[mode]:
                return global_modes[mode][method_name]
        return self.__dict__.get(key)

    def set_modules(self, mode, value, module=None):
        global global_modes
        if not global_modes.get(mode):
            global_modes[mode] = {}
        if module == None:
            key = value.__class__.__name__.lower()
        else:
            key = value
            value = module
        global_modes[mode][key] = value

    def get_modules(self, name):
        global global_modes
        if name in global_modes:
            return global_modes[name]
        else:
            return {}

    def set_module(self, mode, value):
        global global_modes
        global_modes[mode] = value

    def get_module(self, mode, methd_name=None):
        global global_modes
        if methd_name != None:
            return global_modes[mode][methd_name]
        else:
            return global_modes[mode]

    def set_com(self, value):
        self.set_modules('com', value)

    def set_db(self, value):
        self.set_modules('db', value)

    def set_mode(self, value):
        self.set_modules('mode', value)

    def set_thread(self, value):
        self.set_modules('thread', value)

    def get_com(self, key):
        return self.get_module('com', key)

    def get_db(self, key):
        return self.get_module('db', key)

    def get_mode(self, key):
        return self.get_module('mode', key)

    def get_thread(self, key):
        return self.get_module('thread', key)

    def get_coms(self):
        return self.get_modules('com')

    def get_modes(self):
        return self.get_modules('mode')

    def get_dbs(self):
        return self.get_modules('db')

    def get_threads(self):
        return self.get_modules('thread')

    def getcwd(self, file=None, suffix=""):
        if file == None:
            main_file_path = os.path.abspath(sys.argv[0])
            cwd = os.path.dirname(main_file_path)
        else:
            cwd = os.path.dirname(file)
        if suffix != "":
            cwd = os.path.join(cwd, suffix)
        return cwd

    def get_env_file(self):
        return os.path.join(self.getcwd(), ".env")

    def read_env(self):
        file_path = self.get_env_file()
        lines = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        result = []
        for line in lines:
            line_values = [value.strip() for value in line.split('=')]
            result.append(line_values)
        return result

    def save_env(self, env_arr):
        filtered_env_arr = [subarr for subarr in env_arr if len(subarr) == 2]
        formatted_lines = [f'{subarr[0]}={subarr[1]}' for subarr in filtered_env_arr]
        result_string = '\n'.join(formatted_lines)
        env_file_path = self.get_env_file()
        try:
            with open(env_file_path, 'w', encoding='utf-8') as file:
                file.write(result_string)
        except Exception as e:
            print(f"Base-Class: Error saving environment variables: {str(e)}")

    def set_env(self, key, value):
        env_arr = self.read_env()
        key_exists = False
        for subarr in env_arr:
            if subarr[0] == key:
                subarr[1] = value
                key_exists = True
                break
        if not key_exists:
            env_arr.append([key, value])
        self.save_env(env_arr)

    def is_env(self, key):
        val = self.get_env(key=key, )
        if val == "":
            return False
        return True

    def getcwd(self,file=None,suffix=""):
        if file == None:
            cwd = __file__.split('kernel')[0]
        else:
            cwd = os.path.dirname(file)
        cwd = os.path.join(cwd,suffix)
        return cwd

    def get_cwd(self,file=None,suffix=""):
        return self.getcwd(file=file,suffix=suffix)


    def easy_log(self, log_text, log_type="info", max_total_size_mb=500, log_filename=None, max_file=5, cwd=None):
        if not cwd:
            cwd = self.get_cwd()
        self.write_log(log_text, log_type, max_total_size_mb, log_filename, max_file, cwd)

    def get_env(self, key):
        env_arr = self.read_env()
        for subarr in env_arr:
            if subarr[0] == key:
                return subarr[1]
        return ""

    def warn(self, *args, show=True):
        yellow_color = '\033[93m'
        no_print_value = self.get_env("NO_PRINT")
        if no_print_value and no_print_value.lower() == "true":
            show = False
        for msg in args:
            if show:
                self._print_formatted(yellow_color, msg)
            else:
                self.easy_log(msg, "warn")

    def error(self, *args, show=True):
        red_color = '\033[91m'
        no_print_value = self.get_env("NO_PRINT")
        if no_print_value and no_print_value.lower() == "true":
            show = False
        for msg in args:
            self._print_formatted(red_color, msg)
            self.easy_log(msg, "error")

    def success(self, *args, show=True):
        green_color = '\033[92m'
        no_print_value = self.get_env("NO_PRINT")
        if no_print_value and no_print_value.lower() == "true":
            show = False
        for msg in args:
            if show:
                self._print_formatted(green_color, msg)
            else:
                self.easy_log(msg, "success")

    def info(self, *args, show=True):
        blue_color = '\033[94m'
        no_print_value = self.get_env("NO_PRINT")
        if no_print_value and no_print_value.lower() == "true":
            show = False
        for msg in args:
            if show:
                self._print_formatted(blue_color, msg)
            else:
                self.easy_log(msg, "info")

    def _print_formatted(self, color_code, msg):
        end_color = '\033[0m'
        if isinstance(msg, (list, dict, tuple)):
            pprint(msg)
        else:
            print(f"{color_code}{msg}{end_color}")

    def info_log(self, *args):
        blue_color = '\033[94m'
        show = self.should_print()
        for msg in args:
            if show:
                self._print_formatted(blue_color, msg)
            else:
                self.easy_log(msg, "info")

    def success_log(self, *args):
        green_color = '\033[92m'
        show = self.should_print()
        for msg in args:
            if show:
                self._print_formatted(green_color, msg)
            else:
                self.easy_log(msg, "success")

    def warn_log(self, *args):
        yellow_color = '\033[93m'
        show = self.should_print()
        for msg in args:
            if show:
                self._print_formatted(yellow_color, msg)
            else:
                self.easy_log(msg, "warn")

    def error_log(self, *args):
        red_color = '\033[91m'
        show = self.should_print()
        for msg in args:
            self._print_formatted(red_color, msg)
            self.easy_log(msg, "error")

    def should_print(self):
        no_print_value = self.get_env("NO_PRINT")
        return not (no_print_value and no_print_value.lower() == "true")