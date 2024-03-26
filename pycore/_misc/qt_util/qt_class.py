from pycore.base.base import Base
import sys
import os
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtUiTools import QUiLoader

class QtClass(Base):
    __app_width = 1200
    __app_widget = 800
    __app_style = "Fusion"
    #使用load ui的方式启动
    __load_ui = True

    def __init__(self,args):
        # super(QtClass, self).__init__()
        # super(MainWindow, self).__init__()
        pass

    def main(self,args):
        if self.com_config.get("ui") is False:
            return
        # self.setWindowTitle("My App")
        # self.load_ui()
        mode = self.mode
        app = QApplication(args)
        app.setStyle(self.__app_style)
        widget = QtWidgetClass(load_ui=self.__load_ui)
        # widget.resize(self.__app_width, self.__app_widget)
        widget.show()
        # print(f"app {app}")
        sys.exit(app.exec())
        pass

class QtWidgetClass(Base,QtWidgets.QWidget):
# class QtWidgetClass(Base,QMainWindow):
    __load_ui = None
    def __init__(self,load_ui=True):
        super().__init__()
        if load_ui:
            self.load_ui()
        else:
            self.import_ui()

    # @QtCore.Slot()
    def common_file_test(self):
        print("test")

    def __getattr__(self, key):
        def not_find(*args, **kwargs):
            print(key.split("_"))
            print(f'你调用的方法：{key}不存在！，参数为：{args}, {kwargs}')
        if key in dir(self):
            return getattr(self, key)
        return not_find

    def load_ui(self):
        self.__load_ui = True
        loader = QUiLoader()
        qt_ui_dir = self.getcwd(__file__,"qt.ui")
        self.__load_ui = loader.load(qt_ui_dir,None)
        # self.setCentralWidget(self.centralWidget)
        # dialog.show()

    def import_ui(self):
        from pycore.qt.qt_ui import Ui_Dialog
        ui = Ui_Dialog()
        ui.setupUi(self)

    # 重写父show方法
    def show(self):
        if self.__load_ui is not None:
            self.__load_ui.show()
        else:
            # super(QtWidgetClass, self).show()
            super().show()