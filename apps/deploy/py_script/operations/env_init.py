# import os
from apps.deploy.py_script.provider.deployenv import env, compose_env,main_dir,wwwroot_dir
from apps.deploy.py_script.operations.ssh import ssh
from apps.deploy.py_script.system.user_tools import user_tools
from pycore.base import Base

class EnvInit(Base):
    relative_settings = {}

    def __init__(self):
        pass

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
        ssh.restart_ssh()


env_init = EnvInit()
