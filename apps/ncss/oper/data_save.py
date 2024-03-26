import os.path
import os
from datetime import datetime
import time
from kernel.utils import file,strtool
from kernel.utils import screen,oper
from apps.ncss.provider.project_info import project_name,app_name
from kernel.practicals import cv2
from kernel.base.base import Base

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