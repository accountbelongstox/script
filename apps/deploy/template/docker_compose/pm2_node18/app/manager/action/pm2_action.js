
const fs = require('fs');
const path = require('path');
const { web_dir } = require('../provider/local_env');
const npm_action = require('../action/npm_action');
const { plattool, file, fpath, arr, strtool } = require('../../node_provider/utils_prune');
const node_provider = require('../provider/node_provider');
const pm2_provider = require('../provider/pm2_provider');
const Base = require('../../node_provider/base/base');
const node_action = require('./node_action');
const directory = require('../provider/directory');
class Ecosystem extends Base {
    projectArray = []

    constructor() {
        super();
    }
    isRunningByPm2(name) {
        const pm2_list = pm2_provider.getAllRunningByPm2()
        for (const item of pm2_list) {
            if (item.name === name) {
                return item;
            }
        }
        return null;
    }

    addToProjectArray(value) {
        if (Array.isArray(value)) {
            this.projectArray = this.projectArray.concat(value);
        } else {
            this.projectArray.push(value);
        }
        if (this.projectArray.length) {
            this.startAllApps((result) => {
                console.log(`result`, result);
            });
        }
    }

    getFromProjectArray() {
        if (this.projectArray.length > 0) {
            return this.projectArray.shift();
        } else {
            return null;
        }
    }

    async startAllApps(callback, step_callback) {
        if (this.startAllAppsIsStarted) {
            return
        }
        this.startAllAppsIsStarted = true
        const installNextApp = async () => {
            const appConfig = this.getFromProjectArray();
            if (!appConfig) {
                this.infoLog('All apps installed and started successfully');
                if (callback) callback(true, 'All apps installed and started successfully');
                this.startAllAppsIsStarted = false
                return;
            }
            if (!node_action.check_node_version(appConfig)) {
                this.infoLog(`The current project node version does not match`)
                await installNextApp();
            } else {
                const app_dir = appConfig.dir;
                const modules_dir = node_provider.get_node_modules(app_dir);
                if (appConfig.is_ecosystem) {
                    if (!this.error[appConfig.name]) this.error[appConfig.name] = [];
                    if (!fs.existsSync(modules_dir)) {
                        this.infoLog(`Installing dependencies for ${appConfig.name}...`, appConfig.name);
                        const status = await npm_action.yarn_install(app_dir);
                        let { success, expected_versions, error, stdout } = status;
                        let message;
                        if (success) {
                            message = 'Apps started successfully' + stdout;
                        } else {
                            message = `Error starting apps: ${error ? error.message : 'Unknown error'}` + stdout;
                            return await installNextApp();
                        }
                        this.infoLog(message, appConfig.name);
                        if (step_callback) step_callback(success, message);
                    }
                    this.infoLog(`Node modules already installed for ${appConfig.name}`, appConfig.name);
                    this.startPm2ByAppConfig(appConfig, app_dir, async () => {
                        await installNextApp();
                    });
                } else {
                    this.infoLog(`not Pm2 config.`, appConfig.name);
                    await installNextApp();
                }
            }
        };
        setTimeout(async () => {
            await installNextApp();
        }, 300);
    }

    startPm2ByAppConfig(appConfig, callback) {
        if (strtool.isStr(appConfig)) {
            appConfig = directory.classifiedAsPM2Project(appConfig)
        }
        const app_dir = appConfig.dir;
        const run = this.isRunningByPm2(appConfig.name)
        if (!run) {
            plattool.cmdSync(`pm2 start ${appConfig.ecosystem_file}`, true, app_dir)
        } else {
            this.successLog(`Exists ${appConfig.name} running by pm2,spiking.`, appConfig.name);
            if (callback && typeof callback === 'function') {
                callback();
            }
        }
    }

    stopPm2ByAppConfig(appConfig) {
        if (strtool.isStr(appConfig)) {
            appConfig = directory.classifiedAsPM2Project(appConfig)
        }
        const runningApp = this.isRunningByPm2(appConfig.name);
        if (runningApp) {
            const pm2Id = runningApp.id;
            plattool.cmdSync(`pm2 stop ${pm2Id}`, true);
            plattool.cmdSync(`pm2 delete ${pm2Id}`, true);
            this.successLog(`PM2 ${appConfig.name} stopped successfully.`, appConfig.name);
            return true
        } else {
            return false
        }
    }

    deletePm2ByAppConfig(appConfig) {
        if (strtool.isStr(appConfig)) {
            appConfig = directory.classifiedAsPM2Project(appConfig);
        }
        const runningApp = this.isRunningByPm2(appConfig.name);
        if (runningApp) {
            const pm2Id = runningApp.id;
            plattool.cmdSync(`pm2 stop ${pm2Id}`, true);
            plattool.cmdSync(`pm2 delete ${pm2Id}`, true);
            this.successLog(`PM2 ${appConfig.name} stopped and deleted successfully.`, appConfig.name);
            return true;
        } else {
            this.infoLog(`PM2 process ${appConfig.name} is not running. Skipping deletion.`, appConfig.name);
            return false;
        }
    }

    getLogsByAppConfig(appConfig) {
        if (strtool.isStr(appConfig)) {
            appConfig = directory.classifiedAsPM2Project(appConfig);
        }
        const runningApp = this.isRunningByPm2(appConfig.name);
        if (runningApp) {
            const pm2Id = runningApp.id;
            const logs = plattool.cmdSync(`pm2 logs ${pm2Id}`, true);
            this.infoLog(`Logs for PM2 process ${appConfig.name}:\n${logs}`, appConfig.name);
            return logs;
        } else {
            this.infoLog(`PM2 process ${appConfig.name} is not running. Cannot retrieve logs.`, appConfig.name);
            return null;
        }
    }

}



const ecosystem = new Ecosystem();
module.exports = ecosystem;



