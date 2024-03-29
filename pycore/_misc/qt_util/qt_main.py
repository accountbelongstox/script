from queue import Queue

from pycore.base.base import Base
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from pycore.qt.qt_controller import *

GLOBAL_Queue = Queue()

class QtMain(Base):
    __app_width = 1349
    __app_widget = 780
    __app_style = "Fusion"
    #使用load ui的方式启动
    __use_uifile = False
    __ui_object = None
    ui_stack = []
    current_ui = None

    def __init__(self,args):
        # super().__init__()
        # super(MainWindow, self).__init__()
        pass

    def main(self,args):
        global GLOBAL_Queue
        if self.com_config.get("ui") is False:
            return
        # self.setWindowTitle("My App")
        app = QApplication(args)
        app.setStyle(self.__app_style)
        self.controller = QtController()
        self.load_module.global_modes["qt"]["controller"] = [self.controller]
        self.load_module.attach_module(self.controller,info=True)
        self.select_loadui()
        self.controller.main(GLOBAL_Queue)
        # self.controller.resize(self.__app_width, self.__app_widget)
        self.show()
        sys.exit(app.exec())

    def import_uiclass(self):
        from pycore.qt.ui.mainui import MainUi
        # 依次载入UI模块，并将UI实例添加到堆栈中
        self.ui_stack = [MainUi(),]
        # 设置当前UI
        self.current_ui = self.ui_stack[0]
        # 初始化当前UI
        self.current_ui.setupUi(self.controller)
        setattr(self.controller,'ui',self.current_ui)

    def select_loadui(self):
        # super().__init__()
        if self.__use_uifile:
            self.load_uifile()
        else:
            self.import_uiclass()

    # 重写父show方法
    def show(self):
        if self.__ui_object is not None:
            self.__ui_object.show()
        else:
            self.controller.show()

    def load_uifile(self):
        loader = QUiLoader()
        qt_ui_dir = self.getcwd(__file__, "qt.ui")
        self.__ui_object = loader.load(qt_ui_dir, None)
        # self.setCentralWidget(self.centralWidget)
        # dialog.show()


