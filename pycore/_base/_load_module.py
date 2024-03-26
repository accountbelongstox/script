# from queue import Queue
from pycore.base import Base
from pycore._base._config_manager import ConfigManager
import importlib, importlib.util
import os
import json
import sys
# import re
import threading
# import configparser
# import traceback
import platform
import uuid
import urllib3

# import glob
controlClass = None


class LoadModule(Base):
    __kernel_name = "pycore"
    __control_name = ""
    __control_module = None
    __defaultdb = None
    __args = None
    __window_x = -20
    __window_y = -20
    __uuid = None
    config_mergedict = None
    global_modes = {}

    def __init__(self, module_name, control):
        global controlClass
        controlClass = control
        short_id = uuid.uuid1().int >> 64
        self.__uuid = short_id
        argv = sys.argv
        self.argv = argv
        self.args = argv
        if len(argv) > 1:
            module_name = argv[1]
        if module_name == None:
            raise KeyError("Not argv as module_name")
        self.__control_name = module_name
        pass

    def load_kernel_class(self):
        from pycore.com.api import Api
        from pycore.com.config import Config
        from pycore.com.dbbase import Dbbase
        # from pycore.com.exchange import Exchange
        # from pycore.com.exchangerate import Exchangerate
        from pycore.com.file import File
        from pycore.com.flask import Flask
        from pycore.com.http import Http
        # from pycore.com.linuxdeploy import Linuxdeploy
        from pycore.com.log import Log
        # from pycore.com.selenium import Selenium
        from pycore.com.string import String
        from pycore.com.thread import Thread
        # from pycore.com.translate import Translate
        from pycore.com.dictionary import Dictionary
        from pycore.com.user import User
        from pycore.com.userinfo import Userinfo
        from pycore.com.util import Util
        from pycore.com.xml import Xml
        from pycore.com.graphql import Graphql
        # from pycore.com.numpy import Numpy
        # from pycore.com.ffmpeg import Ffmpeg
        self.set_modules("com", Api(sys.argv))
        self.set_modules("com", Config(sys.argv))
        self.set_modules("com", Dbbase(sys.argv))
        self.set_modules("com", Graphql(sys.argv))
        # self.set_modules("com",Exchange(sys.argv))
        # self.set_modules("com",Exchangerate(sys.argv))
        self.set_modules("com", File(sys.argv))
        self.set_modules("com", Flask(sys.argv))
        self.set_modules("com", Http(sys.argv))
        # self.set_modules("com",Linuxdeploy(sys.argv))
        # self.set_modules("com", Selenium(sys.argv))
        self.set_modules("com", Log(sys.argv))
        self.set_modules("com", String(sys.argv))
        self.set_modules("com", Thread(sys.argv))
        # self.set_modules("com", Translate(sys.argv))
        self.set_modules("com", Dictionary(sys.argv))
        self.set_modules("com", User(sys.argv))
        self.set_modules("com", Userinfo(sys.argv))
        self.set_modules("com", Util(sys.argv))
        self.set_modules("com", Xml(sys.argv))
        # self.set_modules("com", Numpy(sys.argv))
        # self.set_modules("com", Ffmpeg(sys.argv))

        # from pycore.mode.webdown import Webdown
        # from pycore.mode.webserver import Webserver
        # self.set_modules("mode",Webdown(sys.argv))
        # self.set_modules("mode",Webserver(sys.argv))

        # from pycore.db.mongo import Mongo
        # self.set_modules("db", Mongo(sys.argv))
        #
        # from pycore.db.mysql import Mysql
        # self.set_modules("db", Mysql(sys.argv))
        #
        # from pycore.db.redis import Redis
        # self.set_modules("db", Redis(sys.argv))

        from pycore.db.sqlite import Sqlite
        self.set_modules("db", Sqlite(sys.argv))

        # from pycore.thread.buyThread import BuyThread
        # self.set_modules('thread','buy',BuyThread)

        from pycore.thread.comThread import ComThread
        self.set_modules('thread', "com", ComThread)

        # from pycore.thread.downThread import DownThread
        # self.set_modules('thread',"down",ComThread)

        from pycore.thread.flaskThread import FlaskThread
        self.set_modules('thread', "flask_router", FlaskThread)

        # from pycore.thread.pingThread import PingThread
        # self.set_modules('thread',"ping",pingThread)

        # from pycore.thread.seleniumThread import SeleniumThread
        # self.set_modules('thread', "selenium", SeleniumThread)

        # from pycore.thread.translateThread import TranslateThread
        # self.set_modules('thread', "translate", TranslateThread)

        # from pycore.thread.webDownOpenUrlThread import WebDownOpenUrlThread
        # self.set_modules('thread',"web_down_open_url",WebDownOpenUrlThread)

        # from pycore.thread.webdownThread import WebdownThread
        # self.set_modules('thread',"web_down",WebdownThread)

        self.set_module('load_module', self)

    def init(self):
        argv = sys.argv
        sys.setrecursionlimit(300000)
        # 首先是加载核心组件
        self.load_kernel_class()
        control = self.load_control_class(argv)
        self.__control_module = control
        self.disable_errorouput()
        self.execute_com_main()
        self.prerun_mode_class()
        self.execute_db_main()
        self.set_defaultdb()
        self.initialize_db()
        # 加载qt UI模块
        self.load_qt(argv)
        # 数据库初始化
        # self.db_initial_from_config(control)
        control.main(argv)

    def disable_errorouput(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_uuid(self):
        return self.__uuid

    def load_qt(self, args):
        config = self.get_config()
        if self.is_windows():
            if config["global"]['ui'] == "True":
                print('load ui')
                from pycore.qt.qt_main import QtMain
                qt = QtMain(args)
                self.global_modes['qt'] = {
                    "main": qt,
                }
                self.create_thread(target=qt.main, argv=args)

    def initialize_db(self):
        db = self.get_com('dbbase')
        db.init_database()

    def load_control_class(self, argv):
        global controlClass
        control = controlClass(argv)
        self.add_config(control)
        return control

    def execute_com_main(self):
        # Mode 里的主方法放到单独的线程运行以免阻塞其他线程执行，其中qt_mode是用来执行界面的
        modes = self.get_coms()
        self.execute_main(modes, thread_execute=False)

    def execute_db_main(self):
        # Mode 里的主方法放到单独的线程运行以免阻塞其他线程执行，其中qt_mode是用来执行界面的
        modes = self.get_dbs()
        config = self.get_config()
        exclude_names = {}
        for name, mode in modes.items():
            try:
                use_db = config["use_db"][name]
                if use_db == "True":
                    exclude_names[name] = mode
            except:
                pass
        self.execute_main(exclude_names, thread_execute=False)

    def set_defaultdb(self):
        db = self.get_defaultdb()
        self.set_module('com_db', db)

    def get_defaultdb(self):
        if self.__defaultdb == None:
            com_config = self.get_com('config')
            use_db = com_config.get_translate("use_db")
            if use_db != None:
                util = self.get_com('util')
                util.print_info(f"Use Main Database {use_db}")
                db = self.get_db(use_db)
                self.__defaultdb = db
        return self.__defaultdb

    def prerun_mode_class(self):
        # Mode 里的主方法放到单独的线程运行以免阻塞其他线程执行，其中qt_mode是用来执行界面的
        modes = self.get_modes()
        self.execute_main(modes, thread_execute=True)

    def set_args(self, key=None, value=None):
        args = {
            "file": self.argv[0],
            "control_name": self.__control_name,
            "control_module": self.control_module
        }
        if key != None:
            args[key] = value
        return args

    def execute_main(self, modules, thread_execute=False):
        args = self.set_args()
        for name, mode in modules.items():
            if "main" in dir(mode):
                if thread_execute:
                    self.create_thread(mode.main, argv=args)
                else:
                    mode.main(args=args)

    def create_thread(self, target, argv):
        mode_thread = ThreadBase(target=target, argv=argv)
        mode_thread.start()

    def add_config(self, control):
        config_json = self.get_control_dir("config.json")
        if self.file_exists(config_json):
            f = open(config_json, f"r+", encoding="utf-8")
            content = f.read()
            f.close()
            config = json.loads(content)
            setattr(control, "config", config)
            return config
        return None

    def db_initial_from_config(self, control):
        config = control.config
        control.com_sqlite.init_db_integrity(config)
        # control.com_mysql.init_db_integrity(config)

    def set_property(self, module, property, default_name="com"):
        property_name = property.__class__.__name__.lower()
        property_name = f"{default_name}_{property_name}"
        setattr(module, property_name, property)
        return module

    def get_control_name(self):
        return self.__control_name

    def get_control_dir_name(self):
        return f"control_{self.__control_name}"

    def get_control_dir(self, filename=None, suffix=None):
        curdir = self.getcwd()
        module_name = self.get_control_dir_name()
        module_dir = os.path.join(curdir, module_name)
        if filename is not None:
            module_dir = os.path.join(module_dir, filename)
        if suffix is not None:
            module_dir = os.path.join(module_dir, suffix)
        return module_dir

    def get_control(self):
        return self.__control_module

    def get_control_config(self):
        return self.__control_module.config

    def get_control_core_dir(self, suffix=None):
        core_file = self.get_control_dir(suffix="core_file")
        if os.path.exists(core_file) != True:
            os.mkdir(core_file)
        if suffix is not None:
            core_file = os.path.join(core_file, suffix)
        return core_file

    def copyandexclude(self, arr, exclude):
        return [val for val in arr if val not in exclude]

    def load_module_fram_file(self, module_name, module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        return spec

    def load_class(self, module_type_name, module_name, *args, **kwargs):
        module_load_name = self.get_kernel_module_name(module_type_name, module_name)
        if module_type_name == "control":
            class_name = "Main"
        else:
            class_name = module_name
            if not class_name[0].isupper():
                class_name = class_name.title()
            # 形式为 pycore.com_main

        module_meta = __import__(module_load_name, globals(), locals(), [class_name])
        class_meta = getattr(module_meta, class_name)
        try:
            module = class_meta(*args, **kwargs)
        except Exception as e:
            print(e)
            print(f"class_name {class_name},module_load_name {module_load_name}")
            exit(-1)
        return module

    def load_module(self, module_type_name, module_name, *args, **kwargs):
        module_load_name = self.get_kernel_module_name(module_type_name, module_name)
        if module_type_name == "control":
            class_name = "Main"
        else:
            class_name = module_name[0].upper() + module_name[1:]
            # 形式为 pycore.com_main
        module_meta = __import__(module_load_name, globals(), locals(), [class_name])
        class_meta = getattr(module_meta, class_name)
        # module = class_meta(*args, **kwargs)
        return class_meta

    def get_window_position(self, addnum=0):
        self.__window_x += addnum
        self.__window_y += addnum
        window_position = {
            "x": self.__window_x,
            "y": self.__window_y,
        }
        return window_position

    def get_base_dir(self):
        return __file__.split('pycore')[0]

    def get_kernel_dir(self, suffix=None):
        kernel_dir = os.path.join(self.getcwd(), self.__kernel_name)
        if suffix != None:
            kernel_dir = os.path.join(kernel_dir, suffix)
        return kernel_dir

    def file_exists(self, filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            return True
        else:
            return False

    def is_windows(self):
        sysstr = platform.system()
        windows = "windows"
        if (sysstr.lower() == windows):
            return True
        else:
            return False

    def get_config(self):
        if self.config_mergedict == None:
            config_manager = ConfigManager(self.__control_name)
            merged_config = config_manager.merge_config()
            self.config_mergedict = merged_config
        return self.config_mergedict


class ThreadBase(threading.Thread):
    def __init__(self, target=None, argv=(), daemon=False):
        if target == None:
            raise "load_module ThreadBase target conn't None."
        thread_name = target.__class__.__name__
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.target = target
        self.argv = argv

    def run(self):
        self.target(self.argv)


class Component():
    def __setattr__(self, key, value):
        self.__dict__[key] = value
