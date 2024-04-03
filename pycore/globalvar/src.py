import os
import subprocess
import shutil
import tempfile
import re
import requests
import zipfile

class Source:
    def __init__(self):
        self.config = {}

    def setConfig(self, conf):
        self.config = conf

    def getDriverPathByChrome(self, driverType):
        chromePath = self.getBrowserDriverPath(driverType)
        version = self.getDriverVersion(driverType)
        driverPath = self.installDriver(version, driverType)

        driverVersion = self.getRealDriverVersion(driverPath)
        if version != driverVersion:
            print('The driver version may not match the browser version')
            print(f'Browser version ({driverType}): {version} <=> Driver version: {driverVersion}')

        seleniumInfo = f"""
        Selenium info:
        \tBrowser ({driverType}): {version}
        \tDriver: {driverVersion}
        \tDriver name: {self.getDriverName()}
        \tChrome: {chromePath}
        \tDriver: {driverPath}"""
        print(seleniumInfo)
        return driverPath

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

        if self.isWindows():
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

    def isWindows(self):
        return os.name == 'nt'

    def downloadChromeBinary(self):
        if self.isWindows():
            remoteUrl = self.config.get('remote_url')
            url = f'{remoteUrl}/public/static/chrome_105.0.5195.52.zip'
            downloadDir = os.path.join(os.path.dirname(__file__), 'downloads')
            if not os.path.exists(downloadDir):
                os.makedirs(downloadDir)
            downloadPath = os.path.join(downloadDir, 'chrome.zip')
            with open(downloadPath, 'wb') as f:
                response = requests.get(url)
                f.write(response.content)
            with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
                zip_ref.extractall(downloadDir)
            chromePath = os.path.join(downloadDir, 'chrome.exe')
            return chromePath
        else:
            # Commands for Linux
            pass

    def getChromeVersion(self):
        versionRe = re.compile(r'\d+\.\d+\.\d+\.\d+')

        if self.isWindows():
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

    def getRealDriverVersion(self, driverPath):
        print('driverPath', driverPath)
        # Some code here to get driver version
        pass

    def getSupportedVersion(self, driverType):
        # Some code here to get supported versions
        pass

    # Rest of the methods...

# Main block
if __name__ == "__main__":
    source = Source()
    # Set configuration
    source.setConfig({})
    # Call methods as needed
    source.getDriverPathByChrome('chrome')
