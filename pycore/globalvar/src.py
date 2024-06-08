import os
import subprocess
import shutil
import tempfile
import re
import platform
from pycore.base.base import Base
from pycore.globalvar.gdir import gdir

class Source(Base):

    def getDefaultImageFile(self):
        icon = Util.file.get_stylesheet('img/default_app.png')
        return icon

    def getBrowserPath(self, browser):
        browserRegs = {
            'IE': 'SOFTWARE\\Clients\\StartMenuInternet\\IEXPLORE.EXE\\DefaultIcon',
            'chrome': 'SOFTWARE\\Clients\\StartMenuInternet\\Google Chrome\\DefaultIcon',
            'edge': 'SOFTWARE\\Clients\\StartMenuInternet\\Microsoft Edge\\DefaultIcon',
            'firefox': 'SOFTWARE\\Clients\\StartMenuInternet\\FIREFOX.EXE\\DefaultIcon',
            '360': 'SOFTWARE\\Clients\\StartMenuInternet\\360Chrome\\DefaultIcon',
        }

        if self.is_windows():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, browserRegs[browser])
                value, _ = winreg.QueryValueEx(key, '')
                return value.split(',')[0]
            except Exception as e:
                print(e)
                return None
        else:
            # Get browser path in non-Windows systems
            pass

        return None

    def getBrowserDriverPath(self, driverType):
        if driverType == 'chrome':
            return self.getChromePath()
        else:
            return self.getEdgeInstallPath()

    def getEdgeInstallPath(self):
        possiblePaths = [
            os.path.join(os.getenv('ProgramFiles'), 'Microsoft', 'Edge', 'Application'),
            os.path.join(os.getenv('ProgramFiles(x86)'), 'Microsoft', 'Edge', 'Application'),
        ]
        for path in possiblePaths:
            msedgeExe = os.path.join(path, 'msedge.exe')
            if os.path.exists(msedgeExe):
                return msedgeExe

        return None

    def getEdgeVersion(self, edgeExePath):
        try:
            output = subprocess.check_output(f'"{edgeExePath}" --version', shell=True, encoding='utf-8')
            return output.strip()
        except Exception as e:
            print(f'Error while getting Edge version: {e}')
            return None

    def getChromePath(self):
        chromePath = self.config.get('chrome_path')

        if not os.path.isabs(chromePath):
            chromePath = os.path.join(os.getcwd(), chromePath)

        if not os.path.isfile(chromePath):
            chromePath = self.getBrowserPath('chrome')
            if not chromePath:
                chromePath = self.downloadChromeBinary()

        if chromePath:
            self.config['chrome_path'] = chromePath

        return chromePath

    def getChromeVersion(self):
        versionRe = re.compile(r'\d+\.\d+\.\d+\.\d+')

        if self.is_windows():
            chromePath = self.getChromePath()
            visualElementsManifest = os.path.join(os.path.dirname(chromePath), 'chrome.VisualElementsManifest.xml')
            visualElementsManifestTmp = tempfile.NamedTemporaryFile(delete=False)
            shutil.copy(visualElementsManifest, visualElementsManifestTmp.name)
            with open(visualElementsManifestTmp.name, 'r') as f:
                content = f.read()
                versionMatches = versionRe.findall(content)
                if versionMatches:
                    return versionMatches[0]
                try:
                    key = self.getWindowsRegistryValue('Software\\Google\\Chrome\\BLBeacon', 'version')
                    registryVersion = versionRe.findall(key)
                    return registryVersion[0] if registryVersion else self.config.get('chrome_version')
                except Exception as e:
                    print(e)
                    print('Error getting Chrome version, falling back to config version.')
                    return self.config.get('chrome_version')
            os.unlink(visualElementsManifestTmp.name)
        else:
            try:
                output = subprocess.check_output('google-chrome --version', shell=True, encoding='utf-8')
                versionMatches = versionRe.findall(output)
                return versionMatches[0] if versionMatches else self.config.get('chrome_version')
            except Exception as e:
                print(e)
                print('Error getting Chrome version, falling back to config version.')
                return self.config.get('chrome_version')

    def get_git_executable(self):
        git_executable = "git"  # Default to "git" which works on both Windows and Linux

        if self.is_windows():
            possible_paths = [
                "D:\\applications\\Git\\cmd\\git.exe",
                "C:\\Program Files\\Git\\cmd\\git.exe",
                "C:\\Program Files (x86)\\Git\\cmd\\git.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            try:
                result = subprocess.run(["where", "git"], capture_output=True, text=True, check=True)
                if result.stdout:
                    git_path = result.stdout.splitlines()[0]
                    return git_path
            except subprocess.CalledProcessError:
                pass

            return "git.exe"

        else:
            possible_paths = [
                "/usr/bin/git",
                "/usr/local/bin/git",
                "/opt/local/bin/git",
                "/usr/lib/git-core/git",
                "/bin/git"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            try:
                result = subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
                if result.stdout:
                    git_path = result.stdout.strip()
                    return git_path
            except subprocess.CalledProcessError:
                pass

            return "git"

    def get_php_executable(self):
        php_executable = "php"  # Default to "php" which works on both Windows and Linux
        if self.is_windows():
            base_dir = "D:\\lang_compiler"
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file == "php.exe":
                        return os.path.join(root, file)

            try:
                result = subprocess.run(["where", "php"], capture_output=True, text=True, check=True)
                if result.stdout:
                    php_path = result.stdout.splitlines()[0]
                    return php_path
            except subprocess.CalledProcessError:
                pass

            return "php.exe"

        else:
            possible_paths = [
                "/usr/bin/",
                "/usr/local/bin/",
                "/opt/local/bin/",
                "/usr/lib/git-core/",
                "/bin/"
            ]
            for path in possible_paths:
                php_path = os.path.join(path, "php")
                if os.path.exists(php_path) and os.access(php_path, os.X_OK):
                    return php_path
            try:
                result = subprocess.run(["which", "php"], capture_output=True, text=True, check=True)
                if result.stdout:
                    php_path = result.stdout.strip()
                    return php_path
            except subprocess.CalledProcessError:
                pass

            return "php"

    def get_7z_executable(self):
        if self.is_windows():
            executable_path = gdir.getLibraryByWin32Dir("7za.exe")
        else:
            executable_path = gdir.getLibraryByLinuxDir("7z")
        return executable_path

src = Source()