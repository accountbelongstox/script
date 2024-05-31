
import hashlib
import os, re
import platform
import subprocess
import sys
import time
import uuid
import socket
from urllib.parse import urlparse
from pycore.globalvar.gdir import gdir

class AutoInstall():
    server_role = ""
    windows_package = ["pywin32", "pyautogui", "windows-curses"]

    def __init__(self):
        self.venv_dir = self.read_dynamic_dir()
        self.pip_source_name = self.get_env("PIP_SOURCE")
        self.server_role = self.get_server_role()

    def read_dynamic_dir(self):
        with open('/usr/local/venv_dir', 'r') as f:
            venv_dir = f.read().strip()
        return venv_dir

    def get_server_role(self):
        server_role = self.get_env("SERVER_ROLE")
        if server_role == "" or not server_role:
            if self.is_windows():
                server_role = "client"
            else:
                server_role = "linux"
        return server_role

    def install(self):
        self.install_package()

    def start(self):
        self.install_package()

    def get_pip_source(self):
        if self.pip_source_name == "tencent":
            return "http://mirrors.cloud.tencent.com/pypi/simple/"
        elif self.pip_source_name == "aliyun":
            return "https://mirrors.aliyun.com/pypi/simple/"
        elif self.pip_source_name == "netease":
            return "http://mirrors.163.com/pypi/simple/"
        else:
            return "https://pypi.org/simple/"

    def get_require_file(self):
        if self.server_role == "linux":
            file_name = '.requirements_linux.txt'
        else:
            file_name = '.requirements.txt'
        return file_name

    def get_installed_requirements(self):
        system_info = self.system_info()
        if self.server_role != "linux":
            self.success(system_info)
        installed_requirement = ".installed_requirements_" + self.md5(system_info)
        installed_requirement = installed_requirement.replace(":", "_")
        installed_requirement = os.path.join(self.venv_dir,installed_requirement)
        return installed_requirement

    def md5(self, input_string):
        md5_hash = hashlib.md5()
        md5_hash.update(input_string.encode('utf-8'))
        md5_result = md5_hash.hexdigest()
        return md5_result

    def system_info(self):
        result_string = ""
        result_string += f"Server Role : {self.server_role}\n"
        operating_system = platform.system()
        result_string += f"Operating System: {operating_system}\n"

        os_version = self.get_version()
        result_string += f"System Version: {os_version}\n"

        os_version = platform.version()
        result_string += f"Version: {os_version}\n"

        machine_architecture = platform.machine()
        result_string += f"Machine Architecture: {machine_architecture}\n"

        processor_info = platform.processor()
        result_string += f"Processor Information: {processor_info}\n"

        system_info = platform.uname()
        result_string += f"System Information: {system_info}\n"

        python_version = platform.python_version()
        result_string += f"Python Version: {python_version}\n"

        python_compiler = platform.python_compiler()
        result_string += f"Python Compiler: {python_compiler}\n"

        python_architecture, os_bits = platform.architecture()
        result_string += f"Python Architecture: {python_architecture}\n"
        result_string += f"Operating System Bits: {os_bits}\n"

        mac_address = self.get_mac_address()
        result_string += f"MAC Address: {mac_address}\n"

        cpu_cores = os.cpu_count()
        result_string += f"CPU Cores: {cpu_cores}\n"
        current_user = self.get_current_user()
        result_string += f"Current User: {current_user}\n"

        hostname = platform.node()
        result_string += f"Hostname: {hostname}\n"

        return result_string

    def get_current_user(self):
        current_user = ""
        try:
            current_user = os.getlogin()
        except Exception as e:
            pass
        return current_user

    def get_cpu_model(self):
        try:
            system_info = platform.uname()
            cpu_model = system_info.processor
            return cpu_model
        except Exception as e:
            return f"{e}"

    def get_version(self):
        system = platform.system()
        if system == 'Linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('VERSION_ID='):
                            return line.split('=')[1].strip().strip('"')
            except FileNotFoundError:
                return 'Linux'
        elif system == 'Windows':
            version = platform.version()
            return f"Windows {version}"
        else:
            return 'Windows'

    def is_windows(self):
        system = platform.system()
        if system == 'Windows':
            return True
        else:
            return False

    def mkdir(self, path):
        if os.path.exists(path):
            return True
        try:
            os.makedirs(path)
            return True
        except Exception as e:
            print(f"Failed to create path: {e}")
            return False

    def get_pip_source_url(self):
        settings_dir = os.path.join(self.venv_dir, "settings")
        os.makedirs(settings_dir, exist_ok=True)
        venv_setting_dir = os.path.join(self.venv_dir,"settings")
        vpython_trusted_host = os.path.join(venv_setting_dir, ".trusted_host")

        url = self.get_pip_source()
        pip_cmd = f"{sys.executable} -m pip config set global.index-url {url}"
        trust_url = urlparse(url).hostname
        trust_cmd = f"{sys.executable} -m pip config set global.trusted-host {trust_url}"
        url_set_val = f"-i {url} --trusted-host {trust_url}"
        if os.path.exists(vpython_trusted_host):
            return url_set_val
        self.cmd(trust_cmd, info=False)
        with open(vpython_trusted_host, 'w', encoding='utf-8') as b_file:
            b_file.write(trust_url)
        return url_set_val

    def is_package_installed(self, package_name):
        package_name = package_name.split('=')[0].strip()
        pip_cmd = f"{sys.executable} -m pip show {package_name}"
        result = self.cmd(pip_cmd, info=False)
        return result

    def install_package(self):
        python_exe = sys.executable
        if self.server_role != "linux":
            self.info("\ndetection. Must depend on the library.")
        require_file = self.get_requirefile()
        if not self.file_exist(require_file):
            return
        installed_requirements = self.join_file(self.get_installed_requirements(),"logs")
        a_lines = self.read_fileline(require_file)
        if os.path.isfile(installed_requirements):
            b_lines = self.read_fileline(installed_requirements)
            extra_lines = [line for line in a_lines if line not in b_lines]
        else:
            extra_lines = [line for line in a_lines]
        source_url = self.get_pip_source_url()
        if len(extra_lines) > 0:
            self.success(f"using {require_file}")
            if self.server_role != "linux":
                self.success(f"Current linux:{self.server_role}, using {require_file}")
            upgrade_pip_cmd = f"{python_exe} -m pip install --upgrade pip"
            self.cmd(upgrade_pip_cmd)
            success = 0
            fail = 0
            install_commands = []
            for package in extra_lines:
                if not self.is_windows() and package in self.windows_package:
                    # if not self.is_windows():
                    #     self.info(f"Skipping Windows-specific package on Linux: {package}")
                    continue
                # is_installed = self.is_package_installed(package)
                target_dir = f"{self.venv_dir}/lib/python3.9/site-packages"
                install_cmd = f"{python_exe} -m pip install {package} {source_url}"
                #install_cmd = f"{python_exe} -m pip install {package} {source_url}"
                # if not is_installed:
                #     install_commands.append(install_cmd)
                self.success("package", package)
                result = self.cmd(install_cmd)
                if result == True:
                    success += 1
                    with open(installed_requirements, 'a', encoding='utf-8') as b_file:
                        b_file.write(package + "\n")
                    fail_message = ""
                else:
                    fail += 1
                    fail_message = f",fail:{fail}"
                    self.warn(f"fail: {package}")

                if fail > 0:
                    self.warn(f"fail: {package}")

                self.success(f"install {success}/{len(extra_lines)}{fail_message}")
                print()

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac_address = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        return mac_address

    def check_install(self):
        requirefile = self.get_requirefile()
        installed_requirements = self.join_file(self.get_installed_requirements())
        a_lines = self.read_fileline(requirefile)
        if os.path.isfile(installed_requirements):
            b_lines = self.read_fileline(installed_requirements)
            extra_lines = [line for line in a_lines if line not in b_lines]
        else:
            extra_lines = [line for line in a_lines]
        if len(extra_lines) > 0:
            return False
        else:
            return True

    def getcwd(self):
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


    def join_file(self, file,dir=None):
        up_up_dir = self.getcwd()
        if dir != None:
            up_up_dir = os.path.join(up_up_dir, dir)
            self.mkdir(up_up_dir)
        file_path = os.path.join(up_up_dir, file)
        return file_path

    def get_requirefile(self):
        require_file = self.join_file(self.get_require_file())
        return require_file

    def cmd(self, command, info=True):
        if isinstance(command, list):
            command = " ".join(command)
        if info:
            self.info(command)
        if platform.system() == "Linux":
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    executable="/bin/bash")
        else:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
        if result.returncode == 0:
            if info:
                self.info(self.byte_to_str(result.stdout))
            return True
        else:
            if info:
                self.warn(self.byte_to_str(result.stderr))
            return False

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

    def get_venvdir(self):
        cwd = self.getcwd()
        return os.path.join(cwd, self.venv_dir)

    def read_file(self, file_name, encoding="utf-8"):
        file_object = self.get_file_encode(file_name, encoding=encoding)
        content = None
        if file_object != None:
            content = file_object.get("content")
        return content

    def read_fileline(self, file_name, encoding="utf-8"):
        text = self.read_file(file_name, encoding)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines

    def file_exist(self, filename):
        return os.path.exists(filename)

    def get_file_encode(self, file_name, encoding=None):
        codings = [
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
        if encoding != None:
            codings = [encoding] + codings
        index = 0
        while index < len(codings):
            encoding = codings[index]
            try:
                f = open(file_name, f"r+", encoding=encoding)
                content = f.read()
                f.close()
                result = {
                    "encoding": encoding,
                    "content": content
                }
                return result
            except Exception as e:
                index += 1
        print(f"open error, all encode not decode the file {file_name}")
        return None

    def error(self, *args, show=True):
        if show:
            red_color_code = '\033[91m'
            reset_color_code = '\033[0m'
            message = " ".join(map(str, args))
            decoded_message = self.decode_if_bytes(message)
            print(f"{red_color_code}{decoded_message}{reset_color_code}")

    def success(self, *args, show=True):
        if show:
            green_color_code = '\033[92m'
            reset_color_code = '\033[0m'
            message = " ".join(map(str, args))
            decoded_message = self.decode_if_bytes(message)
            print(f"{green_color_code}{decoded_message}{reset_color_code}")

    def info(self, *args, show=True):
        if show:
            blue_color_code = '\033[94m'
            reset_color_code = '\033[0m'
            message = " ".join(map(str, args))
            decoded_message = self.decode_if_bytes(message)
            print(f"{blue_color_code}{decoded_message}{reset_color_code}")

    def warn(self, *args, show=True):
        if show:
            yellow_color_code = '\033[93m'
            reset_color_code = '\033[0m'
            message = " ".join(map(str, args))
            decoded_message = self.decode_if_bytes(message)
            print(f"{yellow_color_code}{decoded_message}{reset_color_code}")

    def decode_if_bytes(self, message):
        if isinstance(message, bytes):
            try:
                return message.decode('utf-8')
            except UnicodeDecodeError:
                return repr(message)
        return message

    def get_env_file(self):
        return os.path.join(self.getcwd(), ".env")

    def get_env_example_file(self):
        return os.path.join(self.getcwd(), ".env_example")

    def get_env_example_file_alias(self):
        return os.path.join(self.getcwd(), ".env-example")

    def ini_env(self):
        file_path = self.get_env_file()
        env_example_file = self.get_env_example_file()
        if not os.path.exists(file_path):
            if os.path.exists(env_example_file):
                example_envs = self.read_env(env_example_file)
                self.save_env(example_envs)
            else:
                env_example_file = self.get_env_example_file_alias()
                if os.path.exists(env_example_file):
                    example_envs = self.read_env(env_example_file)
                    self.save_env(example_envs)

    def read_env(self, env_file=None):
        file_path = env_file or self.get_env_file()
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
        self.ini_env()
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
        self.ini_env()
        val = self.get_env(key=key, )
        if val == "":
            return False
        return True

    def get_env(self, key):
        self.ini_env()
        env_arr = self.read_env()
        for subarr in env_arr:
            if subarr[0] == key:
                return subarr[1]
        return ""


auto_install = AutoInstall()
