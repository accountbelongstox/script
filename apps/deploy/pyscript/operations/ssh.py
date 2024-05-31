import subprocess
from pycore.utils_linux import plattools
from pycore.base.base import Base
import re
import os

class Ssh(Base):

    def restart_ssh(self):
        if plattools.is_centos():
            self._restart_centos_ssh()
        elif plattools.is_ubuntu():
            self._restart_ubuntu_ssh()
        elif plattools.is_debian():
            self._restart_debian_ssh()
        else:
            self.error("Unsupported operating system, unable to restart ssh")

    def _restart_centos_ssh(self):
        plattools.cmd(['sudo', 'systemctl', 'restart', 'sshd'])
        self.success("SSH restarted on CentOS")

    def _restart_ubuntu_ssh(self):
        plattools.cmd(['sudo', 'systemctl', 'restart', 'ssh'])
        self.success("SSH restarted on Ubuntu")

    def _restart_debian_ssh(self):
        plattools.cmd(['sudo', 'systemctl', 'restart', 'ssh'])
        self.success("SSH restarted on Debian")


    def modify_ssh_config(self):
        config_file = '/etc/ssh/sshd_config'
        backup_file = '/etc/ssh/sshd_config.bak'

        # 备份原始配置文件
        os.system(f'sudo cp {config_file} {backup_file}')

        with open(config_file, 'r') as file:
            lines = file.readlines()

        permit_root_login_pattern = re.compile(r'^\s*PermitRootLogin\s+(\S+)\s*$')
        password_authentication_pattern = re.compile(r'^\s*PasswordAuthentication\s+(\S+)\s*$')

        found_permit_root_login = False
        found_password_authentication = False
        modified = False

        for i in range(len(lines)):
            if not found_permit_root_login:
                match = permit_root_login_pattern.match(lines[i])
                if match:
                    found_permit_root_login = True
                    if match.group(1) != 'yes':
                        lines[i] = 'PermitRootLogin yes\n'
                        modified = True

            if not found_password_authentication:
                match = password_authentication_pattern.match(lines[i])
                if match:
                    found_password_authentication = True
                    if match.group(1) != 'yes':
                        lines[i] = 'PasswordAuthentication yes\n'
                        modified = True

            if found_permit_root_login and found_password_authentication:
                break

        if not found_permit_root_login:
            lines.append('PermitRootLogin yes\n')
            modified = True

        if not found_password_authentication:
            lines.append('PasswordAuthentication yes\n')
            modified = True

        if modified:
            with open(config_file, 'w') as file:
                file.writelines(lines)
            print("PermitRootLogin and/or PasswordAuthentication have been set to yes")

            os.system('sudo systemctl restart sshd')
        else:
            print("No changes made to the sshd_config file")



ssh = Ssh()
