module.exports = {
  apps: [
    {
      name: 'strapi',
      script: '/www/wwwroot/api.local.12gm.com/start.js',
      exec_mode: 'cluster',
      instances: 1,
      args: ' -i max --env production',
	  exec_interpreter: 'node',
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      },
      cwd: '/www/wwwroot/api.local.12gm.com/',
      watch: false
    },
    {
      name: 'dev_code',
      script: './node_modules/vite/bin/vite.js',
      exec_mode: 'cluster',
      instances: 1,
      args: ' --host 0.0.0.0 --port 3006',
      cwd: '/www/wwwroot/dev.local.12gm.com',
      watch: false
    },
    {
      name: 'task_dev',
      script: '/www/wwwroot/task.local.12gm.com/server.js',
      exec_mode: 'cluster',
      instances: 1,
      args: '',
      cwd: '/www/wwwroot/task.local.12gm.com',
      watch: false
    }
  ]
}
/*
    {
      name: 'strapi',
      script: './node_modules/@strapi/strapi/bin/strapi.js',
      exec_mode: 'cluster',
      instances: 1,
      args: ' -i max --env production',
	  exec_interpreter: 'node',
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      },
      cwd: '/www/wwwroot/api.local.12gm.com',
      watch: false
    },

    {
      name: 'strapi',
      exec_mode: 'cluster',
      instances: 1,
	  script: 'start.js',
	  exec_interpreter: 'node',
      args: 'start',
      cwd: '/www/wwwroot/api.local.12gm.com',
      watch: false,
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      }
    },


module.exports = {
  apps: [
    {
      name: 'my-nuxtjs-app',
      exec_mode: 'cluster',
      instances: 2,
      cwd: '/var/www',
      script: './node_modules/nuxt-start/bin/nuxt-start.js',
      args: '-c /var/www/nuxt.config.js'
    }
  ]
}


*/


//{
//  "apps": [
//    {
//      "name": "app",
//      "script": "app.js",
//      "cwd": "/home/user/app",
//      "env": {
//        "PORT": 3000,
//        "NODE_ENV": "production"
//      },
//      "error_file": "/home/user/logs/app-error.log",
//      "out_file": "/home/user/logs/app-out.log"
//    },
//    {
//      "name": "server",
//      "script": "server.js",
//      "cwd": "/home/user/server",
//      "env": {
//        "PORT": 4000,
//        "NODE_ENV": "development"
//      },
//      "error_file": "/home/user/logs/server-error.log",
//      "out_file": "/home/user/logs/server-out.log"
//    }
//  ]
//}
//
