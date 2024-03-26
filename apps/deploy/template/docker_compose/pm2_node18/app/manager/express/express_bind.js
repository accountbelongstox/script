const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const app = express();
const cluster = require('../cluster');
const pm2_action = require('../action/pm2_action');
const pm2_provider = require('../provider/pm2_provider');
const winston = require('winston');
const { plattool } = require('../../node_provider/utils_prune');
const { exec } = require('child_process');
const fs = require('fs');
const { promisify } = require('util');
const execAsync = promisify(exec);
const semver = require('semver');
// app.use('/stylesheet', express.static(path.join(__dirname, 'stylesheet')));

class ExpressBind {
  ipaddress = `0.0.0.0`
  constructor() {
    app.use(bodyParser.json());
    this.baseDir = __dirname;
    app.get('/get_clusters', this.getClusters.bind(this));
    app.get('/up_cluster', this.upCluster.bind(this));
    app.get('/add_cluster', this.addCluster.bind(this));
    app.get('/reset_pm2', this.resetPM2.bind(this));
    app.get('/shutdown_pm2', this.shutdownPM2.bind(this));
    app.get('/start_down_pm2', this.startDownPM2.bind(this));
  }

  getClusters(req, res) {
    const cluster_list = pm2_provider.getAllRunningByPm2()
    res.send(cluster_list);
  }
  
  // upCluster(req, res) {
  //   const clusterName = pm2_provider.getAllRunningByPm2(() => {

  //   }) // 假设集群名称为 "faker"
  //   const appConfigs = pm2_provider.getAppConfigsForCluster(clusterName);

  //   if (appConfigs.length === 0) {
  //     res.send('No Node projects to start.');
  //     return;
  //   }

  //   const startPromises = appConfigs.map((appConfig) => {
  //     return new Promise((resolve) => {
  //       const ecosystemFilePath = pm2_provider.getEcosystemFile(appConfig.dir);
  //       if (!ecosystemFilePath) {
  //         console.error(`Ecosystem file not found for ${appConfig.name}`);
  //         resolve();
  //         return;
  //       }

  //       plattool.cmdAsync(`pm2 start ${ecosystemFilePath}`, true, appConfig.dir)
  //         .then(() => {
  //           console.log(`Node project ${appConfig.name} started successfully.`);
  //           resolve();
  //         })
  //         .catch((error) => {
  //           console.error(`Error starting Node project ${appConfig.name}:`, error);
  //           resolve();
  //         });
  //     });
  //   });

  //   Promise.all(startPromises)
  //     .then(() => {
  //       res.send('All Node projects started successfully.');
  //     })
  //     .catch((error) => {
  //       console.error('Error starting Node projects:', error);
  //       res.status(500).send('Error starting Node projects.');
  //     });
  // }




