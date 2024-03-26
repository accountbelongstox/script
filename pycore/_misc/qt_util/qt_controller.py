import time
from queue import Queue
import random
import win32api
import win32con
import pyperclip

from pycore.qt.base.qt_base import *
from pycore.qt.qt_server import QTServer
import re
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox)

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QObject, Slot, QUrl,QIODevice, QByteArray,QDataStream,Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtWebChannel import QWebChannelAbstractTransport
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtNetwork import *
from PySide6.QtTest import QTest

class MyBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    @Slot(str)
    def receiveMessage(self, message):
        QMessageBox.information(None, 'Message from JavaScript', message)

    @Slot(str)
    def handleMessage(self, message):
        print(f'Received message from JavaScript: {message}')


class QtController(QTBase, QtWidgets.QWidget):
    __initroomselect = None
    __js_task = Queue()
    account_charcheck = {}
    __invalidate_account = []
    page = None
    __text_edit_textindex = 0
    __ad_sentences = []
    listen_tick = 0
    fixed_url = 'https://api.obob515.top'
    __crypt_key = 'FDZdmIVO8anN_FkhNFoghFfBqgCE4HfbvwysLpIxe6c='
    __debug = True

    def __init__(self,argv=None):
        super().__init__()
        pass

    # @QtCore.Slot()
    def start(self):
        if self.is_auth() == False:
            return
        self.web_view = QWebEngineView()
        self.web_view.setWindowTitle("观察页面")
        self.web_view.resize(1200, 600)
        self.web_view.load(QUrl(self.main_url))
        self.web_view.show()
        self.web_view2 = QWebEngineView()
        self.web_view2.setWindowTitle("对打窗口")
        self.web_view2.resize(1200, 600)
        self.web_view2.load(QUrl(self.main_url))
        self.web_view2.show()
        self.load_module.create_thread(target=self.tick, argv=[])
        # channel = QWebChannel(self)
        # bridge = MyBridge()
        # self.web_view.page().setWebChannel(channel)
        # channel.registerObject('handler', bridge)
        # 在 QWebChannel 中注册 transport 对象
        # 页面加载完成时注入 JavaScript 并执行操作
        # self.web_view.loadFinished.connect(self.inject_js_test)
        # self.tick()
        # 监听 QWebChannel 的 messageReceived 信号
        # QObject.connect(channel, QtCore.SIGNAL('messageReceived(QJsonObject, QWebChannelAbstractTransport*)'),
        #                 self.handleMessage)
        # 监听本地主机的 8888 端口
        # self.server = QTcpServer(self)
        # self.server.listen(QHostAddress.Any, 8889)
        # self.server.newConnection.connect(self.on_new_connection)
        # self.server.readyRead.connect(self.on_ready_read)
        # self.server.disconnected.connect(self.on_disconnected)
        # self.server.newConnection.connect(self.on_new_connection)

    def add_room(self,flask):
        items = self.com_flask.get_request(flask,'data')
        if len(items) > 0:
            for item in items:
                if self.ui.room_selection_combobox.findText(item) == -1:
                    self.ui.room_selection_combobox.addItem(item)
        software_config = self.com_config.software_config()
        uiname = 'room_selection_combobox'
        if software_config[uiname] != None:
            ui = getattr(self.ui, uiname)
            index = ui.findText(software_config[uiname])
            if index >= 0:
                ui.setCurrentIndex(index)
        return {}

    def enable_chat(self,flask):
        enable_chat = self.com_flask.get_request(flask,'data')
        chat = enable_chat.get('chat')
        current_user = enable_chat.get('account')
        amount = enable_chat.get('amount')
        if chat == None:
            if self.account_charcheck[current_user]["chat_check"] >= 0:
                self.account_charcheck[current_user]["chat_check"] += 1
        elif chat == True:
            self.account_charcheck[current_user]["chat_check"] = -1
            self.set_table(current_user,["","",amount,"1"])
            line = self.get_line()
            self.account_charcheck[current_user]["x"] = enable_chat.get('x')
            self.account_charcheck[current_user]["y"] = enable_chat.get('y')
            self.__ad_sentences.append(line)
        elif chat == False:
            self.__invalidate_account.append(current_user)
            self.set_table(current_user,["","",amount,"0","","无效"])
            return {
                "code":"-1",
                "message":"outtime",
            }

        if self.account_charcheck[current_user]["chat_check"] > 10:
            print(f"{current_user} ready invalidate")
            self.__invalidate_account.append(current_user)
            self.set_table(current_user,["","",amount,"0","","无效"])
            return {
                "code":"-1",
                "message":"outtime",
            }

        return {
            "code": "0",
            "message": "good",
        }

    def get_text_edit_text(self):
        text = self.ui.text_area.toPlainText()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines

    # 取出一行
    def get_line(self):
        lines = self.get_text_edit_text()
        if self.ui.send_mode_combobox.currentIndex() == 0:
            # 顺序模式下，循环取出每一行
            line = lines[self.__text_edit_textindex]
            self.__text_edit_textindex = (self.__text_edit_textindex + 1) % len(lines)
            return line
        else:
            # 随机模式下，随机取出一行
            index = random.randint(0, len(lines))
            line = lines[index]
            return line

    def account_status(self,flask):
        data = self.com_flask.get_request(flask,'data')
        current_user = data.get('user')
        if data.get('action') == 'delete':
            self.set_table(current_user,["","","0","0","","无效."])
        return {}


    def send_message(self, message):
        data = QByteArray()
        stream = QDataStream(data, Qt.WriteOnly)
        stream.writeBytes(message.encode())
        self.socket.write(data)

    def on_new_connection(self):
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            socket.readyRead.connect(self.on_ready_read)
            socket.disconnected.connect(self.on_disconnected)
            print(f'New connection from {socket.peerAddress().toString()}:{socket.peerPort()}')

    def on_ready_read(self):
        socket = self.sender()
        while socket.bytesAvailable():
            readAll = socket.readAll()
            dataOrigin = readAll.data()
            data = dataOrigin.decode()
            # 将收到的消息作为参数执行 Python 代码
            self.on_message_from_js(data)
            # 发送响应消息
            socket.write(f'Received message: {data}'.encode())

    # @QtCore.Slot(str)
    def on_message_from_js(self, message):
        print(f'Messagea received from JavaScript: {message}')

    def on_disconnected(self):
        socket = self.sender()
        print(f'Client {socket.peerAddress().toString()}:{socket.peerPort()} disconnected.')

    def handleMessage(self, message, transport):
        print(f"Receiveda message from JavaScript: {message['data']}")

    def main(self,GLOBAL_Queue):
        # get main url
        website_url = self.ui.website_input.text()
        url_protocol = self.com_http.get_url_protocol(website_url)
        url_body = self.com_http.get_url_body(website_url)
        main_url = url_protocol+url_body
        self.url_protocol = url_protocol
        self.url_body = url_body
        self.main_url = main_url

        self.GLOBAL_Queue = GLOBAL_Queue
        self.load_soundtext()
        software_config = self.com_config.software_config()
        uiname = 'send_interval_input'
        if software_config.get(uiname) != None:
            ui = getattr(self.ui,uiname)
            ui.setText(software_config[uiname])
        uiname = 'website_input'
        if software_config.get(uiname) != None:
            ui = getattr(self.ui,uiname)
            ui.setText(software_config[uiname])
        uiname = 'send_mode_combobox'
        if software_config.get(uiname) != None:
            ui = getattr(self.ui,uiname)
            index = ui.findText(software_config[uiname])
            if index >= 0:
                ui.setCurrentIndex(index)
        uiname = 'room_selection_combobox'
        if software_config.get(uiname) != None:
            ui = getattr(self.ui, uiname)
            index = ui.findText(software_config[uiname])
            if index >= 0:
                ui.setCurrentIndex(index)

    def load_soundtext(self):
        cwd = self.getcwd()
        hanhua = os.path.join(cwd,'hanhua.txt')
        if not self.com_file.isfile(hanhua):
            self.com_file.save(hanhua,'')
        hanhua = self.com_file.read(hanhua)
        self.ui.text_area.setPlainText(hanhua)
        zhanghao = os.path.join(cwd,'zhanghao.txt')
        if not self.com_file.isfile(zhanghao):
            self.com_file.save(zhanghao,'')
        accounts = self.com_file.read(zhanghao)
        accounts = re.split(re.compile(r'\n+'),accounts)
        data = []
        for account in accounts:
            words = re.split(re.compile(r'\s+'), account)
            usr = self.com_util.get_list_value(words,0,None)
            pwd = self.com_util.get_list_value(words,1,None)
            salary = self.com_util.get_list_value(words,2,"50")
            chat = self.com_util.get_list_value(words,3,"1")
            chat_ok = self.com_util.get_list_value(words,4,"0")
            bz = self.com_util.get_list_value(words,5,'')
            if usr == None or pwd == None:
                continue
            data.append({"用户名": usr, "密码": pwd, "余额": salary, "聊天权限": chat,
                             "成功聊天次数": chat_ok, "备注": bz})
        account_text = ''
        for item in data:
            account_text+=" ".join(item.values())+'\n'
        self.com_file.save(zhanghao,account_text,overwrite=True)
        self.add_totable(data)

    def receiveMessage(self, message):
        # 接收来自 JavaScript 的消息并进行处理
        QMessageBox.information(self, 'Message from JavaScript', message)

    def on_text_changed(self):
        cwd = self.getcwd()
        hanhua = os.path.join(cwd,'hanhua.txt')
        self.com_file.save(hanhua,self.ui.text_area.toPlainText(),overwrite=True)

    def ready_logtin(self):
        if self.GLOBAL_Queue.qsize() > 0:
            QMessageBox.warning(self, "警告", "你已经登陆过.")
            return True
        return False

    def is_auth(self):
        if self.GLOBAL_Queue.qsize() == 0 and self.__debug != True:
            QMessageBox.warning(self, "警告", "请先登陆代理账号,再使用软件.")
            return False
        return True

    @QtCore.Slot()
    def login(self):
        if self.ready_logtin() == True:
            return
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码")
            return
        userobj = {
            'name':username,
            'password':password,
        }
        # simple_url = self.com_http.simple_url(self.main_url)
        url = f'{self.fixed_url}/api/auth/login'
        result = self.com_http.post(url,userobj)
        result = self.com_string.to_json(result)
        try:
            self.com_util.pprint(result)
            data = result.get('data')
            user_info = data.get('user_info')
            is_in_on = user_info.get('is_in_on')
            if is_in_on != 1:
                QMessageBox.warning(self, "警告", "你登陆的账号不是内部账号,无法使用")
                return
            money = user_info.get('money')
            name = user_info.get('name')

            QMessageBox.information(self, "提示", "登陆成功！")
            self.GLOBAL_Queue.put(user_info)
            self.ui.available_login_value.setText(name)
            self.ui.daily_usage_value.setText(money)
        except Exception as e:
            QMessageBox.warning(self, "警告", "登陆错误")


    def tick(self,argv=None):
        self.listen_tick += 1
        action = "check();"

        if len(self.__invalidate_account) > 0:
            self.__invalidate_account = []
            action = "outlogin();"
        elif len(self.__ad_sentences) > 0:
            interval = self.ui.send_interval_input.text()
            try:
                interval = int(interval)
            except:
                interval = 1
            interval = abs(interval)
            if interval == 0 or self.listen_tick % interval == 0:
                ad_sentences = self.__ad_sentences.pop(0)
                pyperclip.copy(ad_sentences)
                action = f"send_ad(`{ad_sentences}`,{self.listen_tick});"
                # 在QWebEngineView中粘贴字符串
                # clipboard = QApplication.clipboard()
                # mime_data = QMimeData()
                # mime_data.setText(pyperclip.paste())
                # clipboard.setMimeData(mime_data)
                view_pos = self.web_view.mapToGlobal(QtCore.QPoint(0, 0))
                x = view_pos.x() + self.account_charcheck[self.current_user]["x"]+10
                y = view_pos.y() + self.account_charcheck[self.current_user]["y"]+5
                print("x",x,"y",y)
                # input_element = self.web_view.page().findElement("#chat-public")
                # input_element.setFocus()
                # input_element.evaluateJavaScript("document.execCommand('paste')")
                x = int(x)
                y = int(y)

                # 获取当前鼠标位置
                # pos = QCursor.pos()

                # 将鼠标移动到指定位置
                # QCursor.setPos(x, y)
                # widget = QApplication.instance().activeWindow()
                # QTest.mouseClick(widget, Qt.LeftButton, pos=widget.rect().center())
                # 模拟鼠标点击
                # QCursor.mousePressEvent(QApplication.instance().activeWindow(), QCursor.LeftButton)
                # QCursor.mouseReleaseEvent(QApplication.instance().activeWindow(), QCursor.LeftButton)

                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

                # pyperclip.paste()
                win32api.keybd_event(0x11, 0, 0, 0)  # 按下Ctrl键
                win32api.keybd_event(0x56, 0, 0, 0)  # 按下V键
                win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放V键
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放Ctrl键
            else:
                action = ""
        if self.listen_tick % 3 == 0:
            account = self.find_chat_authority(self.ui.table)
            if account == None and len(self.__ad_sentences) > 0:
                QMessageBox.warning(self, "提示", "账号已经使用完毕")
                time.sleep(10)
                self.tick()
                return
            if account != None:
                current_user = account[0]
                self.current_user = current_user
                current_pwd = account[1]
                current_pwd = self.com_string.decrypt(current_pwd,self.__crypt_key)
                print('current_pwd',current_pwd)
                self.current_pwd = current_pwd
            else:
                current_user = ""
                current_pwd = ""
            if current_user:
                if self.account_charcheck.get(current_user) == None:
                    self.account_charcheck[current_user] = {
                        "chat_check":0
                    }
        else:
            current_user = ""
            current_pwd = ""
            if action == "check();":
                action = ""

        js_code = """
            function return_currentuser(){
                return '%s'
            }
            
            function checklogin() {
                if (!document.body) return false;
                if (window.location.href === 'about:blank') return false;
                const usernameInput = document.querySelector('input[placeholder="用户名"]');
                if (usernameInput) {
                    return false;
                }
                return true;
            }
            
            function is_gameroom() {
                if (document.querySelector('#video-wrapper')) {
                    return true
                }
                return false
            }
            
            function send_ad(str,win_x,win_y){
                let button = document.querySelector('button[data-role="message-input__button"]')
                if(button){
                    console.log(button)
                    button = button.click()
                }
            }
            
            function check_bete() {
                let amount = document.querySelector('span[data-role="balance-label__value"]')
                if(amount){
                    amount = amount.innerHTML
                }else{
                    amount = 0
                }
                amount = parseInt(amount)
                if(amount != 50){
                    const messages = document.querySelectorAll('[data-role="chat-message__text"]');
                    let message_text_list = Array.from(messages).map(message => message.innerHTML);
                    let enable_chat = null
                    if (message_text_list.includes('您的聊天权限已被禁用。')) {
                        enable_chat = false
                    }else if (message_text_list.includes('您的聊天权限已被启用。')) {
                        enable_chat = true
                    }
                    var element = document.querySelector('#chat-public');
                    var x=0,y=0
                    if(element){
                        var rect = element.getBoundingClientRect();
                        x = rect.left + window.pageXOffset;
                        y = rect.top + window.pageYOffset;
                    }
                    fetch(`http://127.0.0.1:8889/api?method=enable_chat&module=qt&key=9LrQN0~14,dSmoO^`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                data:{
                                    chat:enable_chat,
                                    amount:amount,
                                    account:return_currentuser(),
                                    x,
                                    y
                                }
                            }),
                        }
                    )   
                }else{
                    let status = document.querySelector('div.text--27a51[data-role="status-text"]');
                    if (status) {
                        status = status.innerHTML;
                        let bate = /^\s*投注\s*\d+/g
                        if (bate.test(status)) {
                            const regex = /\d+/g;
                            let numbers = status.match(regex);
                            numbers = parseInt(numbers)
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                            document.querySelector('#root > div > div.app--2c5f6 > div > div.content--82383 > div:nth-child(2) > div > div.bottom-container--65e5b > div.bottom-game-overlay--18b5c > div > div.gameOverlay--be047 > div > div > div > div.mainContainer--f3872 > div.player--5adf8').click()
                        }
                    }
                }
            }
            
            function login(username, password) {
                if(!username || !password){
                    return 
                }
                const usernameInput = document.querySelector('input[placeholder="用户名"]');
                if (usernameInput) {
                    usernameInput.value = username;
                    usernameInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const passwordInput = document.querySelector('input[placeholder="密码"]');
                if (passwordInput) {
                    passwordInput.value = password;
                    passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const loginButton = document.querySelector('button[class="button1 change-bg-color ajax-submit-without-confirm-btn"]');
                if (loginButton) {
                    loginButton.click();
                }
            }
            
            function pageCategory(category, result = false) {
                const hash = window.location.hash;
                const jsonStr = hash.substring(1);
                const searchParams = new URLSearchParams(jsonStr);
                const entries = searchParams.entries();
                const obj = Object.fromEntries(entries);
                if (result) return obj
                if (obj && obj.category && obj.category == category) {
                    return true;
                }
                return false;
            }
            
            function getList() {
                if (is_gameroom()) {
                    check_bete();
                    return;
                }
                if (!pageCategory("baccarat")) {
                    return;
                }
                let list = [];
                document.querySelectorAll('p[data-role="tile-name"]').forEach((e) => {
                    list.push(e.innerHTML);
                });
                if (list.length > 0) {
                    let data = { data: list };
                    fetch(`http://127.0.0.1:8889/api?method=add_room&module=qt&key=9LrQN0~14,dSmoO^`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify(data),
                        }
                    );
                }
            }
            
            function outlogin() {
                if (document.querySelector('.logout1')) {
                    document.querySelector('.logout1').click()
                } else {
                    window.location.href = '<--main_url-->/#/Live'
                    document.querySelector('.logout1').click()
                }
            }
            
            function dirTo() {
                if (pageCategory("baccarat")) {
                    return;
                }
                if (document.querySelector('.logout1')) {
                    setTimeout(() => {
                        let money = document.querySelector('#main > div.head > div.head-t1 > div > div:nth-child(2) > ul > li.moneys > span > curses.pyc > i').innerHTML
                        const regex = /\d+/g;
                        let numbers = money.match(regex);
                        numbers = parseInt(numbers)
                        if (numbers < 50) {
                            fetch(`http://127.0.0.1:8889/api?method=account_status&module=qt&key=9LrQN0~14,dSmoO^`,
                                {
                                    method: "POST",
                                    headers: {
                                        "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify({
                                        data: {
                                            action: 'delete',
                                            code: 0,
                                            user: return_currentuser(),
                                        }
                                    }),
                                }
                            );
                            outlogin()
                            return
                        } else {
                            if (!window.location.href.endsWith('EVO')) {
                                window.location.href = '<--main_url-->/#/LoginToSupplier?gameCode=0&gameType=1&api_code=EVO'
                            }
                        }
                    }, 2000)
                }
                clickButton('button[data-role="games-button"]');
                clickButton_n('.Category--8570c', 1);
            }
            
            function clickButton_n(selector, n) {
                let button = document.querySelectorAll(selector)[n];
                if (button) {
                    button.click();
                }
            }
            function clickButton(selector) {
                let button = document.querySelector(selector);
                if (button) {
                    button.click();
                }
            }
            
            function check() {
                if (!checklogin()) {
                    login('%s', '%s')
                } else {
                    getList();
                    dirTo();
                }
            }
            %s
        """ % (current_user,current_user,current_pwd,action)
        js_code = js_code.replace('<--main_url-->', self.main_url)
        if action != "":
            page = self.web_view.page()
            page.runJavaScript(js_code)
        time.sleep(1)
        self.tick()

    # @QtCore.Slot()
    def stop(self):
        print('stop')

    def find_chat_authority(self,table_widget):
        row_count = table_widget.rowCount()
        col_count = table_widget.columnCount()
        for row in range(row_count):
            chat_authority = table_widget.item(row, 3).text()  # 获取 "聊天权限" 列的文本
            yue = table_widget.item(row, 2).text()  # 获取 "余额" 列的文本
            yue = int(yue)
            if chat_authority != "0":
                table_widget.setItem(row, 5,  QTableWidgetItem(str("使用中.")))
                record = []
                for col in range(col_count):
                    record.append(table_widget.item(row, col).text())
                return record
        return None

    def get_table(self):
        table_widget = self.ui.table
        row_count = table_widget.rowCount()
        col_count = table_widget.columnCount()
        record = []
        for row in range(row_count):
            item = []
            for col in range(col_count):
                item.append(table_widget.item(row, col).text())
            record.append(item)
        return record

    def table_totext(self):
        tables = self.get_table()
        table_text = ''
        for item in tables:
            table_text+=" ".join(item)+'\n'
        return table_text

    def set_table(self,user,vals):
        table_widget = self.ui.table
        row_count = table_widget.rowCount()
        for row in range(row_count):
            chat_user = table_widget.item(row, 0).text()  # 获取 "聊天权限" 列的文本
            if chat_user == user:
                for j in range(len(vals)):
                    val = vals[j]
                    if val:
                        table_widget.setItem(row, j,  QTableWidgetItem(str(val)))
        table_text = self.table_totext()
        cwd = self.getcwd()
        zhanghao = os.path.join(cwd,'zhanghao.txt')
        self.com_file.save(zhanghao,table_text,overwrite=True)

    # @QtCore.Slot()
    def auto_register(self):
        if self.is_auth() == False:
            return
        key = self.com_string.create_fernetkey()
        print(key)
        key = key.decode('utf-8')
        print(key)
        key = key.encode('utf-8')
        print(key)
        cwd = self.getcwd()
        zhanghao = os.path.join(cwd,'zhanghao.txt')
        if not self.com_file.isfile(zhanghao):
            self.com_file.save(zhanghao,'')

        register = self.ui.registration_count_input.text()
        try:
            register = int(register)
        except:
            register = 0
        if register == 0:
            QMessageBox.warning(self, "警告", "请输入正确的注册数量.")
            return
        simple_url = self.com_http.simple_url(self.main_url)
        url = f'{self.url_protocol}api.{simple_url}/api/auth/register'
        success = []
        for i in range(register):
            account = self.com_string.create_string(8)
            pwd = self.com_string.create_string(7)
            print('register pwd',pwd)
            register_acc = {
                "invite_code":"",
                "name":account,
                "password":pwd,
                "password_confirmation":pwd,
                "phone":self.com_string.create_phone(),
                "qk_pwd":"123456",
                "realname":self.com_string.create_string(8),
                "register_site":self.main_url,
                'autoregister':"yes",
            }
            result = self.com_http.post(url, register_acc)
            try:
                code = result.get('code')
                print(code,type(code))
                if code == 200:
                    success.append(register_acc)
            except:
                pass
        QMessageBox.information(self, "提示", f"注册成功 {len(success)}个账号")
        # 在这里添加通过 website_url 请求远程 URL 的逻辑
        # 假设获取到的 JSON 数据如下：
        data = []
        account_text = ''
        for account in success:
            pwd = account['password']
            pwd = self.com_string.encrypt(pwd,self.__crypt_key)
            # pwd = pwd[0:7]
            account_text = account_text+account['name']+" "+pwd+" 50 1 0 无"+'\n'
            data.append({ "用户名":account['name'],"密码": pwd, "余额": 50, "聊天权限": "1", "成功聊天次数": 0, "备注": ""})
        self.com_file.save(zhanghao,account_text)
        self.add_totable(data)

    def add_totable(self,data):
        self.ui.table.setRowCount(len(data))
        for i, item in enumerate(data):
            for j, (key, value) in enumerate(item.items()):
                table_item = QTableWidgetItem(str(value))
                self.ui.table.setItem(i, j, table_item)

    # @QtCore.Slot()
    def change_room(self, index):
        selected_room = self.ui.room_selection_combobox.itemText(index)
        # 在这里添加房间更改逻辑，将 selected_room 传递给 change_room 方法
    def on_send_interval_input(self):
        newval = self.ui.send_interval_input.text()
        self.com_config.set_software_config('send_interval_input',newval)

    # @QtCore.Slot()
    def on_website_input(self):
        if self.is_auth() == False:
            return
        newval = self.ui.website_input.text()
        self.main_url = newval
        self.com_config.set_software_config('website_input',newval)
    def on_send_mode_combobox(self):
        newval = self.ui.send_mode_combobox.currentText()
        self.com_config.set_software_config('send_mode_combobox',newval)

    # @QtCore.Slot()
    def on_room_selection_combobox(self):
        newval = self.ui.room_selection_combobox.currentText()
        self.com_config.set_software_config('room_selection_combobox',newval)
        js_code = """
            let ps = document.querySelectorAll(`p`);
            ps.forEach((ele)=>{
                if(ele.innerHTML == '%s'){
                    ele.click()
                }
            })
            window.nwp = {
                "change_room":'%s'
            }
        """ % (newval,newval)
        page = self.web_view.page()
        page.runJavaScript(js_code)
        # print(js_code)

