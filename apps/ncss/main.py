import os
import os.path
import time

from apps.ncss.flask_router.auto_flask_conf import config
from apps.ncss.flask_router.router import Router
from apps.ncss.oper.down import down
from apps.ncss.provider.data_src import data_src
from apps.ncss.provider.project_info import project_name
from kernel.base.base import Base
from kernel.threads import FlaskThread
from kernel.utils import file

class autoMain(Base):
    current_screen_file = None
    default_prompts_dir = ".prompts"

    def __init__(self):
        pass

    def start(self):
        flask = FlaskThread(config=config, router=Router)
        flask.start()
        self.info("正在启动Ncss非侵入式抓取")


auto_main = autoMain()
