const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { promisify } = require('util');
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);

class Env {

    mainEnvFile = null;
    annotationSymbol = "#";

    constructor(rootDir = null, envName = ".env", delimiter = "=") {
        rootDir = this.getCwd();
        this.setRootDir(rootDir, envName, delimiter);
    }

    getCwd() {
        return path.dirname(__filename);
    }

    setDelimiter(delimiter = "=") {
        this.delimiter = delimiter;
    }

    async exampleTo(examplePath) {
        const envFile = examplePath.replace("-example", "").replace("_example", "").replace(".example", "");
        await this.mergeEnv(envFile, examplePath);
    }

    async setRootDir(rootDir, envName = ".env", delimiter = "=") {
        this.setDelimiter(delimiter);
        this.rootDir = rootDir;
        this.localEnvFile = path.join(this.rootDir, envName);
        this.exampleEnvFile = path.join(this.rootDir, `${envName}_example`);
        if (!fs.existsSync(this.exampleEnvFile)) {
            this.exampleEnvFile = path.join(this.rootDir, `${envName}-example`);
        }
        if (!fs.existsSync(this.exampleEnvFile)) {
            this.exampleEnvFile = path.join(this.rootDir, `${envName}.example`);
        }
        await this.getLocalEnvFile();
    }

    async load(rootDir, envName = ".env", delimiter = "=") {
        return new Env(rootDir, envName, delimiter);
    }

    async getLocalEnvFile() {
        if (!fs.existsSync(this.localEnvFile)) {
            fs.writeFileSync(this.localEnvFile, "");
        }
        await this.mergeEnv(this.localEnvFile, this.exampleEnvFile);
        return this.localEnvFile;
    }

    getEnvFile() {
        return this.localEnvFile;
    }

    arrToDict(array) {
        const result = {};
        for (const item of array) {
            if (Array.isArray(item) && item.length > 1) {
                const [key, val] = item;
                result[key] = val;
            }
        }
        return result;
    }

    dictToArr(dictionary) {
        const result = [];
        for (const [key, value] of Object.entries(dictionary)) {
            result.push([key, value]);
        }
        return result;
    }

    async mergeEnv(envFile, exampleEnvFile) {
        if (!fs.existsSync(exampleEnvFile)) {
            return;
        }
        const exampleArr = this.readEnv(exampleEnvFile);
        const localArr = this.readEnv(envFile);
        const addedKeys = [];
        const exampleDict = this.arrToDict(exampleArr);
        const localDict = this.arrToDict(localArr);
        for (const [key, value] of Object.entries(exampleDict)) {
            if (!(key in localDict)) {
                localDict[key] = value;
                addedKeys.push(key);
            }
        }
        if (addedKeys.length > 0) {
            console.log(`Env-Update env: ${envFile}`);
            const updatedArr = this.dictToArr(localDict);
            await this.saveEnv(updatedArr, envFile);
        }
        for (const addedKey of addedKeys) {
            console.log(`Env-Added key: ${addedKey}`);
        }
    }

    readKey(key) {
        const content = fs.readFileSync(this.mainEnvFile, 'utf8');
        const lines = content.split('\n');
        for (const line of lines) {
            const [k, v] = line.split(this.delimiter);
            if (k.trim() === key) {
                return v.trim();
            }
        }
        return null;
    }

    replaceOrAddKey(key, val) {
        let updated = false;
        const lines = [];
        const content = fs.readFileSync(this.mainEnvFile, 'utf8');
        const fileLines = content.split('\n');
        for (const line of fileLines) {
            const [k, v] = line.split(this.delimiter);
            if (k.trim() === key) {
                lines.push(`${key}${this.delimiter}${val}`);
                updated = true;
            } else {
                lines.push(line);
            }
        }
        if (!updated) {
            lines.push(`${key}${this.delimiter}${val}`);
        }
        const updatedContent = lines.join('\n');
        fs.writeFileSync(this.mainEnvFile, updatedContent);
    }

