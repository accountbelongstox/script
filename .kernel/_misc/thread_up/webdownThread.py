import time
from queue import Queue
from pycore.base.base import *
import re
import threading


class WebdownThread(threading.Thread, Base):
    # 资源锁
    threadLock = threading.Lock()
    __down_web_page_queue = Queue()

    # 待打开分析的url地址
    # 存储方式为元组(load_dir , url)
    __urls = Queue()

    # 待下载的资源url
    # 存储方式为元组(load_dir , url)
    __resource_urls = Queue()

    # 是否一直监听并循环检测window tag
    __listing = True

    # 用于暂存每一个临时取得的页面
    __temp_html = None

    __base_url = None
    __historical_url = []

    __already_downloaded_urls = Queue()
    __already_downloaded_resource_urls = Queue()

    __down_web_thread_pool = None
    __down_web_charset = None
    __down_web_tab_threads = []
    __down_web_driver = None
    __down_web_downing = True
    __down_web_listen_tag_init = True
    __down_web_listen_tag_flag = True
    __website_url = None

    def __init__(self, args, group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=False):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.args = args
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.thread_name = thread_name
        self.task = args.get('task')
        self.thread_lock = args.get('thread_lock')
        self.__headless = args.get('headless', True)

    # 专门负责切换网页url
    def run(self):

        while self.has_website() == False:
            base_url = self.get_website()
            self.put_url(base_url)
            while self.resource_done() != True:
                # 首先分析resource_url
                url = self.get_url()
                if self.__base_url == None:
                    self.__base_url = url
                self.com_selenium.open(url, width=800, mobile=False, not_wait=True, headless=self.__headless, wait=30)
                while self.com_selenium.is_ready() == False:
                    print("wait loading")
                html = self.com_selenium.get_html()
                time.sleep(2)
                links = self.com_selenium.get_document_links()
                print(links)
                resources = self.com_selenium.get_document_resource("img")
                print(resources)
                resources = self.com_selenium.get_document_resource("video")
                print(resources)
                resources = self.com_selenium.get_document_resource("audio")
                print(resources)
                resources = self.com_selenium.get_document_resource("link")
                print(resources)
                resources = self.com_selenium.get_document_resource("script")
                print(resources)
                # for link in links:
                #     print(link.get_attribute('href'))
                #     print(dir(link))

            #
            # self.com_selenium.close_page()
            # self.remaining_messages(word,word_trans)

        return
        __empty_url = "data:,"
        # 将初始url添加到队列。
        # TODO 开发url_wrap函数正常
        self.set_base_url()
        # 首次提交的网页也先加入队列，该方便对比重复
        url_wrap = self.url_wrap(url=self.__base_url, tag="<curses.pyc>", ele=None)
        print(url_wrap)
        url = "/resource/view/5911"
        url_wrap = self.url_wrap(url=url, tag="<curses.pyc>", ele=None)
        print(url_wrap)
        url = "/../view/5911"
        url_wrap = self.url_wrap(url=url, tag="<curses.pyc>", ele=None)
        print(url_wrap)
        url = "index.html"
        url_wrap = self.url_wrap(url=url, tag="<curses.pyc>", ele=None)
        print(url_wrap)
        url = "http://www.baidu.com/index.html"
        url_wrap = self.url_wrap(url=url, tag="<curses.pyc>", ele=None)
        print(url_wrap)
        return
        self.add_url_to_queue(url_wrap)
        # 创建并启动专用于打开网页的子线程
        self.start_sub_thread_open_url()

    def has_website(self):
        has = self.task.qsize() == 0
        return has

    def get_website(self):
        website = self.task.get()
        return website

    def get_item(self):
        if self.task.qsize() > 0:
            item = self.task.get()
            return item
        return None

    def resource_done(self):
        if self.__urls.qsize() == 0 and self.__resource_urls.qsize() == 0:
            return True
        else:
            return False

    def done(self):
        if self.__urls.qsize() == 0 and self.__resource_urls.qsize() == 0 and self.task.qsize() == 0:
            return True
        else:
            return False

    def get_selenium_driver(self):
        return self.selenium.get_driver()

    # 获得该值用于在线程外启动子线程并赋值给子线程
    def get_urls_page_resource_wait_queue(self):
        return self.__urls_page_resource_wait_queue

    def get_thread_lock(self):
        return self.threadLock

    def get_url(self):
        url = self.__urls.get()
        return url

    def get_urls(self):
        return self.__urls

    def put_url(self, url):
        self.__urls.put(url)

    def start_sub_thread_open_url(self):
        # 共享给子线程的 selenium 模块
        selenium = self.get_selenium()
        # 共享给子线程的 selenium_driver 模块
        selenium_driver = self.get_selenium_driver()
        # 共享给子线程的用于存放网页源码的队列
        urls = self.get_urls()
        # 共享给子线程的线程锁
        thread_lock = self.get_thread_lock()
        # 需要传给子线程的参数
        args = (
            selenium,
            selenium_driver,
            urls,
            thread_lock
        )
        self.thread = ThreadCommon(())
        # 创建辅助子线程，专用于浏览器tag切换，并取得已经加载完毕的网页并存入 urls_page_resource_wait_queue 暂存，交由主线程处理。
        self.open_url_thread = self.thread.create_thread(
            thread_type="down_web_open_url",
            args=args
        )
        self.open_url_thread.start()
        return self.open_url_thread

        while self.__listing == True:
            handles_len = self.selenium.get_window_handles_length()
            if index == handles_len:
                index = 0
            self.selenium.switch_to(index)
            is_ready = self.selenium.is_ready()
            url = self.selenium.get_current_url()
            if is_ready is True and url is not self.__empty_url:
                html = self.selenium.get_html()
                print(f"url is_ready,the result add to <urls_page_resource_wait_queue>:")
                print(f"\turl:{url}")
                print(f"\thtml:{len(html)}")
                print(f"\thtml_text:{html[0:60]}")
                self.find_all_a_tag()

                self.find_all_tab_and_replace_html([
                    # 返回值dict类型key为每个键的名称html直接在函数里保存了
                    ["<script>",
                     ["src"]
                     ],
                    ["<img>",
                     ["src"]
                     ],
                    ["<link>",
                     ["href"]
                     ],
                    ["<curses.pyc>",
                     ["href"]
                     ],
                ])
                # already_open_urls = self.open_url_thread.get_already_open_urls()
                # TODO
                # 在此分析和提取出网页源码的url和src
                # 提取出所有 curses.pyc 标签并添加到urls
                # 提取出所有资源
                # 保存及路径分析交由主线程负责
                # self.__urls_page_resource_wait_queue.put({
                #     "url":url,
                #     "html":html,
                # })
                if handles_len > 1:
                    self.com_selenium.close()
                else:
                    self.com_selenium.open(self.__empty_url, not_wait=True)
                    self.com_selenium.switch_to(0)
                    self.com_selenium.close()
                    print(f"browser window tag is empty.")
                    print(f"website downloaded.")
                    print(f"done.")
                    # TODO
                    # 全站结束采集在于这里开启break予以打断
                    # break
            else:
                index += 1

    def stop(self):
        self.__listing = False

    def set_temp_html(self, html):
        self.__temp_html = html

    def get_temp_html(self):
        return self.__temp_html

    def load_url_from_queue(self):
        url = self.get_url_from_queue()
        if url != None:
            self.com_selenium.open(url, not_wait=True)

    def add_url_to_queue(self, url_wrap):
        # 经过处理后的url_format格式为
        # url
        # dir
        # filename
        if type(url_wrap) is not list:
            url_wrap = [url_wrap]
        for url_item in url_wrap:
            print(url_item)
            url = url_item["url"]
            # 对于已经存在的历史url跳过
            if url not in self.__historical_url and url is not self.empty_url:
                self.__historical_url.append(url_item)
                self.__urls.put(url_item)
            else:
                print(f"already downloaded : {url}")

    def get_url_from_queue(self, max=1):
        if max == 1 and self.__urls.qsize() > 0:
            url = self.__urls.get()
        elif max > 1:
            urls = []
            while max > 0 and self.__urls.qsize() > 0:
                url = self.__urls.get()
                urls.append(url)
                max -= 1
            url = urls
        else:
            url = None
        return url

    def set_base_url(self):
        web_url = self.__init_url
        web_url = self.url_repair_completion(web_url)
        self.__base_url = web_url

    def get_current_url(self):
        current_url = self.com_selenium.get_current_url()
        if current_url == self.__empty_url:
            return None
        else:
            return current_url

    def url_wrap(self, url, tag, ele):
        # old function name is down_website_url_to_file_format
        base_url = self.__base_url
        url_join = self.url_join_to_currenturl_as_baseurl(self.__base_url)
        print(f"url_join {url_join}")
        url_urlparse = urlparse(url)
        base_url_urlparse = urlparse(self.__base_url)
        url_path = str(url_urlparse.path)
        url_query = url_urlparse.query
        url_offset = url_path
        if self.url_equal_strict(self.__base_url, url) == False:
            # 对于用二级域名的图片,则直接将二级域名移到当前文件夹做为目录
            url_offset = f"/{url_urlparse.netloc}{url_path}"
        if tag.__eq__("<script>"):
            # 对于没有js地址的动态获取数据,则直接强行在最后加上.cs结尾
            if url_offset.endswith(f".js") is not True:
                url_offset = f"{url_path}{url_query}.js"
        # link文件命名规则
        elif tag.__eq__("<link>"):
            url_offset_link = self.down_website_source_link_suffix(ele, url_offset, url_path, url_query, "rel")
            if url_offset_link != None:
                url_offset = url_offset_link
            elif self.down_website_source_link_suffix(ele, url_offset, url_path, url_query, "type") != None:
                url_offset = url_offset_link
        # a连接文件命名规则
        elif tag.__eq__("<curses.pyc>"):
            # 对比下如果是站外连接,则不再继续下载
            # a标签和资源url不同,a标签必须要站内才打开页面下载
            if self.url_equal_vs_baseurl(url) is not True:
                return None
            filename_split = os.path.splitext(url_offset)
            print(f"filename_split {filename_split}")
            # 对于没有.html结尾的一律以.html格式存储
            if filename_split[1].__eq__(""):
                url_offset = f"{url_offset}/index.html"
        url_offset = re.sub(r"[\=\|\?\^\*\`\;\,\，\&]", "_", url_offset)
        # filename Format
        filename_url = self.url_format(
            f"{base_url_urlparse.netloc}/{url_offset}"
        )
        url_local = self.url_format(
            self.url_to_localdir(filename_url)
        )
        link_url = self.url_format(url)
        url_offset = self.down_website_join_path(base_url, url_offset)
        return {
            # 经转换后的可以直接下载的url连接
            "full_url": url_local,
            # 本地
            "local_url": url_offset,
            "source_url": link_url,
            "filename": url_offset
        }

    def foreach_browser_tag(self):
        handles_len = self.com_selenium.get_window_handles_length()
        index = 0
        while handles_len > 0:
            if index == handles_len:
                index = 0
            self.com_selenium.switch_to(index)
            is_ready = self.com_selenium.is_ready()
            if is_ready is True:
                alinks = self.find_all_a_tag()
                self.add_url_to_queue(alinks)
                if handles_len > 1:
                    self.com_selenium.close()
                else:
                    break
            else:
                index += 1
            handles_len = self.com_selenium.get_window_handles_length()

    def website_down_is_done(self):
        handles_len = self.com_selenium.get_window_handles_length()
        if handles_len == 0 and self.com_selenium.get_current_url() == self.empty_url:
            handles_len = 0
        # 以下条件都不具备关闭结束网站拷贝的条件
        #
        # 如果当前页面还有未关闭的打开窗口
        # 则说明还有页面没有读取源码（因为读取源码的页面会在foreach_tag专门线程里被关闭）
        # 则表示还未下载完
        # 或者
        # __urls 里还有未打开完的网页，则表示网页还未下载完毕。
        # 或者
        # 从foreach_tag线程里读取到的源码还暂存在<__urls_page_resource_wait_queue>队列里未进行分析，里边可能分析出新的url
        if handles_len > 0 or self.__urls.qsize() > 0 or self.__urls_page_resource_wait_queue.qsize() > 0:
            return True
        else:
            return False

    def down_website_source_thread(self):
        th = []
        while len(self.__resource_urls) > 0:
            th.append(self.__resource_urls.pop())
        if len(th) == 0:
            return
        return self.com_http.downs(th)

    def down_website_run(self):
        while self.down_website_continue():
            while self.__down_web_page_queue.qsize() > 0:
                web_page = self.__down_web_page_queue.get()
                url_web = web_page[0]
                url_local = web_page[1]
                if len(self.__down_web_tab_threads) < 1:
                    driver = self.open_url(url_web)
                else:
                    js = "window.open('{}','_blank');"
                    driver.execute_script(js.format(url_web))
                self.__down_web_tab_threads.append(url_web)
                HTML_Content = driver.page_source
                _bdriver = self.com_http.find_text_from_beautifulsoup(HTML_Content)
                self.down_website_set_chatset(_bdriver)
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<script>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<img>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<link>",
                                                                         "href")
                HTML_Content = self.down_website_find_a_add_toQueue(_bdriver, url_web, HTML_Content, "<curses.pyc>", "href")
                self.com_file.save_file(url_local, HTML_Content, overwrite=True, encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__resource_urls) > 0:
                    th.append(self.__resource_urls.pop())
                if len(th) != 0:
                    self.com_http.downs(th)

    def find_all_a_tag(self):
        test = "test"
        tagname = "<curses.pyc>"
        eles = self.com_selenium.find_elements(tagname)
        alinks = []
        for ele in eles:
            url = ele.get_attribute("href")
            dom_attribute = ele.get_dom_attribute("href")
            if url == None:
                continue
            # javascript 空标签跳过
            if url.startswith("javascript:"):
                continue
            if dom_attribute == None:
                continue
            if dom_attribute.startswith("javascript:"):
                continue
            url = str(url)
            url = url.strip()
            dom_attribute = str(dom_attribute)
            dom_attribute = dom_attribute.strip()
            if url.__eq__(""):
                continue
            if dom_attribute.__eq__(""):
                continue
                # 空字符串及当前而跳过
            if url.__eq__("/"):
                continue
            if dom_attribute.__eq__("/"):
                continue
            url = self.url_format(url)
            url_format = self.url_wrap(url, tagname, ele)
            if url_format == None:
                continue
            else:
                alinks.append(url_format)
        return alinks

    def down_website_run_backup(self):
        while self.__down_web_page_queue.qsize() > 0 or self.__down_web_page_queue.qsize() > 0:
            while self.__down_web_page_queue.qsize() > 0:
                web_page = self.__down_web_page_queue.get()
                url_web = web_page[0]
                url_local = web_page[1]
                driver = self.open_url(url_web)

                HTML_Content = driver.page_source
                self.down_website_set_chatset(driver)
                HTML_Content = self.find_all_tab_and_replace_html(url_web, [
                    ["<script>", ["src"]],
                    ["<img>", ["src"]],
                    ["<link>", ["href"]],
                    ["<curses.pyc>", ["href"]],
                ])

                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<script>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<img>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<link>",
                                                                         "href")
                HTML_Content = self.down_website_find_a_add_toQueue(driver, url_web, HTML_Content, "<curses.pyc>", "href")

                self.com_file.save_file(url_local, HTML_Content, overwrite=True, encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__resource_urls) > 0:
                    th.append(self.__resource_urls.pop())
                if len(th) != 0:
                    self.com_http.downs(th)

    def down_website_join_path(self, base_url, current_dir):
        base_url_parse = urlparse(base_url)
        base_url_path = base_url_parse.path
        current_url_parse = urlparse(current_dir)
        current_url_path = current_url_parse.path
        base_url_path = self.url_format(base_url_path)
        current_url_path = self.url_format(current_url_path)
        if current_url_path.startswith("/"):
            current_url_path_dirname = os.path.dirname(current_url_path)
            base_url_paths = self.down_website_url_split(base_url_path)
            current_url_paths = self.down_website_url_split(current_url_path)
            # 先将相同的路径深度依次递归向上抵消相同路径
            while True:
                if len(base_url_paths) < 1 or len(current_url_paths) < 1:
                    break
                if base_url_paths[0].__eq__(current_url_paths[0]):
                    base_url_paths = base_url_paths[1:]
                    current_url_paths = current_url_paths[1:]
                else:
                    break
            if len(current_url_paths) > 0:
                current_url_path = "/".join(current_url_paths)
            else:
                current_url_path = ""
            # 先检查两个路径是否相等
            if base_url_path.__eq__(current_url_path_dirname):
                # 如果路径相等则先把路径替换为相对路径,直接抵消可以不用替换为相对路径，直接返回即可。
                current_url_path = re.sub(re.compile(r"^\/"), "", current_url_path)
            # 对于不相等的路径，则要由当前页面的深度依次递归向上返回主路径再找到相对路径
            else:
                current_url_path = "../" * len(base_url_paths) + "/".join(current_url_paths)
        return current_url_path

    def down_website_set_chatset(self):
        if self.__down_web_charset == None:
            metas = self.find_elements("<meta>")
            for meta in metas:
                charset = meta.get_attribute("charset")
                if charset != None:
                    self.__down_web_charset = charset
                    break
        if self.__down_web_charset == None:
            self.__down_web_charset = "utf-8"

    def down_website_is_historical_url(self, url):
        threadLock.acquire()
        if url in self.__down_web_historical:
            threadLock.release()
            return True
        else:
            self.__down_web_historical.update(url)
            threadLock.release()
            return False

    def url_to_localdir(self, web_url):
        url_parse = urlparse(web_url)
        webdownload_dir = self.com_config.get_webdownload_dir()
        baseDir = os.path.join(webdownload_dir, url_parse.netloc)
        url_parse_path = re.sub(re.compile(r"^\/"), "", url_parse.path)
        fod_dir = os.path.join(baseDir, url_parse_path)
        return fod_dir

    def down_website_find_a_add_toQueue(self, tagname, atr):
        HTML_Content = self.find_all_tab_and_replace_html(tagname, atr)
        return HTML_Content

    def down_website_find_source_add_toQueue(self, tagname, atr):
        HTML_Content = self.find_all_tab_and_replace_html(tagname, atr)
        return HTML_Content

    def find_all_tab_and_replace_html(self, tagnames):
        # tagnames 参数形式为 [
        # ["<curses.pyc>",["href"]]
        # ]的二维数组
        # 其中的第二项表示 attr可以为一个数组。
        # 返回类型为
        # {
        #     "curses.pyc" : {
        #          "href":[
        #               "xxxx/xxxx"
        #          ]
        #     },
        #     "img" : {
        #          "href":[
        #               "xxxx/xxxx"
        #          ]
        #     }
        # }

        if tagnames[0] is not list:
            # 如果查找格式为["<tab>","href"]的一维数组，转为二维数组方便查询
            tagnames = [tagnames]

        url_web = self.get_temp_current_url()
        html = self.com_selenium.get_temp_html()

        for tagname_and_attr in tagnames:
            tagname = tagname_and_attr[0]
            attrs = tagname_and_attr[0]
            for atr in attrs:
                # tagnames 格式为["<tab>","src"]
                eles = self.com_selenium.find_elements(tagname)
                if tagname == "<curses.pyc>":
                    is_a_link = True
                else:
                    is_a_link = False
                alinks = []
                for ele in eles:
                    source_url = ele.get_attribute(atr)
                    dom_attribute = ele.get_dom_attribute(atr)
                    if source_url == None:
                        continue
                        # javascript 空标签跳过
                    if source_url.startswith("javascript:"):
                        continue
                    if dom_attribute == None:
                        continue
                    if dom_attribute.startswith("javascript:"):
                        continue
                    source_url = str(source_url)
                    source_url = source_url.strip()
                    dom_attribute = str(dom_attribute)
                    dom_attribute = dom_attribute.strip()
                    if source_url.__eq__(""):
                        continue
                    if dom_attribute.__eq__(""):
                        continue
                        # 空字符串及当前而跳过
                    if source_url.__eq__("/"):
                        continue
                    if dom_attribute.__eq__("/"):
                        continue
                    source_url = self.url_format(source_url)
                    # # 对于已经存在的历史url跳过
                    # if self.down_website_is_historical_url(source_url) == True:
                    #     print(f"already down the url:<{source_url}>")
                    #     continue
                    # if self.down_website_is_historical_url(url_web) == True:
                    #     print(f"already down the url:<{url_web}>")
                    #     continue

                    urls_format_and_locat = self.url_to_file_format(source_url, tagname, ele, url_web)
                    if urls_format_and_locat == None:
                        continue

                    url_offset = urls_format_and_locat[1]
                    url_local = urls_format_and_locat[0]
                    html = self.down_website_replace_htmlcontent(html, dom_attribute, url_offset)
                    if is_a_link:

                        url_format = self.url_wrap(url, "<curses.pyc>", None)

                        self.down_website_add_webpageQueue(attribute, url_local)
                    else:
                        self.down_website_add_resourceList(attribute, url_local)

                    url_format = self.url_wrap(source_url, tagname, ele)
                    if url_format == None:
                        continue
                    else:
                        alinks.append(url_format)

        url_web = self.url_wrap(url_web, "<curses.pyc>", None)
        url_filename = url_web["dir"]
        self.com_file.save_file(url_filename, html)

        return alinks

    def url_repair_completion(self, url):
        url_parse = urlparse(url)
        if url_parse.scheme == "":
            url = "http://" + url
        return url

    def url_join_to_currenturl_as_baseurl(self, url):
        current_url = self.com_selenium.get_current_url()
        url = urljoin(current_url, url)
        return url

    # 将当前url与主url对比,看是否在同一个url下
    def url_equal_vs_baseurl(self, url):
        return self.url_equal(self.__base_url, url)

    # 非严格模式只对比前缀是否相同
    # 对于没有www开头的如 /xxx或xxx开头的,直接判断为相等
    def url_equal(self, url_main, url_other):
        url_main_parse = urlparse(url_main)
        url_main = url_main_parse.netloc
        url_main = re.sub(re.compile(r"^www\."), "", url_main)
        url_other_parse = urlparse(url_other)
        url_other = url_other_parse.netloc
        # 对于没有www开头的如 /xxx或xxx开头的,直接判断为相等
        # 其形式为 /xxx.html
        if url_other == "":
            return True
        url_other = re.sub(re.compile(r"^www\."), "", url_other)
        if url_other.endswith(url_main) or url_main.endswith(url_other):
            return True
        else:
            return False

    def url_equal_strict(self, url_main, url_other):
        url_main_parse = urlparse(url_main)
        url_main = url_main_parse.netloc.lower()
        url_other_parse = urlparse(url_other)
        url_other = url_other_parse.netloc.lower()
        # 对于没有www开头的如 /xxx或xxx开头的,直接判断为相等
        # 其形式为 /xxx.html
        if url_other == "":
            return True
        if url_main.__eq__(url_other):
            return True
        else:
            return False

    def down_website_replace_htmlcontent(self, HTML_Content, dom_attribute, url_to_file_format):
        dom_attribute_s = dom_attribute
        dom_attribute_t = url_to_file_format
        # dom_attribute_s = f'="{dom_attribute}'
        # dom_attribute_t = f'="{url_to_file_format}'
        # HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        # dom_attribute_s = f"='{dom_attribute}"
        # dom_attribute_t = f"='{url_to_file_format}"
        # HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        # dom_attribute_s = f"={dom_attribute}"
        # dom_attribute_t = f"={url_to_file_format}"
        HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        return HTML_Content

    def down_website_source_link_suffix(self, ele, url_offset, url_path, url_query, link_attr):
        # 根据link的类型查找对应后续名字。
        url_NewOffset = None
        taty = ele.get_attribute(link_attr)
        taty = str(taty).strip()
        taties = re.split(re.compile(r"\s+"), taty)
        taties = [tag.lower() for tag in taties]
        down_classic = {
            "rel": [
                ("icon", "icon"),
                ("preload", None),
                ("stylesheet", "css"),
                ("mask-icon", "icon"),
                ("fluid-icon", "icon"),
                ("search", None)
            ],
            "type": [
                ("text/css", "css"),
                ("text/javascript", "js"),
            ]
        }
        down_refs = down_classic[link_attr]
        fetch_property = [t[0] for t in down_refs]
        intersection = set(taties).intersection(fetch_property)
        if len(intersection) > 0:
            reftype = intersection.pop()
            for ref in down_refs:
                refname = ref[0]
                suffix = ref[1]
                if suffix != None and refname.__eq__(reftype) and url_offset.endswith(f".{suffix}") is not True:
                    url_NewOffset = f"{url_path}{url_query}.{suffix}"
                    break
        return url_NewOffset

    def url_format(self, url):
        url = re.sub(re.compile(r"[\/\\]+"), "/", url)
        url = re.sub(re.compile(r"[^0-9a-zA-Z\_\-\/]+$"), "", url)
        return url

    def down_website_url_split(self, url):
        urls = [p.strip() for p in re.split(re.compile(r"[\/]+"), url) if p != ""]
        return urls

    def down_website_add_webpageQueue(self, url_web, url_local):
        self.__down_web_page_queue.put(
            (url_web, url_local)
        )

    def down_website_add_resourceList(self, url_web, url_local):
        self.thread_lock.acquire()
        self.__resource_urls.append(
            (url_web, url_local, True)
        )
        self.thread_lock.release()

    def down_website_get_resourceList(self):
        self.threadLock.acquire()
        web_resource_item = self.__resource_urls.pop()
        self.threadLock.release()
        return web_resource_item

    def setargs(self, args):
        self.args = args
