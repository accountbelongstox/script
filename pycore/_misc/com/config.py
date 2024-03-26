from pycore._base import *
import configparser
import os
import re
from pycore._base._config_manager import ConfigManager

class Config(Base):
    __merge_config = None
    def __init__(self, args):
        # super.__init__()
        # self.com = self.get_common()
        # self.mode = self.get_mode()
        pass

    def get_static(self, sub_dir):
        sub_dir = self.config_cfg("static", sub_dir)
        sub_dir = self.abs_dir__(sub_dir)
        if self.com_file.isdir(sub_dir) == False:
            self.com_file.mkdir(sub_dir)
        return sub_dir

    def get_public(self, dir=None):
        if self.com_file.is_absolute_path(dir):
            return dir
        sub_dir = self.config_cfg("static", "public_dir")
        self.com_file.mkdir(sub_dir)
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        create_dir = sub_dir
        if os.path.splitext(sub_dir)[1]:
            create_dir = os.path.dirname(sub_dir)
        if not self.com_file.isdir(create_dir):
            self.com_file.mkdir(create_dir)
        return sub_dir

    def get_control_tempdir(self, suffix=""):
        sub_dir= self.load_module.get_control_core_dir(f"temp")
        sub_dir = os.path.join(sub_dir, suffix)
        self.com_file.mkdir(sub_dir)
        return sub_dir


    def get_control_core_file(self, suffix=""):
        sub_dir= self.load_module.get_control_core_dir()
        sub_dir = os.path.join(sub_dir, suffix)
        self.com_file.mkdir(sub_dir)
        return sub_dir

    def get_bin_dir(self, dir=None):
        sub_dir = self.config_cfg("static", "bin_dir")
        self.com_file.mkdir(sub_dir)
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def get_template_dir(self, dir=None):
        sub_dir = self.config_cfg("static", "template_dir")
        self.com_file.mkdir(sub_dir)
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def is_mainserver(self):
        is_main_server = self.config_cfg("global", "is_main_server")
        return is_main_server

    def get_webdownload_dir(self):
        sub_dir = self.config_cfg("static", "webdownload_dir")
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def abs_dir__(self, dir):
        cwd = self.getcwd()
        dir = f"{os.path.join(cwd, dir)}".replace('\\', '/')
        if os.path.exists(dir) == True:
            if os.path.isdir(dir):
                dir = dir + "/"
        # else:
        #     if self.com_file.ext(dir) == "":
        #         self.com_file.mkdir(dir)
        #     else:
        #         self.com_file.mkdir(os.path.dirname(dir))
        return dir

    def get(self, key):
        return self.get_global(key)

    def get_section(self,section):
        cfg_parser = self.cfg_parser()
        return cfg_parser[section]

    def get_keys(self,section):
        cfg_parser = self.cfg_parser()
        keys = []
        if cfg_parser.has_section(section):
            for key, _ in cfg_parser.items(section):
                keys.append(key)
        return keys

    def get_global(self, key,default_value=None):
        return self.config_cfg("global", key,default_value=default_value)

    def get_translate(self, key,default_value=None):
        return self.config_cfg("translate", key,default_value=default_value)

    def get_config(self, section, key,default_value=None):
        return self.config_cfg(section, key,default_value=default_value)

    def config_cfg(self, section, key,default_value=None):
        cfg = self.config( section=section, key=key,default_value=default_value)
        return cfg

    def config_ini(self, section, key,default_value=None):
        cfg = self.config( section=section, key=key,default_value=default_value)
        return cfg

    def get_libs(self, dir=""):
        sub_dir = self.load_module.get_kernel_dir("libs")
        sub_dir = os.path.join(sub_dir, dir)
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def cfg_parser(self):
        if self.__merge_config == None:
            self.__merge_config = self.merge_config()
        return self.__merge_config

    def config(self, section=None, key=None,default_value=None):
        if section is None or key is None:
            return default_value
        cfg_parser = self.cfg_parser()
        try:
            cfg = cfg_parser[section][key]
        except KeyError:
            return default_value
        if cfg in ["True", "true"]:
            cfg = True
        elif cfg in ["false", "False"]:
            cfg = False
        elif cfg in ["None",]:
            cfg = None
        elif re.search(re.compile("^\d+$"), cfg) is not None:
            cfg = int(cfg)
        elif re.search(re.compile("^\d+\.\d+$"), cfg) is not None:
            cfg = float(cfg)
        return cfg

    def get_common_cfg(self):
        cwd = self.getcwd()
        cfg_path = os.path.join(cwd, "config/config.cfg")
        return cfg_path

    def get_common_cfgfile(self):
        sub_dir= self.load_module.get_control_dir(f"config.cfg")
        return sub_dir

    def get_control_cfgfile(self):
        sub_dir= self.load_module.get_control_dir(f"config.cfg")
        return sub_dir

    def merge_config(self):
        file1 = self.get_common_cfg()
        file2 = self.get_control_cfgfile()
        config1 = configparser.ConfigParser()
        config1.read(file1)
        if self.com_file.isfile(file2):
            config2 = configparser.ConfigParser()
            config2.read(file2)
            for section in config2.sections():
                if section not in config1.sections():
                    config1.add_section(section)
                for key, value in config2.items(section):
                    config1.set(section, key, value)
        with open(file2, 'w', encoding='utf-8') as f:
            config1.write(f)
        return config1

    def getcwd(self, suffix=""):
        cwd = os.path.abspath(__file__).split('pycore')[0]
        cwd = os.path.join(cwd, suffix)
        return cwd

    def set_config(self, session=None, key=None, value=None):
        config = self.cfg_parser()
        cfg_file = self.get_control_cfgfile()
        config.read(cfg_file, encoding='utf-8')
        if session not in config:
            config.add_section(session)
        config.set(session, key, value)
        with open(cfg_file, 'w', encoding='utf-8') as f:
            config.write(f)

    def get_software_configfile(self):
        gwd = self.getcwd()
        control_name = self.load_module.get_control_name()
        default = os.path.join(gwd,f'default.{control_name}.ini')
        return default

    def software_config(self):
        default = self.get_software_configfile()
        if self.com_file.isfile(default) == False:
            self.com_file.save(default,'default=0')
        default = self.com_file.read(default)
        default = re.split(re.compile(r'\n+'),default)
        config = {}
        for line in default:
            if line.find('=') != -1:
                key, value = line.strip().split('=')
                key = key.strip()
                value = value.strip()
                config[key] = value
        # if len(config.keys()) == 0:
        #     config = {
        #         'send_interval_input'
        #     }
        return config

    def set_software_config(self,key,value):
        config = self.software_config()
        config[key] = value
        default = self.get_software_configfile()
        with open(default, 'w',encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f'{key}={value}\n')

    def get_cookie_key(self):
        return self.get_global('cookie_key',"py_token_cookie")