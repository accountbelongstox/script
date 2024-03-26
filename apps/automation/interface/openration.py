from abc import ABC, abstractmethod

class OperationInterface(ABC):

    @abstractmethod
    def is_chrome_open(self):
        """
        判断Chrome是否打开。
        """
        pass

    @abstractmethod
    def open_chrome(self):
        """
        打开Chrome。
        """
        pass

    @abstractmethod
    def is_chrome_open_with_url(self, url):
        """
        判断Chrome是否打开某个网址。
        :param url: 要检查的网址。
        """
        pass

    @abstractmethod
    def open_website_in_chrome(self, url):
        """
        使用Chrome打开一个网站。
        :param url: 要打开的网址。
        """
        pass

    @abstractmethod
    def open_new_chrome_tab(self):
        """
        打开一个新的Chrome tab标签栏。
        """
        pass

    @abstractmethod
    def is_new_chat_created(self):
        """
        判断是否出现新建一个聊天。
        """
        pass

    @abstractmethod
    def is_current_chat_input_enabled(self):
        """
        判断当前的聊天是否可输入。
        """
        pass

    @abstractmethod
    def is_current_chat_returned(self):
        """
        判断当前的聊天是否已返回。
        """
        pass

    @abstractmethod
    def send_chat_message(self, message):
        """
        发送聊天消息。
        :param message: 要发送的消息内容。
        """
        pass

    @abstractmethod
    def create_new_chat(self):
        """
        创建一个新的聊天。
        """
        pass

    @abstractmethod
    def get_current_chat_content(self):
        """
        获取当前聊天内容。
        """
        pass

    @abstractmethod
    def scroll_chat_to_position(self, position):
        """
        滚动聊天到指定位置。
        :param position: 要滚动到的位置。
        """
        pass

    @abstractmethod
    def get_chat_history(self):
        """
        获取聊天历史记录。
        """
        pass

    @abstractmethod
    def navigate_to_chat_history(self):
        """
        跳转到聊天历史记录。
        """
        pass

    @abstractmethod
    def refresh_chat(self):
        """
        刷新聊天。
        """
        pass

    @abstractmethod
    def resend_chat_message(self, message):
        """
        重新发送聊天消息。
        :param message: 要重新发送的消息内容。
        """
        pass