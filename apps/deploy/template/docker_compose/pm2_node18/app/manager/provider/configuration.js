const fs = require('fs');
const path = require('path');

class Configuration {
  readEcosystemConfig(directoryPath) {
    const configFilePath = path.join(directoryPath, 'ecosystem.config.js');
    if (this.fileExists(configFilePath)) {
      const { apps } = require(configFilePath);
      if (apps?.length > 0) {
        return apps[0].name || null;
      }
    }
    return null;
  }

  getPortFromEcosystemArgs(clusterInfo) {
    const { ecosystem_config, package_json } = clusterInfo;
    const args = ecosystem_config?.apps?.[0]?.args || '';
    const portMatch = args.match(/--port (\d+)/);
    if (portMatch?.[1]) {
      return parseInt(portMatch[1], 10);
    }
    const scripts = package_json?.scripts;
    for (const script in scripts) {
      const scriptContent = scripts[script];
      const portMatch = scriptContent?.match(/--port (\d+)/);
      if (portMatch?.[1]) {
        return parseInt(portMatch[1], 10);
      }
    }

    return null;
  }

  readConfigFile(filePath) {
    return this.fileExists(filePath) ? require(filePath) : null;
  }

  fileExists(filePath) {
    return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
  }
}

const configuration = new Configuration();
module.exports = configuration;