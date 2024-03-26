const fs = require('fs');
const { web_dir  } = require('../provider/local_env');
const node_provider = require('../provider/node_provider');
const { plattool,file,fpath } = require('../../node_provider/utils_prune');
const Base = require('../../node_provider/base/base');

class NodeAction extends Base {
    error = {}
    constructor() {
        super();
    }

    check_node_version(appPath) {
        const node_version = node_provider.get_version();
        const engines_versions = node_provider.extract_nodeversip(appPath);
        const minVersion = engines_versions.length > 0 ? engines_versions[0] : null;
        const maxVersion = engines_versions.length > 1 ? engines_versions[1] : null;
        if(minVersion){
            if(node_version<minVersion){
                return false
            }
        }
        if(maxVersion){
            if(node_version>maxVersion){
                return false
            }
        }
        return true
    }
    

}
const node_action = new NodeAction()
module.exports = node_action;
