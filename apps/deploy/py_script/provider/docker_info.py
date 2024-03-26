import json
import os
from pycore.utils_prune import plattools, file, strtool
from pycore.base import Base
from apps.deploy.py_script.provider.deployenv import env, deploy_dir, compose_env
from pycore.practicals_prune import yml

class DockerInfo(Base):
    def __init__(self):
        pass

    def get_compose_list(self):
        return self.get_docker_compose_service_keys()
        compose_str = compose_env.get_env("full")
        compose_list = compose_str.split()
        return compose_list

    def get_compose_list_by_env(self, compose_name="default"):
        DOCKER_COMPOSE_NAME = compose_name  # env.get_env("DOCKER_COMPOSE") or "default"
        compose = compose_env.get_env(DOCKER_COMPOSE_NAME)
        compose_list = compose.split()
        return compose_list

    def set_compose_list_to_env(self, compose_list, name="default"):
        if isinstance(compose_list,list):
            compose_str = " ".join(compose_list)
        else:
            compose_str = compose_list
        env.set_env("DOCKER_COMPOSE", name)
        compose_env.set_env(name, compose_str)
        return True

    def get_docker_dir(self):
        docker_dir = env.get_env("DOCKER_DIR")
        if not docker_dir:
            root_id = "root_id_"+strtool.create_string()
            main_dir = env.get_env("MAIN_DIR")
            docker_dir = os.path.join(main_dir, f"docker/{root_id}")
        if not file.isdir(docker_dir):
            file.mkbasedir(docker_dir)
        return docker_dir

    def get_docker_data_dir(self):
        docker_dir = env.get_env("DOCKER_DATA")
        if not docker_dir:
            main_dir = env.get_env("MAIN_DIR")
            docker_dir = os.path.join(main_dir, "data")
        if not file.isdir(docker_dir):
            file.mkbasedir(docker_dir)
        return docker_dir

    def check_docker_snap(self, docker_infos_text=None):
        docker_infos_text = docker_infos_text or self.get_docker_infos_text()
        return 'snap' in docker_infos_text

    def get_daemon_file(self, snap=None):
        snap = snap or self.check_docker_snap()
        if snap == True:
            return "/var/snap/docker/current/etc/docker/daemon.json"
        else:
            return "/etc/docker/daemon.json"

    def get_docker_snap_and_daemon(self):
        docker_infos_text = self.get_docker_infos_text()
        snap = self.check_docker_snap(docker_infos_text)
        docker_infos = self.get_docker_infos(docker_infos_text)
        daemon_file = self.get_daemon_file(snap)
        sock_file = self.get_docker_sock(snap)
        root_dir = self.get_docker_root_dir(docker_infos)
        return root_dir, daemon_file, snap, sock_file, docker_infos

    def get_docker_sock(self, snap=None):
        snap = snap or self.check_docker_snap()
        if snap:
            docker_sock = "/var/snap/docker/common/run/docker.sock"
        else:
            docker_sock = "/var/run/docker.sock"
        return docker_sock

    def get_docker_infos_text(self):
        docker_info_text = plattools.exec_cmd(["docker", "info", "--format", '"{{json .}}"'], info=False)
        return docker_info_text

    def get_docker_infos(self, docker_info_text=None):
        docker_info_text = docker_info_text or self.get_docker_infos_text()
        docker_infos = json.loads(docker_info_text)
        return docker_infos

    def get_docker_root_dir(self, docker_infos=None):
        docker_infos = docker_infos or self.get_docker_infos()
        docker_root_dir = docker_infos.get('DockerRootDir', None)
        return docker_root_dir

    def get_old_docker_root_dir(self, docker_infos=None):
        return self.get_docker_root_dir(docker_infos)

    def get_mirrors(self):
        registry_mirrors = [
            "https://4idglt5r.mirror.aliyuncs.com",
            "https://docker.m.daocloud.io",
            "https://hub-mirror.c.163.com",
            "https://dockerproxy.com",
            "https://mirror.baidubce.com",
            "https://docker.nju.edu.cn",
            "https://docker.mirrors.sjtug.sjtu.edu.cn"
        ]
        return registry_mirrors

    def get_docker_compose_template_dir(self):
        docker_compose_dir = os.path.join(deploy_dir, "template/docker_compose")
        return docker_compose_dir

    def get_docker_compose_template_file(self):
        compose_template_dir = self.get_docker_compose_template_dir()
        docker_compose_file = os.path.join(compose_template_dir, "docker-compose-template.yml")
        return docker_compose_file

    def get_docker_compose_template(self):
        compose_dir = self.get_docker_compose_template_file()
        return yml.load(compose_dir)

    def save_docker_compose_template(self, compose_config):
        compose_file = self.get_docker_compose_template_file()
        with open(compose_file, 'w') as new_file:
            yml.safe_dump(compose_config, new_file)

    def get_docker_compose_service(self):
        compose_dir = self.get_docker_compose_template()
        return compose_dir.get_val("services")

    def get_docker_compose_service_keys(self):
        compose_dir = self.get_docker_compose_template()
        return list(compose_dir.get_keys("services"))

    def get_docker_compose_version(self):
        compose_dir = self.get_docker_compose_template()
        return compose_dir.get_val("version")

    def get_docker_compose_volumes(self, key):
        compose_service = self.get_docker_compose_service()
        nginx_conf = compose_service.get(key)
        nginx_volumes = nginx_conf.get("volumes")
        return nginx_volumes

    def get_docker_compose_volume_by_val(self, key, volume_val):
        volumes = self.get_docker_compose_volumes(key)
        # result_dict = {}
        for volume in volumes:
            parts = volume.split(':')
            if len(parts) == 2:
                host_path, docker_path = parts
                if docker_path == volume_val:
                    return self.replace_to_env(host_path)
                    # result_dict = {
                    #     "host_path":host_path,
                    #     "docker_path":docker_path,
                    # }
        return ""

    def replace_to_env(self, template_str):
        template_keys = strtool.extract_template_keys(template_str)
        keyword_args = {key: env.get_env(key) for key in template_keys}
        replaced_path = strtool.replace_template(template_str, keyword_args)
        return replaced_path


docker_info = DockerInfo()
