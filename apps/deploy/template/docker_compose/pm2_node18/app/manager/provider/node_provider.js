const fs = require('fs');
const path = require('path');
const which = require('which');
const Base = require('../../node_provider/base/base');
const { http } = require('../../node_provider/practicals_prune');
const { file } = require('../../node_provider/utils_prune');
const { exec, execSync } = require('child_process');
const https = require('node:https');
const readline = require('readline');
const tmpDir = '/tmp'; // 临时目录的路径
const versionNumber = ''

class NodeProvider extends Base {
    error = {}

    constructor(tmpDir) {
        super()
        this.tmpDir = tmpDir || '';
        this.versionNumber = '';
        this.nodeInstallDir = '/usr/node';
    }

    get_node_downloads() {
        return {
        }
    }

    get_version() {
        return parseFloat(process.version.slice(1));
    }

    get_version_full() {
        return process.version;
    }

    get_node_modules(appPath) {
        return path.join(appPath, "node_modules");
    }

    extract_nodeversip(appConfig) {
        const specified_node_version = appConfig.package_json?.engines?.node;
        this.warn(appConfig.name, specified_node_version);

        return specified_node_version
            ? specified_node_version.split(' ')
                .map(token => parseFloat(token.replace(/^[^\d]*(\d.*)$/, '$1')))
                .filter(number => !isNaN(number))
            : [];
    }

    extractVersionsByOut(content) {
        return content
            ? (content.match(/Expected version "([0-9 ||]+)"/)?.[1]?.split(' || ') || null)
            : null;
    }

    extractErrorsByStr(inputString) {
        return inputString
            ? inputString.split('\n')
                .filter(line => line.includes('error'))
                .map(line => line.trim()) || null
            : null;
    }
    async readVersionNumber() {
        return new Promise((resolve) => {
            const readline = require('readline').createInterface({
                input: process.stdin,
                output: process.stdout
            });
            readline.question('Enter the version number: ', (version) => {
                this.versionNumber = version;
                readline.close();
                resolve();
            });
        });
    }
    async checkAndDownloadNodeDistHtml() {
        const nodeDistHtmlPath = path.join(__dirname, 'node_dist.html');

        try {
            if (!fs.existsSync(nodeDistHtmlPath)) {
                console.log('node_dist.html not found. Downloading from https://nodejs.org/dist/...');
                await this.downloadNodeDistHtml(nodeDistHtmlPath);
                console.log('node_dist.html downloaded successfully.');
            } else {
                const stats = fs.statSync(nodeDistHtmlPath);
                const createTime = new Date(stats.birthtimeMs);
                const currentTime = new Date();
                const timeDifference = (currentTime - createTime) / (1000 * 60 * 60);

                if (timeDifference > 24) {
                    console.log('node_dist.html file older than 24 hours. Downloading from https://nodejs.org/dist/...');
                    await this.downloadNodeDistHtml(nodeDistHtmlPath);
                    console.log('node_dist.html downloaded and replaced successfully.');
                } else {
                    console.log('node_dist.html file exists and is up to date.');
                }
            }

            const filedir = path.join(nodeDistHtmlPath, 'node_dist.html');
            fs.readFile(filedir, 'utf8', async (err, data) => {
                if (err) {
                    console.error('Error reading file:', err);
                    return;
                }

                // 使用正则表达式匹配版本号
                const versionPattern = /\bv(\d+\.\d+)\.\d+\b/g;
                const versionsList = data.match(versionPattern);

                if (versionsList) {
                    const latestVersionsList = await this.getLatestVersionFromList(versionsList);
                    console.log('Latest versions for each major version:', latestVersionsList);
                    this.readVersionNumber()
                    const rl = readline.createInterface({
                        input: process.stdin,
                        output: process.stdout
                    });

                    rl.question('Enter the major version number: ', (answer) => {
                        rl.close();
                        const majorNumber = parseInt(answer);
                        if (isNaN(majorNumber)) {
                            console.log('Invalid input. Please enter a valid integer.');
                        } else {
                            console.log(`Major version number entered: ${majorNumber}`);
                            this.getLatestVersionByMajor(majorNumber, latestVersionsList)
                                .then((resolvedValue) => {
                                    console.log(resolvedValue);
                                    const version = resolvedValue;
                                    console.log("version", version);
                                    this.installNode(version)
                                    const projectName = 'faker'
                                    const startScript = 'main.js';
                                    const nodePath = '/usr/node/' + version + '/node-' + version + '-linux-x64' + '/bin/node';
                                    const command = `${nodePath} ${startScript}`;
                                    exec(command, (error, stdout, stderr) => {
                                        if (error) {
                                            console.error(`执行命令时发生错误：${error}`);
                                            return;
                                        }
                                        console.log(`${projectName}`);
                                    });
                                    this.getNpmByVersion(version);
                                    this.getYarnByVersion(version);
                                    this.getPm2ByVersion(version);
                                    // 定义项目目录、项目类型、启动参数和 Node.js 版本
                                   let projectDir = '/mnt/d/programing/faker/';
                                   let projectType = 'vue'; // 项目类型
                                   let startParameter = 'dev'; // 启动参数
                                //    let nodeVersion = '18'; // Node.js 版本
                                   this.runByPm2(projectDir, projectType, startParameter, version);
                                })
                                .catch((error) => {
                                    console.error('An error occurred:', error);
                                });

                        }

                    });

                } else {
                    console.log('No versions found in the file.');
                }
            });
        } catch (error) {
            console.error('Error checking and downloading node_dist.html:', error);
        }
    }
    async getLatestVersionFromList(versionsList) {
        const latestVersionsMap = {};

        for (const version of versionsList) {
            const versionNumber = version.replace(/^v/, '');
            const [major, minor, patch] = versionNumber.split('.').map(Number);
            const currentMajor = latestVersionsMap[major];

            if (!currentMajor || minor > currentMajor.minor || (minor === currentMajor.minor && patch > currentMajor.patch)) {
                latestVersionsMap[major] = { minor, patch, version };
            }
        }

        const latestVersions = Object.values(latestVersionsMap).map(({ version }) => version);
        return latestVersions;
    }

