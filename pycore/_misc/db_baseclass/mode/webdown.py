from pycore.base.base import Base
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from queue import Queue
threadLock = threading.Lock()
import re

class Webdown(Base):
    __down_web_resource_list = []
    __down_web_page_queue =Queue()
    __down_web_base_url = None
    __down_web_historical = set()
    __down_web_thread_pool = None
    __down_web_charset = None
    __down_web_tab_threads = []
    __down_web_driver = None
    __down_web_downing = True
    __down_web_listen_tag_init = True
    __down_web_listen_tag_flag = True

    def __init__(self,args):
        pass

    def down_website_openurl_by_thread(self, url):
        PoolExecutor = ThreadPoolExecutor(max_workers=3)
        PoolExecutor.submit(self.down_website_open, (url,))
        PoolExecutor.submit(self.down_website_foreach_tag)

    def down_website_open(self, urls):
        url = urls[0]
        driver = self.open_url(url)

    def down_website(self, web_url):
        # 通过新线程启动一个浏览器
        web_url_parse = urlparse(web_url)
        down_web_base_url = web_url_parse.scheme + "://" + web_url_parse.netloc
        self.__down_web_base_url = down_web_base_url
        # 首次提交的网页也先加入队列，该方便对比重复
        website_url_to_file_format = self.down_website_url_to_file_format(web_url, "<curses.pyc>", None, web_url)
        url_local = website_url_to_file_format[0]
        # t = threading.Thread(target=self.down_website_openurl_by_thread,args=(url_local,),daemon=True)
        # t.run()
        self.down_website_openurl_by_thread(url_local)
        return

        self.down_website_add_webpageQueue(web_url, url_local)
        self.down_website_add_webpageQueue("https://translate.google.cn/?sl=en&tl=zh-CN&op=translate", url_local)
        self.down_website_add_webpageQueue("https://blog.csdn.net/chaodaibing/article/details/115016791", url_local)
        # self.down_website_add_to_thread()
        # max_workers = 1
        # with ThreadPoolExecutor(max_workers=max_workers) as Pool:
        #     trail_page_thread = Pool.submit(self.down_website_run)
        #     trail_page_thread.result()
        #     print("the tick.")
        max_workers = 30
        with ThreadPoolExecutor(max_workers=max_workers) as Pool:
            while self.down_website_queue_not_clear():
                # 初始化执行，先监听所有TAG而，并单独使用一个线程实时切换。
                request_type = None
                if self.__down_web_listen_tag_init == True:
                    request_type = "listen_tag"
                    self.__down_web_listen_tag_init = False
                    run_parame = (request_type, None)
                elif self.__down_web_page_queue.qsize() > 0:
                    request_type = 'page_url'
                    web_page = self.__down_web_page_queue.get()
                    run_parame = (request_type, web_page)
                if request_type == "listen_tag":
                    # th = threading.Thread(target=self.down_website_open_page_on_tag,args=request_type)
                    # th.daemon = True
                    # print(th.daemon)
                    # th.start()
                    th = threading.Thread(target=self.down_website_foreach_tag)
                    th.daemon = True
                    th.start()
                elif request_type == "page_url":
                    trail_page_thread = Pool.submit(self.down_website_open_page_on_tag, run_parame)
                if request_type == 'page_url':
                    try:
                        trail_page_thread.result()
                    except:
                        print("timeout")
                        pass
                    # print("trail_page_threadtick",trail_page_thread.done())
                    pass
                    # trail_page_thread.result()
                    # print("ok!.")
                    # elif len(self.__down_web_resource_list) > 0:
                    #     pass
                    # print('self.__down_web_page_queue.qsize() ', self.__down_web_page_queue.qsize(),web_page )
                    # trail_page_thread = Pool.submit(self.down_website_open_page_on_tag,run_parame)
            # 一旦所有页面都下载完毕。
        self.__down_web_downing = False
        # trail_page_thread.result()
        # self.down_website_run()
        # 所有tab都关闭，代表没有页面了
        # 所有资源表都清空，代表下载完了
        # 所有列表面都清空，代表不开新的TAB标签了。

    def down_website_url_to_file_format(self, current_url, tag_type, ele, base_url):
        url_urlparse = urlparse(current_url)
        base_url_urlparse = urlparse(self.__down_web_base_url)
        url_path = str(url_urlparse.path)
        url_query = url_urlparse.query
        url_offset = url_path
        if self.down_website_equal_url_strict(self.__down_web_base_url, current_url) == False:
            # 对于用二级域名的图片,则直接将二级域名移到当前文件夹做为目录
            url_offset = f"/{url_urlparse.netloc}{url_path}"
        if tag_type.__eq__("<script>"):
            # 对于没有js地址的动态获取数据,则直接强行在最后加上.cs结尾
            if url_offset.endswith(f".js") is not True:
                url_offset = f"{url_path}{url_query}.js"
        # link文件命名规则
        elif tag_type.__eq__("<link>"):
            url_offset_link = self.down_website_source_link_suffix(ele, url_offset, url_path, url_query,"rel")
            if url_offset_link != None:
                url_offset = url_offset_link
            elif self.down_website_source_link_suffix(ele, url_offset, url_path, url_query,"type") != None:
                url_offset = url_offset_link
        # a连接文件命名规则
        elif tag_type.__eq__("<curses.pyc>"):
            if self.down_website_equal_url(self.__down_web_base_url, current_url) is not True:
                return None
            filename_split = os.path.splitext(url_offset)
            if filename_split[1].__eq__(""):
                url_offset = f"{url_offset}/index.html"
        url_offset = re.sub(r"[\=\|\?\^\*\`\;\,\，\&]", "_", url_offset)
        # filename Format
        filename_url = self.down_website_url_format(
            f"{base_url_urlparse.netloc}/{url_offset}"
        )
        url_local = self.down_website_url_format(
            self.down_website_url_to_localdir(filename_url)
        )
        url_offset = self.down_website_join_path(base_url, url_offset)
        return (url_local, url_offset)


    def down_website_foreach_tag_test(self):
        print("listening ：while")
        while True:
            print("self.__down_web_downing", self.__down_web_downing)

    async def down_website_open_page_on_tag_async(self):
        url_web = "http://www.google.com"
        threadLock.acquire()
        web_tab_threads = len(self.__down_web_tab_threads)
        if web_tab_threads < 1 or self.__down_web_driver == None:
            self.__down_web_driver = self.get_empty_driver()
            # self.__down_web_driver.set_script_timeout(1)
            # self.__down_web_driver.set_page_load_timeout(3)
            threadLock.release()
            self.open_url(url_web)
        else:
            js = "window.open('{}','_blank');"
            threadLock.release()
            self.__down_web_driver.execute_script(js.format(url_web))
        # --线程安全==
        index = self.down_website_get_webtab_index(url_web)
        # self.down_website_foreach_tag()
        self.__down_web_tab_threads.append(url_web)
        if self.__down_web_listen_tag_flag:
            self.__down_web_listen_tag_flag = False
        # ===========
        print("exec ok.", index)

        yield 1

    # 两个线程池，一个专用于打开页面，用于等待页面加载完成,
    # 另一个用于专门下载资源，也可两个线程同时调用，其中的资源文件直接下载，html和css则提取其中内容。
    def down_website_open_page_on_tag(self, run_param):
        request_type = run_param[0]
        if request_type == "page_url":
            web_page = run_param[1]
            # print("self.__down_web_page_queue.qsize()",self.__down_web_page_queue.qsize())
            url_web = web_page[0]
            url_local = web_page[1]

            threadLock.acquire()
            web_tab_threads = len(self.__down_web_tab_threads)

            if web_tab_threads < 1 or self.__down_web_driver == None:
                self.__down_web_driver = self.get_empty_driver(headless=False)
                # self.__down_web_driver.set_script_timeout(1)
                # self.__down_web_driver.set_page_load_timeout(3)
                threadLock.release()
                self.open_url(url_web)
            else:
                js = """return window.open('{}','_blank');"""
                threadLock.release()
                self.__down_web_driver.execute_script(js.format(url_web))

            index = self.down_website_get_webtab_index(url_web)
            # self.down_website_foreach_tag()
            self.__down_web_tab_threads.append(url_web)
            if self.__down_web_listen_tag_flag:
                self.__down_web_listen_tag_flag = False
            # ===========
            print("exec ok.", index)

    def down_website_queue_not_clear(self):
        if len(self.__down_web_tab_threads) > 0 \
                or \
                self.__down_web_page_queue.qsize() > 0 \
                or \
                len(self.__down_web_resource_list) > 0:
            return True
        else:
            return False

    def down_website_source_thread(self):
        th = []
        while len(self.__down_web_resource_list) > 0:
            th.append(self.__down_web_resource_list.pop())
        if len(th) == 0:
            return
        return self.http_common.downs(th)

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
                _bdriver = self.http_common.find_text_from_beautifulsoup(HTML_Content)
                self.down_website_set_chatset(_bdriver)
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<script>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<img>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web, HTML_Content, "<link>",
                                                                         "href")
                HTML_Content = self.down_website_find_a_add_toQueue(_bdriver, url_web, HTML_Content, "<curses.pyc>", "href")

                self.file_common.save_file(url_local, HTML_Content, override=True, encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__down_web_resource_list) > 0:
                    th.append(self.__down_web_resource_list.pop())
                if len(th) != 0:
                    self.http_common.downs(th)

    def down_website_get_webtab_index(self, web_url):
        threadLock.acquire()
        for id, url in enumerate(self.__down_web_tab_threads):
            if url.__eq__(web_url):
                threadLock.release()
                return id
        threadLock.release()
        return None

    def down_website_run_backup(self):
        while self.__down_web_page_queue.qsize() > 0 or self.__down_web_page_queue.qsize() > 0:
            while self.__down_web_page_queue.qsize() > 0:
                web_page = self.__down_web_page_queue.get()
                url_web = web_page[0]
                url_local = web_page[1]
                driver = self.open_url(url_web)

                HTML_Content = driver.page_source
                self.down_website_set_chatset(driver)
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<script>",
                                                                         "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<img>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web, HTML_Content, "<link>",
                                                                         "href")
                HTML_Content = self.down_website_find_a_add_toQueue(driver, url_web, HTML_Content, "<curses.pyc>", "href")

                self.file_common.save_file(url_local, HTML_Content, override=True, encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__down_web_resource_list) > 0:
                    th.append(self.__down_web_resource_list.pop())
                if len(th) != 0:
                    self.http_common.downs(th)

    def down_website_join_path(self, base_url, current_dir):
        base_url_parse = urlparse(base_url)
        base_url_path = base_url_parse.path
        current_url_parse = urlparse(current_dir)
        current_url_path = current_url_parse.path
        base_url_path = self.down_website_url_format(base_url_path)
        current_url_path = self.down_website_url_format(current_url_path)
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

    def down_website_url_to_localdir(self, web_url):
        url_parse = urlparse(web_url)
        webdownload_dir = self.config_common.get_webdownload_dir()
        baseDir = os.path.join(webdownload_dir, url_parse.netloc)
        url_parse_path = re.sub(re.compile(r"^\/"), "", url_parse.path)
        fod_dir = os.path.join(baseDir, url_parse_path)
        return fod_dir

    def down_website_find_a_add_toQueue(self, url_web, HTML_Content, tagname, atr):
        HTML_Content = self.down_website_find_add_toQueue(url_web, HTML_Content, tagname, atr, is_alink=True)
        return HTML_Content

    def down_website_find_source_add_toQueue(self, url_web, HTML_Content, tagname, atr):
        HTML_Content = self.down_website_find_add_toQueue(url_web, HTML_Content, tagname, atr, is_alink=False)
        return HTML_Content

    def down_website_find_add_toQueue(self, url_web, HTML_Content, tagname, atr, is_alink=False):
        tags = self.find_elements(tagname)
        for ele in tags:
            attribute = ele.get_attribute(atr)
            dom_attribute = ele.get_dom_attribute(atr)
            if attribute == None:
                continue
                # javascript 空标签跳过
            if attribute.startswith("javascript:"):
                continue
            if dom_attribute == None:
                continue
            if dom_attribute.startswith("javascript:"):
                continue

            attribute = str(attribute)
            attribute = attribute.strip()
            dom_attribute = str(dom_attribute)
            dom_attribute = dom_attribute.strip()
            if attribute.__eq__(""):
                continue
            if dom_attribute.__eq__(""):
                continue
                # 空字符串及当前而跳过
            if attribute.__eq__("/"):
                continue
            if dom_attribute.__eq__("/"):
                continue
            # 对于已经存在的历史url跳过
            if self.down_website_is_historical_url(attribute) == True:
                print(f"already down the url:<{attribute}>")
                continue
            if self.down_website_is_historical_url(url_web) == True:
                print(f"already down the url:<{url_web}>")
                continue

            urls_format_and_locat = self.down_website_url_to_file_format(attribute, tagname, ele, url_web)
            if urls_format_and_locat == None:
                continue
            url_offset = urls_format_and_locat[1]
            url_local = urls_format_and_locat[0]
            if is_alink:
                self.down_website_add_webpageQueue(attribute, url_local)
            else:
                HTML_Content = self.down_website_replace_htmlcontent(HTML_Content, dom_attribute, url_offset)
                self.down_website_add_resourceList(attribute, url_local)
        return HTML_Content

    def down_website_equal_url(self, url_main, url_other):
        url_main_parse = urlparse(url_main)
        url_main = url_main_parse.netloc
        url_main = re.sub(re.compile(r"^www\."), "", url_main)
        url_other_parse = urlparse(url_other)
        url_other = url_other_parse.netloc
        url_other = re.sub(re.compile(r"^www\."), "", url_other)
        if url_other.endswith(url_main) or url_main.endswith(url_other):
            return True
        else:
            return False

    def down_website_equal_url_strict(self, url_main, url_other):
        url_main_parse = urlparse(url_main)
        url_main = url_main_parse.netloc.lower()
        url_other_parse = urlparse(url_other)
        url_other = url_other_parse.netloc.lower()
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

    def down_website_url_format(self, url):
        url = re.sub(re.compile(r"[\/\\]+"), "/", url)
        return url

    def down_website_url_split(self, url):
        urls = [p.strip() for p in re.split(re.compile(r"[\/]+"), url) if p != ""]
        return urls

    def down_website_add_webpageQueue(self, url_web, url_local):
        self.__down_web_page_queue.put(
            (url_web, url_local)
        )

    def down_website_add_resourceList(self, url_web, url_local):
        threadLock.acquire()
        self.__down_web_resource_list.append(
            (url_web, url_local, True)
        )
        threadLock.release()

    def down_website_get_resourceList(self):
        threadLock.acquire()
        web_resource_item = self.__down_web_resource_list.pop()
        threadLock.release()
        return web_resource_item