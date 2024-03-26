import queue
import threading
from kernel.base.base import Base
import uuid

class ComThread(threading.Thread, Base):
    def __init__(self, target, task=None, retry_task=False):
        threading.Thread.__init__(self)
        self.task = task
        self.target = target  # "cmd" or def
        self.retry_task = retry_task
        self.resultQueue = queue.Queue()
        self.is_alive = True
        self.stop_flag = threading.Event()
        self.subprocess = None
        self.thread_id = self.generate_id()

    def cmd(self, cmd):
        if self.subprocess is None:
            import subprocess
            self.subprocess = subprocess
        try:
            result = self.subprocess.check_output(cmd, shell=False)
            return result
        except self.subprocess.CalledProcessError as e:
            self.error(f"{e},{cmd}")
            return None

    def generate_id(self):
        return str(uuid.uuid4())

    def run(self):
        self.is_alive = True
        if self.target is None:
            return self.resultQueue
        elif self.target == "cmd":
            while not self.task.empty() and not self.stop_flag.is_set():
                args = self.task.get()
                if self.stop_flag.is_set():
                    self.info("ComThread stopped.")
                    break
                elif isinstance(args, str) or isinstance(args, list):
                    cmd = args
                elif isinstance(args, dict):
                    cmd = args.get('cmd')
                else:
                    cmd = args
                result = self.cmd(cmd)
                self.resultQueue.put(result)
        else:
            if self.task:
                while not self.task.empty():
                    if self.stop_flag.is_set():
                        self.info("ComThread stopped.")
                        break
                    args = self.task.get()
                    try:
                        result = self.target(args)
                    except Exception as e:
                        self.error(f"Thread-com: {e}")
                        if self.retry_task:
                            self.task.put(args)
                    else:
                        self.resultQueue.put(result)
                self.info("The task completes and the current thread ends")
            else:
                try:
                    result = self.target()
                except Exception as e:
                    self.error(f"Thread-com: {e}")
                else:
                    self.resultQueue.put(result)
        self.is_alive = False

    def set(self, name, data):
        self.__dict__[name] = data

    def set_args(self, args):
        self.args = args

    def done(self):
        if self.is_alive is False:
            return True
        return False

    def is_task_done(self):
        if self.task:
            return self.task.empty()
        else:
            return True

    def result(self):
        while not self.done():
            self.warn("Waiting for ComThread return.")
        result_queue = []
        while not self.resultQueue.empty():
            result_queue.append(self.resultQueue.get())
        return result_queue

    def stop(self):
        self.warn("Stopping ComThread...")
        self.stop_flag.set()
        self.join()
