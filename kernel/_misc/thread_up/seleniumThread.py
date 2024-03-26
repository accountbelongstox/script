import json
from queue import Queue
from pycore.base import *
import os
import re
import operator
import time
import threading

threadLock = threading.Lock()
global_thread = {}

# selenium
class SeleniumThread(threading.Thread, Base):  # 继承父类threading.Thread
    __driver = None
    __init_driver_open = True
    args = None

    def __init__(self, target, args, group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=True):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        user = args
        # config = user.config
        json_file = open('./control_douyin/config.json', encoding="utf-8")
        config = json.load(json_file)
        self.target = target
        self.args = config
        self.name = thread_name
        self.__send_args = Queue()
        self.__config = config

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        if self.target != None:
            self.target(self.args)
        else:
            try:
                if self.__config["must_login"] == True:
                    self.login()

                if self.__config["login"]["active_check"] == True:
                    self.logined_acitve()
            except:
                pass
            # self.url_open_active()

    def set(self, name, data):
        self.__dict__[name] = data

    def setargs(self, args):
        self.args = args

    def send(self, send_args):
        self.__send_args.put(send_args)

    def url_open_active(self):
        return
        # while True:
        #     self.__driver = self.selenium.get_driver()
        #     print(f"self.__driver {self.name } -> {self.__driver}")
        #     time.sleep(1)
        # return
        active_period = self.__config["login"]["login_active"]["active_period"]
        while True:
            # 开始活动检查标志
            self.__config["login"]["active_check"] = True
            print("processing active checking.")
            if self.__config["login"]["mustLogin"]:
                isLogin = self.login_check()
                self.__config["login"]["isLogin"] = isLogin
                # if not isLogin:
                #     self.__config["login"]["isLogin"] = self.login_and_verify()
            if self.__config["login"]["isLogin"]:
                self.logined_acitve()
            # 关闭活动检查标志
            self.__config["login"]["active_check"] = False
            # 开始睡眠
            time.sleep(active_period)

    def login_check(self, init_check=False):
        if self.__driver is None:
            self.__driver = self.com_selenium.get_driver()
        # 如果有验证页，则说明已经登陆过可能已过期，则刷新
        time.sleep(1)
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        url_exists = self.com_selenium.find_url_from_driver_handles(loginVerifyURL)
        # print(f"login_check {loginVerifyURL} exists as {url_exists}")
        if url_exists == None:
            return False
        if init_check:
            return True
        self.__driver.refresh()
        # 如果刷新过后页面依然存在，则说明未过期
        url_exists = self.com_selenium.find_url_from_driver_handles(loginVerifyURL)
        # print(f"login_check {loginVerifyURL} exists as {url_exists}")
        if url_exists == None:
            return False
        return True

    def login_and_verify(self):
        self.login()
        is_login = self.login_verify_continue()
        self.login_pre()
        return is_login

    def login_pre(self):
        login_pre = self.__config["login"]["login_pre"]
        if "clicks" in login_pre:
            clicks = login_pre["clicks"]
            for click_selector in clicks:
                time.sleep(3)
                click_element = self.com_selenium.find_element_wait(click_selector)
                if click_element is not None:
                    try:
                        click_element.click()
                    except:
                        pass

    def verification_from_login(self, x_offset=None, y_offset=None, code_verify=None):
        if x_offset is not None and y_offset is not None:
            self.verification_of_swipe(x_offset, y_offset)
        if code_verify is not None:
            self.verification_of_code(code_verify)

    def verification_of_swipe(self, x_offset=None, y_offset=None):
        if x_offset is not None and y_offset is not None:
            move_to_element = self.com_selenium.find_elements('.vcode-spin-button', is_beautifulsoup=True)
            move_to_element = move_to_element[0][0]
            id = move_to_element["id"]
            id = f"#{id}"
            self.com_selenium.move_to_element(id, x_offset, y_offset)

    def verification_of_code(self, code_verify=None):
        uc_token = self.com_selenium.find_element('#uc-com-token', is_beautifulsoup=False)
        uc_token.send_keys(code_verify)
        time.sleep(1)
        uc_token = self.com_selenium.find_element('.uc-token-confirm-btn', is_beautifulsoup=False)
        uc_token.click()

    def login_submit(self):
        submit_css = self.__config["login"]["submit"]
        submit = self.com_selenium.find_element_wait(submit_css)
        if self.com_selenium.is_element(submit):
            submit.click()
        if self.login_check():
            return True
        else:
            return False

    def login(self):
        userInput = self.__config["login"]["userInput"]
        pwdInput = self.__config["login"]["pwdInput"]
        submit = self.__config["login"]["submit"]
        loginURL = self.__config["login"]["loginURL"]
        loginUser = self.__config["login"]["loginUser"]
        loginPwd = self.__config["login"]["loginPwd"]
        html = self.com_selenium.get_html()
        current_url = self.com_selenium.get_current_url()
        self.com_selenium.open_url_as_new_window(loginURL)
        userInputElement = self.com_selenium.find_element_wait(userInput)
        pwdInputElement = self.com_selenium.find_element_wait(pwdInput)
        submitElement = self.com_selenium.find_element_wait(submit)
        send_keys_user = False
        send_keys_pwd = False
        click_login = False
        if userInputElement.__class__.__name__ == "WebElement":
            userInputElement.send_keys("")
            time.sleep(0.5)
            userInputElement.send_keys(loginUser)
            send_keys_user = True
        if pwdInputElement.__class__.__name__ == "WebElement":
            pwdInputElement.send_keys("")
            time.sleep(0.5)
            pwdInputElement.send_keys(loginPwd)
            send_keys_pwd = True
        if submitElement.__class__.__name__ == "WebElement":
            try:
                submitElement.click()
                click_login = True
            except:
                pass
        result = {}
        if send_keys_user and send_keys_pwd and click_login:
            if self.login_check(init_check=True):
                result["type"] = "success-init-check"
                result["status"] = True
                return result
            elif self.com_selenium.exists_element(".vcode-spin-img"):
                vcode_close = self.com_selenium.find_element(".vcode-close", is_beautifulsoup=False)
                vcode_close.click()
                submitElement.click()
                time.sleep(1)
                if self.login_check(init_check=True):
                    result["type"] = "success-vcode-close"
                    result["status"] = True
                else:
                    result["type"] = "fail-at-vcode-close"
                    result["status"] = False
                return result
            elif self.com_selenium.exists_element("#token-img"):
                screenshot_save_file = self.com_selenium.screenshot_of_selector("#token-img")
                ocr = self.com_file.image_to_str_from_paddleorc(screenshot_save_file)
                ocr_text = ocr["text"]
                code_verify = ocr_text
                print(f"ocr text {code_verify}")
                self.login_click(code_verify=code_verify)
                time.sleep(2)
                if self.login_check():
                    result["type"] = "success-code-verify"
                    result["status"] = True
                else:
                    result["type"] = "fail-to-code_verify"
                    result["status"] = False
                return result
            result = self.get_login_verify_html()
            return result
        else:
            log = "\n---------------------------------------------------------------------------------------------------------------------\n"
            log = log + f"userInputElement{type(userInputElement)}\n"
            log = log + f"pwdInputElement{type(pwdInputElement)}\n"
            log = log + f"submitElement{type(submitElement)}\n"
            log = log + html
            file_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            self.com_file.save_file(f"{file_time}{current_url}-{file_time}.log.html".replace("/", "").replace(":", ""),
                                    log)
            result["type"] = "fail-to-send_keys_user-and send_keys_pwd-click_login"
            result["status"] = False
            return result

    def login_verify_continue(self, check_deep=0):
        if check_deep == 0:
            return False
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        loginVerifyURL = loginVerifyURL.split("?")[0]
        current_url = self.__driver.current_url
        current_url = current_url.split("?")[0]
        if operator.__eq__(current_url, loginVerifyURL):
            return True
        else:
            print(f"login_verify_continue check is :{self.__driver.current_url} to {loginVerifyURL} ")
            time.sleep(1)
            check_deep += 1
            return self.login_verify_continue(check_deep)

    #
    # def init_driver(self,url,cb=None):
    #     if self.__init_driver_open == True:
    #         self.com_selenium.open_url(url=url)
    #         print('load_JQuery loading..')
    #         self.com_selenium.load_JQuery_wait()
    #         self.__init_driver_open = False
    #     else:
    #         len_drivers = len(self.__driver.window_handles)
    #         url_exists = False
    #         for index in range(len_drivers):
    #             self.__driver.switch_to.window(self.__driver.window_handles[index])
    #             if self.__driver.current_url.find(url) == 0:
    #                 url_exists = True
    #                 print(f"init_driver found url is {self.__driver.current_url}")
    #                 break
    #         if not url_exists:
    #             js = "window.open('{}','_blank');"
    #             self.__driver.execute_script(js.format(url))
    #             print(f"init_driver open url by new window for page {url}")
    #             self.com_selenium.load_JQuery_wait()
    #     if cb != None: cb()

    def logined_acitve(self):
        active_url = self.__config["login"]["login_active"]["active_url"]
        buttons = self.__config["login"]["login_active"]["buttons"]
        self.com_selenium.open_url_as_new_window(active_url)
        for button_selector in buttons:
            button_selector = self.com_selenium.find_element_wait(button_selector)
            button_selector.click()
            time.sleep(3)

    def get_html_resource(self):
        # vcode-spin-img
        html = self.__driver.page_source
        html += "取得滑动登陆验证距离的javascript代码"
        return html

    def get_login_verify_html(self):
        result = {}
        if self.login_check():
            result["type"] = "success"
            result["src"] = "初始化成功,该接口可以正常请求但请不要随意重启服务器"
            return result
        else:
            self.__driver.refresh()
            self.login()
        time.sleep(3)

        selector_css = self.com_selenium.find_element(".vcode-spin-img", is_beautifulsoup=False)
        if self.com_selenium.is_element(selector_css):
            vcode_close = self.com_selenium.find_element(".vcode-close", is_beautifulsoup=False)
            vcode_close.click()
            result["type"] = "success"
            result["src"] = "初始化成功,该接口可以正常请求但请不要随意重启服务器"
            result["status"] = self.login_submit()
            return result
        else:
            try:
                result["type"] = "token_code"
                screenshot_save_file = self.com_selenium.screenshot_of_selector("#token-img")
                ocr = self.com_file.image_to_str_from_paddleorc(screenshot_save_file)
                ocr_text = ocr["text"]
                token_img_content = self.file.b64encode(screenshot_save_file)
                os.remove(screenshot_save_file)
                result["src"] = token_img_content

                return result
            except:
                result["type"] = "html"
                result["src"] = self.selenium.find_html_wait()
                return result
        # try:
        #     selector_css = self.com_selenium.find_element(".vcode-spin-img", is_beautifulsoup=True)
        #     vcode_spin_img = selector_css[0]
        #     # vcode_spin_img = insert_html_link_as_style + str(vcode_spin_img)
        #     vcode_spin_img = vcode_spin_img["src"]
        #     result["type"] = "rotate"
        #     result["src"] = vcode_spin_img
        #     return result
        # except:
        #     pass

    def get_data(self, args):
        while self.__config["login"]["active_check"] is True:
            time.sleep(1)
        getdata_result = {}
        try:
            datatypes_str = args["datatypes"]
            datatypes = datatypes_str.split(',')
            getdata_result["type"] = 0
            getdata_result["message"] = "successfully get data"
        except:
            # 如果不是当前token name请求，则跳过
            getdata_result["type"] = 0
            getdata_result["message"] = "no request name is datatype"
            getdata_result["error"] = f"no request name is datatype,datatype is {datatypes_str}"
            return getdata_result
        #
        # password = None
        # if "password" in args:
        #     password = args["password"]
        # method = None
        # if "method" in args:
        #     method = args["method"]

        graspFields = self.__config["data_fields"]
        fields_data = []
        self.com_util.pprint(graspFields)
        for grasp_unit in graspFields:
            datatype = grasp_unit["datatype"]
            if datatype not in datatypes:
                continue
            page = grasp_unit["page"]
            self.com_selenium.open_url_as_new_window(page)
            datas_by_class = grasp_unit["datas_by_class"]
            sentinel_selector = datas_by_class["sentinel_selector"]
            self.com_selenium.find_elements_value_wait(sentinel_selector, url=page)
            datas = datas_by_class["datas"]
            for data in datas:
                selectors = data["selectors"]
                datatype = data["datatype"]
                description = data["description"]
                for selector_value in selectors:
                    selectors = selector_value["selectors"]
                    # 将selector转换成标准格式
                    # [
                    #     attr:"val,attr" ,
                    #     selector:".selector"
                    # ]
                    if type(selectors) == str:
                        selectors = selectors.split(",")
                        selector_dict = {}
                        selectors_temp = []
                        for selector in selectors:
                            selector_dict["selector"] = selector
                            selector_dict["attr"] = "val"
                            selectors_temp.append(selector_dict)
                        selectors = selectors_temp
                    elif type(selectors) == dict:
                        selectors = [selectors]

                    selector_names = selector_value["selector_names"]
                    if type(selector_names) == str:
                        selector_names = selector_names.split(",")

                    get_data_unit = {}
                    for selector_dict in selectors:
                        if "attr" in selector_dict:
                            attr = selector_dict["attr"]
                        else:
                            attr = "val"
                        selector = selector_dict["selector"]

                        if "callback" in selector_dict:
                            callback = selector_dict["callback"]
                        else:
                            callback = None

                        if attr == "val":
                            results = self.com_selenium.find_elements_value_by_js_wait(selector, page)
                        if attr == "attr":
                            attr_val = selector_dict["attr_val"]
                            results = self.com_selenium.find_elements_attr_by_js_wait(selector, attr_val, page)

                        for i in range(len(selector_names)):
                            selector_name = selector_names[i]
                            try:
                                result = results[i]
                            except:
                                result = None
                            if callback != None:
                                result = callback(result)
                            if len(selectors) > 1:
                                if selector_name not in get_data_unit:
                                    get_data_unit[selector_name] = [result]
                                else:
                                    get_data_unit[selector_name].append(result)
                            else:
                                get_data_unit[selector_name] = result

                    fields_data.append({
                        "datatype": datatype,
                        "description": description,
                        "data": get_data_unit
                    })
                    print(f"get_data_unit {get_data_unit}")
        getdata_result["data"] = fields_data
        return getdata_result

    def quit(self):
        self.__driver.quit()

    def get_config(self, keys):
        pass
