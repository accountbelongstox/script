const fs = require('fs');
const path = require('path');
class Tool {
  constructor() {
    this.baseDir = path.dirname(__dirname);
  }

  getBaseDir() {
    return this.baseDir;
  }

  joinPath(...paths) {
    return path.join(this.baseDir, ...paths);
  }

  scanDirectories(directory = this.baseDir) {
    const absolutePath = path.isAbsolute(directory) ? directory : this.joinPath(directory);

    try {
      const subDirectories = fs.readdirSync(absolutePath)
        .filter(item => fs.statSync(path.join(absolutePath, item)).isDirectory())
        .map(item => path.join(absolutePath, item));

      return subDirectories;
    } catch (error) {
      console.error(`Error scanning directory: ${absolutePath}`, error);
      return [];
    }
  }

  generateDefaultJSON(options) {
    const defaultOptions = {
      name: 'my-nuxtjs-app',
      exec_mode: 'cluster',
      instances: 2,
      cwd: '/var/www',
      script: './node_modules/nuxt-start/bin/nuxt-start.js',
      args: '-c /var/www/nuxt.config.js',
      ...options
    };
    return defaultOptions;
  }

  readOrCreateJSON(filePath) {
    try {
      const data = fs.existsSync(filePath) ? JSON.parse(fs.readFileSync(filePath, 'utf-8')) : {};
      return data;
    } catch (error) {
      console.error(`Error reading or creating JSON file: ${filePath}`, error);
      return {};
    }
  }
}

const tool = new Tool()
module.exports = tool;