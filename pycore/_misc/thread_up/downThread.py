from pycore.base import Base
import threading

threadLock = threading.Lock()
global_thread = {}


# 多线程下载模块
class DownThread(threading.Thread, Base):  # 继承父类threading.Thread
    # down线程的args传入的是一个Queue对象,所创建的其他线程共同竞争
    __count = 0
    __resultList = []

    def __init__(self, target, args, group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=True):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.target = target
        self.__queue = args["queue"]
        if "info" in args:
            self.__info = args["info"]
        else:
            self.__info = True
        self.thread_name = thread_name
        self.__count = self.__queue.qsize()

    def get_task_item(self):
        if self.__queue.qsize() > 0:
            item = self.__queue.get()
            return item
        return None

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        """
        @ 参数 url为 tuple 类型，则格式为 [
            ( url, file_name , override),
            ( url, file_name , override)
                                        ]  后面filename 及 override 不用传
        @ 参数为 list 类型,则格式为[url] filename 及 override 将会自动解析
        :param url:
        :param file_name:
        :param override:
        :return:
        """
        item = self.get_task_item()
        while item != None:
            item = self.com_http.set_down_url_default_property(item)
            result = self.error_redown(item)
            item = self.get_task_item()
            self.__resultList.append(result)
            self.__count += 1

    def error_redown(self, item, index=0):
        try:
            result = self.com_http.down_file(item, info=self.__info)
            return result
        except Exception as e:
            if index > 10:
                print(e)
                self.com_util.print_danger(f"When the number of retries reaches {index}, give up the attempt.")
                return None
            self.com_util.print_danger(e)
            self.com_util.print_warn(f"retrying down_file.")
            index += 1
            return self.error_redown(item, index)

    def done(self):
        if self.__queue.qsize() == 0:
            return True
        else:
            return False

    def result(self):
        self.__count = 0
        result = self.__resultList
        self.__resultList = []
        return result
