from pycore.base.base import Base
import time
import threading


class WebDownOpenUrlThread(threading.Thread, Base):
    __urls = None  # 用来接收从主线程传过来的Queue
    selenium = None
    __urls_page_resource_wait_queue = None  # 取得的每个页面的URL及源码暂存，交由主线程处理
    threadLock = None
    __listing = True
    # 最大打开页面数
    __max_open_url = 50

    # __already_open_urls = {}
    def __init__(self, target=None, args=(), max_open=50, timeout=10, group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=False):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.args = args
        self.target = target
        self.__max_open_url = max_open
        # 如果在该时间段内加载出一定的代码将转至动态加载时间翻倍
        self.__timeout = timeout
        self.thread_name = thread_name
        self.selenium = args[0]
        driver = args[1]
        self.selenium.set_driver(driver)
        self.__urls = args[2]
        self.threadLock = args[3]

    def run(self):
        max = self.__max_open_url
        while True:
            # 初始化执行，先监听所有TAG而，并单独使用一个线程实时切换。
            url_formats = self.get_url_from_queue(max=max)
            print(f"need new open urls {url_formats}")
            for url_format in url_formats:
                url = url_format["url"]
                # dir = url_format["dir"]
                # filename = url_format["filename"]
                self.com_selenium.open(url, not_wait=True)
                # url_format["index"] = self.selenium.get_current_window_handle_index()
                # self.threadLock.acquire()
                # self.__already_open_urls[url] = url_format
                # self.threadLock.release()
            # 分析由WebDownForeachTagThread在切换tag中获取到地网页源码。
            time.sleep(0.2)

    # def get_already_open_urls(self):
    #     self.threadLock.acquire()
    #     already_open_urls = self.__already_open_urls
    #     self.threadLock.release()
    #     return already_open_urls

    def get_url_from_queue(self, max=1):
        if max == 1 and self.__urls.qsize() > 0:
            url = self.__urls.get()
        elif max > 1:
            urls = []
            while max > 0 and self.__urls.qsize() > 0:
                url = self.__urls.get()
                urls.append(url)
                max -= 1
            url = urls
        else:
            url = None
        return url
