import os
import os.path
import time
from pycore.base.base import Base
from pycore.utils import *
import json


class Release(Base):

    def __init__(self):
        pass

    def start(self):
        filter = filefilter.filter("D:/programing")
        self.pprint(filter)
        self.info("正在启动Tasks Flask..")

release = Release()
