const fs = require('fs');
const path = require('path');
const { web_dir } = require('./local_env');
const pm2_provider = require('./pm2_provider');
const { file, log } = require('../../node_provider/utils_prune');

class Directory {
  constructor() {
    this.ecosystem_projects = new Set();
    this.nonecosystem_projects = new Set();
    this.error = {};
  }

  getClusters(subdirectories) {
    subdirectories = subdirectories || this.scanSubdirectories();
    const ecosystem_projects = subdirectories
      .map(directory => this.classifiedAsPM2Project(directory))
      .filter(clusterInfo => {
        if (clusterInfo.is_ecosystem) {
          this.ecosystem_projects.add(clusterInfo);
          return true;
        } else {
          this.nonecosystem_projects.add(clusterInfo);
          return false;
        }
      });
    return ecosystem_projects;
  }

  scanSubdirectories() {
    return fs.readdirSync(web_dir)
      .filter(item => fs.statSync(path.join(web_dir, item)).isDirectory());
  }

  classifiedAsPM2Project(subdirectory) {
    const subdirectory_dir = file.isAbsolute(subdirectory) ? subdirectory : path.join(web_dir, subdirectory);
    let name = pm2_provider.readEcosystemConfig(subdirectory_dir) || subdirectory;
    const node_modules_dir = path.join(subdirectory_dir, 'node_modules');
    const ecosystem_config = pm2_provider.getEcosystemFile(subdirectory_dir);
    const is_ecosystem = !!ecosystem_config;
    const clusterInfo = {
      name,
      dir_name: subdirectory,
      dir: subdirectory_dir,
      node_modules: file.isDir(node_modules_dir),
      is_ecosystem,
      ecosystem_config: file.readByRequire(ecosystem_config),
      ecosystem_file: ecosystem_config ? path.basename(ecosystem_config) : null,
      package_json: file.readByPackage(subdirectory_dir),
      logs: log.info(name),
      port: pm2_provider.getPortFromEcosystemArgs({ is_ecosystem, dir: subdirectory_dir }),
    };
<<<<<<< HEAD
=======

>>>>>>> origin/main
    return clusterInfo;
  }
}

const directory = new Directory();
module.exports = directory;