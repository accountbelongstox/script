import os
import hashlib
import random
import string
import time
import asyncio
import zipfile
import subprocess
import threading
import sys
from pathlib import Path

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

