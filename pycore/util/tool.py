# import re
# # import socket
# # import os
# import requests
# import urllib
# from urllib.parse import *
# import http.cookiejar
# # import time
# # from queue import Queue

class Tool():
    def copy(self,origin_json, option={}):
        option_copy = {**origin_json, **option}
        return option_copy

    def merge(self,origin_json, option={}):
        option_copy = {**origin_json, **option}
        return option_copy

    def deep_update(self, target, source):
        if not isinstance(target, dict):
            target = {}
        if not isinstance(source, dict):
            return target
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                target[key] = self.deep_update(target[key], value)
            elif isinstance(value, list) and isinstance(target.get(key), list):
                target[key] = list(set(target[key] + value))
            else:
                target[key] = value
        return target