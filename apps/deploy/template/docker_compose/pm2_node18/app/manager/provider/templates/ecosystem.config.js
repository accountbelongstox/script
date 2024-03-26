module.exports = {
  apps : [{ 
    name:  'API',
    script: 'API.js',
    instances: 4,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    },
    env_production: {
      NODE_ENV: 'production'
    }
  }]
};
