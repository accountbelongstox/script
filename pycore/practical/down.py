import re
# import socket
import os
import requests
import urllib
from urllib.parse import *
import http.cookiejar
import time
from pycore._base import Base
from pycore.utils import file, http
from queue import Queue

threadQueue = None
webdownQueue = None


class Down(Base):
    _download_dir = ""

    def __init__(self, root_dir=None):
        if root_dir == None:
            root_dir = file.resolve_path("out/download")
        self._download_dir = root_dir

    __header = {
        "accept-language": "zh-CN,zh,en;q=0.9",
        "sec-ch-ua": "Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "Connection": "close",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    }

    def mkdir(self, dir):
        if os.path.exists(dir) and os.path.isdir(dir):
            return False
        else:
            os.makedirs(dir, exist_ok=True)
            return True

    def webdown(self, flask, website=None):
        global webdownQueue
        if webdownQueue == None:
            webdownQueue = Queue()
        if website == None:
            website = flask.flask_request.args.get("website")
        if website == None:
            return
        webdownQueue.put(website)
        headless = False
        debug = True
        args = {
            "task": webdownQueue,
            # "save_db":True,
            "info": True,
            "headless": headless,
            "debug": debug,
            "tasks_per_thread": 1,
        }
        self.com_thread.create_thread_pool("webdown", args=args, )
        message = f"website {website} on downloading"
        result = self.com_util.print_result(data=message)
        return result

    def set_down_url_property(self, urlitem, key, value):
        if key not in urlitem:
            urlitem[key] = value
        return urlitem

    def set_down_url_default_property(self, urlitem, extract=False, overwrite=True, callback=None, save_filename=None):
        self.set_down_url_property(urlitem, "extract", extract)
        self.set_down_url_property(urlitem, "overwrite", overwrite)
        self.set_down_url_property(urlitem, "callback", callback)
        if save_filename != None and save_filename:
            self.set_down_url_property(urlitem, "save_filename", save_filename)
        return urlitem

    def get_base_down_dir(self):
        return self._download_dir

    def url_to_savename(self, url):
        base_save_dir = self.get_base_down_dir()
        filename = self.url_to_filename(url)
        save_filename = os.path.join(base_save_dir, filename)
        save_filename = file.dir_normal(save_filename)
        return save_filename

    def downs(self, tupes_or_list, save_filename=None, extract=False, overwrite=True, wait=False, callback=None,
              info=True, no_thread=False):
        global threadQueue
        # downs 由多线程模块传给file_down处理,参数使用down_file的参数
        if type(tupes_or_list) != list:
            tupes_or_list = [tupes_or_list]
        if threadQueue == None:
            threadQueue = Queue()

        no_thread_result = {}
        for url in tupes_or_list:
            if type(url) == str:
                urlli = {
                    "url": url,
                    "extract": extract,
                    "overwrite": overwrite,
                    "callback": callback,
                }
                if no_thread:
                    down_result = self.down_file(urlli, overwrite=overwrite, callback=callback, extract=extract,
                                                 info=info)
                    no_thread_result[url] = down_result
                else:
                    urlli = self.set_down_url_default_property(urlli, extract=extract, overwrite=overwrite,
                                                               callback=callback, save_filename=save_filename)
                    threadQueue.put(urlli)

        if no_thread:
            return no_thread_result
        else:
            thread_args = {
                "queue": threadQueue,
                "info": info,
                # "tasks_per_thread":,
            }
            result_list = self.com_thread.create_thread_pool("downs", args=thread_args, max_thread=30, wait=wait,
                                                             info=info, callback=callback)
            return result_list

    def down_file(self, url, save_path=None, overwrite=False, extract=False, info=True):
        save_path = file.resolve_path(save_path, self._download_dir)
        if overwrite == False and file.isfile(save_path):
            if info: print(f"down_file not overwrite and The file exists of {save_path}")
            result = save_path
            if extract:
                result = file.file_extract(save_path)
            result = self.down_result_wrap(url, result, save_path)
            return result
        if info:
            self.info(f"down_file {url}")
            self.info(f"\t -> {save_path}")
        if file.is_empty(save_path):
            overwrite = True
        connection = False
        connection_max = 10
        connection_count = 0
        re_try = False
        content = None
        while connection == False and connection_count < connection_max:
            try:
                if re_try:
                    self.warn(f"retrying, {url}.")
                content = http.get(url)
                if content != None:
                    connection = True
            except Exception as e:
                re_try = True
                self.warn(f"retrying, Error downloading {url}.")
                self.warn(e)
                connection = False
                connection_count += 1
                time.sleep(3)
        self.warn("content",len(content))
        if content == None:
            self.warn(f"The file content was not downloaded.")
            result = self.down_result_wrap(url, save_path, content)
            return result
        file.mkbasedir(save_path)
        file.save(save_path, content, overwrite=overwrite, encoding="binary")
        result = save_path
        if extract:
            result = file.file_extract(save_path)
        return self.down_result_wrap(url, result, content)

    def simple_down(self, url, save_path=None, overwrite=False):
        try:
            save_path = save_path or os.path.basename(url)
            file_path = file.resolve_path(save_path, self._download_dir)
            if not overwrite and os.path.exists(file_path):
                print(f"文件已存在：{file_path}")
                return file_path
            response = requests.get(url, verify=True)
            response.raise_for_status()
            with open(file_path, 'wb') as dFile:
                dFile.write(response.content)
            print(f"文件下载成功，保存在：{file_path}")
            return file_path
        except requests.exceptions.RequestException as e:
            print(f"文件下载失败：{e}")
            return None

    def down_result_wrap(self, url, save_filename, content):
        content_len = 0
        if content or content != None:
            content_len = len(str(content))
        else:
            save_filename = None
        url_result = {
            "url": url,
            "save_filename": save_filename,
            "content_len": content_len,
        }
        return url_result

    def down_web(self, url):
        # 创建主线程，专用于打开页面，以及分析页面并调用多线程下载
        th_main = self.com_thread.create_thread(
            thread_type="down_web",
            args=url
        )
        th_main.start()

    def url_to_filename(self, url):
        url_parse = urlparse(url)
        url_netloc = url_parse.netloc
        url_path = url_parse.path
        url_query = url_parse.query
        middle_path = url_path.split("/")
        filename = middle_path.pop()
        middle_path = "/".join(middle_path)
        if filename.find(".") == -1:
            special_characters = re.compile(r"[\\\:\*\?\"\<\>\|]+")
            filename = url_path + "?" + url_query
            filename = re.sub(special_characters, "", filename)
        path_dirname = os.path.join(middle_path, filename)
        filename = f"{url_netloc}/{path_dirname}"
        filename = file.dir_normal(filename)
        return filename

    def down_file_from_request(self, flask):
        """Download curses.pyc file from the request."""
        file = flask.request.files['file']
        url = self.com_flask.get_request(flask, "url")
        save_name = self.com_flask.get_request(flask, "save_name")
        if not save_name:
            save_name = file.url_tofile(url)

        if file.content_type != 'application/octet-stream':
            self.warn(
                f'com_http down_file_from_request File is application/octet-stream. \n url: {url} \n save_name: {save_name}')
            save_object = {
                "save_dir": None
            }
        else:
            down_file = os.path.join(self._download_dir, save_name)
            with open(down_file, 'wb') as f:
                for chunk in file.stream:
                    f.write(chunk)
            save_object = {
                "save_dir": down_file
            }
        result = self.com_util.print_result(data=save_object)
        return result