    readEnv(filePath = null) {
        if (filePath === null) {
            filePath = this.localEnvFile;
        }
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split('\n');
        const result = lines.map(line => line.split(this.delimiter).map(value => value.trim()));
        return result;
    }

    getEnvs(filePath = null) {
        return this.readEnv(filePath);
    }

    async saveEnv(envArr, filePath = null) {
        if (filePath === null) {
            filePath = this.localEnvFile;
        }
        const filteredEnvArr = envArr.filter(subArr => subArr.length === 2);
        const formattedLines = filteredEnvArr.map(subArr => `${subArr[0]}${this.delimiter}${subArr[1]}`);
        const resultString = formattedLines.join('\n');
        await this.saveFile(filePath, resultString, true);
    }

    async setEnv(key, value, filePath = null) {
        if (filePath === null) {
            filePath = this.localEnvFile;
        }
        const envArr = this.readEnv(filePath);
        let keyExists = false;
        for (const subArr of envArr) {
            if (subArr[0] === key) {
                subArr[1] = value;
                keyExists = true;
                break;
            }
        }
        if (!keyExists) {
            envArr.push([key, value]);
        }
        await this.saveEnv(envArr, filePath);
    }

    isEnv(key, filePath = null) {
        const isArg = process.argv.includes("is_env");
        const val = this.getEnv(key, filePath);
        if (val === "") {
            if (isArg) {
                console.log("False");
            }
            return false;
        }
        if (isArg) {
            console.log("True");
        }
        return true;
    }

    getEnv(key, filePath = null) {
        if (filePath === null) {
            filePath = this.localEnvFile;
        }
        const envArr = this.readEnv(filePath);
        for (const subArr of envArr) {
            if (subArr[0] === key) {
                return subArr[1];
            }
        }
        return "";
    }

    async saveFile(filePath, content, overwrite) {
        if (!fs.existsSync(filePath) || overwrite) {
            await writeFileAsync(filePath, content);
        }
    }
}

const env = new Env()

class AutoInstaller {
    projects = ['.', 'frontend'];
    projectsFullDirs = [];
    dependesDirs = ['node_provider', 'node_spider'];
    dependesFullDirs = [];
    dependesPaths = [];
    currentDirectory = path.dirname(__filename);
    constructor() {
        this.scanFrontends()
    }

    scanDependes() {
        this.dependesDirs.forEach(project => {
            const dirToScan = path.join(`.`, project);
            this.scanDirectoryRecursive(dirToScan);
        });
        this.projects.forEach(project => {
            const dirToScan = path.join(`.`, project);
            this.projectsFullDirs.push(dirToScan);
        });
    }

    scanDirectoryRecursive(directory) {
        if (fs.existsSync(directory)) {
            const files = fs.readdirSync(directory);
            files.forEach(file => {
                const filePath = path.join(directory, file);
                if (fs.statSync(filePath).isDirectory()) {
                    if (this.dependesDirs.includes(file)) {
                        this.dependesFullDirs.push(filePath);
                    }
                    this.scanDirectoryRecursive(filePath);
                }
            });
        }
    }

    scanFrontends() {
        const frontend = env.getEnv(`FRONTEND`)
        if (!frontend.startsWith(`http`)) {
            this.projects.push(frontend)
        }
    }

    getArgName(name, default_val = null) {
        const arg = this.getArgumentValue(name);
        if (arg) {
            if(typeof arg == "string"){
                return path.normalize(arg);
            }
            return arg;
        } else {
            return default_val;
        }
    }

    scanSubdirectories(directory) {
        const contents = fs.readdirSync(directory);
        for (const content of contents) {
            const absolutePath = path.join(directory, content);
            try {

                const stat = fs.statSync(absolutePath);
                if (stat.isDirectory()) {
                    if (this.dependesDirs.some(dir => content === dir)) {
                        this.requireDir.push(absolutePath);
                        this.dependesPaths.push(absolutePath);
                    } else {
                        this.scanSubdirectories(absolutePath);
                    }
                }
            } catch (e) {
                console.log(e)
            }
        }
    }

