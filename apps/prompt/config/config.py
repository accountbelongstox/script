import os
# import json
# import pprint

<<<<<<< HEAD
from kernel.utils import file, tool
from kernel.base.base import Base
=======
from pycore.utils import file, tool
from pycore._base import Base
>>>>>>> origin/main

class Config(Base):
    def __init__(self):
        self.config = None
<<<<<<< HEAD
        self.root_dir = os.path.join(file.get_root_dir(),"apps/prompt")
=======
        self.root_dir = os.path.join(file.get_root_dir(),"applications/prompt")
>>>>>>> origin/main

    def get_pprojects_path(self):
        return os.path.join(self.root_dir, '.pprojects.json')

    def get_pprojects(self):
        config_path = self.get_pprojects_path()
        return file.read_json(config_path)

    def load_config_from_file(self):
        if not self.config:
            file_path = os.path.join(self.root_dir, 'fix_prompt.json')
            self.config = file.read_json(file_path)

    def get_config(self, path=None):
        if self.config == None:
            self.load_config_from_file()
        if path != None:
            pconfs = os.path.join(path, '.pconfs.json')
            if file.is_file(pconfs):
                pconfs = file.read_json(pconfs)
                config = tool.deep_update(self.config, pconfs)
                return config
            else:
                self.warn(f"Getting a configuration error based on the path : {pconfs}, which does not exist.")
        return self.config

pConfig = Config()
config = pConfig.get_config()