  addCluster(req, res) {

    const basePath = "/mnt/d/programing/";
    const clusterName = pm2_provider.gfindProjectNameWithEcosystemFile(basePath);
    console.log("clusterName:", clusterName)
    if (!clusterName || typeof clusterName !== 'string') {
      res.status(400).send('Invalid cluster name.');
      return;
    }
    const clusterDir = path.join(basePath, clusterName); // 构建集群目录路径

    // 检查指定文件夹中是否存在ecosystem.config.js文件
    const ecosystemFilePath = pm2_provider.getEcosystemFile(clusterDir);
          console.log(ecosystemFilePath)
    if (!ecosystemFilePath) {
      res.send('No ecosystem.config.js file found in the specified cluster folder.');
      return;
    }

    // 获取项目名称
    const projectName = pm2_provider.readEcosystemConfig(clusterDir);

    if (!projectName) {
      res.send('Failed to read project name from ecosystem.config.js file.');
      return;
    }

    // 启动项目
    plattool.cmdAsync(`pm2 start ${ecosystemFilePath}`, true, clusterDir)
      .then(() => {
        console.log(`Project ${projectName} started successfully.`);
        res.send(`Project ${projectName} started successfully.`);
      })
      .catch((error) => {
        console.error(`Error starting project ${projectName}:`, error);
        res.status(500).send(`Error starting project ${projectName}.`);
      });
  }
async upCluster(req, res) {
    const basePath = "/mnt/d/programing/";
    const clusterName = pm2_provider.gfindProjectNameWithEcosystemFile(basePath);

    if (!clusterName || typeof clusterName !== 'string') {
        res.status(400).send('Invalid cluster name.');
        return;
    }

    const clusterDir = path.join(basePath, clusterName); // 构建集群目录路径

    const ecosystemFilePath = pm2_provider.getEcosystemFile(clusterDir);

    if (!ecosystemFilePath) {
        res.send('No ecosystem.config.js file found in the specified cluster folder.');
        return;
    }

    const projectName = pm2_provider.readEcosystemConfig(clusterDir);

    if (!projectName) {
        res.send('Failed to read project name from ecosystem.config.js file.');
        return;
    }

    try {
        // 获取项目所需的 Node.js 版本
        const requiredNodeVersion = await getRequiredNodeVersion(clusterDir);

        // 获取当前系统安装的 Node.js 版本
        const installedNodeVersion = await getInstalledNodeVersion();

        // 检查 Node.js 版本是否满足要求
        if (!semver.satisfies(installedNodeVersion, requiredNodeVersion)) {
            // 更新 Node.js
            await updateNodeVersion(requiredNodeVersion);
        }

        // 启动项目
        await plattool.cmdAsync(`pm2 start ${ecosystemFilePath}`, true, clusterDir);
        console.log(`Project ${projectName} started successfully.`);
        res.send(`Project ${projectName} started successfully.`);
    } catch (error) {
        console.error(`Error starting project ${projectName}:`, error);
        res.status(500).send(`Error starting project ${projectName}.`);
    }
}

async  getRequiredNodeVersion(clusterDir) {
  const packageJsonPath = path.join(clusterDir, 'package.json');
  try {
      // 读取 package.json 文件
      const packageJsonData = await fs.readFile(packageJsonPath, 'utf-8');
      const packageJson = JSON.parse(packageJsonData);

      // 检查是否定义了 engines.node 字段
      if (packageJson.engines && packageJson.engines.node) {
          return packageJson.engines.node;
      } else {
          throw new Error('Node.js version requirement is not defined in package.json.');
      }
  } catch (error) {
      throw new Error(`Error reading package.json file: ${error.message}`);
  }
}

async getInstalledNodeVersion() {
    const { stdout, stderr } = await execAsync('node -v');
    if (stderr) {
        throw new Error(stderr);
    }
    return stdout.trim().replace('v', '');
}


async updateNodeVersion(requiredVersion) {
    try {
        // 使用 nvm 安装所需的 Node.js 版本
        const command = `nvm install ${requiredVersion}`;
        const { stdout, stderr } = await execAsync(command);

        if (stderr) {
            throw new Error(stderr);
        }

        console.log(stdout);

        // 设置安装的 Node.js 版本为默认版本
        await setDefaultNodeVersion(requiredVersion);

    } catch (error) {
        throw new Error(`Error updating Node.js version: ${error.message}`);
    }
}

async setDefaultNodeVersion(version) {
    try {
        // 使用 nvm 设置默认的 Node.js 版本
        const command = `nvm alias default ${version}`;
        const { stdout, stderr } = await execAsync(command);

        if (stderr) {
            throw new Error(stderr);
        }

        console.log(stdout);
    } catch (error) {
        throw new Error(`Error setting default Node.js version: ${error.message}`);
    }
}



  resetPM2(req, res) {
    const runningApps = pm2_provider.getAllRunningByPm2();

    if (runningApps.length === 0) {
      res.send('No running PM2 processes to reset.');
      return;
    }

    const resetPromises = runningApps.map((app) => {
      const pm2Id = app.id;
      return new Promise((resolve) => {
        plattool.cmdAsync(`pm2 restart ${pm2Id}`)
          .then(() => {
            console.log(`PM2 process ${app.name} restarted successfully.`);
            resolve();
          })
          .catch((error) => {
            console.error(`Error restarting PM2 process ${app.name}:`, error);
            resolve();
          });
      });
    });

    Promise.all(resetPromises)
      .then(() => {
        res.send('PM2 processes reset successfully.');
      })
      .catch((error) => {
        console.error('Error resetting PM2 processes:', error);
        res.status(500).send('Internal Server Error');
      });
  }


  shutdownPM2(req, res) {
    const runningApps = pm2_provider.getAllRunningByPm2();

    if (runningApps.length === 0) {
      res.send('No running PM2 processes to shutdown.');
      return;
    }

    runningApps.forEach((app) => {
      const pm2Id = app.id;
      plattool.cmdSync(`pm2 stop ${pm2Id}`, true);
      plattool.cmdSync(`pm2 delete ${pm2Id}`, true);
      console.log(`PM2 process ${app.name} stopped and deleted successfully.`);
    });

    res.send('PM2 processes shutdown successfully.');
  }



  startDownPM2(req, res) {
    const runningApps = pm2_provider.getAllRunningByPm2();

    if (runningApps.length === 0) {
      res.send('No running PM2 processes to restart.');
      return;
    }

    const restartPromises = runningApps.map((app) => {
      const pm2Id = app.id;
      return new Promise((resolve) => {
        exec(`pm2 restart ${pm2Id}`, (error) => {
          if (error) {
            console.error(`Error restarting PM2 process ${app.name}:`, error);
          } else {
            console.log(`PM2 process ${app.name} restarted successfully.`);
          }
          resolve();
        });
      });
    });

    Promise.all(restartPromises)
      .then(() => {
        res.send('PM2 processes restarted successfully.');
      })
      .catch((error) => {
        console.error('Error restarting PM2 processes:', error);
        res.status(500).send('Internal Server Error');
      });
  }




  start(port = 3000) {
    app.listen(port, () => {
      console.log(`Express app is running on http://${this.ipaddress}:${port}`);
    });
  }
}

const express_bind = new ExpressBind()
module.exports = express_bind;
