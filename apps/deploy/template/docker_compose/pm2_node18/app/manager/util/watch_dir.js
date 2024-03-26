const fs = require('fs');
const path = require('path');
const { web_dir,template_dir } = require('../provider/local_env');
const { file,arr } = require('../../node_provider/utils_prune');
class WatchDir {
    cwdlist = [];
    error = {};
    foundDirs = new Set();
    newDirlist = []
    watchDirEvent = null

    constructor() {
    }

    get_template_dir() {
        return template_dir;
    }

    async updateDirectoryList() {
        const files = await fs.readdir(template_dir);
        this.cwdlist = [];
        for (const file of files) {
            const filePath = path.join(template_dir, file);
            const stats = await fs.stat(filePath);
            if (stats.isDirectory()) {
                this.cwdlist.push(filePath);
            }
        }
        console.log('Updated directory list:', this.cwdlist);
    }

    watchDir(callback){
        if(this.watchDirEvent){
            return
        }
        this.watchDirEvent = setInterval(async ()=>{
            await this.updateWebDirList();
            const newDirlist = this.getAndClearNewDirs()
            if(callback)callback(newDirlist)
        },1000)
    }

    async updateWebDirList() {
        const currentList = file.scanDir(web_dir);
        for (const dir of currentList) {
            if(file.isDir(dir)){
                if (!this.foundDirs.has(dir)) {
                    this.newDirlist.push(dir)
                    this.foundDirs.add(dir);
                }
            }
        }
    }

    getAndClearNewDirs() {
        const dirs = arr.copy(this.newDirlist);
        this.newDirlist = [];
        return dirs;
    }
}

module.exports = new WatchDir();
