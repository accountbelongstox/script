
const { exec } = require('child_process');

class SystemTool {
  executeCommand(command, cwd) {
    return new Promise((resolve, reject) => {
      exec(command, { cwd }, (error, stdout, stderr) => {
        error ? reject(error) : resolve(stdout + stderr);
      });
    });
  }

  async listRunningApps(appName) {
    const pm2ListOutput = await this.executeCommand('pm2 list');
    const runningApps = this.parsePM2List(pm2ListOutput);

    if (appName) {
      const appStatus = this.getAppStatusByName(runningApps, appName);
      const message = appStatus
        ? [`Status of app '${appName}':`, appStatus]
        : [`App '${appName}' not found in running apps.`];

      console.log(...message);
      return { success: !!appStatus, message, data: appStatus || null };
    } else {
      console.log('Running Apps:', runningApps);
      return { success: true, message: 'List of running apps:', data: runningApps };
    }
  }

  getAppStatusByName(runningApps, appName) {
    return runningApps.find(app => app.name === appName);
  }

  parsePM2List(pm2ListOutput) {
    return pm2ListOutput
      .split('\n')
      .slice(2, -1)
      .map(line => {
        const [id, name, mode, status, restarts, memory, cpu] = line.trim().split(/\s+/);
        return { id, name, mode, status, restarts, memory, cpu };
      });
  }
}

const system_tool = new SystemTool();
module.exports = system_tool;

