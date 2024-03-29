from pycore.base.base import Base
from pycore.utils_linux import file
from apps.deploy.pyscript.provider.deployenv import deploy_dir, env
from apps.deploy.pyscript.tools.nginx import nginx
from apps.deploy.pyscript.provider.docker_info import docker_info
import os
# import re

class Migrate(Base):
    php_default_version = "82"
    template_dir = os.path.join(deploy_dir, "template/nginx")
    nginx_conf_dir = ""

    def __init__(self):
        pass

    def migrate(self):
        bt_dir = "/www/server"
        if file.isdir(bt_dir):
            bt_tmp = os.path.join(deploy_dir, ".bt_server_bak")
            bt_template = os.path.join(deploy_dir, ".bt_template")
            if file.is_empty(bt_tmp):
                file.delete(bt_tmp)
            if file.is_empty(bt_template):
                file.delete(bt_template)
            if not file.isdir(bt_tmp):
                self.info(f"migrage: {bt_dir} to {bt_tmp}")
                file.copy(bt_dir, bt_tmp)
            else:
                self.info(f"File {bt_tmp} already exists, no need to migrate")
            if not file.isdir(bt_template):
                self.info(f"migrage: {bt_dir} to {bt_template}")
                file.copy(bt_dir, bt_template)
            else:
                self.info(f"File {bt_template} already exists, no need to migrate")
        log_files = [
            "ib_logfile",
            "ibdata",
            "ibtmp",
            "core",
            "php",
            "php-cgi",
            "phpdbg",
            "php-fpm",
            "nginx",
            "php",
            "high_risk_vul-9",
        ]
        exts = [
            "so",
            "jpg",
            "png",
            "gz",
            "7m",
            "7",
            "8",
            "curses.pyc",
            "rsp",
            "h",
            "js",
            "css",
            "svg",
            "gif",
            "py",
            "pyc",
            "ext",
            "html",
            "pl",
            "ext",
            "sh",
            "decTest",
            "pxd",
        ]
        bt_template = os.path.join(deploy_dir, ".bt_template")
        self.del_log(bt_template, log_files, exts, 2)
        bt_server_bak = os.path.join(deploy_dir, ".bt_server_bak")
        self.del_log(bt_server_bak, log_files, exts, 2)
        bt_wwwroot = "/www/wwwroot"
        web_dir = env.get_env("WEB_DIR")
        if file.isdir(bt_wwwroot):
            contents = os.listdir(bt_wwwroot)
            for item in contents:
                item_path = os.path.join(bt_wwwroot, item)
                target_path = os.path.join(web_dir, item)
                if file.is_empty(target_path):
                    file.delete(target_path)
                if not file.isdir(target_path):
                    self.info(f"migrage: {item_path} to {target_path}")
                    file.copy(item_path, target_path)
                else:
                    self.info(f"File {target_path} already exists, no need to migrate")

    def copy_nginx_template(self):
        self.nginx_conf_dir = docker_info.get_docker_compose_volume_by_val("nginx", "/etc/nginx")
        file.mkdir(self.nginx_conf_dir)
        # self.copy_main_conf()
        self.copy_template_conf()
        # self.copy_base_conf()

    def del_log(self, folder_path, keywords, exts=[], size_limit=2):
        if not os.path.isdir(folder_path):
            return
        for root, dirs, files in os.walk(folder_path):
            for afile in files:
                file_path = os.path.join(root, afile)
                file_name, file_extension = os.path.splitext(afile)
                if any(keyword in afile for keyword in keywords) and os.path.getsize(
                        file_path) > size_limit * 1024 * 1024:
                    print(f"Clear: {file_path}")
                    os.remove(file_path)
                if file_extension[1:] in exts and os.path.isfile(file_path):
                    print(f"Clear: {file_extension} file: {file_path}")
                    os.remove(file_path)

    def copy_template_conf(self):
        for root, dirs, files in os.walk(self.template_dir):
            for filename in files:
                file_path = os.path.join(self.template_dir, filename)
                conf_path = os.path.join(self.nginx_conf_dir, filename)
                if filename.startswith("enable-php"):
                    php_version = self.php_default_version if filename.startswith(
                        "enable-php.") else filename[len("enable-php-"):len("enable-php-") + 2]
                    conf = nginx.read_conf(file_path)
                    conf = nginx.set_val("fastcgi_pass", f"php{php_version}:9000;", conf)
                    nginx.save_conf(conf_path, conf)
                else:
                    config_content = nginx.replace_wwwroot(file_path)
                    file.save(conf_path, config_content)
                self.info(f"{filename} to {conf_path}")

    def copy_base_conf(self):
        base_confs = [
            "fastcgi.conf",
            "fastcgi.conf.default",
            "fastcgi_params",
            "fastcgi_params.default",
            "koi-utf",
            "koi-win",
            "luawaf.conf",
            "mime.types",
            "mime.types.default",
            "pathinfo.conf",
            "scgi_params",
            "scgi_params.default",
            "uwsgi_params",
            "uwsgi_params.default",
            "win-utf",
        ]
        for base_file in base_confs:
            file_path = os.path.join(self.template_dir, base_file)
            file.copy(file_path, self.nginx_conf_dir)

    def copy_main_conf(self):
        base_confs = [
            "nginx.conf",
            "nginx.conf.default",
        ]
        nginx_dir = os.path.join(deploy_dir, ".nginx")
        for base_file in base_confs:
            nginx_conf_dir = docker_info.get_docker_compose_volume_by_val("nginx", "/etc/nginx")
            file.mkdir(nginx_conf_dir)
            file_path = os.path.join(self.template_dir, base_file)
            save_path = os.path.join(nginx_dir, base_file)
            conf_text = file.read_text(file_path)
            conf_text = nginx.replace_wwwroot(conf_text)
            file.save(save_path, conf_text, overwrite=True)

    def copy_all_conf(self):
        pass

migrate = Migrate()
