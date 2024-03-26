
const { template_dir  } = require('./local_env.js');

class Template {
    error = {}
    
    constructor() {
    }

    get_template_dir(){
        return template_dir
    }

}
const template = new Template()
module.exports = template;