    isStartedWith(nodeCommand) {
        const args = process.argv;
        const nodeExecutable = args[0].replace(/\.[^.]+$/, '');
        return nodeExecutable.endsWith(nodeCommand);
    }
    isNodeModulesNotEmpty(directory) {
        const nodeModulesPath = path.join(directory, 'node_modules');
        if (!fs.existsSync(nodeModulesPath)) {
            return false;
        }
        return !this.isEmptyDir(nodeModulesPath);
    }
    isPackageJson(directory) {
        const filePath = path.join(directory, 'package.json');
        if (fs.existsSync(filePath)) {
            return true;
        }
        return false;
    }
    isEmptyDir(directory) {
        if (!fs.existsSync(directory)) {
            return true;
        }
        const contents = fs.readdirSync(directory);
        return contents.length == 0;
    }
    getSystemArguments() {
        const args = process.argv;
        return args;
    }
    getArgumentValue(arg_name) {
        const args = this.getSystemArguments();
        for (const arg of args) {
            if(arg == arg_name){
                return true;
            }
            const [name, value] = arg.split(/=/);
            if (name === arg_name) {
                return value;
            }
        }
        return null;
    }
    deleteDirectory(directory) {
        if (fs.existsSync(directory)) {
            const files = fs.readdirSync(directory);
            for (const file of files) {
                const filePath = path.join(directory, file);
                if (fs.lstatSync(filePath).isDirectory()) {
                    deleteDirectory(filePath);
                } else {
                    fs.unlinkSync(filePath);
                }
            }
            fs.rmdirSync(directory);
        }
    }
    runInstallInDirectories(callback) {
        this.scanDependes()
        const yarn = this.getArgName("yarn", "yarn");
        const dependesPaths = this.dependesFullDirs;
        const git = this.getArgName("git", "git");
        for (const directory of dependesPaths) {
            if (this.isEmptyDir(directory)) {
                const basename = path.basename(directory)
                const baseDir = path.dirname(directory)
                const env_key = basename.toUpperCase()
                process.chdir(baseDir);
                this.deleteDirectory(directory)
                const gitUrl = env.getEnv(env_key)
                const gitCmd = `${git} clone ${gitUrl}`
                execSync(gitCmd, { stdio: 'inherit' });
            }
        }
        const projects = this.projectsFullDirs;
        for (const directory of projects) {
            if (!this.isNodeModulesNotEmpty(directory) && this.isPackageJson(directory)) {
                process.chdir(directory);
                execSync(`${yarn} install`, { stdio: 'inherit' });
            }
        }
        const npm = this.getArgName("npm", `npm`)
        this.yarn = yarn
        this.npm = npm
        this.git = git
    }
    setStartExe(start_exec) {
        this.start_exec = start_exec
    }
    setStartCommand(start_command) {
        this.start_command = start_command
    }
    setStartFile(start_file) {
        if(start_file){
            if(!path.isAbsolute(start_file)){
                start_file = path.join(this.currentDirectory,start_file)
            }
        }
        this.start_file = start_file
    }
    setStartParameter(start_parameter) {
        this.start_parameter = start_parameter
    }
    startBy() {
        process.chdir(this.currentDirectory)
        if(!this.start_command){
            if(this.start_file){
                this.start_command = this.start_file
            }
        }
        const startCmd = `${this.start_exec} ${this.start_command} ${this.start_parameter}`
        console.log(`Start-Command: ${startCmd}`);
        execSync(startCmd, { shell: true, stdio: 'inherit' });
    }
}
console.log(`app start.`)
//** ----------- Start ----------- */
const express_bind = require('./manager/express/express_bind');
const cluster = require('./manager/cluster');
express_bind.start(3099);
cluster.initApps();
