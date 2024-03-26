const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const app = express();
const cluster = require('./cluster');

app.use('/stylesheet', express.static(path.join(__dirname, 'stylesheet')));
let pm2Start = 0
class MyExpressApp {
  ipaddress = `0.0.0.0`
  constructor() {
    app.use(bodyParser.json());
    this.baseDir = __dirname;
    app.get('/', this.homePage.bind(this));
    app.get('/get_clusters', this.getClusters.bind(this));
    app.post('/up_cluster', this.upCluster.bind(this));
    app.post('/add_cluster', this.addCluster.bind(this));
    app.post('/reset_pm2', this.resetPM2.bind(this));
    app.post('/shutdown_pm2', this.shutdownPM2.bind(this));
    app.post('/start_down_pm2', this.startDownPM2.bind(this));
  }

  installApps(req, res) {
    const cluster_list = cluster.getClusters()
    let resinfo = cluster.installApps(cluster_list, (status) => {
      console.log(status)
    })
  }

  homePage(req, res) {
    const indexPath = path.join(this.baseDir, 'html_compile', 'index.html');
    res.sendFile(indexPath);
  }

  getClusters(req, res) {
    const cluster_list = cluster.getClusters()
    res.send(cluster_list);
  }

  upCluster(req, res) {
    res.send('Update Cluster');
  }

  addCluster(req, res) {
    res.send('Add Cluster');
  }

  resetPM2(req, res) {
    res.send('Reset PM2');
  }

  shutdownPM2(req, res) {
    res.send('Shutdown PM2');
  }

  startDownPM2(req, res) {
    res.send('Start/Stop PM2');
  }

  start(port) {
    app.listen(port, () => {
      console.log(`Express app is running on http://${this.ipaddress}:${port}`);
    });
  }
}

const myExpressApp = new MyExpressApp();
myExpressApp.start(3099);
if (pm2Start == 0) {
  pm2Start = 1
  myExpressApp.installApps();
}
