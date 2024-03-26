import os.path
import os
from datetime import datetime
import time
from pycore.utils import file,strtool
from pycore.utils import screen,oper
from apps.ncss.provider.project_info import project_name,app_name
from pycore.practicals import cv2
from pycore.base import Base

class DataSrc(Base):

    def __init__(self):
        pass

    def append_data(self, title=None):
        src_data = file.get_source(f"{app_name}/full_data.txt")
        file.save(src_data,title)

    def append_result(self, title=None):
        src_data = file.get_source(f"{app_name}/result.csv")
        file.save(src_data,title)

data_save = DataSrc()