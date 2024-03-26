const fs = require('fs');
const path = require('path');
const envPath = path.resolve(__dirname, '.env');

const {env} = require('../node_provider/practicals_prune');
let envConfig = {}
if(fs.existsSync(envPath)){
    envConfig = env.load(envPath)
}
module.exports = {
    apps: [
        {
            name: 'app',
            cwd: '/home/ubuntu/app-production/current',
            script: 'start.js',
            exec_interpreter: 'node',
            instances: 'max',
            exec_mode: 'cluster',
            env: {
                ...envConfig,
            },
        },
    ],
};
