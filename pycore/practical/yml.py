import yaml
import os
from pycore.utils_linux import file
from pycore.base.base import Base
# import shutil

class Yml(Base):
    yml_path = None
    yarm_content = None
    compose_template_dir = None
    compose_template_file = None

    def __init__(self, yml_path=None):
        self.yml_path = yml_path
        if yml_path != None:
            self.read_yml(yml_path)

    def docker_compose(self):
        self.compose_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "template/docker")
        self.compose_template_file = os.path.join(self.compose_template_dir, "docker-template.yml")

    def load(self, file_path=None):
        return Yml(file_path)

    def save(self, file_path=None,compose_config=None,info=True):
        return self.save_yml(file_path=file_path,compose_config=compose_config,info=info)

    def save_yml(self, file_path=None,compose_config=None,info=True):
        if compose_config==None:
            return
        if file_path==None:
            file_path = self.yml_path
        if file.is_file(file_path):
            file.delete_file(file_path)
        file.mkbasedir(file_path)
        if info:
            self.info(f"save-yml: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as new_file:
            yaml.safe_dump(compose_config, new_file)

    def read(self, file_path=None,info=True):
        return self.read_yml(file_path=file_path,info=info)

    def read_yml(self, file_path=None,info=True):
        with open(file_path, 'r', encoding='utf-8') as content:
            yarm_content = yaml.safe_load(content)
        self.yarm_content = yarm_content
        return yarm_content

    def get_val(self, key):
        return self.yarm_content.get(key, {})

    def get_config(self):
        return self.yarm_content

    def get_body(self):
        return self.get_config()

    def get_keys(self, key):
        return self.yarm_content.get(key, {}).keys()

    def show(self):
        print(self.yarm_content)

    def parse_docker_compose(self, file_path=None):
        if file_path == None:
            file_path = self.local_env_file
        with open(file_path, 'r', encoding='utf-8') as file:
            compose_data = yaml.safe_load(file)
        return compose_data.get('services', {}).keys()


