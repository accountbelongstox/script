import os
from pycore.base.base import Base

class Env(Base):
    annotationSymbol = '#'

    def __init__(self, rootDir=None, envName='.env', delimiter='='):
        self.rootDir = rootDir or os.getcwd()
        self.envName = envName
        self.delimiter = delimiter
        self.initEnv = False

    def _init(self):
        if not self.initEnv:
            self.initEnv = True
            self.localEnvFile = self._getLocalEnvFile()
            self.exampleEnvFile = self._getExampleEnvFile()
            self.mergeEnv(self.localEnvFile, self.exampleEnvFile)

    def _getLocalEnvFile(self):
        localEnvFile = os.path.join(self.rootDir, self.envName)
        return localEnvFile

    def _getExampleEnvFile(self):
        exampleFiles = [
            os.path.join(self.rootDir, f"{self.envName}_example"),
            os.path.join(self.rootDir, f"{self.envName}-example"),
            os.path.join(self.rootDir, f"{self.envName}.example"),
        ]
        for exampleFile in exampleFiles:
            if os.path.exists(exampleFile):
                return exampleFile
        return None

    def load(self, rootDir, envName='.env', delimiter='='):
        return Env(rootDir, envName, delimiter)

    def loadFile(self, envFilePath, delimiter='='):
        rootDir = os.path.dirname(envFilePath)
        envName = os.path.basename(envFilePath)
        return Env(rootDir, envName, delimiter)

    def mergeEnv(self, envFile, exampleEnvFile):
        if not exampleEnvFile:
            return
        exampleArr = self.readEnv(exampleEnvFile)
        localArr = self.readEnv(envFile)
        exampleDict = Env.arrToDict(exampleArr)
        localDict = Env.arrToDict(localArr)
        addedKeys = [key for key in exampleDict.keys() if key not in localDict]
        for key in addedKeys:
            localDict[key] = exampleDict[key]
        if addedKeys:
            print(f"Env-Update env: {envFile}")
            updatedArr = Env.dictToArr(localDict)
            self.saveEnv(updatedArr, envFile)
            for key in addedKeys:
                print(f"Env-Added key: {key}")

    def readKey(self, key):
        self._init()
        with open(self.localEnvFile, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                k, v = line.strip().split(self.delimiter, 1)
                if k.strip() == key:
                    return v.strip()
        return None

    def replaceOrAddKey(self, key, val):
        lines = []
        with open(self.localEnvFile, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                k, v = line.strip().split(self.delimiter, 1)
                if k.strip() == key:
                    lines.append(f"{key}{self.delimiter}{val}")
                else:
                    lines.append(line.strip())
            if not any(line.startswith(f"{key}{self.delimiter}") for line in lines):
                lines.append(f"{key}{self.delimiter}{val}")
        updatedContent = '\n'.join(lines) + '\n'
        with open(self.localEnvFile, 'w') as file:
            file.write(updatedContent)

    def readEnv(self, filePath):
        with open(filePath, 'r') as file:
            content = file.read().strip()
            return [line.strip().split(self.delimiter, 1) for line in content.split('\n')]

    def getEnvs(self, filePath=None):
        return self.readEnv(filePath or self.localEnvFile)

    def saveEnv(self, envArr, filePath):
        content = '\n'.join([f"{k}{self.delimiter}{v}" for k, v in envArr]) + '\n'
        with open(filePath, 'w') as file:
            file.write(content)

    def setEnv(self, key, value, filePath=None):
        self._init()
        filePath = filePath or self.localEnvFile
        envArr = self.readEnv(filePath)
        updatedArr = [[k, value] if k == key else [k, v] for k, v in envArr]
        if not any(k == key for k, _ in updatedArr):
            updatedArr.append([key, value])
        self.saveEnv(updatedArr, filePath)

    def isEnv(self, key, filePath=None):
        self._init()
        val = self.getEnv(key, filePath)
        result = bool(val)
        if 'is_env' in os.sys.argv:
            print('True' if result else 'False')
        return result

    def getEnv(self, key, default_val='', filePath=None):
        self._init()
        filePath = filePath or self.localEnvFile
        envArr = self.readEnv(filePath)
        for k, v in envArr:
            if k == key:
                return v
        return default_val

    @staticmethod
    def arrToDict(array):
        return dict(array)

    @staticmethod
    def dictToArr(dictionary):
        return list(dictionary.items())




env = Env()
