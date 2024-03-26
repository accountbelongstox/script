import os
import hashlib
import random
import string
import time
import asyncio
from base import Base
import zipfile
import subprocess
import threading
import sys
from pathlib import Path
import platform
import aiohttp
from aiohttp import ClientError
import aiofiles
import requests
import os
import platform
import urllib.parse
import re
from datetime import datetime
from get_temp_directory import download_node_dist_html


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
        """获取字符串的 MD5 散列值"""
        hash_md5 = hashlib.md5(value.encode())
        return hash_md5.hexdigest()

    def createString(self, length=10):
        """生成指定长度的随机字符串"""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

    def create_id(self, value=None):
        """根据给定值创建唯一 ID"""
        if not value:
            value = self.createString(128)
        return self.get_id(value)

    def get_id(self, value, pre=None):
        """根据给定值和可选前缀创建唯一 ID"""
        value = str(value)
        md5 = self.get_md5(value)
        _id = f'id{md5}'
        if pre:
            _id = pre + _id
        return _id

    def getCurrentOS(self):
        """获取当前操作系统类型"""
        return os.platform()

    def isWindows(self):
        """判断当前操作系统是否为 Windows"""
        return self.getCurrentOS() == 'win32'

    def get7zExeName(self):
        """获取 7z 压缩工具的可执行文件名称"""
        exeFile = '7zz'
        if self.isWindows():
            exeFile = '7z.exe'
        return exeFile

    def get7zExe(self):
        """获取 7z 压缩工具的完整路径"""
        folder = 'linux'
        exeFile = self.get7zExeName()
        if self.isWindows():
            folder = 'win32'
        return os.path.join(self.libraryDir, f'{folder}/{exeFile}')

    def mkdirSync(self, directoryPath):
        """同步创建目录"""
        return self.mkdir(directoryPath)

    def mkdir(self, dirPath):
        """创建目录"""
        if not os.path.exists(dirPath):
            os.makedirs(dirPath, exist_ok=True)


    def is_file_locked(filePath):
        """检查文件是否被锁定"""
        if not os.path.exists(filePath):
            return False
        try:
            # 尝试以读写方式打开文件
            with open(filePath, 'r+') as f:
                pass  # 打开并关闭文件
            return False  # 如果能成功打开，则文件未被锁定
        except IOError as error:
            # 检查错误类型
            if error.errno == 13:  # EACCES：权限不足
                return True
            elif error.errno == 11:  # EAGAIN：文件被其他进程占用
                return True
            else:
                return False  # 其他错误，认为文件未被锁定

    def get_modification_time(fp):
        # 检查文件或路径是否存在
        if not os.path.exists(fp):
            return 0
        try:
            # 使用os模块获取文件的最后修改时间（以时间戳的形式）
            mtime = os.path.getmtime(fp)
            # 转换时间戳为实际时间
            return time.ctime(mtime)
        except Exception as error:
            # 打印异常信息
            print(f'Error getting modification time: {error}')
            return 0

    def get_file_size(self, file_path):
        # 检查文件或路径是否存在
        if not os.path.exists(file_path):
            return -1
        try:
            # 使用os模块获取文件大小，单位是字节
            file_size_in_bytes = os.path.getsize(file_path)
            return file_size_in_bytes
        except Exception as error:
            return -1

    # 设置模式
    def set_mode(self, mode):
        self.mode = mode

    # 记录消息
    def log(self, msg, event):
        if event:
            self.success(msg)

    # 在这里定义你的成功方法
    def success(self, msg):
        print(msg)  # 这里对成功信息的处理方式是打印出来，可以根据实际需要修改

    async def compress_directory(self, src_dir, out_dir, token, callback):
        # 解析绝对路径
        src_abs_path = os.path.abspath(src_dir)
        out_abs_path = os.path.abspath(out_dir)
        # 检查源目录是否存在
        if not os.path.exists(src_abs_path):
            return
        # 检查目标目录是否存在，如果不存在则创建
        if not os.path.exists(out_abs_path):
            os.makedirs(out_abs_path)
        # 获取源目录下的子目录
        sub_directories = [entry for entry in os.listdir(src_abs_path)
                           if os.path.isdir(os.path.join(src_abs_path, entry)) and not entry.startswith('.')]
        for sub_dir_name in sub_directories:
            sub_dir_path = os.path.join(src_abs_path, sub_dir_name)
            # 将zip任务添加到队列（假设put_zip_queue_task是异步方法）
            await self.put_zip_queue_task(sub_dir_path, out_dir, token, callback)

    # 在这里定义你的put_zip_queue_task异步方法
    async def put_zip_queue_task(self, sub_dir_path, out_dir, token, callback):
        # 实现压缩操作，可能涉及异步调用第三方库或自己的其他异步方法
        # 这里保留了一个示例方法调用
        pass

    def get_zip_path(src_dir, out_dir):
        """获取压缩文件路径"""
        src_dir_name = os.path.basename(src_dir)  # 获取源目录的名称
        zip_file_name = f"{src_dir_name}.zip"  # 压缩文件的名称
        zip_file_path = os.path.join(out_dir, zip_file_name)  # 构建压缩文件的完整路径
        return zip_file_path

    def add_to_pending_tasks(self, command, callback=None):
        """将命令添加到待处理任务中"""
        self.concurrent_tasks += 1  # 增加并发任务计数

        def execute_command(command, callback):
            """执行命令"""
            start_time = time.time()  # 记录命令开始执行的时间
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process.communicate()  # 执行命令并获取标准输出和标准错误
            if process.returncode != 0:
                print(f"Error executing command: {stderr.decode('utf-8')}")
            else:
                print(f"Command executed successfully: {stdout.decode('utf-8')}")
            if callback:
                callback(time.time() - start_time)  # 调用回调函数，并传入命令执行时间

        thread = threading.Thread(target=execute_command, args=(command, callback))  # 创建线程执行命令
        thread.start()  # 启动线程

    def processes_count(process_name):
        normalized_process_name = process_name.lower()
        cmd = ''

        # 检测操作系统类型，并根据操作系统构建相应的命令
        if sys.platform.startswith('win'):
            cmd = f'tasklist /fi "imagename eq {process_name}"'
        else:
            cmd = f'ps aux | grep {process_name}'

        try:
            # 执行命令并获取输出结果
            stdout = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True, encoding='utf8').stdout
            # 在Windows中，tasklist命令已经包含了应用名的匹配输出，在非Windows系统中的grep需要去掉最后一行因为它会包含grep本身
            count = stdout.lower().split('\n').count(normalized_process_name)
            if not sys.platform.startswith('win'):
                count -= 1
            return count
        except subprocess.CalledProcessError as err:
            # 如果命令执行出现错误，打印错误信息
            print('Error executing command:', err)
            return 10000

    async def exec_task(self):
        # 如果当前没有执行的任务事件，则开始执行
        if not self.exec_task_event:
            await self.log('Background compaction task started', True)
            self.exec_task_event = True

            while self.exec_task_event:
                process_zip_count = await self.a7z_processes_count()
                if process_zip_count != 10000:
                    self.concurrent_tasks = process_zip_count

                if self.concurrent_tasks >= self.max_tasks:
                    await self.log(f'7zProcesse tasks is full. current tasks:{self.concurrent_tasks}, waiting...')
                elif len(self.pending_tasks) > 0:
                    task_object = self.pending_tasks.pop(0)  # 类似于 JS 中的 shift
                    command = task_object['command']
                    is_queue = task_object['is_queue']
                    token = task_object['token']

                    zip_path = task_object['zip_path']
                    zip_name = os.path.basename(zip_path)  # 使用 os.path.basename 代替 path.basename

                    if not await self.is_file_locked(zip_path):
                        await self.log(f'Unzipping {zip_name}, background:{self.concurrent_tasks}', True)
                        self.exec_count_tasks += 1
                        await self.add_to_pending_tasks(command, token, is_queue)
                    else:
                        self.pending_tasks.append(task_object)
                        await self.log(f'The file is in use, try again later, "{zip_path}"')
                else:
                    if self.exec_count_tasks < 1:
                        self.exec_task_event = False
                        await self.log('There is currently no compression task, end monitoring.')
                        await self.exec_task_queue_callback()
                    else:
                        await self.log(f'There are still {self.exec_count_tasks} compression tasks, waiting')

                await asyncio.sleep(1)  # 暂停一秒钟，然后继续循环

    def exec_task_queue_callback(self):
        # 遍历 zipQueTokens 中的所有 tokens
        for token in self.zip_que_tokens:
            self.exec_task_callback(token)

    def exec_task_callback(self, token):
        # 检查 callbacks 中是否存在给定的 token
        if token in self.callbacks:
            # 从 callbacks 中获取 callback 和 usetime
            callback = self.callbacks[token]['callback']
            usetime = self.callbacks[token]['usetime']
            src = self.callbacks[token]['src']

            # 从 callbacks 中移除当前的 token
            del self.callbacks[token]

            # 如果 callback 存在，则调用它
            if callback:
                callback(usetime, src)

    def put_zip_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback, False)

    # 用于放置一个等待执行的zip任务
    def put_zip_queue_task(self, src, out, token, callback):
        self.put_task(src, out, token, True, callback)

    # 用于放置一个解压的任务
    def put_unzip_task(self, src, out, callback):
        token = self.get_id(src)  # suppose we have this function to get id from src
        self.put_task(src, out, token, False, callback, False)

    # 用于放置一个等待解压的任务
    def put_unzip_queue_task(self, src, out, callback):
        token = self.get_id(src)  # suppose we have this function to get id from src
        self.put_task(src, out, token, False, callback)

    # 设置等待队列的回调
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

    # 每种任务类型的执行都需要现实putTask这个函数
    def put_task(self, src, out, token, is_zip, callback, queue=None):
        # You need to implement this function based on your requirements
        pass

    async def put_unzip_task_promise(self, zip_file_path, target_directory):
        # 使用event loop来等待异步任务的完成
        loop = asyncio.get_running_loop()

        # 创建一个future对象，它将在稍后运行的put_unzip_task中被解析
        future = loop.create_future()

        # 定义完成任务时调用的回调函数
        def callback(error):
            if error:
                future.set_exception(error)  # 如果有错误，设置future为异常状态
            else:
                future.set_result(None)  # 如果成功，设置future的结果

        # 这里假设put_unzip_task是一个已经定义好的函数
        self.put_unzip_task(zip_file_path, target_directory, callback)

        try:
            # 等待future完成
            await future
        except Exception as error:
            # 处理异常
            print(f"An error occurred: {error}")
            # 处理完毕后，可以选择抛出此异常或者其他方式
            raise

    def put_task(self, src, out, token, is_zip=True, callback=None, is_queue=True):
        # 如果有回调并且还没有相同的token的回调，则添加回调
        if callback and token not in self.callbacks:
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': src
            }

        # 如果是队列任务，则添加到队列
        if is_queue:
            self.zip_queue_tokens.append(token)

        zip_path = ""
        command = ""

        # 根据是否是压缩任务来执行不同的操作
        if is_zip:
            zip_path = self.get_zip_path(src, out)  # 假设有这个函数来创建zip文件的路径
            # 检查文件是否存在
            if os.path.exists(zip_path):
                # 根据不同的模式（update或override）来处理文件
                # 此处省略了mode的相关代码，标准是用户应该根据自己的逻辑去实现这个部分
                pass

            # 再次检查文件是否存在且大小为0，如果是，则删除它
            if os.path.isfile(zip_path) and os.path.getsize(zip_path) == 0:
                os.remove(zip_path)

            command = self.create_zip_command(src, out)  # 假设有这个函数来创建压缩命令
        else:
            zip_path = src
            command = self.create_unzip_command(src, out)  # 假设有这个函数来创建解压缩命令

        # 检查任务是否已经在任务列表中
        if not self.is_task(zip_path):  # 假设有这个函数来检查任务是否存在
            zip_act = 'compression' if is_zip else 'unzip'
            zip_name = os.path.basename(zip_path)
            print(f"Add a {zip_act} {zip_name}, background: {len(self.pending_tasks)}")  # 日志的例子

            # 添加到待执行任务列表
            self.pending_tasks.append({
                'command': command,
                'zip_path': zip_path,
                'token': token,
                'is_queue': is_queue
            })

        # 执行任务
        self.exec_task()  # 假设有这个函数来执行任务

    def delete_task(self, zip_path):
        # 在pending_tasks中找到所有不匹配zipPath的项目，即移除匹配的项目
        self.pending_tasks = [item for item in self.pending_tasks if item['zip_path'] != zip_path]

    def is_task(self, zip_path):
        # 检查是否有任何任务的zipPath与给定的zipPath匹配
        return any(item['zip_path'] == zip_path for item in self.pending_tasks)

    def create_zip_command(self, src_dir, out_dir):
        src_dir_name = os.path.basename(src_dir)  # 获取源目录的基础名称
        zip_file_name = f"{src_dir_name}.zip"  # 创建zip文件名
        zip_file_path = os.path.join(out_dir, zip_file_name)  # 创建zip文件的完整路径

        # 注意：在Python中创建字符串时，不需要像JavaScript那样使用 "+" 连接，
        # 可以使用 f-string 来更方便的插入变量值。
        command = f'"{self.get_7z_exe()}" a "{zip_file_path}" "{src_dir}"'  # 创建命令

        return command

    def create_unzip_command(self, zip_file_path, destination_path):
        # Command template for extracting a zip file with 7zip
        command = f'"{self.get_7z_exe()}" x "{zip_file_path}" -o"{destination_path}" -y'
        return command


    def test(self, archive_path):
        try:
            # Run the 7zip test command on the archive and capture the output
            subprocess.run([self.get_7z_exe(), 't', archive_path],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as error:
            # Catch the error, log it, and return False
            print(f"Error testing the archive: {error}")
            return False

    # 假定这是一个获取7zip可执行文件路径的方法，需要你根据你的应用环境进行实现
    def get_7z_exe(self):
    # 你需要根据实际情况来实现这个方法
        pass

zip = Zip()# 创建 Zip 类的对象实例

class Getnode(Base):
    def __init__(self, tmp_dir=''):
        # 调用基类的构造方法
        super().__init__()

        # 临时目录的名称，用于节点自动安装程序
        self.tmp_dir_name = "nodes_autoinstaller"

        # 错误信息字典，用于存储潜在错误
        self.error = {}

        # 腾讯镜像的URL，用于下载npm包
        self.mirrors_url = "https://mirrors.tencent.com/npm/"

        # Node.js官方分发URL
        self.node_dist_url = 'https://nodejs.org/dist/'

        # 保存Node.js分发页面的HTML文件名
        self.node_dist_file = 'node_dist.html'

        # 重试次数限制
        self.retry_limit = 30

        # 当前重试计数
        self.retry_count = 0

        # 如果提供了tmp_dir参数，则使用该参数；否则，默认为空字符串
        self.tmp_dir = tmp_dir

        # 版本号初始化为空字符串
        self.version_number = ''

        # 设置默认的node安装目录
        self.node_install_dir = '/usr/node'

    def get_current_os(self):
        """
        获取当前的操作系统类型。
        返回值是小写形式的字符串，常见的值有 'linux'、'win32'、'darwin' (对应MacOS) 等。
        """
        return platform.system().lower()

    def is_windows(self):
        """
        判断当前的操作系统是否为Windows。
        返回类型：布尔值
        """
        return self.get_current_os() == 'windows'

    def is_linux(self):
        """
        判断当前的操作系统是否为Linux。
        返回类型：布尔值
        """
        return self.get_current_os() == 'linux'

    def get_node_directory(self, n_path=None):
        """
        根据提供的路径，生成并返回完整的node目录路径。
        如果当前操作系统为Windows，根节点目录会被设置为 `D:/lang_compiler/nodes`
        否则，根节点目录会被设置为 `/usr/nodes`
        如果提供了n_path参数，它会被接到根节点目录的路径后面。

        :param n_path: 一个相对路径的字符串。默认为None。
        :return: 一个字符串，表示完整的node目录路径。
        """
        current_os = platform.system().lower()
        tmp_dir = '/usr/nodes' if current_os != 'windows' else 'D:/lang_compiler/nodes'
        if n_path:
            tmp_dir = os.path.join(tmp_dir, n_path)
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir

    def get_local_dir(self, subpath=None):
        # 获取本地应用程序数据目录
        app_data_local_dir = os.getenv('LOCALAPPDATA') or os.path.join(os.getenv('APPDATA'), 'Local')

        if subpath:
            # 如果有子路径，则返回子路径的完整路径
            return os.path.join(app_data_local_dir, subpath)
        else:
            # 如果没有子路径，则返回本地应用程序数据目录的路径
            return app_data_local_dir

    def read_file(self, file_path):
        """
        读取指定路径的文件内容。
        如果文件读取成功，返回其内容；如果发生错误，则打印出错误信息，并返回空字符串。

        :param file_path: 要读取的文件的路径。
        :return: 成功时返回文件内容字符串，出错时返回空字符串。
        """
        try:
            # 尝试打开文件并读取内容，使用'utf-8'编码
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as error:
            # 如果出现错误，打印错误信息
            print(f'Error reading file "{file_path}": {error}')
            # 出错时返回空字符串
            return ''

    tmp_dir_name = 'some_temp_dir'  # 请提供具体的临时目录名

    def get_current_os(self):
        """
        获取当前操作系统的名称。

        :return: 当前操作系统的名称，如 'linux', 'win32', 'darwin'。
        """
        return sys.platform

    def mkdir(self, dir_path):
        """
        创建一个新目录。

        如果目录已存在，那么此函数不执行任何操作；否则，会创建指定的目录。
        此函数会创建所有在dirPath中，但还不存在的父目录，类似于运行“mkdir -p dirPath”。

        :param dir_path: 要创建的目录的路径。
        """
        os.makedirs(dir_path, exist_ok=True)

    def get_temp_directory(self):
        """
        获取临时目录的路径。

        如果当前的操作系统是Windows，那么会获取本地目录加上tmpDirName的路径；
        否则，获取的是'/tmp/node'。

        此函数会确保所返回的目录存在（如果需要的话，会创建）。

        :return: 临时目录的路径。
        """
        current_os = self.get_current_os()
        temp_dir = '/tmp/node' if current_os != 'win32' else os.path.join(self.get_local_dir(), self.tmp_dir_name)
        self.mkdir(temp_dir)
        return temp_dir

    def get_download_directory(self, fpath=None):
        """
        获取下载目录的路径。

        如果当前的操作系统是Windows，那么会获取用户的home目录的下的Downloads目录加上tmpDirName的路径；
        否则，获取的是'/tmp/node/Downloads'。

        此函数会确保所返回的目录存在（如果需要的话，会创建）。

        如果提供了fpath参数，那么它将被添加到所得目录的路径末尾。

        :param fpath: 可选的参数，用于在所得目录的路径末尾添加附加的路径。
        :return: 下载目录的路径。
        """
        home_dir = os.path.expanduser('~')
        downloads_dir = os.path.join(home_dir, 'Downloads')
        current_os = self.get_current_os()

        tmp_dir = '/tmp/node/Downloads' if current_os != 'win32' else os.path.join(downloads_dir, self.tmp_dir_name)
        self.mkdir(tmp_dir)

        return os.path.join(tmp_dir, fpath) if fpath else tmp_dir

    def unescape_url(self, url):
        """
        清理URL编码。

        :param url: 编码后的URL字符串。
        :return: 清理后的URL字符串。
        """
        from urllib.parse import unquote
        return unquote(url)

    async def down_file(self, url, save_path):
        """
        异步下载文件。

        :param url: 要下载文件的URL。
        :param save_path: 文件保存在本地的路径。
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

    async def download(self, down_url, down_name=None):
        """
        异步下载指定文件。

        :param down_url: 文件的下载URL。
        :param down_name: 下载后保存的文件名。如果未提供，则从URL中提取。
        :return: 文件本地保存路径。
        """
        download_dir = self.get_download_directory()  # 假设get_download_directory方法已经定义
        if not down_name:
            down_name = down_url.split('/').pop()
        down_name = self.unescape_url(down_name)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        save_path = os.path.join(download_dir, down_name)

        await self.down_file(down_url, save_path)  # 假设down_file方法已经定义

        return save_path

    def make_base_dir(self, directory_path):
        """
        根据给定的文件路径创建其所在的基础目录。

        :param directory_path: 完整的文件路径或目录路径。
        :return: 创建目录的结果。
        """
        # 使用 os.path.dirname 获取文件所在的目录路径
        base_dir = os.path.dirname(directory_path)

        # 如果路径不为空则创建目录
        if base_dir and not os.path.exists(base_dir):
            os.makedirs(base_dir)

        return base_dir

    async def make_base_dir(self, path):
        """
        异步创建给定路径的基础目录。
        """
        base_dir = os.path.dirname(path)
        if base_dir and not os.path.exists(base_dir):
            os.makedirs(base_dir)

    async def down_file(self, down_url, dest):
        """
        异步下载文件，如果下载失败则重试。
        """
        await self.make_base_dir(dest)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(down_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(dest, mode='wb') as f:
                            await f.write(await response.read())
                        return dest
                    else:
                        await self.retry(down_url, dest)
            except ClientError as error:
                await self.retry(down_url, dest)

    async def retry(self, down_url, dest):
        """
        重试下载，如果失败次数少于重试限制则递归重试，否则抛出异常。
        """
        if self.retry_count < self.retry_limit:
            self.retry_count += 1
            print(f'Retry {self.retry_count} for file {dest}')
            return await self.down_file(down_url, dest)
        else:
            print(f'Retry limit reached for file {dest}')
            raise Exception(f'Failed to download {dest}')

    def is_file(filename):
        """
        检查指定的文件名是否为文件。

        :param filename: 文件的路径。
        :return: 如果是文件则返回True，否则返回False。
        """
        # 检查filename参数是否为空或者不是字符串类型。
        if not filename or not isinstance(filename, str):
            return False

        # 检查文件是否存在。
        return os.path.exists(filename) and os.path.isfile(filename)

    # 然后是比较文件大小的异步函数
    async def compare_file_sizes(remote_url, local_path):
        """
        异步比较远程文件和本地文件的大小。

        :param remote_url: 远程文件的URL。
        :param local_path: 本地文件的路径。
        :return: 如果文件大小相同则返回True，否则返回False。
        """
        # 使用is_file函数检查本地文件是否存在
        if not is_file(local_path):
            return False

        try:
            # 获取远程文件的大小
            response = requests.head(remote_url)
            remote_size = int(response.headers.get('Content-Length', 0))

            # 获取本地文件的大小
            local_size = get_file_size(local_path)

            print(f"compareFileSizes : url:{remote_url}, remoteSize:{remote_size}, localPath:{local_path}")
            return remote_size == local_size
        except Exception as err:
            print(f"发生错误: {err}")
            return False

    # 最后是获取文件大小的函数
    def get_file_size(file_path):
        """
        获取指定文件路径的文件大小。

        :param file_path: 文件的路径。
        :return: 文件的大小（以字节为单位），如果获取失败则返回-1。
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return -1

        try:
            # 获取文件的大小
            return os.path.getsize(file_path)
        except Exception as error:
            # 发生错误时返回-1
            return -1

    def unescape_url(url):
        """
        根据给定的URL计算其未转义的形式。

        :param url: 需要解码的URL。
        :return: 已解码的URL。
        """
        return urllib.parse.unquote(url)

    # 取得下载的节点，这个函数目前并不做任何操作，所以在Python中，它只是一个占位函数。
    def get_node_downloads(self):
        """
        返回一个空字典。JavaScript中的原始函数不做任何操作，所以在Python中也是如此。

        :return: 一个空字典
        """
        return {}

    # 取得Python的版本
    def get_version(self):
        """
        返回Python版本的浮点数表示形式。

        :return: Python的版本号，表示为浮点数。
        """
        return float(platform.python_version())

    # 取得Python的详细版本
    def get_version_full(self):
        """
        返回Python版本的完整字符串表示形式。

        :return: 一个包含Python版本详细信息的字符串。
        """
        return platform.python_version()

    # 取得节点模块路径
    def get_node_modules(app_path):
        """
        返回给定应用路径下的"node_modules"目录的完整路径。

        :param app_path: 应用的路径。
        :return: "node_modules"目录的完整路径。
        """
        return os.path.join(app_path, "node_modules")

    def extract_node_version(app_config):
        """
        从应用配置的package_json中提取指定的node版本。

        :param app_config: 包含应用配置信息的字典。
        :return: 包含提取的版本号的列表，如果没有找到则为空列表。
        """
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

    # 通过输出内容提取版本
    def extract_versions_by_out(content):
        """
        根据给定的内容提取版本信息。

        :param content: 用于提取版本信息的字符串。
        :return: 一个包含提取的版本的列表，如果没有找到匹配项则返回None。
        """
        result = re.search(r'Expected version "([0-9 ||]+)"', content)
        return result.group(1).split(' || ') if result else None

    # 通过字符串提取错误
    def extract_errors_by_str(input_string):
        """
        从给定的字符串中提取错误信息。

        :param input_string: 用于提取错误信息的字符串。
        :return: 一个包含提取的错误信息的列表，如果没有找到匹配项则返回None。
        """
        if input_string:
            errors = [line.strip() for line in input_string.split('\n') if 'error' in line]
            return errors if errors else None
        else:
            return None

    # 读取版本号
    def read_version_number(self):
        """
        从用户输入中读取版本号。

        :return: 用户输入的版本号。
        """
        version_number = input('Enter the version number: ')
        return version_number

    def has_sudo(self):
        """
        检查当前用户是否有sudo权限。

        :return: 如果用户有sudo权限则返回True，否则返回False。
        """
        try:
            subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL)
            return True
        except subprocess.SubprocessError:
            return False

    # 获取文件的最后修改时间
    def get_last_modified_time(file_path):
        """
        获取指定文件的最后修改时间。

        :param file_path: 文件的路径。
        :return: 文件的最后修改时间，如果获取失败则返回None。
        """
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime)
        except OSError as error:
            print(f"获取文件 '{file_path}' 的最后修改时间时出错:", error)
            return None

    async def get_node_dist_html(download_dir):
        """
        在给定的下载目录中查找node_dist.html文件，并根据需要下载新的版本。

        :param download_dir: 文件的下载目录。
        :return: 'node_dist.html'文件的完整路径。
        """
        node_dist_html_path = os.path.join(download_dir, 'node_dist.html')

        # 初始条件，假设我们不需要重新下载文件
        redownload = False

        # 如果文件存在于给定的路径中
        if os.path.isfile(node_dist_html_path):
            last_modified_time = get_last_modified_time(node_dist_html_path)

            if last_modified_time is not None:
                # 计算距文件最后修改的时间经过了多久
                diff_in_seconds = (datetime.datetime.now() - last_modified_time).total_seconds()

                # 如果超过24小时，则需要重新下载
                if diff_in_seconds > (24 * 60 * 60):
                    redownload = True
            else:
                redownload = True
        else:
            redownload = True

        # 如果需要重新下载
        if redownload:
            await download_node_dist_html(node_dist_html_path)

        return node_dist_html_path

    async def get_local_versions_list(download_dir):
        """
        在node_dist.html文件中提取版本列表。

        :param download_dir: 文件的下载目录。
        :return: 一个包含找到的版本的列表。
        """
        dist_html = await get_node_dist_html(download_dir)

        # 读取文件内容
        with open(dist_html, 'r') as file:
            content = file.read()

        # 使用正则表达式匹配版本模式
        version_pattern = re.compile(r'\bv(\d+\.\d+)\.\d+\b')
        versions_list = version_pattern.findall(content)

        if versions_list:
            # 得到最新的版本列表
            latest_versions_list = await get_latest_version_from_list(versions_list)

            # 读取用户输入的主版本号
            major_number = int(input('Enter the major version number: '))

            # 通过主版本号获取最新的版本
            version = await get_latest_version_by_major(major_number, latest_versions_list)

            # 使用获取到的版本进行一系列操作
            # ... 此处缺少对应的Python函数 ...

            install_node(version)
        else:
            print('No versions found in the file.')

    async def get_latest_version_from_list(download_dir, versions_list=None):
        """
        从给定的版本列表中提取每个主要版本的最新版本。

        :param download_dir: node_dist.html文件的下载目录。
        :param versions_list: 需要提取最新版本的版本列表，如果此参数为None，则将会从node_dist.html中获取版本列表。
        :return: 包含每个主要版本的最新版本的列表。
        """
        # 如果没有提供版本列表，则从node_dist.html中获取
        if versions_list is None:
            versions_list = await get_local_versions_list(download_dir)

        latest_versions_map = {}

        for version in versions_list:
            version_number = version.lstrip('v')
            major, minor, patch = list(map(int, version_number.split('.')))
            current_major_version = latest_versions_map.get(major)

            if current_major_version is None or minor > current_major_version[1] or (
                    minor == current_major_version[1] and patch > current_major_version[2]):
                latest_versions_map[major] = (version, minor, patch)

        latest_versions = [v[0] for v in latest_versions_map.values()]
        return latest_versions