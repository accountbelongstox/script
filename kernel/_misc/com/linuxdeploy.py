from kernel.base.base import *
import subprocess
import os
class Linuxdeploy(Base):

    def __init__(self, args):
        pass
    def check_GLIBCXX(self):
        # 执行命令并获取输出结果
        output = subprocess.check_output("strings /usr/lib64/libstdc++.so.6 | grep GLIBCXX", shell=True)
        # 解析输出结果，获取GLIBCXX的最高版本号
        max_version = None
        for line in output.decode().split('\n'):
            if line.startswith('GLIBCXX_'):
                version = line.split('_')[1]
                if not max_version or version > max_version:
                    max_version = version
        return max_version

    def install_GLIBCXX(self):
        libstdc_so = self.load_module.get_kernel_dir('libs/libstdc++.so.6.0.24')
        script = f"""
        cp {libstdc_so} /usr/lib64/
        rm -rf /usr/lib64/libstdc++.so.6
        ln -s /usr/lib64/libstdc++.so.6.0.24 /usr/lib64/libstdc++.so.6
        strings /usr/lib64/libstdc++.so.6 | grep GLIBCXX
        """
        # 执行Shell脚本
        print(script)
        subprocess.run(script, shell=True, check=True)

    def is_install_chrome(self):
        # 执行命令检查是否已安装Chrome浏览器
        command = 'which google-chrome'
        result = os.system(command)
        # 根据命令返回值判断是否已安装Chrome浏览器
        if result == 0:
            print('Chrome browser is installed.')
            return True
        else:
            print('Chrome browser is not installed.')
            return False