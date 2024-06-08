import os
import time
from pycore.practicals_linux import yml
from pycore.globalvar.gdir import gdir
from pycore.base.base import Base
from ruamel.yaml import YAML

# Define a global proxies list
global_proxies = []

cwd = gdir.getRootDir()
datadir = os.path.join(cwd, "data")
openwrt_dir = os.path.join(datadir, "openwrt")
main_yaml = os.path.join(openwrt_dir, "main.yaml")
attach_yamls = os.path.join(openwrt_dir, "attach_yaml")
new_dir = os.path.join(openwrt_dir, "new")

class Op(Base):

    def start(self):
        self.extract_proxies(main_yaml)
        self.extract_proxies_from_directory(attach_yamls)
        self.print_global_proxies()
        self.print_proxy_names()
        self.save_new_yaml_with_global_proxies()
        self.format_global_proxies()


    def extract_proxies(self, yaml_path):
        data = yml.read_yml(yaml_path)
        if 'proxies' in data:
            file_proxies_count = len(data['proxies'])
            global_proxies.extend(data['proxies'])
            self.info(f"Extracted {file_proxies_count} proxies from {yaml_path}")

    def extract_proxies_from_directory(self, dir_path):
        if os.path.isdir(dir_path):
            for file_name in os.listdir(dir_path):
                if file_name.endswith(".yaml"):
                    yaml_path = os.path.join(dir_path, file_name)
                    self.extract_proxies(yaml_path)

    def print_global_proxies(self):
        self.info("Global proxies:")
        self.info(global_proxies)
        self.info(f"Total proxies in global list: {len(global_proxies)}")

    def get_proxy_names(self):
        proxy_names = [proxy['name'] for proxy in global_proxies]
        return proxy_names

    def print_proxy_names(self):
        proxy_names = self.get_proxy_names()
        self.info("Proxy names:")
        for name in proxy_names:
            self.info(name)
        self.info(f"Total number of proxy names: {len(proxy_names)}")

    def save_new_yaml_with_global_proxies(self):
        os.makedirs(new_dir, exist_ok=True)
        main_data = yml.read_yml(main_yaml)
        main_data['proxies'] = global_proxies
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_yaml_path = os.path.join(new_dir, f"main_{timestamp}.yaml")

        self.info(f"New YAML file saved: {new_yaml_path}")

    def format_proxy(self,proxy):
        ordered_proxy = {'name': proxy['name']}
        for key, value in proxy.items():
            if key != 'name':
                ordered_proxy[key] = value
        proxy_str = ', '.join(f"{key}: {value}" for key, value in ordered_proxy.items())
        return f"{{{proxy_str}}}"

    def format_global_proxies(self):
        for proxy in global_proxies:
            formatted_proxy = self.format_proxy(proxy)
            print(formatted_proxy)

op = Op()