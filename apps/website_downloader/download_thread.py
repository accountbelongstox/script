import threading
threadLock = threading.Lock()
global_thread = {}
import secrets
import os
import requests
from url_tool import  urlTool
from file_tool import  fileTool
from pycore.base.base import Base

class DownThread(threading.Thread,Base):
    __count = 0
    __resultList = []

    def __init__(self, queue,thread_id=None,thread_name=None, daemon=True):
        if thread_id == None:
            thread_id = self.generate_random_string()
        if thread_name == None:
            thread_name = self.generate_random_string()
        self.info("Start multi-threaded download ID "+thread_id)
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__thread_id = thread_id
        self.thread_name = thread_name
        self.__queue = queue
        self.__count = self.__queue.qsize()
        self.download_dir = os.path.join(self.find_out_dir(),"download_website")

    def find_out_dir(self):
        current_directory = os.getcwd()
        parent_directory = os.path.dirname(current_directory)
        out_directory_path = os.path.join(parent_directory, 'out')
        if os.path.exists(out_directory_path) and os.path.isdir(out_directory_path):
            return out_directory_path
        else:
            current_out_directory_path = os.path.join(current_directory, 'out')
            if os.path.exists(current_out_directory_path) and os.path.isdir(current_out_directory_path):
                return current_out_directory_path
            else:
                os.makedirs(current_out_directory_path)
                return current_out_directory_path

    def generate_random_string(self):
        return secrets.token_hex(16)

    def get_task_item(self):
        if self.__queue.qsize() > 0:
            item = self.__queue.get()
            return item
        return None

    def run(self):
        item = self.get_task_item()
        while item != None:
            item = self.get_content(item)
            item = self.get_task_item()
            self.__resultList.append(item)
            self.__count += 1

    def get_content(self, url, overwrite=True):
        try:
            save_path = self.get_save_path(url)
            if not overwrite and os.path.exists(save_path):
                self.info(f"File already exists: {save_path}")
                content = fileTool.read_file(save_path)
                return save_path, content
            response = self._get_response(url)
            if response.status_code == 404:
                self.info(f"404 Error: {url}")
                return save_path, response.content
            response.raise_for_status()
            while response.is_redirect:
                redirected_url = response.headers['Location']
                response = self._get_response(redirected_url)
                response.raise_for_status()
            self.info(f"Downloaded {url} to {save_path}")
            return save_path, response.content
        except requests.RequestException as e:
            self.info(f"Error downloading {url}: {str(e)}")
            return None, None
    def _get_response(self, url):
        return requests.get(url)

    def get_save_path(self, url, save_path=None):
        if save_path is None:
            return urlTool.url_to_downpath(self.download_dir, url)
        return save_path

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