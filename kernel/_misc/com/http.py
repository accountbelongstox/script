import re
import ipaddress
# import socket

from kernel.base.base import *
import os
from lxml import etree
# import re
import requests
# import re
import urllib
from urllib.parse import *
import http.cookiejar
# from multiprocessing import Pool,Process
import time
from queue import Queue
from werkzeug.utils import secure_filename

threadQueue = None
webdownQueue = None

import geoip2.database


class Http(Base):
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
    __remote_ipurlscircle = 0
    __remote_ipurls = [
        # "http://static.hk.12gm.com/index.php",
        'https://update.cz88.net/',
        'http://ip.zxinc.org/ipquery/',
        'https://qifu.baidu.com/?activeKey=SEARCH_IP&trace=apistore_ip_aladdin&activeId=SEARCH_IP_ADDRESS&ip=',
        'https://www.baidu.com/s?wd=ip%E5%9C%B0%E5%9D%80%E6%9F%A5%E8%AF%A2&rsv_spt=1&rsv_iqid=0x870e47a60006aaf8&issp=1&f=3&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&rsv_dl=ts_0&oq=iphone%25E5%25AE%2598%25E7%25BD%2591&rsv_btype=t&inputT=3785&rsv_t=8429A755wKs%2F9DjnrzFx31UYNgAPh%2F5vJX5LTgEUUKEqYsYZk8%2FlpN2mo8vsgQROd3kQ&rsv_sug3=13&rsv_sug1=12&rsv_sug7=101&rsv_pq=9cc7352e000640ba&rsv_sug2=0&prefixsug=ip%2520d&rsp=0&rsv_sug4=4336',
        "https://www.ipplus360.com/",
        "https://ip.zxinc.org/ipquery/",
        "https://www.cz88.net/accurate",
        "https://www.ip133.com/",
        "https://2023.ip138.com/",
        "https://tool.lu/ip/",
        "https://ip.chinaz.com/",
        "https://uutool.cn/ip/",
        "http://myip.ipip.net/",
        "https://zh-hans.ipshu.com/myip_info?random=0.5157084943644001",
        "https://ip.900cha.com/",
        "https://ip125.com/",
        "https://1675494712686-1nbh18mhm5jj.dns-detect.alicdn.com/api/detect/DescribeDNSLookup?cb=__callback__39641181675494712686",
        "https://ip.skk.moe/",
        "https://ip.bmcx.com/",
        "https://tool.ruyo.net/ip/",
        "https://www.ipip5.com/",
        "http://ip.webmasterhome.cn/",
        "https://tools.codercto.com/query_ip.html",
        "https://www.123cha.com/ip/",
        "https://www.iamwawa.cn/ip.html",
        "https://ip.negui.com/"
    ]
    query_ip_data = None

    def __init__(self, args):
        requests.adapters.DEFAULT_RETRIES = 5
        pass

    # @flask_app.route('/okx/<path:xxxx>')
    # def add_account(xxxx):
    #     self = _self
    #     print(xxxx)

    def open_url(self, url, decode="utf-8"):
        cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        header = [
            ("accept-language", "zh-CN,zh,en;q=0.9"),
            ("sec-ch-ua", "Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102"),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", "Windows"),
            ("sec-fetch-dest", "empty"),
            ("sec-fetch-mode", "cors"),
            ("sec-fetch-site", "same-origin"),
            ("user-agent",
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36")
        ]
        opener = urllib.request.build_opener(handler)
        opener.addheaders = header
        text = opener.open(url, verify=False)
        content = text.read()
        if type(decode) == str:
            content = content.decode(decode)
        return content

    def get(self, url, data=None, to_string=True, headers=None):
        proxy = {"http": None, "https": None}
        session = requests.Session()
        # session.keep_alive = False
        session.trust_env = False
        headers = self.set_header(headers)
        if type(data) == dict:
            url = url.strip()
            url = url.strip("?")
            url_query = []
            for key, value in data.items():
                url_query.append(f"{key}={value}")
            url_query = "&".join(url_query)
            if url.find("?") == -1:
                url_query = "?" + url_query
            url = url + url_query
        try:
            response = session.get(url, verify=False, proxies=proxy, headers=headers)
        except Exception as e:
            # self.com_util.print_warn(e)
            return ''
        content = ''
        if response.status_code == 200:
            content = response.content
        else:
            self.com_util.print_warn(f"url {url}, status_code={response.status_code}")
        if to_string:
            content = self.com_string.byte_to_str(content)
        return content

    def post(self, url, data={}, json=False, headers=None):
        proxy = {"http": None, "https": None}
        session = requests.Session()
        # session.keep_alive = False
        session.trust_env = False
        headers = self.set_header(headers)
        information = session.post(url, data, verify=False, proxies=proxy, headers=headers)
        content = None
        if information.status_code == 200:
            if json:
                content = information.json()
            else:
                content = information.content
        if isinstance(content, bytes):
            # 字符串是字节串，进行转换
            content = content.decode("utf-8")

        content = self.com_string.to_json(content)
        return content

    def set_header(self, headers):
        if type(headers) == dict:
            for key, value in headers.items():
                self.__header[key] = value
        return self.__header

    def post_as_json(self, url, data={}):
        return self.post(url, data, json=True)

    def down_web(self, url):
        # 创建主线程，专用于打开页面，以及分析页面并调用多线程下载
        th_main = self.com_thread.create_thread(
            thread_type="down_web",
            args=url
        )
        th_main.start()

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

    def down_file(self, args, overwrite=False, callback=None, extract=False, info=True):
        param = """
            多线程版
            :param tupes_or_list:
            @ 参数为 tuple 类型，则格式为 [
                ( url, file_name , override , callback,extract),
                ( url, file_name , override , callback,extract)
                                        ]
            @ 参数 extract 自动解压下载的zip文件
            @ 参数 url 下载url
            @ 参数 file_name 保存的文件
            @ 参数 override 自动覆盖
            @ 参数 callback 回调
            :return:
            """
        if type(args) == tuple:
            urlistuple = args
            url = urlistuple[0]
            try:
                save_filename = urlistuple[1]
            except:
                save_filename = os.path.basename(url)

            try:
                overwrite = urlistuple[2]
            except:
                pass

            try:
                extract = urlistuple[3]
            except:
                pass

            try:
                callback = urlistuple[4]
            except:
                pass
        elif type(args) == str:
            url = args
            save_filename = self.url_to_savename(url)
            if info: print(f"save_filename {save_filename} ")
        elif type(args) == dict:
            url = args["url"]
            try:
                save_filename = args["save_filename"]
            except:
                save_filename = self.url_to_savename(url)
            try:
                overwrite = args["overwrite"]
            except:
                overwrite = False

            try:
                extract = args["extract"]
            except:
                extract = False

            try:
                callback = args["callback"]
            except:
                callback = None
        else:
            self.com_util.print_warn(param)
            self.com_util.print_warn(f"file download error, parameter {args}.")
            return None

        if overwrite == False and self.com_file.isfile(save_filename):
            if info: print(f"down filename exists of {save_filename}")
            result = save_filename
            if extract:
                result = self.com_file.file_extract(save_filename)
            result = self.down_result_wrap(url, result, save_filename)
            if callback != None:
                return callback(result)
            return result
        if info: self.com_util.print_info(f"wget start url:{url} to save_filename:{save_filename}")
        connection = False
        connection_max = 10
        connection_count = 0
        re_try = False
        content = None
        while connection == False and connection_count < connection_max:
            try:
                if re_try:
                    self.com_util.print_warn(f"retrying, {url}.")
                content = self.get(url, to_string=False)
                if content != None:
                    connection = True
            except Exception as e:
                re_try = True
                self.com_util.print_warn(f"retrying, Error downloading {url}.")
                self.com_util.print_warn(e)
                connection = False
                connection_count += 1
                time.sleep(3)
        if content == None:
            self.com_util.print_warn(f"The file content was not downloaded.")
            result = self.down_result_wrap(url, save_filename, content)
            if callback != None:
                return callback(result)
            return result
        basename = os.path.dirname(save_filename)
        if os.path.exists(basename) is not True and os.path.isdir(basename) is not True:
            self.com_file.mkdir(basename)
        if os.path.exists(save_filename) is not True or os.path.isfile(save_filename) is not True or overwrite == True:
            m = "w"
        else:
            m = "r"
        openmode = f"{m}b+"
        f = open(save_filename, openmode)
        try:
            f.write(content)
            f.close()
        except Exception as e:
            self.com_util.print_warn(f"download error")
            self.com_util.print_warn(e)
            os.remove(save_filename)
        result = save_filename
        if extract:
            result = self.com_file.file_extract(save_filename)
        if callback != None:
            result = self.down_result_wrap(url, save_filename, content)
            return callback(result)
        return self.down_result_wrap(url, result, content)

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
        downfile = self.com_config.get_public("downfile")
        return downfile

    def url_to_savename(self, url):
        base_save_dir = self.get_base_down_dir()
        filename = self.url_to_filename(url)
        save_filename = os.path.join(base_save_dir, filename)
        save_filename = self.com_string.dir_normal(save_filename)
        return save_filename

    def urlparse(self, url):
        return urlparse(url)

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
        filename = self.com_string.dir_normal(filename)
        return filename

    def mkdir(self, dir):
        if os.path.exists(dir) and os.path.isdir(dir):
            return False
        else:
            os.makedirs(dir, exist_ok=True)
            return True

    def is_url(self, url):
        url_parse = urlsplit(url)
        if url_parse.scheme == '':
            return False
        return True

    def extract_url(self, url):
        url_parse = urlsplit(url)
        return url_parse

    def plain_url(self, url):
        url = re.sub(re.compile(r'^.+?\/\/'), '', re.sub(re.compile(r'\s+'), '', url))
        return url

    def get_remote_ip(self, wait_element=None, text_not=None, info=False, city=None):
        if self.__remote_ipurlscircle >= len(self.__remote_ipurls):
            self.__remote_ipurlscircle = 0
        if len(self.__remote_ipurls) == 0:
            return None
        url = self.__remote_ipurls[self.__remote_ipurlscircle]
        self.__remote_ipurlscircle += 1
        try:
            html = self.get(url)
        except:
            html = None
        if html == None:
            self.com_util.print_warn(f"get remote ip fail and remove the url of {url}")
            self.__remote_ipurls.remove(url)
            return self.get_remote_ip(wait_element, text_not, info)
        ips = self.com_selenium.get_html_ips(wait_element=wait_element, text_not=text_not, info=info, html=html)
        if len(ips) == 0:
            # self.com_util.print_warn(f"get remote ip fail by {url}")
            return self.get_remote_ip(wait_element, text_not, info)
        adapter_ip = None
        for ip in ips:
            if self.is_publicip(ip) == True:
                adapter_ip = ip
                break
        if info:
            self.com_util.print_info(f"get remote ip successfully:{adapter_ip} by {url}")
        return adapter_ip

    def is_localip(self, ip):
        pattern = r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'
        if bool(re.match(pattern, ip)) == True:
            try:
                ip_address = ipaddress.ip_address(ip)
                if ip_address.is_private:
                    return True
            except:
                pass
            parts = ip.split('.')
            if len(parts) == 4 and all(len(part) > 1 for part in parts):
                if ip.startswith("8.") \
                        or ip.startswith('19') \
                        or ip.startswith('10.0') \
                        or ip.startswith('192.') \
                        or ip.startswith('172.') \
                        :
                    return True
        return False

    def is_publicip(self, ip):
        pattern = r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'
        if bool(re.match(pattern, ip)) == True:
            parts = ip.split('.')
            if len(parts) == 4 and all(len(part) > 1 for part in parts):
                if ip.startswith("8.") \
                        or ip.startswith('192.') \
                        or ip.startswith('10.0') \
                        or ip.startswith('192.') \
                        or ip.startswith('172.') \
                        or ip.startswith('1.') \
                        :
                    return False
                try:
                    ip_address = ipaddress.ip_address(ip)
                    if ip_address.is_private:
                        return False
                except Exception as e:
                    print("e", e)
                    return False
                if not self.is_localip(ip):
                    return True
            return False
        return False

        # 过滤 8.开头及19开始的局域网IP
        # if ip.startswith('8.') == True or ip.startswith('19') == True:
        #     return True
        # return False

    def website_speedcheck(self, flask=None, url=None, headless=True):
        check_speedurl = "https://ping.chinaz.com/"
        if type(url) == str:
            domain = url
            self.com_http.plain_url(domain)
            domains = [domain]
        else:
            file_dir = self.load_module.get_control_dir('urls.txt')
            file = self.com_file.read(file_dir)
            urls = re.split(re.compile(r'[\n\r]+'), file)
            domains = [self.plain_url(url) for url in urls if url != '']
        while len(domains) > 0:
            domain = domains.pop()
            url = f"{check_speedurl}{domain}"
            wait_element = "#speedlist > div:last-child [name='ipaddress']"
            text_not = "-"
            ips = self.get_remote_ip(wait_element, text_not, info=True, headless=headless)
            self.com_util.pprint(ips)
            if len(ips) == 0:
                self.com_util.print_warn(f"{domain} check speed failed.")
                continue
            ipsresult = self.com_util.ping_ips(ips)
            if ipsresult != None:
                optimization = ipsresult[0]
                optimal_ip = optimization['ip']
                self.com_util.set_hosts_file(domain, optimal_ip)

    def get_ip(self, flask):
        remote_addr = flask.flask_request.remote_addr
        return remote_addr

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

    def get_remote_url(self, method, module="com_translate"):
        key = self.com_config.get_global('execute_function_key')
        local_url = self.com_config.get_global('local_url')
        url = f"{local_url}/api?method={method}&module={module}&key={key}"
        return url

    def get_url_protocol(self, url):
        # 如果URL中包含协议部分，则提取出协议部分
        if '://' in url:
            protocol = url.split('://')[0] + '://'
        else:
            protocol = 'http://'

        return protocol

    def get_url_body(self, url):
        # 如果URL中包含协议部分，则去除协议部分
        if '://' in url:
            domain = url.split('://')[1]
        else:
            domain = url

        return domain

    def simple_url(self, url):
        # 如果输入的是完整的URL，则从中提取出主机名部分
        if '://' in url:
            hostname = url.split('://')[1].split('/')[0]
        else:
            hostname = url

        # 如果主机名中包含'www.'前缀，则将其去除
        if hostname.startswith('www.'):
            hostname = hostname[4:]

        # 按照点号分隔主机名，取最后两部分作为主域名
        tld_parts = hostname.split('.')[-2:]
        tld = '.'.join(tld_parts)

        return tld

    def get_ip_city_by_cz88(self, ip):
        if self.query_ip_data == None:
            from kernel.db.sqliteNative import sqliteNative
            ipdata = self.com_config.get_control_core_file('libs/ipdata/ipdata.db')
            self.query_ip_data = sqliteNative(ipdata)
        ip_split = ip.split(".")[:3]
        ip_start = ".".join(ip_split)
        ip_start = ip_start
        print("ip_start", ip_start)
        select = f"select * from iprange_info where `ip_start` like '{ip_start}.%'"
        iprange_info = self.query_ip_data.query(select)
        province = None
        if len(iprange_info) > 0:
            ipinfo = iprange_info[0]
            province = ipinfo.get('province')
            if province != None:
                try:
                    province = self.com_string.to_pinyin(province)
                except:
                    province = None
        return province

    def get_ip_city_by_baidu(self, ip):
        self.com_selenium.open(
            "https://qifu.baidu.com/?activeKey=SEARCH_IP&trace=apistore_ip_aladdin&activeId=SEARCH_IP_ADDRESS&ip=")

    def get_GeoLite2(self):
        GeoLite2_City_mmd = self.com_config.get_control_core_file('libs/GeoLite2-Country/GeoLite2-City.mmdb')
        reader = geoip2.database.Reader(GeoLite2_City_mmd)
        return reader

    def get_ip_country(self, ip):
        reader = self.get_GeoLite2()
        try:
            response = reader.city(ip)
            return response.country.iso_code
        except:
            return None

    def get_ip_city(self, ip):
        reader = self.get_GeoLite2()
        try:
            response = reader.city(ip)
            print(response.city)
            return response.city.names["en"]
        except:
            return None

    def down_file_from_request(self, flask):
        """Download curses.pyc file from the request."""
        file = flask.request.files['file']
        url = self.com_flask.get_request(flask, "url")
        save_name = self.com_flask.get_request(flask, "save_name")
        if not save_name:
            save_name = self.com_file.url_tofile(url)

        if file.content_type != 'application/octet-stream':
            self.com_util.print_warn(f'com_http down_file_from_request File is application/octet-stream. \n url: {url} \n save_name: {save_name}')
            save_object = {
                "save_dir": None
            }
        else:
            down_dir = self.com_config.get_public(f"downfile")
            down_file = os.path.join(down_dir, save_name)
            with open(down_file, 'wb') as f:
                for chunk in file.stream:
                    f.write(chunk)
            save_object = {
                "save_dir": down_file
            }
        result = self.com_util.print_result(data=save_object)
        return result
