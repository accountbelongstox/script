from pycore.base.base import Base
import os
import re
import threading

threadLock = threading.Lock()
global_thread = {}


class PingThread(threading.Thread, Base):
    def __int__(self):
        pass

    def ping_ip(self, ip):
        cmd = f"ping {ip}"
        outs = os.popen(cmd, 'r')
        out = outs.read()
        get_time = re.compile(r"time\=(\d+)")
        time_group = re.findall(get_time, out)
        time_outs = re.compile(r"request\s+timed\s+out", re.I)
        time_outs_group = re.findall(time_outs, out)
        time_group = [int(t) for t in time_group]
        # 如果有 Request time out
        time_outs_group = [1000 for t in time_outs_group]
        # 合并所有延迟,并计算最终值.
        time_group = time_group + time_outs_group
        timeout = 0
        for t in time_group:
            timeout += t
        divint = len(time_group)
        is_NotFound_mianhost = False
        if divint == 0:
            is_NotFound_mianhost = True
            divint = 1
        timeout = timeout // divint
        # print(f" ping {domain} {ip} {timeout}ms")
        if is_NotFound_mianhost:
            ping_result = None
            print("Error:", outs)
        else:
            print(f"timeout: {timeout}\n")
            ping_result = timeout
        return ping_result
