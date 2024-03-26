import re
import os
from pub_tool import  tools
from urllib.parse import urlparse
from urllib.parse import urljoin
from downloader import Downloader
downloader = Downloader()
from pycore._base import Base

class CssUrlParser(Base):
    def __init__(self, baseUrl=None):
        self.baseUrl = baseUrl
        self.urls = []
        self.file_types = [
            *['.' + value for value in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico', 'jfif', 'pjpeg', 'pjp']],
            *['.' + value for value in ['woff', 'woff2', 'ttf', 'otf', 'eot', 'svg']],
            *['.' + value for value in ['css', 'scss', 'sass', 'less', 'styl']],
        ]

    def is_css_file(self,file_path, allowed_extensions=['css', 'scss', 'less','js']):
        file_extension = file_path.lower().split('.')[-1]
        return file_extension in allowed_extensions

    def set_base_url(self, baseUrl):
        self.baseUrl = baseUrl

    def process_css_content(self, css_content,download=False):
        return self.find_css_img_font(css_content,download=download)

    def process_css_file(self, css_file_path,download=True):
        with open(css_file_path, 'r', encoding='utf-8') as file:
            css_content = file.read()
        return self.find_css_img_font(css_content,download=download)

    def process_css_url(self, css_url):
        downloader = Downloader()
        self.baseUrl = self.getBaseUrl(css_url)
        filepath,content = downloader.download_url(css_url)
        with open(filepath, 'r', encoding='utf-8') as file:
            css_content = file.read()
        return self.find_css_img_font(css_content)

    def extract_valid_part(self,  css_content):
        file_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico', 'jfif', 'pjpeg', 'pjp',
                           'woff', 'woff2', 'ttf', 'otf', 'eot', 'svg',
                           'css', 'scss', 'sass', 'less', 'styl']
        file_extension_pattern = '|'.join(map(re.escape, file_extensions))

        pattern1 = re.compile(fr'[^(\']*?\.({file_extension_pattern})\s*[\')]', re.IGNORECASE)

        # pattern2 = re.compile(fr'[^("]*?{re.escape(value)}\s*[")]', re.IGNORECASE)
        matches = pattern1.findall(css_content)
        # matches2 = pattern2.findall(css_content)

        values = matches
        for i in range(len(values)):
            value = values[i]
            value =value.strip()
            if value and value[-1] in ("'", '"', ')'):
                values[i] = value[:-1]
        return values

    def extract_http_part(self,  css_content):
        pattern_http = re.compile(r"[('\"](https?://[^)'\"]+)[')\"]")
        matches3 = pattern_http.findall(css_content)

        values = matches3
        for i in range(len(values)):
            value = values[i]
            value =value.strip()
            if value and value[-1] in ("(", ')'):
                values[i] = value[:-1]
        return values

    def find_css_img_font(self, css_content,download=True):
        all_img_css_font_array = self.extract_valid_part( css_content)
        all_https_array = self.extract_http_part( css_content)
        all_array = all_img_css_font_array + all_https_array
        find_arr = set()
        find_arr = tools.recursive_traversal(all_array,find_arr)
        if download == False:
            return find_arr
        result = []
        for url in find_arr:
            new_url = self.joinUrl(self.baseUrl,url)
            res = downloader.download_url(new_url)
            result.append(res)
        return result
    
    def getBaseUrl(self, url):
        if '/' not in url:
            return url+ "/"
        else:
            url_parse = urlparse(url)
            scheme = url_parse.scheme
            netloc = url_parse.netloc
            urlpath = url_parse.path
            urlpath = urlpath.split('/')[0:-1]
            urlpath = "/".join(urlpath)
            BaseUrl = scheme + "://" + netloc + urlpath
            return BaseUrl + "/"

    def joinUrl(self, baseurl, attachUrl):
        concatenate_url = urljoin(baseurl, attachUrl)   
        concatenate_url = concatenate_url.replace('\\', '/')
        return concatenate_url
      
# baseUrl = "https://example.com/"
# css_parser = CssUrlParser(baseUrl)

# sample_css_content = '''https://static.jstree.com/latest/assets/dist/themes/default/style.min.css'''
# self.info(sample_css_content)
# css_parser.process_css_url(sample_css_content)

