import os
import configparser

class ConfigManager:
    def __init__(self,control_name):
        self.control_name = control_name
        pass

    def getcwd(self):
        return os.getcwd()

    def get_common_cfg(self):
        """
        获取通用配置文件路径
        :return: 通用配置文件路径
        """
        cwd = self.getcwd()
        cfg_path = os.path.join(cwd, f"config/config.cfg")
        return cfg_path

    def get_common_cfgfile(self):
        """
        获取通用配置文件
        :return: 通用配置文件对象
        """
        cfg_file = self.get_common_cfg()
        config = configparser.ConfigParser()
        config.read(cfg_file)
        return config

    def get_control_cfgfile(self):
        """
        获取控制配置文件
        :return: 控制配置文件对象
        """

        cwd = self.getcwd()
        config_filename = os.path.join(cwd, f"control_{self.control_name}/config.cfg")
        cfg_file = config_filename
        config = configparser.ConfigParser()
        config.read(cfg_file)
        return config

    def merge_config(self):
        """
        合并通用配置文件和控制配置文件
        :return: 合并后的配置文件对象
        """
        common_cfg = self.get_common_cfgfile()
        control_cfg = self.get_control_cfgfile()
        for section in control_cfg.sections():
            if section not in common_cfg.sections():
                common_cfg.add_section(section)
            for key, value in control_cfg.items(section):
                common_cfg.set(section, key, value)
        return common_cfg