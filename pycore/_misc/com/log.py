from pycore.base import Base
import logging
import logging.handlers


class Log(Base):
    log = None

    def __init__(self, args):
        pass

    def main(self, args):
        # 配置日志
        self.log = logging.getLogger('common_log')
        self.log.setLevel(logging.DEBUG)
        # 创建文件处理器
        down_dir = self.com_config.get_control_tempdir()
        log_dir = f"{down_dir}/log/"
        self.com_file.mkdir(log_dir)
        log_file = f"{log_dir}my_log.log"
        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)

        # 配置格式化器
        formatter = logging.Formatter('%(asctime)s %(levelname)s \n%(message)s')
        file_handler.setFormatter(formatter)

        # 将文件处理器添加到日志器
        self.log.addHandler(file_handler)

    def debug(self, s, print=False):
        if print == True:
            self.com_util.print_warn(s)
        else:
            self.com_util.print_warn(s[0:1000])
        return self.log.debug(s)

    def info(self, s, print=False):
        if print == True:
            self.com_util.print_info(s)
        else:
            self.com_util.print_info(s[0:1000])
        return self.log.info(s)

    def warn(self, s, print=False):
        if print == True:
            self.com_util.print_warn(s)
        else:
            self.com_util.print_warn(s[0:1000])
        return self.log.warning(s)

    def error(self, s, print=False):
        if print == True:
            self.com_util.print_warn(s)
        else:
            self.com_util.print_warn(s[0:1000])
        return self.log.error(s)

    def critical(self, s, print=False):
        if print == True:
            self.com_util.print_warn(s)
        else:
            self.com_util.print_warn(s[0:1000])
        return self.log.critical(s)
