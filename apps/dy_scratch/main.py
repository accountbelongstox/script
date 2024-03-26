import os
import os.path
import time

from apps.dy_scratch.flask_router.auto_flask_conf import config
from apps.dy_scratch.flask_router.router import Router
from apps.dy_scratch.oper.down import down
from pycore._base import Base
from pycore.threads import FlaskThread
from pycore.utils import file

class autoMain(Base):
    current_screen_file = None
    default_prompts_dir = ".prompts"
    project_name="douyin"

    def __init__(self):
        pass

    def start(self):
        flask = FlaskThread(config=config, router=Router)
        flask.start()
        self.info("正在启动抖音抓取")


auto_main = autoMain()
