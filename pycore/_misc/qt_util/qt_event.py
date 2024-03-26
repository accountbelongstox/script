from pycore.base import Base
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox)
# from ui_dialog import Ui_Dialog

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtUiTools import QUiLoader

class QtWidgetClass(Base, QtWidgets.QWidget):
    __load_ui = None

    def __init__(self, load_ui=True):
        super().__init__()
        if load_ui:
            self.load_ui()
        else:
            self.import_ui()

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
        qt_ui_dir = self.getcwd(__file__, "qt.ui")
        self.__load_ui = loader.load(qt_ui_dir, None)
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

    # @QtCore.Slot()
    def login(self):
        print("test")

    # @QtCore.Slot()
    def login(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码")
            return

    # 在这里添加验证用户名和密码的逻辑
    # 如果验证成功，请调用 self.update_data_label() 更新数据标签

    # @QtCore.Slot()
    def update_data_label(self):
        # 在这里添加获取可用数据、今日用量和计数方式的逻辑
        # 假设获取到的数据如下：
        available_data = "1000"
        daily_usage = "250"
        counter_mode = "模式1"

        self.ui.available_data_value.setText(available_data)
        self.ui.daily_usage_value.setText(daily_usage)
        self.ui.counter_mode_value.setText(counter_mode)

    # @QtCore.Slot()
    def auto_register(self):
        website_url = self.ui.website_input.text()
        # 在这里添加通过 website_url 请求远程 URL 的逻辑
        # 假设获取到的 JSON 数据如下：
        data = [{"序号": 1, "用户名": "张三", "余额": 100, "聊天权限": "是", "成功聊天次数": 5, "备注": "无"}]

        self.table.setRowCount(len(data))
        for i, item in enumerate(data):
            for j, (key, value) in enumerate(item.items()):
                table_item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, table_item)

    def get_rooms(self):
        # 在这里添加获取房间数据的逻辑
        # 假设获取到的数据如下：
        rooms = ["房间1", "房间2", "房间3"]
        self.ui.room_selection_combobox.addItems(rooms)

    # @QtCore.Slot()
    def change_room(self, index):
        selected_room = self.ui.room_selection_combobox.itemText(index)
        # 在这里添加房间更改逻辑，将 selected_room 传递给 change_room 方法

