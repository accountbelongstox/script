const path = require('path');
const os = require('os');

const app_dir = path.join(__dirname, '..');
const root_dir = path.join(app_dir, '..');
const template_dir = path.join(app_dir, 'template');

const { plattool } = require('../../node_provider/utils_prune');

const wsl_web_dir = "/mnt/d/programing/";
const liunx_web_dir = "/www/programings";
const windows_web_dir = "D:/programings";
let web_dir;

if (plattool.isWsl()) {
    web_dir = wsl_web_dir;
} else if (os.platform().toLowerCase().includes("linux")) {
    web_dir = liunx_web_dir;
} else if (os.platform() === "win32") {
    web_dir = windows_web_dir;
} else {
    console.error('Unsupported platform');
}

module.exports = {
  app_dir,
  root_dir,
  template_dir,
  web_dir,
  wsl_web_dir,
  liunx_web_dir,
  windows_web_dir,
};
