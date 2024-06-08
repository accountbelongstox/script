from pycore.globalvar.encyclopedia import encyclopedia

from pycore.thread.flaskThread import FlaskThread
from pycore.thread.comThread import ComThread
FlaskThread = FlaskThread
ComThread = ComThread

from pycore.thread.ziptask import Ziptask
ziptask = Ziptask()