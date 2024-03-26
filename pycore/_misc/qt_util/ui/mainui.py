import sys
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject, QUrl)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox)
from PySide6.QtWebEngineWidgets import QWebEngineView

class MainUi(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("自动发送软件")
        layout = QGridLayout(Dialog)
        # layout.setColumnCount(3)
        # layout.setRowCount(3)

        # Row 1
        self.username_label = QLabel("账号")
        self.username_input = QLineEdit()
        self.password_label = QLabel("密码")
        self.password_input = QLineEdit()
        self.login_button = QPushButton("登录")

        self.website_label = QLabel("网站地址")
        self.website_input = QLineEdit()
        self.website_input.textChanged.connect(Dialog.on_website_input)
        self.registration_pwd_label = QLabel("注册密码")
        self.registration_pwd_input = QLineEdit()
        self.registration_count_label = QLabel("注册数量")
        self.registration_count_input = QLineEdit()
        self.one_click_registration_button = QPushButton("一键注册")

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 0, 2)
        layout.addWidget(self.password_input, 0, 3)
        layout.addWidget(self.login_button, 0, 4)
        layout.addWidget(self.website_label, 0, 5)
        layout.addWidget(self.website_input, 0, 6)
        # layout.rowStretch(0)
        layout.addWidget(self.registration_count_label, 0, 7)
        layout.addWidget(self.registration_count_input, 0, 8)
        layout.addWidget(self.registration_pwd_label, 0, 9)
        layout.addWidget(self.registration_pwd_input, 0, 10)
        layout.addWidget(self.one_click_registration_button, 0, 11)

        self.available_login_label = QLabel("已登陆")
        self.available_login_value = QLabel("-")
        self.available_data_label = QLabel("可用数据")
        self.available_data_value = QLabel("0")
        self.daily_usage_label = QLabel("今日用量")
        self.daily_usage_value = QLabel("0")
        self.counter_mode_label = QLabel("计数方式")
        self.counter_mode_value = QLabel("0")

        layout.addWidget(self.available_login_label, 1, 0)
        layout.addWidget(self.available_login_value, 1, 1)
        layout.addWidget(self.available_data_label, 1, 2)
        layout.addWidget(self.available_data_value, 1, 3)
        layout.addWidget(self.daily_usage_label, 1, 4)
        layout.addWidget(self.daily_usage_value, 1, 5)
        layout.addWidget(self.counter_mode_label, 1, 6)
        layout.addWidget(self.counter_mode_value, 1, 7)

        # Row 2
        # layout.setRowMinimumHeight(2, 100)
        self.send_mode_checkbox = QCheckBox("发送方式")
        self.send_mode_combobox = QComboBox()
        self.send_mode_combobox.addItem("顺序")
        self.send_mode_combobox.addItem("随机")
        self.send_mode_combobox.currentIndexChanged.connect(Dialog.on_send_mode_combobox)

        self.room_selection_label = QLabel("房间选择")
        self.room_selection_combobox = QComboBox()
        self.room_selection_combobox.currentIndexChanged.connect(Dialog.on_room_selection_combobox)
        self.send_interval_label = QLabel("发送间隔")
        self.send_interval_input = QLineEdit()
        self.start_button = QPushButton("开始 F7")
        self.stop_button = QPushButton("停止 F8")
        self.send_interval_input.textChanged.connect(Dialog.on_send_interval_input)

        layout.addWidget(self.send_mode_checkbox, 2, 0)
        layout.addWidget(self.send_mode_combobox, 2, 1)
        layout.addWidget(self.room_selection_label, 2, 2)

        layout.addWidget(self.room_selection_combobox, 2, 3)
        layout.addWidget(self.send_interval_label, 2, 4)
        layout.addWidget(self.send_interval_input, 2, 5)
        layout.addWidget(self.start_button, 2, 6)
        layout.addWidget(self.stop_button, 2, 7)
        layout.setRowMinimumHeight(3, 600)
        self.text_area = QTextEdit()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["用户名", "密码","余额", "聊天权限", "成功聊天次数", "备注"])

        layout.addWidget(self.text_area, 3, 0, 1, 6)
        layout.addWidget(self.table, 3, 6, 2,10)
        # 添加 QWebEngineView 组件
        self.web_view = QWebEngineView()
        # self.web_view.load(QUrl('https://www.baidu.com'))
        # self.web_view.show()
        # self.web_view.loadFinished.connect(self.on_load_finished)
        # layout.addWidget(self.web_view, 2, 7, 2,10)

        self.retranslateUi(Dialog)
        self.text_area.textChanged.connect(Dialog.on_text_changed)  # 绑定 textChanged 信号到 on_text_changed 方法
        self.login_button.clicked.connect(Dialog.login)
        self.one_click_registration_button.clicked.connect(Dialog.auto_register)
        self.start_button.clicked.connect(Dialog.start)
        self.stop_button.clicked.connect(Dialog.stop)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
