import errno
import os
import subprocess
import time
import zipfile

import py7zr

from pycore.base.base import Base
import hashlib
import random
import platform
import asyncio

class Ziptask(Base):
    def __init__(self):
        super().__init__()
        self.callbacks = {}
        self.maxTasks = 10
        self.pendingTasks = []
        self.concurrentTasks = 0
        self.execCountTasks = 0
        self.execTaskEvent = None
        self.libraryDir = os.path.join(os.path.dirname(__file__), '../library')
        self.zipQueueTokens = []

    def get_md5(self, value):
        hash = hashlib.md5()
        hash.update(value.encode())
        return hash.hexdigest()

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
        return platform.system()

    def isWindows(self):
        return self.getCurrentOS() == 'windows'

    def get7zExeName(self):
        exeFile = '7zz' if not self.isWindows() else '7z.exe'
        return exeFile

    def get7zExe(self):
        folder = 'linux' if not self.isWindows() else 'windows'
        exeFile = self.get7zExeName()
        return os.path.join(self.libraryDir, f'{folder}/{exeFile}')

    def mkdirSync(self, directoryPath):
        return self.mkdir(directoryPath)

    def mkdir(self, dirPath):
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

    def isFileLocked(self, filePath):
        if not os.path.exists(filePath):
            return False
        try:
            with open(filePath, 'r+') as f:
                pass
            return False
        except Exception as e:
            if getattr(e, 'errno', 0) in [errno.EACCES, errno.EAGAIN]:
                return True
            return False

    def getModificationTime(self, fp):
        if not os.path.exists(fp):
            return 0
        try:
            return os.path.getmtime(fp)
        except Exception as e:
            print(f"Error getting modification time: {str(e)}")
            return 0

    def getFileSize(self, filePath):
        if not os.path.exists(filePath):
            return -1
        try:
            return os.path.getsize(filePath)
        except Exception as e:
            return -1

    def setMode(self, mode):
        self.mode = mode

    def log(self, msg, event=None):
        if event:
            self.success(msg)
    def compressDirectory(self, srcDir, outDir, token, callback):
        srcAbsPath = os.path.abspath(srcDir)
        outAbsPath = os.path.abspath(outDir)
        if not os.path.exists(srcAbsPath):
            return
        if not os.path.exists(outAbsPath):
            self.mkdirSync(outAbsPath)
        subDirectories = [entry for entry in os.listdir(srcAbsPath) if
                          os.path.isdir(os.path.join(srcAbsPath, entry)) and not entry.startswith('.')]
        for subDir in subDirectories:
            subDirPath = os.path.join(srcAbsPath, subDir)
            self.putZipQueueTask(subDirPath, outDir, token, callback)

    def getZipPath(self, srcDir, outDir):
        srcDirName = os.path.basename(srcDir)
        zipFileName = f'{srcDirName}.zip'
        zipFilePath = os.path.join(outDir, zipFileName)
        return zipFilePath

    def addToPendingTasks(self, command, callback):
        self.concurrentTasks += 1
        startTime = time.time()
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.log(f'Error compressing: {str(e)}')
        finally:
            if callback:
                callback(int((time.time() - startTime) * 1000))

    def processesCount(self, processName):
        normalizedProcessName = processName.lower()
        cmd = f'tasklist /fi "imagename eq {processName}"' if self.isWindows() else f'ps aux | grep {processName}'
        try:
            stdout = subprocess.check_output(cmd, shell=True, universal_newlines=True)
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
            self.log('Background compaction task started', True)
            self.execTaskEvent = asyncio.get_event_loop().call_later(1, self._execTask)

    def _execTask(self):
        processZipCount = self.a7zProcessesCount()
        if processZipCount != 10000:
            self.concurrentTasks = processZipCount
        if self.concurrentTasks >= self.maxTasks:
            self.log(f'7zProcesse tasks is full. current tasks:{self.concurrentTasks}, waiting...')
        elif self.pendingTasks:
            TaskObject = self.pendingTasks.pop(0)
            command = TaskObject['command']
            isQueue = TaskObject['isQueue']
            token = TaskObject['token']
            zipPath = TaskObject['zipPath']
            zipName = os.path.basename(zipPath)
            if not self.isFileLocked(zipPath):
                self.log(f'Unziping {zipName}, background:{self.concurrentTasks}', True)
                self.execCountTasks += 1
                asyncio.ensure_future(self.addToPendingTasks(command,lambda usetime: self._execTaskCallback(usetime, zipPath,token, isQueue)))
            else:
                self.pendingTasks.insert(0, TaskObject)
                self.log(f'The file is in use, try again later, "{zipPath}"')
        else:
            if self.execCountTasks < 1:
                self.execTaskEvent = None
                self.log('There is currently no compression task, end monitoring.')
                self.execTaskQueueCallback()
            else:
                self.log(f'There are still {self.execCountTasks} compression tasks, waiting...')
        if self.execTaskEvent:
            self.execTaskEvent = asyncio.get_event_loop().call_later(1, self._execTask)

    def _execTaskCallback(self, usetime, zipPath, token, isQueue):
        self.log(f'{os.path.basename(zipPath)} Compressed.runtime: {usetime / 1000}s', True)
        self.deleteTask(zipPath)
        self.callbacks[token]['usetime'] += usetime
        self.execCountTasks -= 1
        self.concurrentTasks -= 1
        if not isQueue:
            self.execTaskCallback(token)

    def execTaskQueueCallback(self):
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

    def addZipTask(self, src, out, token, callback):
        self.putZipTask(src, out, token, callback)

    def putZipTask(self, src, out, token, callback):
        self.putTask(src, out, token, True, callback, False)

    def putZipQueueTask(self, src, out, token, callback):
        self.putTask(src, out, token, True, callback)

    def putUnZipTask(self, src, out, callback):
        token = self.get_id(src)
        self.putTask(src, out, token, False, callback, False)

    def putUnZipQueueTask(self, src, out, callback):
        token = self.get_id(src)
        self.putTask(src, out, token, False, callback)

    def putQueueCallback(self, callback, token=None):
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
        try:
            self.putUnZipTask(zipFilePath, targetDirectory, lambda error: None)
        except Exception as e:
            raise e  # 调整错误处理方式
        # try:
        #     # 使用subprocess调用7z解压缩命令
        #     subprocess.run(['7z', 'x', zipFilePath, f'-o{targetDirectory}'])
        # except Exception as e:
        #     raise e  # 调整错误处理方式

    def putTask(self, src, out, token, isZip=True, callback=None, isQueue=True):
        if callback and token not in self.callbacks:
            self.callbacks[token] = {
                'callback': callback,
                'usetime': 0,
                'src': src
            }
        if isQueue:
            self.zipQueueTokens.append(token)
        zipPath = self.getZipPath(src, out) if isZip else src
        command = self.createZipCommand(src, out) if isZip else self.createUnzipCommand(src, out)
        if not self.isTask(zipPath):
            zipAct = 'compression' if isZip else 'unzip'
            zipName = os.path.basename(zipPath)
            self.log(f'Add a {zipAct} {zipName}, background:{self.concurrentTasks}', True)
            self.pendingTasks.append({
                'command': command,
                'zipPath': zipPath,
                'token': token,
                'isQueue': isQueue
            })
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
        command = f'"{self.get7zExe()}" x "{zipFilePath}" -o"{destinationPath}" -y'
        return command

    def test(self, archivePath):
        try:
            subprocess.run([self.get7zExe(), 't', archivePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=True)
            return True
        except Exception as e:
            print("Error testing the archive:", e)
            return False

