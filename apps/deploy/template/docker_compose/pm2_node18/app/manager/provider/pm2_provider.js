const fs = require('fs');
const path = require('path');
const { plattool } = require('../../node_provider/utils_prune');
class Pm2Provider {
    error = {}

    constructor() {
        this.clustersDir = path.join(__dirname, 'clusters');

    }

    getAllRunningByPm2() {
        const pm2_list = plattool.cmdSync('pm2 list', true);
        const lines = pm2_list.split('\n');
        const filteredLines = lines.filter(line => /[a-zA-Z0-9]/.test(line));
        const splitLines = filteredLines.map(line => line.split('│').map(part => part.trim()).slice(1));
        const keys = splitLines[0];
        const objects = splitLines.slice(1).map(line => {
            const obj = {};
            line.forEach((value, index) => {
                obj[keys[index]] = value;
            });
            return obj;
        });
        return objects
    }
    gfindProjectNameWithEcosystemFile(basePath) {
        const files = fs.readdirSync(basePath);
        for (const file of files) {
            const filePath = path.join(basePath, file);
            if (fs.statSync(filePath).isDirectory()) {
                const ecosystemFilePath = path.join(filePath, 'ecosystem.config.js');
                if (fs.existsSync(ecosystemFilePath)) {
                    return file; // 返回包含 ecosystem.config.js 的文件夹名称
                }
            }
        }
        return null; // 未找到含有 ecosystem.config.js 的项目
    }
    
    getEcosystemFile(directoryPath) {
        const ecosystemFilePath = path.join(directoryPath, 'ecosystem.config.js');
        if (fs.existsSync(ecosystemFilePath)) {
            return ecosystemFilePath;
        }
        const ecosystemAFilePath = path.join(directoryPath, 'ecosystem-config.js');
        if (fs.existsSync(ecosystemAFilePath)) {
            return ecosystemAFilePath;
        }
        let pm2ConfigPath = path.join(directoryPath, 'pm2.config.js');
        if (fs.existsSync(pm2ConfigPath)) {
            return pm2ConfigPath;
        }
        pm2ConfigPath = path.join(directoryPath, 'pm2.config.json');
        if (fs.existsSync(pm2ConfigPath)) {
            return pm2ConfigPath;
        }
        let ecosystemJsonPath = path.join(directoryPath, 'ecosystem.json');
        if (fs.existsSync(ecosystemJsonPath)) {
            return ecosystemJsonPath;
        }
        ecosystemJsonPath = path.join(directoryPath, 'ecosystem.config.json');
        if (fs.existsSync(ecosystemJsonPath)) {
            return ecosystemJsonPath;
        }
        ecosystemJsonPath = path.join(directoryPath, 'ecosystem-config.json');
        if (fs.existsSync(ecosystemJsonPath)) {
            return ecosystemJsonPath;
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

    readEcosystemConfig(directoryPath) {
        const configFilePath = this.getEcosystemFile(directoryPath);
        if (configFilePath) {
            try {
                const configContent = require(configFilePath);
                if (configContent && configContent.apps && configContent.apps.length > 0) {
                    return configContent.apps[0].name || null;
                }
            } catch (error) {
                console.error(`Error ecosystem-reading ${configFilePath}:`, error.message);
            }
        }
        return null;
    }

    async checkPm2configIncludeApp(configPath) {
        try {
            fs.accessSync(configPath, fs.constants.R_OK);
            const config = require(configPath);
            if (config.apps && Array.isArray(config.apps)) {
                for (const app of config.apps) {
                    if (app.cwd) {
                        return true
                    }
                }
            } else {
                console.error('Invalid config file structure. "apps" array not found.');
            }
        } catch (error) {
            console.error(`Error reading or processing ${configPath}:`, error.message);
        }
        return false
    }


    

 
    getAppConfigsForCluster(clusterName) {
        const basePath = "/mnt/d/programing/";
        const clusterDir = path.join(basePath, clusterName);
        const appConfigFiles = fs.readdirSync(clusterDir).filter(file => file.endsWith('.js')); // 修改此处为 .js
        const appConfigs = appConfigFiles.map(file => {
            const filePath = path.join(clusterDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            return content; 
        });
       
        return appConfigs;
    }
    
    
    

    

    
}

const pm2_provider = new Pm2Provider()
module.exports = pm2_provider;
