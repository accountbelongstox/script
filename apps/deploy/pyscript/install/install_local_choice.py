# import os
from apps.deploy.pyscript.tools.choice import choice
from apps.deploy.pyscript.operations.env_init import env_init
from apps.deploy.pyscript.provider.deployenv import env, main_dir, wwwroot_dir
from apps.deploy.pyscript.system.user_tools import user_tools
from apps.deploy.pyscript.operations.samba import samba
from pycore.utils_linux import file
from pycore.base.base import Base

class installLocalChoice(Base):
    relative_settings = {}

    def __init__(self):
        pass

    def local_install(self):
        self.success("The debian12 starts installation using python3")
        self.success("Initialize environment variables")
        self.init_local_env()
        self.success("Configure the ssh service to allow remote login and root account login")
        env_init.set_ssh_config()
        # disk.create_main_dir()
        # docker.mount_docker()
        # self.success("Copy nginx configuration")
        # migrate.copy_nginx_template()

    def init_local_env(self, show=False):
        samba_enable = env.get_env("SAMBA_ENABLE")
        show_settings = [
            ["SAMBA_ENABLE", samba_enable],
        ]
        set_name = "samba.setting"
        choice.set_and_collection_envs(show_settings, setting_name=set_name, show=show)

        samba_enable = env.get_env("SAMBA_ENABLE")
        if samba_enable != "no":
            set_name = "samba-setting"
            current_username = user_tools.get_current_username()
            default_pwd = "123456"
            samba_pwd_key = "SAMBA_PW"
            prompt_settings = [
                ["SAMBA_USER", current_username],
                [samba_pwd_key, default_pwd],
                ["SAMBA_SHARE_DIR", wwwroot_dir],
            ]
            choice.set_and_collection_envs(prompt_settings, set_name, show)
            samba_user_key = "SAMBA_USER"
            samba_username = env.get_env(samba_user_key)
            username = user_tools.ensuer_username(samba_username)
            if samba_username != username:
                env.set_env(samba_user_key, samba_username)
            samba_password = env.get_env(samba_pwd_key)
            samba.set_samba_password(username, samba_password)
            share_dir = env.get_env("SAMBA_SHARE_DIR")
            samba.add(username, share_dir)


install_local_choice = installLocalChoice()
