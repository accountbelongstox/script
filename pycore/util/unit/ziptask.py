import errno
import os
import threading
import time
import subprocess
from pycore.base.base import Base
from pycore.globalvar.src import src
thread_name = "ziptask"

class Ziptask( Base):
    #TODO 1 完成本类。 不要调用Python的内置的压缩方法。 只使用7z命令行，严格按照要求。严格按照要求写每一个函数。 以防止程序错乱。 添加一个方法 （生成task_entity），根据传入的 src, out=None, group_name="default", is_compress=False, the_task_callback=None,the_group_task_callback=None, print_log=True，生成一个对应字段的 task_entity，同时还要包含字段 压缩命令，分组名,生成时间（用于计时）

    # 完成add_task方法。 add_task(self, src, out=None, group_name="default", is_compress=False, the_task_callback=None,the_group_task_callback=None, print_log=True): 该方法接受以上参数。 然后将以上参数。 调用上面的方法生成一个 task_entity。 并根据分组名加入公共对象并加入公共队列当中。

    #TODO 2 完成方法(执行队列 )只需要判断到公共队列当中还有任务。 则根据分组取出一个任务task_entity的。 然后进行执行，传给执行压缩方法。

    #TODO 3 完成方法(执行压缩) 根据传入的task_entity。读取中的 压缩命令，调用supper.exe_cmd执行，并且执行前设置一个开始计时。执行完后根据开始计时统计出执行时间。 将执行时间值给 task_entity。每个任务执行完后判断是否有 the_task_callback，如果有则执行。 分组执行完后。 判断the_group_task_callback。

    #TODO 4 完成方法（测试一个压缩文件是否正确）调用7z命令

    def create_command(self, source, output, is_compress=True):
        if is_compress:
            command = f'"{src.get_7z_executable()}" a "{output}" "{source}"'
        else:
            command = f'"{src.get_7z_executable()}" x "{source}" -o"{output}" -y'
        return command


    def generate_zip_dir(self, source_dir, output_dir=None, is_compress=True):
        s_base_name = os.path.basename(source_dir.rstrip('/\\')).lower()
        output_name_tmp = f'{s_base_name}.7z'
        if is_compress:
            if output_dir is None:
                output_dir = output_name_tmp
            else:
                o_base_name = os.path.basename(output_dir.rstrip('/\\')).lower()
                o_base_name = os.path.splitext(o_base_name)[0]
                if s_base_name != o_base_name:
                    output_dir = os.path.join(output_dir,output_name_tmp)
            src_new = source_dir
            out_new = output_dir
        else:
            if output_dir is None:
                output_dir = os.path.dirname(source_dir)
            src_new = source_dir
            out_new = output_dir
        return src_new, out_new