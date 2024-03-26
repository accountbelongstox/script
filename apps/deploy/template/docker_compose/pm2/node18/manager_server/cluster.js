const fs = require('fs');
const path = require('path');
const util = require('util');
const { exec } = require('child_process');
const ecosystem_filename = `ecosystem.config.js`
const execPromise = util.promisify(exec);
const os = require('os');
const liunx_web_dir = `/www`
const windows_web_dir = `D:/programing`

class Cluster {
    error = {

    }
    constructor() {
        this.baseDir = __dirname
        this.wwwRootDir = this.getWebDir()
    }

    getWebDir(){
        const wwwRootDir = os.platform() === 'win32' ? windows_web_dir : liunx_web_dir;
        return wwwRootDir
    }

    // installApps(configPath, callback) {
    //     const configFile = require(configPath);
    //     configFile.apps.forEach((app) => {
    //         const appPath = path.join(app.cwd, app.name);
    //         const nodeModulesPath = path.join(appPath, 'node_modules');

    //         if (!fs.existsSync(nodeModulesPath)) {
    //             console.log(`Installing dependencies for ${app.name}...`);

    //             exec('yarn install', { cwd: appPath }, (error, stdout, stderr) => {
    //                 if (error) {
    //                     console.error(`Error installing dependencies for ${app.name}: ${error.message}`);
    //                     callback({ success: false, message: `Error installing dependencies for ${app.name}: ${error.message}` });
    //                 } else {
    //                     console.log(`Dependencies installed for ${app.name}`);
    //                     callback({ success: true, message: `Dependencies installed for ${app.name}` });
    //                 }
    //             });
    //         } else {
    //             console.log(`Node modules already installed for ${app.name}`);
    //             callback({ success: true, message: `Node modules already installed for ${app.name}` });
    //         }
    //     });

    //     exec(`pm2 start ${configPath}`, (error, stdout, stderr) => {
    //         if (error) {
    //             console.error(`Error starting apps: ${error.message}`);
    //             callback({ success: false, message: `Error starting apps: ${error.message}` });
    //         } else {
    //             console.log('Apps started successfully');
    //             callback({ success: true, message: 'Apps started successfully' });
    //         }
    //     });
    // }

    logMessage(name, success, message) {
        if (!this.error[name]) this.error[name] = [];
        const msg = { success, message };
        console.log(msg);
        this.error[name].push(msg);
    }

    getMessage(name) {
        if (!this.error[name]) this.error[name] = [];
        return this.error[name]
    }

    async checkAndInstallDependencies() {
        const configPath = `${this.wwwRootDir}/${ecosystem_filename}`;
        try {
            fs.accessSync(configPath, fs.constants.R_OK);
            const config = require(configPath);
            if (config.apps && Array.isArray(config.apps)) {
                for (const app of config.apps) {
                    if (app.cwd) {
                        await this.installModule(app.cwd);
                    }
                }
            } else {
                console.error('Invalid config file structure. "apps" array not found.');
            }
        } catch (error) {
            console.error(`Error reading or processing ${configPath}:`, error.message);
        }
    }

    async installModule(appPath) {
        let name = appPath.name ? appPath.name : appPath;
        const nodeModulesPath = path.join(appPath, 'node_modules');
        if (!fs.existsSync(nodeModulesPath)) {
            this.logMessage(name, true, `Installing dependencies for ${name}...`);
            try {
                const { stdout, stderr } = await execPromise('yarn install', { cwd: appPath });
                this.logMessage(name, true, `Dependencies installed for ${name}: ${stdout}`);
            } catch (error) {
                this.logMessage(name, false, `Error installing dependencies for ${name}: ${error.message}`);
            }
        }
    }

    executeCommand(command, cwd) {
        return new Promise((resolve, reject) => {
            exec(command, { cwd }, (error, stdout, stderr) => {
                if (error) {
                    this.logMessage('cluster', false, error + stdout + stderr);
                    reject(error);
                } else {
                    this.logMessage('cluster', true, error + stdout + stderr);
                    resolve(stdout);
                }
            });
        });
    }

    async installApps(configArray, callback) {
        await this.checkAndInstallDependencies()
        const installNextApp = (index) => {
            if(!configArray){
                console.log("Pm2 configuration file not found")
                return 
            }
            if (index >= configArray.length) {
                console.log('All apps installed and started successfully');
                callback({ success: true, message: 'All apps installed and started successfully' });
                return;
            }
            const appConfig = configArray[index];
            const appPath = path.join(this.wwwRootDir, appConfig.dir_name);
            const nodeModulesPath = path.join(appPath, 'node_modules');
            const installDependencies = () => {
                this.logMessage(appConfig.name, true, `Installing dependencies for ${appConfig.name}...`);
                exec('yarn install', { cwd: appPath }, (error, stdout, stderr) => {
                    if (error) {
                        this.logMessage(appConfig.name, false, `Error installing dependencies for ${appConfig.name}: ${error.message}`);
                        callback({ success: false, message: error.message });
                    } else {
                        startApp();
                    }
                });
            };
            const startApp = () => {
                this.listRunningApps(appConfig.name, (status) => {
                    if (status.success === false) {
                        this.logMessage(appConfig.name, true, `pm2 start ecosystem.config.js for ${appConfig.name}`);
                        exec(`pm2 start ${ecosystem_filename}`, { cwd: appPath }, (error, stdout, stderr) => {
                            if (error) {
                                this.logMessage(appConfig.name, false, `Error starting apps: ${error.message}` + stdout + stderr);
                                callback({ success: false, message: error.message });
                            } else {
                                this.logMessage(appConfig.name, true, 'Apps started successfully' + stdout + stderr);
                                callback({ success: true, message: 'Apps started successfully' });
                            }
                            installNextApp(index + 1);
                        });
                    } else {
                        this.logMessage(appConfig.name, true, `Exists ${appConfig.name},spiking.`);
                        installNextApp(index + 1);
                    }
                })
            };
            if (appConfig.ecosystem_config) {
                if (!this.error[appConfig.name]) this.error[appConfig.name] = [];
                if (!fs.existsSync(nodeModulesPath)) {
                    installDependencies();
                } else {
                    this.logMessage(appConfig.name, true, `Node modules already installed for ${appConfig.name}`);
                    startApp();
                }
            } else {
                this.logMessage(appConfig.name, false, `not Pm2 config.`);
                installNextApp(index + 1);
            }
        };
        setTimeout(() => {
            installNextApp(0);
        }, 3000)
    }

