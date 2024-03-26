const fs = require('fs');
const { execSync } = require('child_process');
const { web_dir } = require('../provider/local_env');
const node_provider = require('../provider/node_provider');
const { plattool, file, fpath } = require('../../node_provider/utils_prune');
const Base = require('../../node_provider/base/base');

class NpmAction extends Base {
    error = {}
    constructor() {
        super();
    }

    async installPackage(packageManager, directoryPath = null, packageName = "") {
        const logname = fpath.get_base_name(directoryPath ? directoryPath : packageName);
        this.successLog(`Using ${packageManager} to install ${logname} from ${directoryPath} path`);
        const cmdResult = await plattool.execCmd(`${packageManager} install ${packageName}`, true, directoryPath, logname);
        return {
            success: cmdResult.success,
            expected_versions: node_provider.extractVersionsByOut(cmdResult.stdout),
            error: node_provider.extractErrorsByStr(cmdResult.stdout),
            stdout: cmdResult.stdout
        };
    }

    async npm_install_global(packageName) {
        return await this.installPackage('npm', null, packageName);
    }

    async yarn_add_global(packageName) {
        return await this.installPackage('yarn global add', null, packageName);
    }

    async yarn_install(directoryPath) {
        return await this.installPackage('yarn', directoryPath);
    }

    async npm_install(directoryPath) {
        return await this.installPackage('npm', directoryPath);
    }


    async installModule(appPath) {
        let name = appPath.name ? appPath.name : appPath;
        const nodeModulesPath = path.join(appPath, 'node_modules');
        if (!fs.existsSync(nodeModulesPath)) {
            this.infoLog(name, true, `Installing dependencies for ${name}...`);
            try {
                const { stdout, stderr } = await execPromise('yarn install', { cwd: appPath });
                this.infoLog(name, true, `Dependencies installed for ${name}: ${stdout}`);
            } catch (error) {
                this.infoLog(name, false, `Error installing dependencies for ${name}: ${error.message}`);
            }
        }
    }
}

const npm_action = new NpmAction()
module.exports = npm_action;
