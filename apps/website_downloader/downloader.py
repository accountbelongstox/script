import os
import requests
from urllib.parse import urlparse
from url_tool import  urlTool  
from file_tool import  fileTool
<<<<<<< HEAD
from kernel.base.base import Base
=======
from pycore._base import Base
>>>>>>> origin/main

class Downloader(Base):
    def __init__(self, download_dir=None) -> None:
        self.download_dir = os.path.join(self.find_out_dir(),"download_website") if download_dir is None else download_dir

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

    def download(self, url, save_path=None, overwrite=True, handle=None):
        try:
            save_path = self.get_save_path(url, save_path)
            if not overwrite and os.path.exists(save_path):
                self.info(f"File already exists: {save_path}")
                content = fileTool.read_file(save_path)
                return save_path, content
            response = self._get_response(url)
            if response.status_code == 404:
                self.info(f"404 Error: {url}")
                self._process_and_write_content(save_path, response.content, handle)
                return save_path, response.content
            response.raise_for_status()
            while response.is_redirect:
                redirected_url = response.headers['Location']
                response = self._get_response(redirected_url)
                response.raise_for_status()
            self._process_and_write_content(save_path, response.content, handle)
            self.info(f"Downloaded {url} to {save_path}")
            return save_path, response.content
        except requests.RequestException as e:
            self.info(f"Error downloading {url}: {str(e)}")
            return None, None

    def get_save_path(self, url, save_path=None):
        if save_path is None:
            return urlTool.url_to_downpath(self.download_dir, url)
        return save_path

    def _get_response(self, url):
        return requests.get(url)

    def _process_and_write_content(self, save_path, content, handle):
        if handle is not None:
            content = handle(content)
        fileTool.mkdir(os.path.dirname(save_path))
        fileTool.write(save_path, content)
    
    def download_urls(self, urls):
        for url in urls:
            self.download(url)

    def download_url(self, url):
        return self.download(url)

    def get_filename_by_url(self, url):
        if '/' not in url:
            return os.path.join(self.download_dir,f"index.html")
        parts = url.rsplit('/', 1)
        if len(parts[1]) > 0 and '.' in parts[1]:
            return os.path.join(self.download_dir,parts[1])
        else:
            return os.path.join(self.download_dir,f"index.html")
    
    def get_filedir_by_url(self, url):
        if '/' not in url:
            return os.path.join(self.download_dir, url)
        parts = url.rsplit('/', 1)
        if len(parts[1]) > 0:
            return os.path.join(self.download_dir,parts[0] + '/')
        else:
            return os.path.join(self.download_dir,parts[0])


    
