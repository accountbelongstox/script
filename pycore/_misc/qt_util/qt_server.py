from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtNetwork import *


class QTServer(QObject):
    def __init__(self):
        super().__init__()
        self.server = QTcpServer(self)
        self.server.listen(QHostAddress.LocalHost, 8889)
        self.server.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            socket.readyRead.connect(self.on_ready_read)
            socket.disconnected.connect(self.on_disconnected)
            print(f'New connection from {socket.peerAddress().toString()}:{socket.peerPort()}')

    def on_ready_read(self):
        socket = self.sender()
        while socket.bytesAvailable():
            data = socket.readAll().data().decode()
            print(f'Received message from client: {data}')
            # 将收到的消息作为参数执行 JavaScript 代码
            self.run_javascript(data)

    def on_disconnected(self):
        socket = self.sender()
        print(f'Client {socket.peerAddress().toString()}:{socket.peerPort()} disconnected.')

    def run_javascript(self, data):
        # 执行 JavaScript 代码
        # web_view.page().runJavaScript(f'someFunction("{data}")', self.handle_javascript_result)
        return None

    def handle_javascript_result(self, result):
        print(f'JavaScript result: {result}')