    async downloadNodeDistHtml(filePath) {
        try {
            const url = 'https://nodejs.org/dist/';
            const fileName = 'node_dist.html';
            const fileSavePath = path.join(filePath, fileName);
            await http.download(url, fileSavePath);
            console.log(`Downloaded node_dist.html to ${fileSavePath}.`);
        } catch (error) {
            console.error('Error downloading node_dist.html:', error);
            throw error;
        }
    }
    async getLatestVersionByNumber(versionNumber, versionsList) {
        let maxVersion = null;

        for (const version of versionsList) {
            if (version.startsWith(versionNumber)) {
                if (!maxVersion || this.compareVersions(version, maxVersion) > 0) {
                    maxVersion = version;
                }
            }
        }

        return maxVersion;
    }
    async getLatestVersionByMajor(majorNumber, latestVersionsList) {
        for (const version of latestVersionsList) {
            const versionNumber = version.replace(/^v/, '');
            const [major, ,] = versionNumber.split('.').map(Number);

            if (major === majorNumber) {
                return version;
            }
        }

        return null; // 如果未找到匹配的大版本号，返回 null
    }
    compareVersions(versionA, versionB) {
        const partsA = versionA.split('.').map(Number);
        const partsB = versionB.split('.').map(Number);

        for (let i = 0; i < Math.max(partsA.length, partsB.length); i++) {
            const partA = partsA[i] || 0;
            const partB = partsB[i] || 0;

            if (partA !== partB) {
                return partA - partB;
            }
        }

        return 0;
    }



    async installNode(version) {
        const nodeDir = path.join(this.nodeInstallDir, version);

        if (fs.existsSync(nodeDir)) {
            console.log(`Node version ${version} is already installed at ${nodeDir}`);
            return;
        }

        try {
            if (!fs.existsSync(this.nodeInstallDir)) {
                fs.mkdirSync(this.nodeInstallDir, { recursive: true });
            }

            // 创建目标目录
            if (!fs.existsSync(nodeDir)) {
                fs.mkdirSync(nodeDir, { recursive: true });
            }

            const downloadUrl = `https://nodejs.org/dist/${version}/node-${version}-linux-x64.tar.gz`;
            const downloadPath = path.join(this.nodeInstallDir, `node-${version}-linux-x64.tar.gz`);

            console.log(`Downloading Node.js ${version} from ${downloadUrl}...`);
            await this.downloadFile(downloadUrl, downloadPath);
            console.log(`Node.js ${version} downloaded successfully.`);

            console.log(`Extracting Node.js ${version} to ${nodeDir}...`);
            await this.extractFile(downloadPath, nodeDir);
            console.log(`Node.js ${version} extracted successfully.`);

            console.log(`Node.js ${version} installed successfully at ${nodeDir}`);
        } catch (error) {
            console.error(`Error installing Node.js ${version}:`, error);
        }
    }