    listRunningApps(appName, callback) {
        exec('pm2 list', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error listing running apps: ${error.message}`);
                callback({ success: false, message: error.message });
            } else {
                const runningApps = this.parsePM2List(stdout);
                if (appName) {
                    const appStatus = this.getAppStatusByName(runningApps, appName);
                    if (appStatus) {
                        console.log(`Status of app '${appName}':`, appStatus);
                        callback({ success: true, message: `Status of app '${appName}':`, data: appStatus });
                    } else {
                        console.log(`App '${appName}' not found in running apps.`);
                        callback({ success: false, message: `App '${appName}' not found in running apps.` });
                    }
                } else {
                    console.log('Running Apps:', runningApps);
                    callback({ success: true, message: 'List of running apps:', data: runningApps });
                }
            }
        });
    }

    getAppStatusByName(runningApps, appName) {
        return runningApps.find(app => app.name === appName);
    }

    parsePM2List(pm2ListOutput) {
        const lines = pm2ListOutput.split('\n').slice(2, -1);
        const runningApps = lines.map(line => {
            const [id, name, mode, status, restarts, memory, cpu] = line.trim().split(/\s+/);
            return { id, name, mode, status, restarts, memory, cpu };
        });
        return runningApps;
    }

    getClusters() {
        try {
            const subdirectories = this.scanSubdirectories();
            const clusters = subdirectories.map(dir => this.getClusterInfo(dir));
            return clusters;
        } catch (error) {
            console.error('Error:', error.message);
            return null;
        }
    }

    scanSubdirectories() {
        const subdirectories = fs.readdirSync(this.wwwRootDir)
            .filter(item => fs.statSync(path.join(this.wwwRootDir, item)).isDirectory());

        return subdirectories;
    }

    getClusterInfo(subdirectory) {
        let name = this.readEcosystemConfig(path.join(this.wwwRootDir, subdirectory))
        name = name ? name : subdirectory
        const clusterInfo = {
            name,
            dir_name: subdirectory,
            node_modules: this.directoryExists(path.join(this.wwwRootDir, subdirectory, 'node_modules')),
            package_json: this.readPackageJson(path.join(this.wwwRootDir, subdirectory)),
            ecosystem_config: this.readConfigFile(path.join(this.wwwRootDir, subdirectory, ecosystem_filename)) ||
                this.readConfigFile(path.join(this.wwwRootDir, subdirectory, 'ecosystem.config.json')),
            pm2_config: this.readConfigFile(path.join(this.wwwRootDir, subdirectory, 'pm2.config.js')) ||
                this.readConfigFile(path.join(this.wwwRootDir, subdirectory, 'pm2.config.json')),
            logs: this.getMessage(name)

        };
        clusterInfo.port = this.getPortFromEcosystemArgs(clusterInfo);
        // clusterInfo.ecosystem_config = this.getPortFromEcosystemArgs(clusterInfo);
        return clusterInfo;
    }

    readEcosystemConfig(directoryPath) {
        const configFilePath = path.join(directoryPath, 'ecosystem.config.js');

        if (this.fileExists(configFilePath)) {
            try {
                const configContent = require(configFilePath);
                if (configContent && configContent.apps && configContent.apps.length > 0) {
                    return configContent.apps[0].name || null;
                }
            } catch (error) {
                console.error(`Error reading ${configFilePath}:`, error.message);
            }
        }

        return null;
    }

    getPortFromEcosystemArgs(clusterInfo) {
        if (clusterInfo.ecosystem_config && clusterInfo.ecosystem_config.apps && clusterInfo.ecosystem_config.apps.length) {
            if (clusterInfo.ecosystem_config.apps[0].args) {
                const args = clusterInfo.ecosystem_config.apps[0].args;
                const portMatch = args.match(/--port (\d+)/);
                if (portMatch && portMatch[1]) {
                    return parseInt(portMatch[1], 10);
                } else {
                    const packageJson = clusterInfo.package_json;
                    if (packageJson && packageJson.scripts) {
                        for (const script in packageJson.scripts) {
                            const scriptContent = packageJson.scripts[script];
                            const portMatch = scriptContent.match(/--port (\d+)/);
                            if (portMatch && portMatch[1]) {
                                return parseInt(portMatch[1], 10);
                            }
                        }
                    }
                }
            }
        }
        return null;
    }

    directoryExists(directoryPath) {
        return fs.existsSync(directoryPath) && fs.statSync(directoryPath).isDirectory();
    }

    readPackageJson(directoryPath) {
        const packageJsonPath = path.join(directoryPath, 'package.json');
        return this.fileExists(packageJsonPath) ? require(packageJsonPath) : null;
    }

    readConfigFile(filePath) {
        return this.fileExists(filePath) ? require(filePath) : null;
    }

    fileExists(filePath) {
        return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
    }
}
const cluster  = new Cluster()
module.exports = cluster;
