import sys
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1349, 780)
        layout = QGridLayout(Dialog)

        # Row 1
        self.username_label = QLabel("账号")
        self.username_input = QLineEdit()
        self.password_label = QLabel("密码")
        self.password_input = QLineEdit()
        self.login_button = QPushButton("登录")
        self.available_data_label = QLabel("可用数据")
        self.available_data_value = QLabel("0")
        self.daily_usage_label = QLabel("今日用量")
        self.daily_usage_value = QLabel("0")
        self.counter_mode_label = QLabel("计数方式")
        self.counter_mode_value = QLabel("N/A")

        self.website_label = QLabel("网站地址")
        self.website_input = QLineEdit()
        self.registration_count_label = QLabel("注册数量")
        self.registration_count_input = QLineEdit()
        self.one_click_registration_button = QPushButton("一键注册")

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 0, 2)
        layout.addWidget(self.password_input, 0, 3)
        layout.addWidget(self.login_button, 0, 4)
        layout.addWidget(self.available_data_label, 0, 5)
        layout.addWidget(self.available_data_value, 0, 6)
        layout.addWidget(self.daily_usage_label, 0, 7)
        layout.addWidget(self.daily_usage_value, 0, 8)
        layout.addWidget(self.counter_mode_label, 0, 9)
        layout.addWidget(self.counter_mode_value, 0, 10)

        layout.addWidget(self.website_label, 0, 11)
        layout.addWidget(self.website_input, 0, 12)
        layout.addWidget(self.registration_count_label, 0, 13)
        layout.addWidget(self.registration_count_input, 0, 14)
        layout.addWidget(self.one_click_registration_button, 0, 15)

        # Row 2
        layout.setRowMinimumHeight(1, 100)
        self.send_mode_checkbox = QCheckBox("发送方式")
        self.send_mode_combobox = QComboBox()
        self.send_mode_combobox.addItem("顺便")
        self.send_mode_combobox.addItem("随机")
        self.room_selection_label = QLabel("房间选择")
        self.room_selection_combobox = QComboBox()
        self.send_interval_label = QLabel("发送间隔")
        self.send_interval_input = QLineEdit()
        self.start_button = QPushButton("开始 F7")
        self.stop_button = QPushButton("停止 F8")

        layout.addWidget(self.send_mode_checkbox, 1, 0)
        layout.addWidget(self.send_mode_combobox, 1, 1)
        layout.addWidget(self.room_selection_label, 1, 2)

        layout.addWidget(self.room_selection_combobox, 1, 3)
        layout.addWidget(self.send_interval_label, 1, 4)
        layout.addWidget(self.send_interval_input, 1, 5)
        layout.addWidget(self.start_button, 1, 6)
        layout.addWidget(self.stop_button, 1, 7)

        # Row 3
        layout.setRowMinimumHeight(2, 600)
        self.text_area = QTextEdit()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["序号", "用户名", "余额", "聊天权限", "成功聊天次数", "备注"])

        layout.addWidget(self.text_area, 2, 0, 1, 6)
        layout.addWidget(self.table, 2, 1, 1, 6)

        self.retranslateUi(Dialog)

        self.login_button.clicked.connect(Dialog.login)
        self.one_click_registration_button.clicked.connect(Dialog.auto_register)
        self.room_selection_combobox.currentIndexChanged.connect(Dialog.change_room)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
