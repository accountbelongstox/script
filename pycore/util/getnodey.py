import hashlib
import random
import string
import time
import zipfile
from pycore.base.base import Base
import subprocess
import threading
import sys
import os
import platform
import urllib.parse
import re
from datetime import datetime
import tarfile
from urllib import request
import requests


class Zip(Base):
    def __init__(self):
        super().__init__()  # 调用父类的构造函数

        # 类属性
        self.callbacks = {}
        self.maxTasks = 10
        self.pendingTasks = []
        self.concurrentTasks = 0
        self.execCountTasks = 0
        self.execTaskEvent = None
        self.libraryDir = os.path.join(os.path.dirname(__file__), '../library')
        self.zipQueueTokens = []
        self.concurrent_tasks = 0
        self.exec_task_event = None
        # 初始化 zipQueueTokens 和 callbacks
        self.zip_que_tokens = []
        self.pending_tasks = []
        self.retry_count = 0
        self.retry_limit = 3  # 重试限制，根据需要调整

    #@staticmethod
    def get_md5(self, value):
        hash_md5 = hashlib.md5(value.encode())
        return hash_md5.hexdigest()

    def create_string(self, length=10):
        letters = string.ascii_lowercase #包含所有小写英文字母（从a到z）的字符串
        result = ''
        for _ in range(length):
            result += random.choice(letters)
        return result

    def create_id(self, value=None):
        if not value:
            value = self.create_string(128)
        return self.get_id(value)

    def get_id(self, value, pre=None):
        value = str(value)
        md5 = self.get_md5(value)
        _id = f'id{md5}'
        if pre:
            _id = pre + _id
        return _id

    def get_current_os(self):
        return platform.system().lower()

    def is_windows(self):
        return self.get_current_os() == 'windows'

    def get_7z_exe_name(self):
        exe_file = '7zz'
        if self.is_windows():
            exe_file = '7z.exe'
        return exe_file

    def get_7z_exe(self):
        folder = 'linux'
        exe_file = self.get_7z_exe_name()
        if self.is_windows():
            folder = 'windows'
        return os.path.join(self.library_dir, f'{folder}/{exe_file}')

    def mkdir_sync(self, directory_path):
        if not os.path.exists(directory_path):
            return self.mkdir(directory_path)

    def mkdir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def is_file_locked(self, filePath):
        if not os.path.exists(filePath):
            return False
        try:
            # 尝试以读写方式打开文件
            with open(filePath, 'r+') as f:
                pass
            return False
        except IOError as error:
            # 检查错误类型
            if error.errno == 13:
                return True
            elif error.errno == 11:
                return True
            else:
                return False

    def get_modification_time(self, fp):
        if not os.path.exists(fp):
            return 0
        try:
            mtime = os.path.getmtime(fp)
            return time.ctime(mtime)
        except Exception as error:
            print(f'Error getting modification time: {error}')
            return 0

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return -1
        try:
            file_size_in_bytes = os.path.getsize(file_path)
            return file_size_in_bytes
        except Exception as error:
            return -1

    def set_mode(self, mode):
        self.mode = mode

    def log(self, msg, event):
        if event:
            self.success(msg)

    def compress_directory(self, src_dir, out_dir, token, callback):

        src_abs_path = os.path.abspath(src_dir)
        out_abs_path = os.path.abspath(out_dir)

        if not os.path.exists(src_abs_path):
            return

        if not os.path.exists(out_abs_path):
            os.makedirs(out_abs_path)

        sub_directories = [entry for entry in os.listdir(src_abs_path)
                           if os.path.isdir(os.path.join(src_abs_path, entry)) and not entry.startswith('.')]
        for sub_dir_name in sub_directories:
            sub_dir_path = os.path.join(src_abs_path, sub_dir_name)

            self.put_zip_queue_task(sub_dir_path, out_dir, token, callback)

    def get_zip_path(self, src_dir, out_dir):
        src_dir_name = os.path.basename(src_dir)
        zip_file_name = f"{src_dir_name}.zip"
        zip_file_path = os.path.join(out_dir, zip_file_name)
        return zip_file_path

    def add_to_pending_tasks(self, command, callback=None):

        self.concurrent_tasks += 1

        def execute_command(command, callback):

            start_time = time.time()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Error executing command: {stderr.decode('utf-8')}")
            else:
                print(f"Command executed successfully: {stdout.decode('utf-8')}")
            if callback:
                callback(time.time() - start_time)

        thread = threading.Thread(target=execute_command, args=(command, callback))
        thread.start()

    def processes_count(self, process_name):
        normalized_process_name = process_name.lower()
        cmd = ''

        if sys.platform.startswith('win'):
            cmd = f'tasklist /fi "imagename eq {process_name}"'
        else:
            cmd = f'ps aux | grep {process_name}'

        try:
            stdout = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True, encoding='utf8').stdout
            count = stdout.lower().split('\n').count(normalized_process_name)
            if not sys.platform.startswith('win'):
                count -= 1
            return count
        except subprocess.CalledProcessError as err:
            print('Error executing command:', err)
            return 10000

    def a7z_processes_count(self):
        process_name = self.get_7z_exe_name()
        process_zip_count = self.processes_count(process_name)
        return process_zip_count

    def exec_task(self):
        if not self.execTaskEvent:
            print('Background compaction task started')
            self.execTaskEvent = threading.Timer(1, self.execTask)
            self.execTaskEvent.start()

            processZipCount = self.a7zProcessesCount()
            if processZipCount != 10000:
                self.concurrentTasks = processZipCount

            if self.concurrentTasks >= self.maxTasks:
                print(f'7zProcesse tasks is full. current tasks:{self.concurrentTasks}, waiting...')
            elif self.pendingTasks:
                taskObject = self.pendingTasks.pop(0)
                command = taskObject['command']
                isQueue = taskObject['isQueue']
                token = taskObject['token']
                zipPath = taskObject['zipPath']
                zipName = os.path.basename(zipPath)

                if not self.isFileLocked(zipPath):
                    print(f'Unziping {zipName}, background:{self.concurrentTasks}')
                    self.execCountTasks += 1
                    threading.Thread(target=self.addToPendingTasks, args=(command, token, zipPath, isQueue)).start()
                else:
                    self.pendingTasks.append(taskObject)
                    print(f'The file is in use, try again later, "{zipPath}"')
            else:
                if self.execCountTasks < 1:
                    self.execTaskEvent.cancel()
                    self.execTaskEvent = None
                    print('There is currently no compression task, end monitoring.')
                    self.execTaskQueueCallbak()
                else:
                    print(f'There are still {self.execCountTasks} compression tasks, waiting')

    def exec_task_queue_callback(self):
        for token in self.zip_que_tokens:
            self.exec_task_callback(token)

    def exec_task_callback(self, token):
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

    def put_unzip_task(self, src, out, callback):
        token = self.get_id(src)  # suppose we have this function to get id from src
        self.put_task(src, out, token, False, callback, False)

    def put_unzip_queue_task(self, src, out, callback):
        token = self.get_id(src)  # suppose we have this function to get id from src
        self.put_task(src, out, token, False, callback)

    def put_queue_callback(self, callback, token):
        if callback and token not in self.callbacks:
            if not token:
                token = self.create_id()  # suppose we have this function to create id
            self.zip_queue_tokens.append(token)
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': ''
            }

    def put_unzip_task_promise(self, zip_file_path, target_directory):
        if zip_file_path.endswith('.zip'):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(target_directory)
        elif zip_file_path.endswith('.tar') or zip_file_path.endswith('.tar.gz') or zip_file_path.endswith('.tgz'):
            with tarfile.open(zip_file_path, 'r:*') as tar_ref:
                tar_ref.extractall(target_directory)
        elif zip_file_path.endswith('.7z'):
            try:
                subprocess.check_call(['7z', 'x', zip_file_path, f'-o{target_directory}'])
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while extracting 7z archive: {e}")
                return False
            except OSError as e:
                print(f"An error occurred: 7z not found or other OS error: {e}")
                return False
        else:
            print(f"Unsupported file type for {zip_file_path}")
            return False
        return True


    def put_task(self, src, out, token, is_zip=True, callback=None, is_queue=True):
        if callback and not self.callbacks.get(token):
            self.callbacks[token] = {'callback': callback, 'usetime': 0, 'src': src}

        if is_queue:
            self.zipQueueTokens.append(token)

        zip_path = ""
        command = ""
        if is_zip:
            zip_path = self.get_zip_path(src, out)
            if os.path.exists(zip_path):
                if not self.mode:
                    return
                if self.mode.update:
                    src_mod_time = os.path.getmtime(src)
                    zip_path_mod_time = os.path.getmtime(zip_path)
                    diff_time = src_mod_time - zip_path_mod_time
                    if diff_time < 60:
                        return
                    os.unlink(zip_path)
                elif self.mode.override:
                    os.unlink(zip_path)
                else:
                    return

            zip_size = os.path.getsize(zip_path)
            if zip_size == 0:
                os.unlink(zip_size)

            command = self.create_zip_command(src, out)
        else:
            zip_path = src
            command = self.create_unzip_command(src, out)

        if not self.is_task(zip_path):
            zip_act = 'compression' if is_zip else 'unzip'
            zip_name = os.path.basename(zip_path)
            self.log(f"Add a {zip_act} {zip_name}, background:{self.concurrentTasks}", True)
            self.pendingTasks.append({'command': command, 'zipPath': zip_path, 'token': token, 'isQueue': is_queue})

        self.exec_task()

    def delete_task(self, zip_path):
        self.pending_tasks = [item for item in self.pending_tasks if item['zip_path'] != zip_path]

    def is_task(self, zip_path):
        return any(item['zip_path'] == zip_path for item in self.pending_tasks)

    def create_zip_command(self, src_dir, out_dir):
        src_dir_name = os.path.basename(src_dir)
        zip_file_name = f"{src_dir_name}.zip"
        zip_file_path = os.path.join(out_dir, zip_file_name)

        command = f'"{self.get_7z_exe()}" a "{zip_file_path}" "{src_dir}"'

        return command

    def create_unzip_command(self, zip_file_path, destination_path):
        command = f"{self.get_7z_exe()} x \"{zip_file_path}\" -o\"{destination_path}\" -y"
        return command

    def test(self, archive_path):
        get_7z_exe = lambda: "7z"

        try:
            subprocess.run(f'{get_7z_exe()} t "{archive_path}"', check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as error:
            print(f"Error testing the archive: {error}")
            return False


zip= Zip()


class Getnode(Base):
    def __init__(self, tmp_dir=None):
        super().__init__()

        self.tmp_dir_name = "nodes_autoinstaller"

        self.error = {}

        self.mirrors_url = "https://mirrors.tencent.com/npm/"

        self.node_dist_url = 'https://nodejs.org/dist/'

        self.node_dist_file = 'node_dist.html'

        self.retry_limit = 30

        self.retry_count = 0

        self.tmp_dir = tmp_dir

        self.version_number = ''

        self.node_install_dir = '/usr/node'

        self.down_url='https://nodejs.org/dist/v18.12.0/'
    def get_current_os(self):
        return platform.system()

    def is_windows(self):
        return self.get_current_os() == 'Windows'

    def is_linux(self):
        return self.get_current_os() == 'linux'

    def get_node_directory(self, n_path=None):
        current_os = self.get_current_os()
        tmp_dir = '/usr/nodes' if current_os != 'Windows' else 'D:/lang_compiler/nodes/'
        if n_path:
            tmp_dir = os.path.join(tmp_dir, n_path)
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir

    def get_local_dir(self, subpath=None):
        app_data_local_dir = os.getenv('LOCALAPPDATA') or os.path.join(os.getenv('APPDATA'), 'Local')

        if subpath:
            return os.path.join(app_data_local_dir, subpath)
        else:
            return app_data_local_dir

    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as error:
            print(f'Error reading file "{file_path}": {error}')
            return ''

    def get_temp_directory(self):
        current_os = self.get_current_os()
        tmp_dir = '/tmp/node' if current_os != 'Windows' else os.path.join(self.get_local_dir(), self.tmp_dir_name)
        self.mkdir(tmp_dir)
        return tmp_dir

    def get_download_directory(self, fpath=None):
        home_dir = os.path.expanduser('~')
        downloads_dir = os.path.join(home_dir, 'Downloads')
        current_os = self.get_current_os()
        tmp_dir = '/tmp/node/Downloads' if current_os != 'Windows' else os.path.join(downloads_dir, self.tmp_dir_name)
        self.mkdir(tmp_dir)
        if fpath:
            tmp_dir = os.path.join(tmp_dir, fpath)
        return tmp_dir

    def mkdir(self,dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as error:
            print(f'Error creating directory "{dir_path}": {error}')
            return False

    def download(self, down_url, down_name=None):
        download_dir = self.get_download_directory()
        if not down_name:
            down_name = down_url.split('/').pop()
        down_name = self.unescape_url(down_name)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        save_path = os.path.join(download_dir, down_name)

        self.down_file(down_url, save_path)

        return save_path

    def make_base_dir(self, directory_path):

        base_dir = os.path.dirname(directory_path)

        if base_dir and not os.path.exists(base_dir):
            os.makedirs(base_dir)

        return base_dir

    def down_file(self, down_url, dest):
        try:
            response = requests.get(down_url, stream=True)
            response.raise_for_status()
            with open(dest, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            if os.path.exists(dest):
                os.remove(dest)
        else:
            return dest

    def retry(self, down_url, dest):
        if self.retry_count < self.retry_limit:
            self.retry_count += 1
            print(f'Retry {self.retry_count} for file {dest}')
            return self.down_file(down_url, dest)
        else:
            print(f'Retry limit reached for file {dest}')
            raise Exception(f'Failed to download {dest}')

    def is_file(self, filename):
        if not filename or not isinstance(filename, str):
            return False
        if os.path.exists(filename):
            return os.path.isfile(filename)
        return False

    def compare_file_sizes(self, remote_url, local_path):
        if not self.is_file(local_path):
            return False
        try:
            remote_size = self.get_remote_file_size(remote_url)
            local_size = self.get_file_size(local_path)
            print(f"compare_file_sizes : url:{remote_url}, remoteSize:{remote_size}, localPath:{local_path}")
            return remote_size == local_size
        except Exception as err:
            print("An error occurred:", err)
            return False

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return -1
        try:
            return os.path.getsize(file_path)
        except Exception as error:
            print("An error occurred while getting file size:", error)
            return -1

    def unescape_url(self, url):
        return urllib.parse.unquote(url)

    def get_node_downloads(self):
        return {}

    def get_version(self):
        return float(platform.python_version())

    def get_version_full(self):
        return platform.python_version()

    def get_node_modules(self, app_path):
        return os.path.join(app_path, "node_modules")

    def extract_node_version(self, app_config):
        specified_node_version = app_config['package_json']['engines'][
            'node'] if 'package_json' in app_config and 'engines' in app_config['package_json'] and 'node' in \
                       app_config['package_json']['engines'] else None
        print(app_config['name'], specified_node_version)

        if specified_node_version:
            return [float(token)
                    for token in re.findall(r'\d+\.\d+', specified_node_version)
                    if token]
        else:
            return []

    def extract_versions_by_out(self, content):
        result = re.search(r'Expected version "([0-9 ||]+)"', content)
        return result.group(1).split(' || ') if result else None

    # 通过字符串提取错误
    def extract_errors_by_str(self, input_string):
        if input_string:
            errors = [line.strip() for line in input_string.split('\n') if 'error' in line]
            return errors if errors else None
        else:
            return None

    # 读取版本号
    def read_version_number(self):
        version_number = '18'
        return version_number

    def has_sudo(self):
        try:
            subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL)
            return True
        except subprocess.SubprocessError:
            return False

    def get_last_modified_time(self, file_path):
        try:
            stats = os.stat(self, file_path)
            last_modified_time = time.ctime(stats.st_mtime)
            return last_modified_time
        except Exception as error:
            print(f'Error getting last modified time for file "{file_path}":', error)
            return None

    def get_node_dist_html(self):
        node_dist_html_path = os.path.join(self.get_download_directory(), 'node_dist.html')
        redownload = False
        if self.is_file(node_dist_html_path):
            last_modified_time = self.get_last_modified_time(node_dist_html_path)
            if last_modified_time:
                diff_in_ms = int((datetime.now() - last_modified_time).total_seconds() * 1000)
                if diff_in_ms > (24 * 60 * 60 * 1000):
                    redownload = True
            else:
                redownload = True
        else:
            redownload = True

        if redownload:
            self.download_node_dist_html()

        return node_dist_html_path

    def get_local_versions_list(self):
        dist_html = self.get_node_dist_html()
        content = self.read_file(dist_html)

        version_pattern = re.compile(r'v\d+\.\d+\.\d+')
        versions_list = re.findall(version_pattern, content)

        return versions_list
        # if versions_list:
        #     latest_versions_list = self.get_latest_version_from_list(versions_list)
        #     major_number = self.read_version_number()
        #     try:
        #         major_number = int(major_number)
        #         resolved_value = self.get_latest_version_by_major(major_number, latest_versions_list)
        #         print(resolved_value)
        #         version = resolved_value
        #
        #     except ValueError:
        #         print('ERROR')
        #
        #
        # else:
        #     print('No versions found in the file.')

    def get_latest_version_from_list(self, versions_list=None):
        if not versions_list:
            versions_list = self.get_local_versions_list()

        latest_versions_map = {}

        for version in versions_list:
            version_number = version.replace('v', '')
            major, minor, patch = map(int, version_number.split('.'))
            current_major = latest_versions_map.get(major)

            if not current_major or minor > current_major['minor'] or (
                    minor == current_major['minor'] and patch > current_major['patch']):
                latest_versions_map[major] = {'minor': minor, 'patch': patch, 'version': version}

        latest_versions = [v['version'] for v in latest_versions_map.values()]
        return latest_versions

    def download_node_dist_html(self):
        self.download(self.node_dist_url, self.node_dist_file)

    def get_latest_version_by_number(self, version_number, versions_list):
        max_version = None

        for version in versions_list:
            if version.startswith(version_number):
                if not max_version or self.compare_versions(version, max_version) > 0:
                    max_version = version

        return max_version

    def get_latest_version_by_major(self, major_number, latest_versions_list):
        for version in latest_versions_list:
            version_number = version.replace('v', '')
            major, _, _ = map(int, version_number.split('.'))
            if major == major_number:
                return version

        return None

    def compare_versions(self, version_a, version_b):
        parts_a = list(map(int, version_a.split('.')))
        parts_b = list(map(int, version_b.split('.')))

        if len(parts_a) < len(parts_b):
            parts_a += [0] * (len(parts_b) - len(parts_a))
        elif len(parts_b) < len(parts_a):
            parts_b += [0] * (len(parts_a) - len(parts_b))

        for part_a, part_b in zip(parts_a, parts_b):
            if part_a != part_b:
                return part_a - part_b

        return 0

    def install_node(self, version):
        node_install_dir = "/usr/node"
        node_dir = os.path.join(node_install_dir, version)

        if os.path.exists(node_dir):
            print(f"Node version {version} is already installed at {node_dir}")
            return

        try:
            os.makedirs(node_install_dir, exist_ok=True)
            os.makedirs(node_dir, exist_ok=True)

            download_url = f"https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.gz"
            download_path = os.path.join(node_install_dir, f"node-{version}-linux-x64.tar.gz")

            print(f"Downloading Node.js {version} from {download_url}...")
            urllib.request.urlretrieve(download_url, download_path)
            print(f"Node.js {version} downloaded successfully.")

            print(f"Extracting Node.js {version} to {node_dir}...")
            with tarfile.open(download_path, "r:gz") as tar:
                tar.extractall(path=node_dir)
            print(f"Node.js {version} extracted successfully.")

            print(f"Node.js {version} installed successfully at {node_dir}")
        except Exception as e:
            print(f"Error installing Node.js {version}: {e}")

    def extract_file(self, src, dest_dir):
        try:
            subprocess.check_call(['tar', '-xzf', src, '-C', dest_dir])
            return True
        except subprocess.CalledProcessError as e:
            print(e)
            return False

    def get_node_executable(self):
        return 'node' if self.is_linux() else 'node.exe'

    def get_npm_executable(self):
        return 'npm' if self.is_linux() else 'npm.cmd'

    def get_npx_executable(self):
        return 'npx' if self.is_linux() else 'npx.cmd'

    def get_yarn_executable(self):
        return 'yarn' if self.is_linux() else 'yarn.cmd'

    def get_pm2_executable(self):
        return 'pm2' if self.is_linux() else 'pm2.cmd'

    def get_file_name_without_extension(self, file_name):
        last_dot_index = file_name.rfind('.')
        if last_dot_index != -1:
            return file_name[:last_dot_index]
        else:
            return file_name

    def find_node_version_by_platform(self, node_href_versions, version):
        match_roles = ['v{}.'.format(version), 'win', 'x64', '.7z']
        if self.is_linux():
            match_roles = ['v{}.'.format(version), 'linux', 'x64', '.gz']
        match_roles_copy = match_roles[:]
        while match_roles_copy:
            for ver in node_href_versions:
                if all(role in ver for role in match_roles_copy):
                    return ver
            match_roles_copy.pop()
        return None

    def extract_node_href_versions(self, node_html_content):
        lines = node_html_content.split('\n')
        href_values = []
        for line in lines:
            href_match = re.search('href="(.*?)"', line)
            if href_match:
                href_values.append(href_match.group(1))

        return href_values

    def install_node_and_yarn(self, node_path, npm_path, node_install_file_dir, mirrors_url):

        def is_linux():
            return sys.platform.startswith('linux')

        def has_sudo():
            try:
                subprocess.check_output(['sudo', '-v'], stderr=subprocess.STDOUT)
                return True
            except subprocess.CalledProcessError:
                return False

        node_version = subprocess.getoutput(f'{node_path} -v')
        npm_version = subprocess.getoutput(f'{npm_path} -v')
        print(f'Node.js version: {node_version}')
        print(f'npm version: {npm_version}')

        cmds = [
            f'{npm_path} config set prefix "{node_install_file_dir}"',
            f'{npm_path} config set registry {mirrors_url}',
            f'{npm_path} install -g yarn',
            f'{npm_path} install -g pm2'
        ]

        for cmd in cmds:
            if is_linux() and has_sudo():
                cmd = 'sudo ' + cmd
            print(cmd)
            output = subprocess.getoutput(cmd)
            print(output)

        print('Node.js installation completed.')

    def get_node_by_version(self, version="18"):
        node_dir = self.get_node_directory()
        node_href_versions = os.listdir(node_dir)
        matching_version = self.find_node_version_by_platform(node_href_versions, version)
        node_exe = self.get_node_executable()

        if not self.is_file(os.path.join(self.get_node_directory(matching_version), node_exe)):
            latest_version_from_list = self.get_latest_version_from_list()
            matched_version = next((version_string for version_string in latest_version_from_list if
                                    version_string.startswith(f"v{version}.")), None)
            if matched_version:
                node_detail_html = f"{matched_version}.html"
                node_detail_download_file = self.get_download_directory(node_detail_html)
                if not self.is_file(node_detail_download_file):
                    node_detail_url = f"{self.node_dist_url}{matched_version}/"
                    node_detail_download_file = self.download(node_detail_url, node_detail_html)
                node_html_content = self.read_file(node_detail_download_file)
                node_href_versions = self.extract_node_href_versions(node_html_content)
                matching_version = self.find_node_version_by_platform(node_href_versions, version)
                if matching_version:
                    matching_version_download_file = self.get_download_directory(matching_version)
                    if not self.is_file(matching_version_download_file):
                        node_download_url = f"{self.node_dist_url}{matched_version}/{matching_version}"
                        matching_version_download_file = self.download(node_download_url, matching_version)
                        matching_version = self.get_file_name_without_extension(matching_version)

                    zip.put_unzip_task_promise(matching_version_download_file, node_dir)

        if matching_version:
            return os.path.join(self.get_node_directory(matching_version), node_exe)
        return None

    def getNpmByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
        yarnExec = os.path.join(nodeInstallPath, self.getYarnExecutable())
        print(f'yarnExec: {yarnExec}')
        if not self.isFile(yarnExec):
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return npmExec

    def getNpxByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        npxExec = os.path.join(nodeInstallPath, self.getNpxExecutable())
        return npxExec

    def getYarnByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        yarnExec = os.path.join(nodeInstallPath, self.getYarnExecutable())
        if not self.isFile(yarnExec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return yarnExec

    def getPm2ByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        pm2Exec = os.path.join(nodeInstallPath, self.getPm2Executable())
        if not self.isFile(pm2Exec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return pm2Exec

    def __str__(self):
        return '[class Getnode]'



getnode_instance = Getnode()

