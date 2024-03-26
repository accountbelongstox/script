import os
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import quote


class urlTool:
    @staticmethod
    def getBaseUrl(url):
        if '/' not in url:
            return url + "/"
        else:
            url_parse = urlparse(url)
            scheme = url_parse.scheme
            netloc = url_parse.netloc
            urlpath = url_parse.path
            urlpath = urlpath.split('/')[0:-1]
            urlpath = "/".join(urlpath)
            BaseUrl = scheme + "://" + netloc + urlpath
            return BaseUrl + "/"

    @staticmethod
    def joinUrl(baseurl, attachUrl):
        if  urlTool.is_url(attachUrl) == True:
            return attachUrl
        baseurl = urlTool.get_url_dir(baseurl)
        concatenate_url = urljoin(baseurl, attachUrl)
        concatenate_url = concatenate_url.replace('\\', '/')
        return concatenate_url

    @staticmethod
    def extract_url_main(url):
        url_parse = urlparse(url)
        netloc = url_parse.netloc
        if '/' in netloc:
            main_part = netloc.split('/')[0]
        else:
            main_part = netloc
        return main_part

    @staticmethod
    def remove_hash(url, slash=["#", "?"]):
        if isinstance(slash, list):
            for char in slash:
                url = url.split(char, 1)[0]
        elif isinstance(slash, str):
            url = url.split(slash, 1)[0]
        return url

    @staticmethod
    def url_to_filepath(url):
        url = urlTool.remove_hash(url, "#")
        if url.startswith(('http://', 'https://')):
            url = url.split('://', 1)[1]
        if '/' not in url:
            return urlTool.url_add_index(url)
        else:
            last_char = url[-1]
            if last_char == '/':
                return urlTool.url_add_index(url)
            else:
                if '/' in url:
                    url_without_last = urlTool.get_mark_after(url, "/")
                    if url_without_last != "":
                        between_slashes_to_questions = url_without_last.split('?')[0]
                        if '.' in between_slashes_to_questions:
                            url = url.split('?')[0]
                        elif '?' in url:
                            question_mark = urlTool.get_mark_after(url, "?")
                            url_after = url.split(question_mark)[0]
                            question_mark = urlTool.quote_url(question_mark)
                            return urlTool.url_format_path(url_after) + question_mark
                        else:
                            url = urlTool.url_add_index(url)
                else:
                    url = urlTool.url_add_index(url)
                return urlTool.url_format_path(url)

    @staticmethod
    def url_add_index(url):
        url = os.path.join(url, "index.html")
        return url

    @staticmethod
    def url_to_downpath(download_dir, url):
        url = urlTool.remove_hash(url,"#")
        url_dir = urlTool.url_to_filepath(url)
        return os.path.join(download_dir, url_dir)

    @staticmethod
    def get_url_dir(url):
        url = urlTool.remove_hash(url)
        if not url.startswith(('http://', 'https://')):
            url = "http://" + url
        last_char = url[-1]
        if last_char == '/':
            return url
        else:
            if '/' in url:
                url_without_last = urlTool.get_mark_after(url, "/")
                if '.' in url_without_last:
                    url = url.rsplit('/', 1)[0]
                else:
                    url = url + "/"
            return url

    @staticmethod
    def get_mark_after(url, mark="/", include=True):
        last_slash_index = url.rfind(mark)
        if last_slash_index != -1:
            if include == False:
                last_slash_index = last_slash_index + 1
            result = url[last_slash_index:]
            return result
        else:
            return ""

    @staticmethod
    def url_format_path(url):
        return url.replace(':', '_').replace('?', '_').replace('&', '_')

    @staticmethod
    def is_url(input_string):
        parsed_url = urlparse(input_string)
        return parsed_url.scheme != '' and parsed_url.netloc != ''
    @staticmethod
    def quote_url(url):
        url = url.replace(':', '_').replace('/', '_')
        return quote(url)


