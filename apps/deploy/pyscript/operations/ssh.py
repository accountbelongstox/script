import subprocess
from pycore.utils_linux import plattools
from pycore.base import Base

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

ssh = Ssh()
