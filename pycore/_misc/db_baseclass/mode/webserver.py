from pycore.base import *
import os
import re
import time
# import socket
from urllib.parse import urlparse
# from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import threading
import sched
# from flask_router import Flask
# import json
# import mimerender
#
# app = Flask(__name__)

class Webserver(Base):
    def __init__(self,args):
        pass

    def create_server(self,target="",port=18080):
        # app.run(port=port)
        pass
