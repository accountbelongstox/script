import os
import os.path
import time

from apps.tasks.flask_router.config import config
from apps.tasks.flask_router.router import Router
from pycore.base.base import Base
from pycore.threads import FlaskThread
from pycore.utils import file

class Tasks(Base):
    current_screen_file = None
    default_prompts_dir = ".prompts"

    def __init__(self):
        pass

    def start(self):
        flask = FlaskThread(config=config, router=Router)
        flask.start()
        self.info("正在启动Tasks Flask..")


tasks = Tasks()
