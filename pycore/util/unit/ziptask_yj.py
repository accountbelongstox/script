import subprocess
import platform
import hashlib
import random
import errno
import time
from pycore.base.base import Base
from pycore.util.unit.gdir_lwj import gdir
import os
class ZipTask(Base):
    def __init__(self):
        self.callbacks = {}
        self.max_tasks = 10
        self.pending_tasks = []
        self.concurrent_tasks = 0
        self.exec_count_tasks = 0
        self.exec_task_event = None
        self.zip_queue_tokens = []

        super().__init__()

    def get_md5(self, value):
        hash = hashlib.md5()
        hash.update(value.encode())
        return hash.hexdigest()

    def create_string(self, length=10):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        result = ''.join(random.choice(letters) for _ in range(length))
        return result

    def create_id(self, value=None):
        if not value:
            value = self.create_string(128)
        _id = self.get_id(value)
        return _id

    def get_id(self, value, pre=None):
        value = str(value)
        md5 = self.get_md5(value)
        _id = f'id{md5}'
        if pre:
            _id = pre + _id
        return _id

    def get_current_os(self):
        return platform.system()

    def is_windows(self):
        return platform.system() == 'Windows'

    def get_7zE_exename(self):
        exeFile = '7zz'
        if self.is_windows():
            exeFile = '7z.exe'
        return exeFile

    def get_7z_exe(self):
        exeFile = self.get_7zE_exename()
        libraryDir = gdir.getLibraryDir()  # assuming gdir is defined elsewhere
        return os.path.join(libraryDir, exeFile)

    def mkdir_sync(self, directory_path):
        return self.mkdir(directory_path)

    def mkdir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def is_file_locked(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'r+'):
                pass
            return False
        except OSError as error:
            if error.errno in (errno.EBUSY, errno.EPERM):
                return True
            return False

    def get_modification_time(self, fp):
        if not os.path.exists(fp):
            return 0
        try:
            stats = os.stat(fp)
            return stats.st_mtime
        except Exception as error:
            print(f'Error getting modification time: {error}')
            return 0

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return -1
        try:
            file_size_in_bytes = os.path.getsize(file_path)
            return file_size_in_bytes
        except OSError:
            return -1

    def set_mode(self, mode):
        self.mode = mode

    def log(self, msg, event=None):
        if event:
            self.success(msg)

    def compress_directory(self, src_dir, out_dir, token, callback):
        src_abs_path = os.path.abspath(src_dir)
        out_abs_path = os.path.abspath(out_dir)

        if not os.path.exists(src_abs_path):
            return

        if not os.path.exists(out_abs_path):
            self.mkdir_sync(out_abs_path)

        sub_directories = [d for d in os.listdir(src_abs_path)
                           if os.path.isdir(os.path.join(src_abs_path, d)) and not d.startswith('.')]

        for sub_dir_name in sub_directories:
            sub_dir_path = os.path.join(src_abs_path, sub_dir_name)
            self.put_zip_queue_task(sub_dir_path, out_dir, token, callback)

    def get_zip_path(self, src_dir, out_dir):
        src_dir_name = os.path.basename(src_dir)
        archive_file_name = f"{src_dir_name}'.zip'"
        archive_file_path = os.path.join(out_dir, archive_file_name)
        return archive_file_path

    def add_to_pending_tasks(self, command, callback, process_callback):
        self.concurrent_tasks += 1
        self.exec_by_spawn(command, callback, process_callback)

    def exec_by_spawn(self, command, callback, process_callback):
        start_time = time.time()
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if output:
                data = self.byte_to_str(output)
                if process_callback:
                    process_callback(data)
            error = process.stderr.readline()
            if error:
                error_data = self.byte_to_str(error)
                print(f'Error: {error_data}')
                if process_callback:
                    process_callback(-1)
            # break the loop if the process is done
            if process.poll() is not None:
                break

        print(f'child process exited with code {process.poll()}')
        if callback:
            callback(time.time() - start_time)

    def byte_to_str(self, a_bytes):
        try:
            a_str = a_bytes.decode('utf-8')
            return a_str
        except UnicodeDecodeError as e:
            a_str = str(a_bytes)
            is_byte = a_str.startswith("b'") or a_str.startswith('b"')
            if is_byte:
                a_str = a_str[2:-1] if a_str.endswith(("'", '"')) else a_str[2:]
            return a_str

    def processes_count(self, process_name):
        normalized_process_name = process_name.lower()
        cmd = None

        if self.is_windows():
            cmd = f"tasklist /fi \"imagename eq {process_name}\""
        else:
            cmd = f"ps aux | grep -i {process_name} | grep -v grep"

        try:
            stdout = subprocess.check_output(cmd, shell=True, text=True)
            count = stdout.count(normalized_process_name)
            return count
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return 10000

    def a7z_processes_count(self):
        process_name = self.get_7zE_exename()
        process_zip_count = self.processes_count(process_name)
        return process_zip_count

    def exec_task(self):
        if not self.exec_task_event:
            self.log("Background compaction tasks started", True)
            self.exec_task_event = True
            while True:
                process_zip_count = self.a7z_processes_count()
                if process_zip_count != 10000:
                    self.concurrent_tasks = process_zip_count
                if self.concurrent_tasks >= self.max_tasks:
                    self.log(f"7zProcesses tasks is full. current tasks: {self.concurrent_tasks}, waiting...")
                elif self.pending_tasks:
                    task_object = self.pending_tasks.pop(0)
                    command = task_object["command"]
                    is_queue = task_object["isQueue"]
                    token = task_object["token"]
                    process_callback = task_object["processCallback"]

                    zip_path = task_object["zipPath"]
                    zip_name = os.path.basename(zip_path)
                    if not self.is_file_locked(zip_path):
                        self.log(f"Unzipping {zip_name}, background: {self.concurrent_tasks}", True)
                        self.success(f"Unzip-Command: {command}")
                        self.exec_count_tasks += 1
                        self.add_to_pending_tasks(command, lambda usetime: self.exec_task_callback(token, usetime),
                                                  process_callback)
                    else:
                        self.pending_tasks.append(task_object)
                        self.log(f"The file is in use, try again later, \"{zip_path}\"")
                else:
                    if self.exec_count_tasks < 1:
                        self.exec_task_event = False
                        self.log("There is currently no compression tasks, end monitoring.")
                        self.exec_task_queue_callback()
                        break
                    else:
                        self.log(f"There are still {self.exec_count_tasks} compression tasks, waiting")

                if not self.pending_tasks and self.concurrent_tasks == 0:
                    print('No pending tasks and no concurrent tasks, exiting...')
                    self.exec_task_event = None
                    break

                time.sleep(1)

    def exec_task_queue_callback(self):
        for token in self.zip_queue_tokens:
            self.exec_task_callback(token)

    def exec_task_callback(self, token):
        if token in self.callbacks:
            callback, usetime, src = self.callbacks[token]['callback'], self.callbacks[token]['usetime'], \
            self.callbacks[token]['src']
            del self.callbacks[token]  # Delete the token entry after using it
            if callback:
                callback(usetime, src)  # Call the callback function with the required arguments

    def put_zip_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback, False)

    def put_zip_queue_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback)

    def put_unzip_task(self, src, out, callback=None, process_callback=None):
        token = self.get_id(src)
        self.put_task(src, out, token, False, callback, False, process_callback)

    def put_unzip_queue_task(self, src, out, callback, process_callback=None):
        token = self.get_id(src)
        self.put_task(src, out, token, False, callback, True, process_callback)

    def put_queue_callback(self, callback, token=None):
        if callback and (token not in self.callbacks):
            if not token:
                token = self.create_id()
            self.zip_queue_tokens.append(token)
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': ''
            }

    def put_unzip_task_promise(self, zip_file_path, target_directory):
        try:
            self.put_unzip_task(zip_file_path, target_directory)
            return True
        except Exception as e:
            print(e)
            return False

    def put_task(self, src, out, token, is_zip=True, callback=None, is_queue=True, process_callback=None):
        if callback and not self.callbacks.get(token):
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': src
            }
        if is_queue:
            self.zip_queue_tokens.append(token)

        zip_path = None
        command = None

        if is_zip:
            zip_path = self.get_zip_path(src, out)
            if os.path.exists(zip_path):
                if not self.mode:
                    return
                if self.mode.update:
                    src_modi_time = self.get_modification_time(src)
                    zip_path_modi_time = self.get_modification_time(zip_path)
                    dif_time = src_modi_time - zip_path_modi_time
                    if dif_time < 1000 * 60:
                        return
                    os.unlink(zip_path)
                elif self.mode.override:
                    os.unlink(zip_path)
                else:
                    return

            zip_size = self.get_file_size(zip_path)
            if zip_size == 0:
                os.unlink(zip_size)

            command = self.create_zip_command(src, out)
        else:
            zip_path = src
            command = self.create_unzip_command(src, out)

        if not self.is_task(zip_path) and isinstance(zip_path, str):
            zip_act = 'compression' if is_zip else 'unzip'
            zip_name = os.path.basename(zip_path)
            self.log(f'Add a {zip_act} {zip_name}, background:{self.concurrent_tasks}', True)
            self.pending_tasks.append({
                'command': command,
                'zipPath': zip_path,
                'token': token,
                'isQueue': is_queue,
                'processCallback': process_callback
            })
        else:
            if process_callback:
                process_callback(-1)
            if callback:
                callback()
        self.exec_task()

    def delete_task(self, zipPath):
        # Filtering out the tasks where zipPath equals the provided zip_path
        self.pending_tasks = [task for task in self.pending_tasks if task['zipPath'] != zipPath]

    def is_task(self, zipPath):
        return any(task['zipPath'] == zipPath for task in self.pending_tasks)

    def create_zip_command(self, srcDir, outDir):
        srcDirName = os.path.basename(srcDir)
        zipFileName = f'{srcDirName}.zip'
        zipFilePath = os.path.join(outDir, zipFileName)
        command = f'"{self.get_7z_exe()}" a "{zipFilePath}" "{srcDir}"'
        return command

    def create_unzip_command(self, zipFilePath, destinationPath):
        command = f'"{self.get_7z_exe()}" x "{zipFilePath}" -o"{destinationPath}" -y'
        return command

    def test(self, archivePath):
        try:
            subprocess.run([self.get_7z_exe(), 't', archivePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=True)
            return True
        except Exception as e:
            print("Error testing the archive:", e)
            return False

    def __str__(self):
        return '[class ZipTask]'

# This would be equivalent to creating an instance for export in JavaScript
zip_task_instance = ZipTask()