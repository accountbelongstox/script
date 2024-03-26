from pycore._base import *
import os,re
import platform
import subprocess
class Plattools(Base):
    def __init__(self):
        pass

    def is_command(self, command):
        try:
            return os.system(f"which {command}") == 0 if os.name != 'nt' else os.system(f"where {command}") == 0
        except Exception as e:
            return False

    def is_windows(self):
        return os.name == 'nt' or sys.platform.startswith('win')

    def is_linux(self):
        return os.name == 'posix' and not sys.platform.startswith('win')

    def is_centos(self):
        try:
            result = subprocess.run(["cat", "/etc/centos-release"], capture_output=True, text=True)
            centos_version = result.stdout.split()[3].split('.')[0]
            return centos_version.isdigit() and int(centos_version) in {7, 8, 9}
        except Exception as e:
            return False

    def is_centos7(self):
        return self.is_centos() and self.get_centos_version() == 7

    def is_centos8(self):
        return self.is_centos() and self.get_centos_version() == 8

    def is_centos9(self):
        return self.is_centos() and self.get_centos_version() == 9

    def is_ubuntu(self):
        try:
            result = subprocess.run(["grep", "VERSION_ID", "/etc/os-release"], capture_output=True, text=True)
            ubuntu_version = result.stdout.split('=')[1].strip().strip('"')
            return ubuntu_version.isdigit() and int(ubuntu_version) in {18, 19, 20, 21, 22, 23}
        except Exception as e:
            return False

    def is_ubuntu18(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 18

    def is_ubuntu19(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 19

    def is_ubuntu20(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 20

    def is_ubuntu21(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 21

    def is_ubuntu22(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 22

    def is_ubuntu23(self):
        return self.is_ubuntu() and self.get_ubuntu_version() == 23

    def is_debian(self):
        try:
            result = subprocess.run(["grep", "VERSION_ID", "/etc/os-release"], capture_output=True, text=True)
            debian_version = result.stdout.split('=')[1].strip().strip('"')
            return debian_version.isdigit() and int(debian_version) in {9, 10, 11, 12}
        except Exception as e:
            return False

    def is_debian8(self):
        return self.is_debian() and self.get_debian_version() == 8

    def is_debian9(self):
        return self.is_debian() and self.get_debian_version() == 9

    def is_debian10(self):
        return self.is_debian() and self.get_debian_version() == 10

    def is_debian11(self):
        return self.is_debian() and self.get_debian_version() == 11

    def is_debian12(self):
        return self.is_debian() and self.get_debian_version() == 12

    def get_centos_version(self):
        result = subprocess.run(["cat", "/etc/centos-release"], capture_output=True, text=True)
        return int(result.stdout.split()[3].split('.')[0])

    def get_ubuntu_version(self):
        result = subprocess.run(["grep", "VERSION_ID", "/etc/os-release"], capture_output=True, text=True)
        return int(result.stdout.split('=')[1].strip().strip('"'))

    def get_debian_version(self):
        result = subprocess.run(["grep", "VERSION_ID", "/etc/os-release"], capture_output=True, text=True)
        return int(result.stdout.split('=')[1].strip().strip('"'))

    def get_linux_distribution(self):
        try:
            result = subprocess.run(['cat', '/etc/os-release'], capture_output=True, text=True)
            os_release_content = result.stdout

            version_id_line = next(line for line in os_release_content.split('\n') if 'VERSION_ID' in line)
            version_id = version_id_line.split('=')[1].strip('"')

            return version_id.lower()
        except Exception as e:
            print(f"Error reading /etc/os-release: {e}")
            return ''

    def is_wsl(self):
        uname_result = platform.uname()
        return "Microsoft" in uname_result.version or "WSL" in uname_result.version

    def install_command_by_system(self, install_command):
        if self.is_windows():
            print("Windows system detected. Installing with Chocolatey (choco) command.")
            self.install_on_windows(install_command)
        elif self.is_centos():
            print("CentOS system detected. Installing with CentOS command.")
            self.install_on_centos(install_command)
        elif self.is_ubuntu():
            print("Ubuntu system detected. Installing with Ubuntu command.")
            self.install_on_ubuntu(install_command)
        elif self.is_debian():
            print("Debian system detected. Installing with Debian command.")
            self.install_on_debian(install_command)
        else:
            print("Unsupported system.")

    def install_on_windows(self, install_command):
        # 在 Windows 上使用 Chocolatey 安装命令的方法
        try:
            subprocess.run(["choco", "install"] + install_command.split(), check=True)
            print("Installation successful with Chocolatey.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing on Windows with Chocolatey: {e}")

    def has_choco_installed(self):
        try:
            subprocess.run(["choco", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def install_choco(self):
        print("Installing Chocolatey...")
        try:
            subprocess.run(["powershell", "-Command", "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"], check=True)
            print("Chocolatey installation successful.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Chocolatey: {e}")
    def install_on_centos(self, install_command):
        try:
            subprocess.run(["sudo", "yum", "install", "-y"] + install_command.split(), check=True)
            print("Installation successful on CentOS.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing on CentOS: {e}")

    def install_on_ubuntu(self, install_command):
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y"] + install_command.split(), check=True)
            print("Installation successful on Ubuntu.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing on Ubuntu: {e}")

    def install_on_debian(self, install_command):
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y"] + install_command.split(), check=True)
            print("Installation successful on Debian.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing on Debian: {e}")

    def is_admin(self):
        if self.is_windows():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        return False

    def run_as_admin(self, cmd, params=""):
        if self.is_windows():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", cmd, params, None, 1)
        else:
            print("Administrator privileges are required.")

    def cmd(self, command, info=False):
        if isinstance(command,list):
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

    def exec_cmd(self, command, info=True):
        if isinstance(command,list):
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

    def reload_systemctl(self):
        system_name = platform.system()
        if system_name == "Linux":
            self.exec_cmd(["sudo", "systemctl", "daemon-reload"])
        else:
            print("Unsupported operating system")