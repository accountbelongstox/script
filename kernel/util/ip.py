import re
import ipaddress
import socket
from kernel.base.base import Base
import requests

threadQueue = None
webdownQueue = None

class Ip(Base):
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

    def __init__(self):
        pass
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

    def __init__(self):
        requests.adapters.DEFAULT_RETRIES = 5
        pass

    def set_header(self, headers):
        if type(headers) == dict:
            for key, value in headers.items():
                self.__header[key] = value
        return self.__header

    def request_url(self, url, data=None, headers=None, text='text'):
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
            return ''
        content = ''
        if response.status_code == 200:
            if text == 'text':
                content = response.text
            else:
                content = response.content
        return content

    def get_local_ip(self):
        try:
            host_name = socket.gethostname()
            local_ip = socket.gethostbyname(host_name)
            return local_ip
        except Exception as e:
            print(e)
            return None

    def get_ips_by_html(self, html):
        if html.find("page can’t be found") != -1 and html.find('No webpage was found for the web address') != -1:
            return []
        ip_pattern = re.compile(r'[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}')
        ips = re.findall(ip_pattern, html)
        filtered_ips = []
        exclude_ips = [
            "223.104.112.241",
            "183.232.231.172",
        ]
        for ip in ips:
            if self.is_publicip(ip) == True and ip not in exclude_ips:
                filtered_ips.append(ip)
        return filtered_ips

    def get_remote_ip(self):
        if self.__remote_ipurlscircle >= len(self.__remote_ipurls):
            self.__remote_ipurlscircle = 0
        if len(self.__remote_ipurls) == 0:
            return None
        url = self.__remote_ipurls[self.__remote_ipurlscircle]
        self.__remote_ipurlscircle += 1

        html = self.request_url(url)

        if html == "":
            self.warn(f"get remote ip fail and remove the url of {url}")
            self.__remote_ipurls.remove(url)
            return self.get_remote_ip()

        ips = self.get_ips_by_html(html)
        if len(ips) == 0:
            return self.get_remote_ip()
        adapter_ip = None
        for ip in ips:
            if self.is_publicip(ip) == True:
                adapter_ip = ip
                break
        self.success(f"get remote ip successfully:{adapter_ip} by {url}")
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

    def get_ip(self, flask):
        remote_addr = flask.flask_request.remote_addr
        return remote_addr


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





