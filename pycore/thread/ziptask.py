import errno
import os
import threading
import time
import subprocess
from pycore.base.base import Base
from pycore.globalvar.src import src
from pycore.thread.interface.threadBase import ThreadBase
from pycore.globalvar.encyclopedia import encyclopedia

thread_name = "ziptask"

class Ziptask(threading.Thread, Base, ThreadBase):
    def __init__(self):
        super().__init__()
        self.tasks_as_group = {}
        self.max_tasks = 10
        self._stop_event = threading.Event()
        self._is_running = threading.Event()
        self.thread_name = thread_name
        self.callbacks = {}
        self.concurrent_tasks = 0
        self.executed_tasks_count = 0

    def stop(self):
        self._stop_event.set()
        self._is_running.clear()

    def run(self):
        self._is_running.set()  # Set running state
        while not self._stop_event.is_set():
            if not self.start_task():
                self.stop()  # Stop the thread if there are no tasks
            time.sleep(1)  # Sleep for 1 second to avoid high CPU usage
        self._is_running.clear()  # Clear running state when exiting

    def start_task(self):
        if self.tasks_as_group:
            for group_name, task_group in list(self.tasks_as_group.items()):
                if task_group:
                    self.execute_task_group(task_group)
                    del self.tasks_as_group[group_name]
                    return True
        return False  # No tasks to process, signal to stop the thread

    def execute_task_group(self, task_group):
        for task in task_group:
            self.execute_single_task(task)
        # Execute group callback after all tasks in the group are done
        group_callback = task_group[0]['group_callback']
        if group_callback:
            group_callback()

    def execute_single_task(self, task):
        command = task['command']
        callback = task['callback']
        print_log = task['print_log']
        start_time = time.time()
        self.exec_cmd(command)
        if callback:
            callback(int((time.time() - start_time) * 1000))

    def add_task(self, src, out=None, group_name="default", is_compress=False, callback=None, group_callback=None, print_log=True):
        src_new, out_new = self.generate_zip_dir(src, out, is_compress)
        command = self.create_command(src_new, out_new, is_compress)
        task = {
            'command': command,
            'src': src_new,
            'out': out_new,
            'callback': callback,
            'group_callback': group_callback,
            'print_log': print_log
        }
        print(task)

        if group_name not in self.tasks_as_group:
            self.tasks_as_group[group_name] = []
        self.tasks_as_group[group_name].append(task)

        if not self.is_running():
            self.start()  # Use start() to run the thread

    def log(self, message, print_log):
        if print_log:
            print(message)

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

    def create_command(self, source, output, is_compress=True):
        if is_compress:
            command = f'"{src.get_7z_executable()}" a "{output}" "{source}"'
        else:
            command = f'"{src.get_7z_executable()}" x "{source}" -o"{output}" -y'
        return command

    def exec_cmd(self, command):
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.log(f'Error executing command: {str(e)}', True)

    def is_running(self):
        return self._is_running.is_set()  # Return the running state
