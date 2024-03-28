import errno
import os
import subprocess
import time
import urllib.request
import re
import querystring
from pycore.base import Base
from pycore.util.units import ziptask
import hashlib
import random
import platform
import asyncio
import requests

class Getnode(Base):
    tmpDirName = 'nodes_autoinstaller'
    error = {}
    mirrors_url = 'https://mirrors.tencent.com/npm/'
    node_dist_url = 'https://nodejs.org/dist/'
    node_dist_file = 'node_dist.html'
    retryLimit = 30
    retryCount = 0

    def __init__(self, tmpDir=''):
        super().__init__()
        self.tmpDir = tmpDir if tmpDir else ''
        self.versionNumber = ''
        self.nodeInstallDir = '/usr/node'

    def getCurrentOS(self):
        return platform.system()

    def isWindows(self):
        return self.getCurrentOS() == 'Windows'

    def isLinux(self):
        return not self.isWindows()

    def getNodeDirectory(self, npath=None):
        isWindows = self.isWindows()
        print("isWindows",isWindows)
        tmpDir = '/usr/nodes'
        if isWindows:
            tmpDir = 'D:/lang_compiler'
        if npath:
            tmpDir = os.path.join(tmpDir, npath)
        self.mkdir(tmpDir)
        return tmpDir

    def getLocalDir(self, subpath=None):
        appDataLocalDir = os.environ.get('LOCALAPPDATA') or os.path.join(os.environ.get('APPDATA'), 'Local')
        if subpath:
            return os.path.join(appDataLocalDir, subpath)
        else:
            return appDataLocalDir

    def readFile(self, filePath):
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f'Error reading file "{filePath}": {str(e)}')
            return ''

    def getTempDirectory(self):
        currentOS = self.getCurrentOS()
        tmpDir = '/tmp/node'
        if currentOS == 'win32':
            tmpDir = os.path.join(self.getLocalDir(), self.tmpDirName)
        self.mkdir(tmpDir)
        return tmpDir

    def getDownloadDirectory(self, fpath=None):
        homeDir = os.path.expanduser("~")
        downloadsDir = os.path.join(homeDir, 'Downloads')
        isWindows = self.isWindows()
        print("isWindows",isWindows)
        tmpDir = '/tmp/node/Downloads'
        if isWindows:
            tmpDir = os.path.join(downloadsDir, self.tmpDirName)
        self.mkdir(tmpDir)
        if fpath:
            tmpDir = os.path.join(tmpDir, fpath)
        print("tmpDir",tmpDir)
        return tmpDir


    def mkdir(self, dirPath):
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)


    def download(self, downUrl, downname=None):
        downloadDir = self.getDownloadDirectory()
        if not downname:
            downname = downUrl.split('/')[-1]
        # downname = querystring.unescape(downname)
        if not downloadDir.endswith(downname):
            downloadDir = os.path.join(downloadDir, downname)
        self.downFile(downUrl, downloadDir)
        return downloadDir

    def downFile(self, downUrl, dest):
        print("downUrl",downUrl)
        response = requests.get(downUrl, stream=True)
        if response.status_code != 200:
            self.retry(downUrl, dest)
            return

        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def retry(self, downUrl, dest):
        if self.retryCount < self.retryLimit:
            self.retryCount += 1
            print(f'Retry {self.retryCount} for file {dest}')
            self.downFile(downUrl, dest)
        else:
            print(f'Retry limit reached for file {dest}')


    def isFile(self, filename):
        if not filename or not isinstance(filename, str):
            return False
        if os.path.exists(filename):
            return os.path.isfile(filename)
        return False


    def compareFileSizes(self, remoteUrl, localPath):
        if not self.isFile(localPath):
            return False
        try:
            remoteSize = self.getRemoteFileSize(remoteUrl)
            localSize = os.path.getsize(localPath)
            print(f'compareFileSizes : url:{remoteUrl},remoteSize:{remoteSize},localPath:{localPath}')
            return remoteSize == localSize
        except Exception as err:
            print("An error occurred:", err)
            return False

    def getRemoteFileSize(self, remoteUrl):
        req = urllib.request.Request(remoteUrl, method='HEAD')
        with urllib.request.urlopen(req) as response:
            size = response.headers.get('Content-Length')
            if size:
                return int(size)
            else:
                return -1

    def getFileSize(self, filePath):
        if not self.isFile(filePath):
            return -1
        try:
            return os.path.getsize(filePath)
        except Exception as error:
            return -1


    # def unescape_url(self, url):
    #     return querystring.unescape(url)

    # 返回空对象
    def get_node_downloads(self):
        return {}


    def get_version(self):
        return float(os.environ.get("NODE_VERSION", "0.0.0")[1:])

    def get_version_full(self):
        return os.environ.get("NODE_VERSION", "v0.0.0")


    def get_node_modules(self, appPath):
        return os.path.join(appPath, "node_modules")


    def extract_nodeversip(self, appConfig):
        specified_node_version = appConfig.get('package_json', {}).get('engines', {}).get('node')
        self.warn(appConfig.get('name'), specified_node_version)

        if specified_node_version:
            return [float(re.sub(r'^[^\d]*(\d.*)$', r'\1', token)) for token in specified_node_version.split(' ') if
                    token.strip()]
        else:
            return []

    # 提取预期的 Node.js 版本号
    def extractVersionsByOut(self, content):
        return re.findall(r'Expected version "(\d+(?:\.\d+)*)"', content)

    # 提取错误信息
    def extractErrorsByStr(self, inputString):
        return [line.strip() for line in inputString.split('\n') if 'error' in line]

    # 检查当前用户是否具有 sudo 权限
    def hasSudo(self):
        try:
            subprocess.run(['sudo', '-n', 'true'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    # 获取指定文件的最后修改时间
    def getLastModifiedTime(self, filePath):
        try:
            return os.path.getmtime(filePath)
        except Exception as error:
            print(f'Error getting last modified time for file "{filePath}": {error}')
            return None

    # 获取节点分发页面的 HTML 内容
    def getNodeDistHtml(self):
        nodeDistHtmlPath = os.path.join(self.getDownloadDirectory(), 'node_dist.html')
        reDownload = False
        if self.isFile(nodeDistHtmlPath):
            lastModifiedTime = self.getLastModifiedTime(nodeDistHtmlPath)
            if lastModifiedTime:
                diffInMs = (time.time() * 1000) - (lastModifiedTime * 1000)
                if diffInMs > (24 * 60 * 60 * 1000):
                    reDownload = True
            else:
                reDownload = True
        else:
            reDownload = True

        if reDownload:
            self.downloadNodeDistHtml()

        return nodeDistHtmlPath


    def getLocalVersionsList(self):
        DistHtml = self.getNodeDistHtml()
        Content = self.readFile(DistHtml)

        versionPattern = r'\bv(\d+\.\d+)\.\d+\b'
        versionsList = re.findall(versionPattern, Content)
        if versionsList:
            latestVersionsList = self.getLatestVersionFromList(versionsList)
            version = self.getLatestVersionByMajor("18", latestVersionsList)
            if version:
                print(version)
                self.installNode(version)
                # Define project directory, project type, start parameter, and Node.js version
                projectDir = '/mnt/d/programing/faker/'
                projectType = 'vue'  # Project type
                startParameter = 'dev'  # Start parameter
                self.runByPm2(projectDir, projectType, startParameter, version)
            else:
                print('An error occurred.')

        else:
            print('No versions found in the file.')

    def getLatestVersionFromList(self, versionsList=None):
        if not versionsList:
            versionsList = self.getLocalVersionsList()
        latestVersionsMap = {}

        for version in versionsList:
            versionNumber = version.replace('v', '')
            major, minor = map(int, versionNumber.split('.'))
            currentMajor = latestVersionsMap.get(major)
            if not currentMajor or minor > currentMajor['minor']:
                latestVersionsMap[major] = {'minor': minor, 'version': version}

        latestVersions = [value['version'] for value in latestVersionsMap.values()]
        return latestVersions

    def downloadNodeDistHtml(self):
        self.download(self.node_dist_url , self.node_dist_file)

    def getLatestVersionByNumber(self, versionNumber, versionsList):
        maxVersion = None
        for version in versionsList:
            if version.startswith(versionNumber):
                if not maxVersion or self.compareVersions(version, maxVersion) > 0:
                    maxVersion = version
        return maxVersion

    def getLatestVersionByMajor(self, majorNumber, latestVersionsList):
        for version in latestVersionsList:
            versionNumber = version.replace('v', '')
            major, _, _ = map(int, versionNumber.split('.'))
            if major == majorNumber:
                return version
        return None

    def compareVersions(self, versionA, versionB):
        partsA = list(map(int, versionA.split('.')))
        partsB = list(map(int, versionB.split('.')))

        for partA, partB in zip(partsA, partsB):
            if partA != partB:
                return partA - partB

        return 0


    def installNode(self, version):
        nodeDir = os.path.join(self.nodeInstallDir, version)

        if os.path.exists(nodeDir):
            print(f'Node version {version} is already installed at {nodeDir}')
            return

        try:
            if not os.path.exists(self.nodeInstallDir):
                os.makedirs(self.nodeInstallDir)

            if not os.path.exists(nodeDir):
                os.makedirs(nodeDir)

            downloadUrl = f'https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.gz'
            downloadPath = os.path.join(self.nodeInstallDir, f'node-{version}-linux-x64.tar.gz')

            print(f'Downloading Node.js {version} from {downloadUrl}...')
            self.downloadFile(downloadUrl, downloadPath)
            print(f'Node.js {version} downloaded successfully.')

            print(f'Extracting Node.js {version} to {nodeDir}...')
            self.extractFile(downloadPath, nodeDir)
            print(f'Node.js {version} extracted successfully.')

            print(f'Node.js {version} installed successfully at {nodeDir}')
        except Exception as error:
            print(f'Error installing Node.js {version}: {error}')

    # 解压缩文件
    def extractFile(self, src, destDir):
        try:
            subprocess.run(['tar', '-xzf', src, '-C', destDir], check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error extracting file: {e}')
            raise e

    def getNodeExecutable(self):
        return 'node' if self.isLinux() else 'node.exe'

    def getNpmExecutable(self):
        return 'npm' if self.isLinux() else 'npm.cmd'

    # 根据操作系统类型确定 npx 可执行文件的名称
    def getNpxExecutable(self):
        return 'npx' if self.isLinux() else 'npx.cmd'

    # 根据操作系统类型确定 yarn 可执行文件的名称
    def getYarnExecutable(self):
        return 'yarn' if self.isLinux() else 'yarn.cmd'

    # 根据操作系统类型确定 pm2 可执行文件的名称
    def getPm2Executable(self):
        return 'pm2' if self.isLinux() else 'pm2.cmd'

    def getFileNameWithoutExtension(self, fileName):
        return os.path.splitext(fileName)[0]

    def findNodeVersionByPlatform(self, nodeHrefVersions, version):
        matchRoles = [f'v{version}.', 'win', 'x64', '.7z'] if self.isLinux() else [f'v{version}.', 'linux', 'x64',
                                                                                   '.gz']
        matchRolesCopy = matchRoles[:]
        matchFound = False

        while matchRolesCopy and not matchFound:
            for nodeVersion in nodeHrefVersions:
                mathis = all(role in nodeVersion for role in matchRolesCopy)
                if mathis:
                    return nodeVersion
            matchRolesCopy.pop()

        return None

    def extractNodeHrefVersions(self, nodeHTMLContent):
        hrefValues = re.findall(r'href="(.*?)"', nodeHTMLContent)
        return hrefValues

    def installNodeAndYarn(self, nodePath, npmPath, nodeInstallFileDir):
        nodeVersion = subprocess.run([nodePath, '-v'], capture_output=True, text=True).stdout.strip()
        npmVersion = subprocess.run([npmPath, '-v'], capture_output=True, text=True).stdout.strip()
        print(f'Node.js version: {nodeVersion}')
        print(f'Npm version: {npmVersion}')

        cmd = [npmPath, 'config', 'set', 'prefix', nodeInstallFileDir]
        if self.isLinux() and self.hasSudo():
            cmd.insert(0, 'sudo')
        print(' '.join(cmd))
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        print(out)

        cmd = [npmPath, 'config', 'set', 'registry', self.mirrors_url]
        if self.isLinux() and self.hasSudo():
            cmd.insert(0, 'sudo')
        print(' '.join(cmd))
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        print(out)

        cmd = [npmPath, 'install', '-g', 'yarn']
        if self.isLinux() and self.hasSudo():
            cmd.insert(0, 'sudo')
        print(' '.join(cmd))
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        print(out)

        cmd = [npmPath, 'install', '-g', 'pm2']
        if self.isLinux() and self.hasSudo():
            cmd.insert(0, 'sudo')
        print(' '.join(cmd))
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        print(out)

        print('Node.js installation completed.')

    def getNodeByVersion(self, version='18'):
        nodeDir = self.getNodeDirectory()
        nodeHrefVersions = os.listdir(nodeDir)
        print("nodeHrefVersions",nodeHrefVersions)
        matchingVersion = self.findNodeVersionByPlatform(nodeHrefVersions, version)

        nodeExe = self.getNodeExecutable()
        if not os.path.isfile(os.path.join(self.getNodeDirectory(matchingVersion), nodeExe)):
            latestVersionFromList = self.getLatestVersionFromList()
            matchedVersion = next(
                (versionString for versionString in latestVersionFromList if versionString.startswith(f'v{version}.')),
                None)
            if matchedVersion:
                nodeDetailHTML = f'{matchedVersion}.html'



                nodeDetailDownloadFile = self.getDownloadDirectory(nodeDetailHTML)
                if not os.path.isfile(nodeDetailDownloadFile):
                    nodeDetailUrl = f'{self.node_dist_url}{matchedVersion}/'
                    nodeDetailDownloadFile = self.download(nodeDetailUrl, nodeDetailHTML)

                nodeHTMLContent = self.readFile(nodeDetailDownloadFile)
                nodeHrefVersions = self.extractNodeHrefVersions(nodeHTMLContent)
                matchingVersion = self.findNodeVersionByPlatform(nodeHrefVersions, version)
                if matchingVersion:
                    matchingVersionDownloadFile = self.getDownloadDirectory(matchingVersion)
                    if not os.path.isfile(matchingVersionDownloadFile):
                        nodeDownloadUrl = f'{self.node_dist_url}{matchedVersion}/{matchingVersion}'
                        matchingVersionDownloadFile = self.download(nodeDownloadUrl, matchingVersion)
                        matchingVersion = self.getFileNameWithoutExtension(matchingVersion)
                        self.extractFile(matchingVersionDownloadFile, nodeDir)

        if matchingVersion:
            return os.path.join(self.getNodeDirectory(matchingVersion), nodeExe)
        return None

    def getNpmByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
        yarnExec = os.path.join(nodeInstallPath, self.getYarnExecutable())
        if not os.path.isfile(yarnExec):
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
        if not os.path.isfile(yarnExec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return yarnExec

    def getPm2ByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        pm2Exec = os.path.join(nodeInstallPath, self.getPm2Executable())
        if not os.path.isfile(pm2Exec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return pm2Exec

    # runByPm2(self, projectDir, projectType, start_parameter, node_version):
    #     print("__dirname:", __dirname)
    #     templatePath = os.path.join(__dirname, 'templates', 'ecosystem.config.js')

    #     if not os.path.exists(templatePath):
    #         print(f'Template for {projectType} does not exist.')
    #         return

    #     with open(templatePath, 'r') as f:
    #         templateContent = f.read()

    #     targetPath = os.path.join(projectDir, 'ecosystem.config.js')

    #     with open(targetPath, 'w') as f:
    #         f.write(templateContent)

    #     print(f'Generated ecosystem.config.js in {targetPath}')

    #     nodeInstallPath = self.getNodeByVersion(node_version)
    #     pm2Command = '/usr/bin/pm2'

    #     command = f'sudo  {pm2Command} start {targetPath} --name {projectType}'

    #     subprocess.run(command, shell=True, check=True)
    #     print(f'Project started using Node.js {node_version} and PM2.')
    # runByPm2(self, projectDir, projectType, start_parameter, node_version):
    #     print("__dirname:", __dirname)
    #     templatePath = os.path.join(__dirname, 'templates', 'ecosystem.config.js')

    #     if not os.path.exists(templatePath):
    #         print(f'Template for {projectType} does not exist.')
    #         return

    #     with open(templatePath, 'r') as f:
    #         templateContent = f.read()

    #     targetPath = os.path.join(projectDir, 'ecosystem.config.js')

    #     with open(targetPath, 'w') as f:
    #         f.write(templateContent)

    #     print(f'Generated ecosystem.config.js in {targetPath}')

    #     nodeInstallPath = self.getNodeByVersion(node_version)
    #     pm2Command = '/usr/bin/pm2'

    #     command = f'sudo  {pm2Command} start {targetPath} --name {projectType}'

    #     subprocess.run(command, shell=True, check=True)
    #     print(f'Project started using Node.js {node_version} and PM2.')


getnode = Getnode()