    downloadFile(url, dest) {
        return new Promise((resolve, reject) => {
            const file = fs.createWriteStream(dest);
            https.get(url, response => {
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    resolve();
                });
            }).on('error', error => {
                fs.unlink(dest, () => reject(error));
            });
        });
    }

    extractFile(src, destDir) {
        return new Promise((resolve, reject) => {
            const tarProcess = exec(`tar -xzf ${src} -C ${destDir}`, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                } else {
                    resolve();
                }
            });

            tarProcess.stdin.end();
        });
    }
    getNodeByVersion(version) {
        const system = process.platform;
        let nodeInstallPath = '';

        switch (system) {
            case 'win32':
                nodeInstallPath = path.join('D:', 'lang_compiler', 'node',version, `node-${version}-win-x64`);
                break;
            case 'linux':
                nodeInstallPath = path.join('/usr', 'node',version, `node-${version}-linux-x64`);
                break;
            default:
                throw new Error(`Unsupported operating system: ${system}`);
        }

        return nodeInstallPath;
    }

    getNpmByVersion(version) {
        const nodeInstallPath = this.getNodeByVersion(version);

        let npmGlobalPath;
        switch (process.platform) {
            case 'win32':
                npmGlobalPath = nodeInstallPath.replace(/node-v[^\\]+-win-x64/, 'npm-global');
                break;
            case 'linux':
                npmGlobalPath = nodeInstallPath.replace(/node-v[^\/]+-linux-x64/, 'npm-global');
                break;
            default:
                throw new Error(`Unsupported operating system: ${process.platform}`);
        }

        // 使用npm命令设置全局路径
        try {
            execSync(`npm config set prefix "${npmGlobalPath}"`, { stdio: 'inherit' });
            console.log(`npm global path set to: ${npmGlobalPath}`);
        } catch (error) {
            console.error('Error setting npm global path:', error.message);
        }
    }

    getYarnByVersion(version) {
        const nodeInstallPath = this.getNodeByVersion(version);
        let yarnPath = path.join(nodeInstallPath, 'bin', 'yarn');

        if (process.platform === 'win32') {
            yarnPath += '.cmd';
        }

        if (fs.existsSync(yarnPath)) {
            console.log(`Yarn found at: ${yarnPath}`);
            return yarnPath;
        } else {
            console.log("Yarn not found. Installing globally...");
            try {
                execSync('npm install -g yarn', { stdio: 'inherit' });
                console.log('Yarn installed globally.');

                // 再次检查Yarn是否存在
                yarnPath = path.join(this.getYarnPath());
                if (yarnPath) {
                    console.log(`Yarn global path: ${yarnPath}`);
                    return yarnPath;
                } else {
                    throw new Error('Failed to locate Yarn after installation.');
                }
            } catch (error) {
                console.error('Error installing Yarn:', error.message);
                return null;
            }
        }
    }

    getYarnPath() {
        try {
            return which.sync('yarn');
        } catch (error) {
            console.error('Error finding Yarn path:', error.message);
            return null;
        }
    }

    getPm2ByVersion(version) {
        const nodeInstallPath = this.getNodeByVersion(version);
        let pm2Path = path.join(nodeInstallPath, 'bin', 'pm2');

        if (process.platform === 'win32') {
            pm2Path += '.cmd';
        }
        if (fs.existsSync(pm2Path)) {
            console.log(`PM2 found at: ${pm2Path}`);
            return pm2Path;
        } else {
            console.log("PM2 not found. Installing globally...");
            try {
                execSync('sudo npm install -g pm2', { stdio: 'inherit' });
                console.log('PM2 installed globally.');
                pm2Path = this.getPM2Path()
                if (pm2Path) {
                    console.log(`PM2 global path: ${pm2Path}`);
                    return pm2Path;
                } else {
                    throw new Error('Failed to locate PM2 after installation.');
                }
            } catch (error) {
                console.error('Error installing PM2:', error.message);
                return null;
            }
        }
    }

    getPM2Path() {
        try {
            return which.sync('pm2');
        } catch (error) {
            console.error('Error finding PM2 path:', error.message);
            return null;
        }
    }
    runByPm2(projectDir, projectType, start_parameter, node_version) {
        // 根据传入的 projectType 确定模板文件路径
        console.log("__dirname:",__dirname);
        let templatePath = path.join(__dirname, 'templates','ecosystem.config.js');

        //检查模板文件是否存在
        if (!fs.existsSync(templatePath)) {
            console.error(`Template for ${projectType} does not exist.`);
            return;
        }

        // 读取模板文件内容
        const templateContent = fs.readFileSync(templatePath, 'utf-8');

        // 构建目标文件路径
        const targetPath = path.join(projectDir, 'ecosystem.config.js');

        // 写入目标文件
        fs.writeFileSync(targetPath, templateContent);
 
        console.log(`Generated ecosystem.config.js in ${targetPath}`);

        // 获取 Node.js 安装路径
        const nodeInstallPath = this.getNodeByVersion(node_version);
        const pm2Command = '/usr/bin/pm2';
        // const pm2Command = path.join(nodeInstallPath, 'bin', 'pm2');

        // 使用 pm2 启动项目
        let command  = `sudo  ${pm2Command} start ${targetPath} --name ${projectType}`;

        // 执行启动命令
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error running project by PM2: ${error.message}`);
            } else {
                console.log(`Project started using Node.js ${node_version} and PM2.`);
            }
        });
    }
}

const node_provider = new NodeProvider(tmpDir);
module.exports = node_provider;


