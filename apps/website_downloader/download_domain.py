# import requests
from downloader import Downloader
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from download_css import CssUrlParser
from pub_tool import tools
from file_tool import  fileTool

downloader = Downloader()
from url_tool import urlTool

css_parser = CssUrlParser()

from pycore._base import Base

class WebPageDownloader(Base):
    def __init__(self):
        self.URLList = {}
        self.ResourceList = []
        self.SRCList = {}
        self.base_url = ""
    def test(self):
        dpath,content = downloader.download("https://fonts.googleapis.com/css?family=Montserrat:300,400,500,600,700")
        self.info(dpath)
        self.info(content)
    
    def download_domain(self, url):
        base_url = urlTool.getBaseUrl(url)
        self.base_url = base_url
        self.addToUrlList(url, "curses.pyc")
        self.monitor()

    def addToUrlList(self, url, url_type, print_item=None):
        is_replace = False
        if urlTool.is_url(url) == True and url_type in ["css","src"]:
            is_replace = True
        url_dict = {
            "url": url,
            "is_replace": is_replace,
            "type": url_type,
            "download": False,
            "download_status": None,
            "download_path": None,
        }
        url_key = url.split('#', 1)[0]
        if url_key not in self.URLList:
            self.URLList[url_key] = url_dict
            if print_item is not None:
                print_item[url] = url_dict

    def addToSrcList(self, url, url_type, print_item=None):
        is_replace = False
        if urlTool.is_url(url) == True and url_type in ["css","src"]:
            is_replace = True
        url_dict = {
            "url": url,
            "is_replace": is_replace,
            "type": url_type,
            "download": False,
            "download_status": None,
            "download_path": None,
        }
        url_key = url.split('#', 1)[0]
        if url_key not in self.SRCList:
            self.SRCList[url_key] = url_dict

    def set_download_status(self, url, download_status):
        if url in self.URLList:
            self.URLList[url]["download"] = download_status
        else:
            self.info(f"URL '{url}' not found in URL list.")

    def get_availble_url(self):
        for url, url_info in self.URLList.items():
            if url_info["download"] == False:
                return url_info
        return None
    def get_availble_src(self):
        for url, url_info in self.SRCList.items():
            if url_info["download"] == False:
                return url_info
        return None

    def has_available_url(self):
        for url_info in self.URLList.values():
            download_status = url_info.get("download", False)
            if not download_status:
                return True
        return False

    def has_available_src(self):
        for url_info in self.SRCList.values():
            download_status = url_info.get("download", False)
            if not download_status:
                return True
        return False

    def monitor(self):
        while self.has_available_url():
            url_dict = self.get_availble_url()
            self.download_href(url_dict)

    def claerSRCList(self,from_page):
        while self.has_available_src():
            url_dict = self.get_availble_src()
            self.download_src(from_page,url_dict)

    def download_src(self,from_page, url_dict):
        url_type = url_dict['type']
        _url = url_dict['url']
        downloadpath, content = downloader.get_content(url=_url,overwrite=False)
        if urlTool.is_url(_url) == True:
            pass
        download_status = False
        if downloadpath is not None:
            download_status = True
            if url_type == 'css':
                css_content = tools.decode(content)
                if css_content != None:
                    find_arr = css_parser.process_css_content(css_content,download=False)
                    base_url = urlTool.get_url_dir(_url)
                    for url in find_arr:
                        new_url = urlTool.joinUrl(base_url,url)
                        # d_css, css_text = downloader.get_content(url=new_url)
                        # self.info("d_css")
                        # self.info(d_css)
        if content != None:
            fileTool.write(downloadpath,content)
            download_status = False
        for url, url_info in self.SRCList.items():
            if url_info.get("url") == _url:
                url_info["download"] = True
                url_info["download_status"] = download_status
                url_info["download_path"] = downloadpath
                break

    def download_href(self, url_dict):
        url_type = url_dict['type']
        _url = url_dict['url']
        save_path = downloader.get_save_path(_url)
        downloadpath, content = downloader.get_content(url=_url,overwrite=False)
        if urlTool.is_url(_url) == True:
            # 替换地址 为 本地低一级地址
            # 并将 downloadpath 替换  _url
            pass
        download_status = False
        if downloadpath is not None:
            download_status = True
            html_content = tools.decode(content)
            if html_content != None:
                self.extract_a(html_content, _url)
        if content != None:
            fileTool.write(downloadpath,content)
            download_status = False
        self.claerSRCList(_url)
        for url, url_info in self.URLList.items():
            if url_info.get("url") == _url:
                url_info["download"] = True
                url_info["download_status"] = download_status
                url_info["download_path"] = downloadpath
                break

    def get_html_content_and_extract_a(self, url):
        download_dir, html_content = downloader.download(url)
        self.extract_links(html_content, url)

    def extract_a(self, html_content, base_url):
        self.extract_links(html_content, base_url)
    def gen_link_dict(self, src, src_type="curses.pyc"):
        return {"url": src, "type": src_type}
    def extract_links(self, html_content, base_url):
        self.info("base_url : "+base_url)
        base_url = urlTool.get_url_dir(base_url)
        self.info(" then : "+base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        print_item = dict()
        #https://uitheme.net/elomoas  login.html
        for a_tag in soup.find_all('curses.pyc', href=True):
            href = urlTool.joinUrl(base_url, a_tag['href'])
            self.info(" href : "+a_tag['href'])
            self.info(" join : "+href)
            self.addToUrlList(href, "curses.pyc", print_item)

        for style_tag in soup.find_all('link', rel='stylesheet', href=True):
            href = urlTool.joinUrl(base_url, style_tag['href'])
            self.addToSrcList(href, "css", print_item)

        for link_tag in soup.find_all('link', href=True):
            href = urlTool.joinUrl(base_url, link_tag['href'])
            if css_parser.is_css_file(href):
                self.addToSrcList(href, "css", print_item)
            else:
                self.addToSrcList(href, "src", print_item)

        for img_tag in soup.find_all('img', src=True):
            src = urlTool.joinUrl(base_url, img_tag['src'])
            self.addToSrcList(src, "src", print_item)

        for script_ in soup.find_all('script', src=True):
            src = urlTool.joinUrl(base_url, script_['src'])
            self.addToSrcList(src, "css", print_item)
        self.handle_content(html_content,print_item)
        self.print_links(print_item)

    def handle_content(self, html_content,tick_links):
        for url, url_info in tick_links.items():
            url_type = url_info["type"]
            src_url = url_info["url"]
            is_replace = urlTool.is_url(src_url)
            if is_replace == True:
                pass
    def print_links(self, print_item):
        for url, url_info in print_item.items():
            url_type = url_info["type"]
            if url_type == "curses.pyc":
                # self.info("Web link:", url)
                pass
            elif url_type == "src":
                # self.info("Resource link:", url)
                pass
            elif url_type == "css":
                self.info("stylesheet link:", url)
            else:
                self.info("Unknown Type URL:", url)


if __name__ == "__main__":
    web_page_downloader = WebPageDownloader()
    # web_page_downloader.test()
    # exit(0)
    web_page_downloader.download_domain("https://uitheme.net/elomoas")
