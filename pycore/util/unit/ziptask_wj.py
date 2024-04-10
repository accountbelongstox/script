import subprocess
import os
import sys
import hashlib
import random
import time

from pycore.base.base import Base
from pycore.globalvar.gdir_wj import gdir
class ZipTask(Base):
    def __init__(self):
        super().__init__()
        self.callbacks = {}
        self.maxTasks = 10
        self.pendingTasks = []
        self.concurrentTasks = 0
        self.execCountTasks = 0
        self.execTaskEvent = None
        self.zipQueueTokens = []

    def get_md5(self, value):
        hash_object = hashlib.md5(value.encode())
        return hash_object.hexdigest()

    def createString(self, length=10):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.choice(letters) for i in range(length))

    def create_id(self, value=None):
        if not value:
            value = self.createString(128)
        _id = self.get_id(value)
        return _id

    def get_id(self, value, pre=None):
        value = str(value)
        md5 = self.get_md5(value)
        _id = f'id{md5}'
        if pre:
            _id = pre + _id
        return _id

    def getCurrentOS(self):
        return sys.platform

    def isWindows(self):
        return self.getCurrentOS() == 'win32'

    def get7zExeName(self):
        exeFile = '7zz' if not self.isWindows() else '7z.exe'
        return exeFile

    def get7zExe(self):
        exeFile = self.get7zExeName()
        print("exeFile",exeFile)
        libraryDir = gdir.getLibraryDir()
        print("libraryDir",libraryDir)
        return os.path.join(libraryDir, exeFile)

        # return r"D:\programing\script\pycore\globalvar\util\base\library\win32\7z.exe"

    def mkdirSync(self, directoryPath):
        return self.mkdir(directoryPath)

    def mkdir(self, dirPath):
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

    def isFileLocked(self, filePath):
        if not os.path.exists(filePath):
            return False
        try:
            with open(filePath, 'r+'):
                pass
            return False
        except Exception as e:
            if isinstance(e, (IOError, OSError)):
                return True
            return False

    def getModificationTime(self, fp):
        if not os.path.exists(fp):
            return 0
        try:
            stats = os.stat(fp)
            return stats.st_mtime
        except Exception as e:
            print(f'Error getting modification time: {e}')
            return 0

    def getFileSize(self, filePath):
        if not os.path.exists(filePath):
            return -1
        try:
            stats = os.stat(filePath)
            return stats.st_size
        except Exception as e:
            return -1

    def setMode(self, mode):
        self.mode = mode

    def log(self, msg, event):
        if event:
            self.success(msg)

    def compressDirectory(self, srcDir, outDir, token, callback):
        srcAbsPath = os.path.abspath(srcDir)
        outAbsPath = os.path.abspath(outDir)
        if not os.path.exists(srcAbsPath):
            return
        if not os.path.exists(outAbsPath):
            self.mkdirSync(outAbsPath)
        subDirectories = [entry for entry in os.listdir(srcAbsPath) if os.path.isdir(os.path.join(srcAbsPath, entry)) and not entry.startswith('.')]
        for subDirName in subDirectories:
            subDirPath = os.path.join(srcAbsPath, subDirName)
            self.putZipQueueTask(subDirPath, outDir, token, callback)

    def getZipPath(self, srcDir, outDir):
        srcDirName = os.path.basename(srcDir)
        zipFileName = f'{srcDirName}.zip'
        zipFilePath = os.path.join(outDir, zipFileName)
        return zipFilePath

    def addToPendingTasks(self, command, callback, processCallback):
        self.concurrentTasks += 1
        self.execBySpawn(command, callback, processCallback)

    def execBySpawn(self, command, callback, processCallback):
        start_time = time.time()
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout:
            stdout_str = stdout.decode('utf-8')
            if processCallback:
                processCallback(stdout_str)
        if stderr:
            stderr_str = stderr.decode('utf-8')
            print(f'Error: {stderr_str}')
            if processCallback:
                processCallback(-1)
            # 更新 self.concurrentTasks 的值为 0
            self.concurrentTasks = 0
        exit_code = process.returncode
        print(f'child process exited with code {exit_code}')
        if callback:
            callback(int((time.time() - start_time) * 1000))

    def processesCount(self, processName):
        normalizedProcessName = processName.lower()
        if self.isWindows():
            cmd = f'tasklist /fi "imagename eq {processName}"'
        else:
            cmd = f'ps aux | grep {processName}'
        try:
            stdout = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            count = len([line for line in stdout.split('\n') if normalizedProcessName in line.lower()]) - 1
            return count
        except Exception as e:
            print('Error executing command:', e)
            return 10000

    def a7zProcessesCount(self):
        processName = self.get7zExeName()
        processZipCount = self.processesCount(processName)
        return processZipCount

    def execTask(self):

        if not self.execTaskEvent:
            print('Background compaction task started')
            self.execTaskEvent = True  # Placeholder for actual interval implementation
            while True:
                processZipCount = self.a7zProcessesCount()
                if processZipCount != 10000:
                    self.concurrentTasks = processZipCount
                if self.concurrentTasks >= self.maxTasks:
                    print(f'7zProcesse tasks is full. current tasks: {self.concurrentTasks}, waiting...')
                elif self.pendingTasks:
                    taskObject = self.pendingTasks.pop(0)
                    command = taskObject['command']
                    isQueue = taskObject['isQueue']
                    token = taskObject['token']
                    processCallback = taskObject['processCallback']
                    zipPath = taskObject['zipPath']
                    zipName = os.path.basename(zipPath)
                    if not self.isFileLocked(zipPath):
                        print(f'Unziping {zipName}, background: {self.concurrentTasks}')
                        print(f'Unzip-Command: {command}')
                        self.execCountTasks += 1
                        self.addToPendingTasks(command, lambda usetime: self.log(
                            f'{zipName} Compressed.runtime: {usetime / 1000}s', True), processCallback)
                    else:
                        self.pendingTasks.append(taskObject)
                        print(f'The file is in use, try again later, "{zipPath}"')
                else:
                    if self.execCountTasks < 1:
                        print('There is currently no compression task, end monitoring.')
                        self.execTaskQueueCallbak()
                        self.execTaskEvent = None  # Exit the event loop
                        break
                    else:
                        print(f'There are still {self.execCountTasks} compression tasks, waiting')
                # 检查是否满足退出循环的条件
                if not self.pendingTasks and self.concurrentTasks == 0:
                    print('No pending tasks and no concurrent tasks, exiting...')
                    self.execTaskEvent = None
                    break
                time.sleep(1)  # Add a sleep to avoid busy waiting

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

    def putZipTask(self, src, out, token, callback):
        self.putTask(src, out, token, True, callback, False)

    def putZipQueueTask(self, src, out, token, callback):
        self.putTask(src, out, token, True, callback)

    def putUnZipTask(self, src, out, callback, processCallback):
        token = self.get_id(src)
        self.putTask(src, out, token, False, callback, False, processCallback)

    def putUnZipQueueTask(self, src, out, callback, processCallback):
        token = self.get_id(src)
        self.putTask(src, out, token, False, callback, True, processCallback)

    def putQueueCallback(self, callback, token):
        if callback and token not in self.callbacks:
            if not token:
                token = self.create_id()
            self.zipQueueTokens.append(token)
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': ''
            }

    def putUnZipTaskPromise(self, zipFilePath, targetDirectory):
        return self.putUnZipTask(zipFilePath, targetDirectory, lambda error: None, lambda data: None)

    def putTask(self, src, out, token, isZip=True, callback=None, isQueue=True, processCallback=None):
        if callback and token not in self.callbacks:
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': src
            }
        if isQueue:
            self.zipQueueTokens.append(token)
        zipPath = src if not isZip else self.getZipPath(src, out)
        command = self.createZipCommand(src, out) if isZip else self.createUnzipCommand(src, out)
        if not self.isTask(zipPath) and isinstance(zipPath, str):
            zipAct = 'compression' if isZip else 'unzip'
            zipName = os.path.basename(zipPath)
            print(f'Add a {zipAct} {zipName}, background: {self.concurrentTasks}')
            self.pendingTasks.append({
                'command': command,
                'zipPath': zipPath,
                'token': token,
                'isQueue': isQueue,
                'processCallback': processCallback
            })
        else:
            if processCallback:
                processCallback(-1)
            if callback:
                callback()
        self.execTask()

    def deleteTask(self, zipPath):
        self.pendingTasks = [task for task in self.pendingTasks if task['zipPath'] != zipPath]

    def isTask(self, zipPath):
        return any(task['zipPath'] == zipPath for task in self.pendingTasks)

    def createZipCommand(self, srcDir, outDir):
        srcDirName = os.path.basename(srcDir)
        zipFileName = f'{srcDirName}.zip'
        zipFilePath = os.path.join(outDir, zipFileName)
        command = f'"{self.get7zExe()}" a "{zipFilePath}" "{srcDir}"'
        return command

    def createUnzipCommand(self, zipFilePath, destinationPath):
        command = f'{self.get7zExe()} x "{zipFilePath}" -o"{destinationPath}" -y'
        return command

    def test(self, archivePath):
        try:
            subprocess.check_output(f'{self.get7zExe()} t "{archivePath}"', stderr=subprocess.PIPE)
            return True
        except Exception as e:
            print("Error testing the archive:", e)
            return False

    def __str__(self):
        return '[class ZipTask]'

zip_task = ZipTask()
