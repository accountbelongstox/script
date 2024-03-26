import subprocess
from pycore.base.base import Base
from pycore.utils_linux import plattools
import json

class ServerInfo(Base):
    def check_docker_snap(self):
        docker_info = plattools.exec_cmd(["docker", "info"],info=False)
        if "snap" in docker_info:
            return True
        else:
            return False

    def get_docker_sock(self):
        if self.check_docker_snap():
            docker_sock = "/var/snap/docker/common/run/docker.sock"
        else:
            docker_sock = "/var/run/docker.sock"
        return docker_sock

    def get_docker_root_dir(self):
        # docker_sock = self.get_docker_sock()
        docker_info_str = plattools.exec_cmd(["docker", "info", "--format", "{{json .RootDir}}"])
        try:
            docker_info = json.loads(docker_info_str)
            root_dir = docker_info.get('RootDir')
            return root_dir
        except json.JSONDecodeError:
            return ""

server_info = ServerInfo()