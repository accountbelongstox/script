import os
import sys
from pycore.utils_linux import strtool, ip, file
from pycore.practicals_linux import select
from apps.deploy.pyscript.tools.server_info import server_info
from apps.deploy.pyscript.tools.disk import disk
from apps.deploy.pyscript.tools.docker import docker
from apps.deploy.pyscript.tools.migrate import migrate
from apps.deploy.pyscript.provider.deployenv import *
from apps.deploy.pyscript.provider.docker_info import docker_info
from apps.deploy.pyscript.operations.ssh import ssh
from apps.deploy.pyscript.tools.choice import choice
from pycore.base.base import Base

class installChoice(Base):
    relative_settings = {}

    def __init__(self):
        self.docker_dir = env.get_env("DOCKER_DIR")

    def show_envs(self):
        self.init_env(show=True)

    def get_envs(self):
        return self.collection_settings()

    def install(self):
        self.success("The debian12 starts installation using python3")
        self.success("Initialize environment variables")
        self.set_envs()
        self.success("Configure the ssh service to allow remote login and root account login")
        self.set_ssh_config()
        # disk.create_main_dir()
        self.success("Mount the Docker runtime environment")
        root_dir, daemon_file, snap, sock_file, docker_infos = docker_info.get_docker_snap_and_daemon()
        # docker.mount_docker()
        docker.update_docker(daemon_file)
        # self.success("Copy nginx configuration")
        # migrate.copy_nginx_template()
        self.success("Generate docker-compose configuration and compile")
        docker.gen_docker_compose()

    def init_info(self,show=False):
        main_ip = ip.get_local_ip()

        snap_docker = server_info.check_docker_snap()
        docker_sock = server_info.get_docker_sock()

        show_settings = [
            ["SNAP_DOCKER", snap_docker],
            ["DOCKER_SOCK", docker_sock],
        ]
        choice.set_and_collection_envs(show_settings, "debian12.information", show=True)

        docker_root_dir = docker_info.get_docker_dir()
        docker_data_dir = docker_info.get_docker_data_dir()

        prompt_settings = [
            ["SERVICE_DIR", SERVICE_DIR],
            ["DOCKER_DIR", docker_root_dir],
            ["DOCKER_DATA", docker_data_dir],
        ]
        choice.set_and_collection_envs(prompt_settings, "SERVICE.information", True)

        prompt_settings = [
            ["MAIN_IP", main_ip],
            ["MAIN_DIR", MAIN_DIR],
            ["WEB_DIR", WWWROOT_DIR],
        ]
        choice.set_and_collection_envs(prompt_settings, "SERVICE.Main-Info", True)

        prompt_settings = [
            ["SCRIPT_DIR", SCRIPT_DIR],
            ["DEPLOY_DIR", DEPLOY_DIR],
            ["APPS_DIR", APPS_DIR],
            ["SHELLS_DIR", SHELLS_DIR],
        ]
        choice.set_and_collection_envs(prompt_settings, "SCRIPT-Info", True)

        prompt_settings = [
            ["PYTHON_EXECUTABLE", PYTHON_EXECUTABLE],
        ]
        choice.set_and_collection_envs(prompt_settings, "Python-Info", True)

    def init_env(self,show=False):
        compose_list = docker_info.get_compose_list()
        valid_compose_list = self.init_docker_compose(compose_list)
        main_ip = ip.get_local_ip()
        # self.success("-The docker-compose you need to configure is:")
        # self.success(valid_compose_list)

        snap_docker = server_info.check_docker_snap()
        docker_sock = server_info.get_docker_sock()

        show_settings = [
            ["SNAP_DOCKER", snap_docker],
            ["DOCKER_SOCK", docker_sock],
        ]
        set_name = "debian12.information"
        choice.set_and_collection_envs(show_settings, setting_name=set_name, show=True)

        docker_root_dir = docker_info.get_docker_dir()
        docker_data_dir = docker_info.get_docker_data_dir()

        set_name = "SERVICE.information"
        prompt_settings = [
            ["SERVICE_DIR", SERVICE_DIR],
            ["DOCKER_DIR", docker_root_dir],
            ["DOCKER_DATA", docker_data_dir],
        ]
        choice.set_and_collection_envs(prompt_settings, set_name, True)

        set_name = "SERVICE.Main-Info"
        prompt_settings = [
            ["MAIN_IP", main_ip],
            ["MAIN_DIR", MAIN_DIR],
            ["WEB_DIR", WWWROOT_DIR],
        ]
        set_name = "global-setting"
        choice.set_and_collection_envs(prompt_settings, set_name, show)

    def compiler_docker(self):
        self.success("Initialize environment variables")
        self.init_docker_env()
        docker.gen_docker_compose()

    def set_ssh_config(self):
        env_c = env.load("/etc/ssh", delimiter=" ", env_name="sshd_config")
        key = "PasswordAuthentication"
        password_authentication = env_c.get_env(key)
        restart=False
        if password_authentication == "":
            restart =True
            env_c.set_env(key, "yes")
        else:
            self.info(f"{key} already set to {password_authentication}. No changes made.")
        key = "PermitRootLogin"
        permit_root_login = env_c.get_env(key)
        if permit_root_login == "":
            restart =True
            env_c.set_env(key, "yes")
        else:
            self.info(f"{key} already set to {permit_root_login}. No changes made.")
        # if restart:
        ssh.restart_ssh()


    def init_docker_compose(self,compose_list=None):
        compose_name = "default"
        compose_list = compose_list or docker_info.get_compose_list()
        all_compose_list = " ".join(compose_list)
        print("---------------------------------------------")
        self.info("All available docker configurations:")
        self.info(all_compose_list)
        env_compose_list = docker_info.get_compose_list_by_env(compose_name)
        env_compose_str = " ".join(env_compose_list)
        select_env_compose_str = select.edit_str(env_compose_str, "Select docker to edit the image")
        choice.save_to_tmp_settings("DOCKER_COMPOSE_SELECT",select_env_compose_str)
        select_env_compose_list = select_env_compose_str.split()
        valid_compose_list = []
        invalid_compose_list = []

        for value in select_env_compose_list:
            value = value.strip()
            if value in compose_list:
                valid_compose_list.append(value)
            else:
                invalid_compose_list.append(value)

        if invalid_compose_list:
            invalid_compose = " ".join(invalid_compose_list)
            self.warn(
                f"Invalid option, the current option {invalid_compose} does not exist in the docker-compose template")
        docker_info.set_compose_list_to_env(valid_compose_list, compose_name)
        # select_compose_list = docker_info.get_compose_list_by_env(compose_name)
        self.success("---------------------------------------------")
        self.success("Select the docker image that needs to be installed")
        self.success(" ".join(valid_compose_list))
        # self.success("-The docker-compose you need to configure is:")
        # self.success(valid_compose_list)
        return valid_compose_list

    def init_docker_env(self, show=False):
        compose_list = docker_info.get_compose_list()
        valid_compose_list = self.init_docker_compose(compose_list)
        for value in valid_compose_list:
            if value == "portainer":
                prompt_settings = [
                ]
                choice.set_and_collection_envs(prompt_settings, value, show)
            elif value == "mysql":
                prompt_settings = [
                    ["MYSQL_ROOT_USER", "root"],
                    ["MYSQL_ROOT_PASSWORD", ],
                    ["MYSQL_USER", "user"],
                    ["MYSQL_PASSWORD", ],
                ]
                choice.set_and_collection_envs(prompt_settings, value, show)
            elif value == "nginx":
                prompt_settings = [
                    ["MIGRATE_NGINX", True, ],
                ]
                choice.set_and_collection_envs(prompt_settings, value, show)
            elif value == "ztncui":
                prompt_settings = [
                    ["ZEROTIER_MYADDR", env.get_env("MAIN_IP")],
                    ["ZEROTIER_DOMIAN", ],
                    ["ZTNCUI_PASSWORD", ],
                ]
                choice.set_and_collection_envs(prompt_settings, value, show)


    def set_envs(self, show=False):
        self.init_env(show=show)
        self.init_docker_env(show=show)


    def collection_settings(self, settings=None, setting_name=""):
        if settings:
            self.relative_settings[setting_name] = settings



install_choice = installChoice()
