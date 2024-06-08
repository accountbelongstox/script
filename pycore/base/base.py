import os
from pprint import pprint
# from pprint import PrettyPrinter
# import datetime
import sys
from pycore.base.log import Log
# from glob import glob
global_modes = {}
import hashlib
import platform
import uuid
import subprocess
import shutil
from pycore.globalvar.encyclopedia import encyclopedia


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

    def md5(self, value):
        hash = hashlib.md5()
        hash.update(value.encode())
        return hash.hexdigest()

    def md5id(self,srcvalue):
        msd5str = self.md5(srcvalue)
        return f"id_{msd5str}"

    def gen_id(self):
        return str(uuid.uuid4())

    def is_windows(self):
        return platform.system() == 'Windows'

    def is_linux(self):
        return platform.system() == 'Linux'

    def get_system_name(self):
        return platform.system()

    def mkdir(self, dirPath):
        os.makedirs(dirPath, exist_ok=True)


    def getcwd(self, file=None, suffix=""):
        if file == None:
            main_file_path = os.path.abspath(sys.argv[0])
            cwd = os.path.dirname(main_file_path)
        else:
            cwd = os.path.dirname(file)
        if suffix != "":
            cwd = os.path.join(cwd, suffix)
        return cwd

    def exec_cmd(self, command, info=True):
        if isinstance(command, list):
            command = " ".join(command)
        if info:
            self.info(f"exec_cmd: {command}")
        os.system(command)
        if platform.system() == "Linux":
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    executable="/bin/bash")
        else:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
        if result.returncode == 0:
            if info:
                self.info(self.byte_to_str(result.stdout))
                self.warn(self.byte_to_str(result.stderr))
            return self.byte_to_str(result.stdout)
        else:
            if info:
                self.warn(self.byte_to_str(result.stderr))
            return self.byte_to_str(result.stderr)

    def run_exe(self, command, info=True):
        command = "start " + command if self.is_windows() else command
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
            if info:
                self.info(f"Run-Exe-command : {command}")
                self.info(result.stdout)
                if result.stderr:
                    self.warn(result.stderr)
            return result.stdout + result.stderr

        except subprocess.CalledProcessError as e:
            print("Error run_exe:", command)
            print("Error run_exe:", e)
            return ""


    def exec_cmd(self, command, info=True):
        if isinstance(command, list):
            executable = command[0]
            command = " ".join(command)
        else:
            executable = command.split(' ')[0]

        if info:
            self.info(f"exec_cmd: {command}")

        if platform.system() == "Linux":
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    executable="/bin/bash")
        else:
            if os.path.isabs(executable):
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        executable=executable)
            else:
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        executable=shutil.which(executable))

        if result.returncode == 0:
            if info:
                self.info(self.byte_to_str(result.stdout))
                self.warn(self.byte_to_str(result.stderr))
            return self.byte_to_str(result.stdout)
        else:
            if info:
                self.warn(self.byte_to_str(result.stderr))
            return self.byte_to_str(result.stderr)

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
            cwd = __file__.split('pycore')[0]
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

    def pprint(self, data):
        blue_color = '\033[94m'
        self._print_formatted(blue_color, data)

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