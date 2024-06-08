import os
import errno
from subprocess import Popen, PIPE
import subprocess
import psutil
from pycore.base.base import Base
class ZipTask(Base):
    def __init__(self):
        self.callbacks = {}
        self.maxTasks = 10
        self.pendingTasks = []
        self.concurrentTasks = 0
        self.execCountTasks = 0
        self.execTaskEvent = None
        self.zipQueueTokens = []

    def get_7z_exe_name(self):
        return '7z.exe' if self.is_windows() else '7zz'

    def is_file_locked(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            fd = os.open(file_path, os.O_RDWR | os.O_EXCL)
            os.close(fd)
            return False
        except OSError as e:
            if e.errno == errno.EBUSY or e.errno == errno.EACCES:
                return True
            return False

    def get_modification_time(self, fp):
        if not os.path.exists(fp):
            return 0
        try:
            return os.path.getmtime(fp)
        except OSError as e:
            print(f"Error getting modification time: {e.strerror}")
            return 0

    def set_mode(self, mode):
        self.mode = mode

    def log(self, msg, event):
        if event:
            print(msg)

    def compress_directory(self, src_dir, out_dir, token, callback):
        src_abs_path = os.path.abspath(src_dir)
        out_abs_path = os.path.abspath(out_dir)
        if not os.path.exists(src_abs_path):
            return
        if not os.path.exists(out_abs_path):
            self.mkdir(out_abs_path)
        sub_directories = [d for d in os.listdir(src_abs_path) if os.path.isdir(os.path.join(src_abs_path, d))]
        for sub_dir in sub_directories:
            if sub_dir.startswith('.'):
                continue
            sub_dir_path = os.path.join(src_abs_path, sub_dir)
            self.put_zip_queue_task(sub_dir_path, out_dir, token, callback)


    def processes_count(self, process_name):
        process_name = process_name.lower()
        return len([p.info for p in psutil.process_iter(['name']) if process_name in p.info['name'].lower()])

    def a7z_processes_count(self):
        process_name = self.get_7z_exe_name()
        return self.processes_count(process_name)

    def exec_task(self):
        if not self.execTaskEvent:
            print("Background compaction task started")
            while True:
                process_zip_count = self.a7z_processes_count()
                if process_zip_count != 10000:
                    self.concurrentTasks = process_zip_count
                if self.concurrentTasks >= self.maxTasks:
                    print(f"7zProcesse tasks is full. current tasks:{self.concurrentTasks}, waiting...")
                elif len(self.pendingTasks) > 0:
                    # The remaining part of this function has been omitted as it depends on other functions
                    pass
                else:
                    if self.execCountTasks < 1:
                        print("There is currently no compression task, end monitoring.")
                        self.execTaskQueueCallbak()
                    else:
                        print(f"There are still {self.execCountTasks} compression tasks, waiting")

    def execTaskQueueCallbak(self):
        for token in self.zipQueueTokens:
            self.execTaskCallback(token)

    def execTaskCallback(self, token):
        if token in self.callbacks:
            callback = self.callbacks[token]['callback']
            usetime = self.callbacks[token]['usetime']
            src = self.callbacks[token]['src']
            del self.callbacks[token]
            if callback:
                callback(usetime, src)

    def put_zip_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback, False)

    def put_zip_queue_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback)

    def put_unzip_task(self, src, out, callback, process_callback):
        token = self.md5id(src)
        self.put_task(src, out, token, False, callback, False, process_callback)

    def put_unzip_queue_task(self, src, out, callback, process_callback):
        token = self.md5id(src)
        self.put_task(src, out, token, False, callback, True, process_callback)

    def put_queue_callback(self, callback, token):
        if callback and token not in self.callbacks:
            if not token:
                token = self.gen_id()
            self.zipQueueTokens.append(token)
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': ''
            }



    def deleteTask(self, zipPath):
        self.pendingTasks = [task for task in self.pendingTasks if task['zipPath'] != zipPath]

    def isTask(self, zipPath):
        return any(task['zipPath'] == zipPath for task in self.pendingTasks)
