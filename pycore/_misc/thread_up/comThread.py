import threading
from pycore.base.base import Base


# 多线程下载模块
class ComThread(threading.Thread, Base):  # 继承父类threading.Thread
    args = None

    def __init__(self, args, target=None, group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=False):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.task = args.get('tasks')
        if target == None:
            target = args.get('target')
        self.target = target
        self.args = args
        self.thread_name = thread_name
        self.resultQueue = []
        self.is_alive = True

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        self.is_alive = True
        if self.target == None:
            return self.resultQueue
        transition_args = "args" in self.com_util.get_parameter(self.target)
        if self.is_queue == True:
            while self.args.qsize() > 0:
                if transition_args:
                    args = self.args.get()
                    result = self.target(args)
                else:
                    result = self.target()
                self.resultQueue.append(result)
            self.is_alive = False
        else:
            if transition_args:
                result = self.target(self.args)
            else:
                result = self.target()
            self.resultQueue.append(result)
            self.is_alive = False

    def set(self, name, data):
        self.__dict__[name] = data

    def setargs(self, args):
        self.args = args

    def done(self):
        if self.is_alive == False:
            return True
        return False

    def result(self):
        while self.done() == False:
            self.com_util.print_warn(f"waiting for ComThread return.")
        resultQueue = self.resultQueue
        self.resultQueue = []
        return resultQueue
