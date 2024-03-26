import time

from pycore._base import *
import os
import json
import re

class Api(Base):
    __eudit_authorization = "NIS q6Ub38GX5BPuUaOO+cm2rcVwrmTzimxzXIxIICziWCx+eyn0n52uiA=="
    __local_dictdomain = ['dict.local', 'api.local', 'local', 'dict']
    __default_dictionaryname = '必背词汇统计.txt'
    __temp_ip = None # 临时IP地址

    def __init__(self, args=None):
        pass

    def get_eudic_groupid(self):
        group_name = self.get_eudic_groupname()
        word_trans = self.com_db.read(self.com_dbbase.get_tablename("translation_group"), {
            'group_n': group_name
        })
        return word_trans[0]

    def get_eudic_groupname(self):
        return self.__default_dictionaryname

    def get_eudic_category(self):
        data = {
            "language": "en",
        }
        api = f"https://api.frdic.com/api/open/v1/studylist/category"
        category = self.eudic_get(api, data)
        category = category["data"][0]
        name = category["name"]
        id = category["id"]
        category = {
            "name": name,
            "id": id,
        }
        return category

    def get_eudic_words(self, id=None, page_id=1, page_size=1000):
        if id == None:
            eudic = self.get_eudic_category()
            # group_name = eudic.get("name")
            id = eudic.get("id")
        data = {
            "id": id,
            "language": "en",
            # "page":page_id,
            "page_size": page_size,
        }
        api = f"https://api.frdic.com/api/open/v1/studylist/words/{id}"
        data = self.eudic_get(api, data)
        data = data["data"]
        words = []
        for datum in data:
            word = datum.get("word").lower()
            words.append(word)
        return words

    def eudic_get(self, url, data):
        result = self.com_http.get(url, data=data, headers={'Authorization': self.__eudit_authorization})
        result = result.replace('\\', '\\\\')
        result = json.loads(result)
        return result

    def update_ip_towebsitelisten(self):
        if self.load_module.is_windows():
            th = self.com_thread.create_thread("com", target=self.update_ip_towebsite)
            th.start()

    def login_domainmanageweb(self):
        user = self.com_config.get_config('west', 'user')
        pwd = self.com_config.get_config('west', 'pwd')
        if user == None or pwd == None:
            self.com_util.print_warn('Not set West.com account by config.cfg')
            return
        try:
            self.com_selenium.send_keys('#J_loginPage_u_name', user)
            self.com_selenium.send_keys('#J_loginPage_u_password', pwd)
            self.com_selenium.click('.g-common-btn.g-blue-btn[type="submit"]')
        except Exception as e:
            self.com_util.print_warn(e)

    def analyze_domain(self, parse_record=None, ip=None, headless=True):
        analyze_url = 'https://www.west.cn/manager/domainnew/rsall.asp?domainid=15030234'
        self.com_selenium.open(analyze_url, headless=headless)
        row_selector = '.el-table__row'
        time.sleep(3)
        table_row = self.com_selenium.find_text_content_list(row_selector, html_split=True)
        if len(table_row) == 0:
            time.sleep(3)
            self.login_domainmanageweb()
            self.analyze_domain(parse_record, ip=ip, headless=headless)
            return
        if parse_record == None:
            parse_record = self.__local_dictdomain

        def check_row(row):
            for record in parse_record:
                record = record.strip()
                row = row.strip()
                if row.find(record) != -1 and len(row) == len(record):
                    return True
            return False

        indexlist = []
        print(table_row)
        for index in range(len(table_row)):
            row = table_row[index]
            record = row[0]
            record = record.strip()
            if check_row(record) == True:
                indexlist.append(index)
        modifier = "('curses.pyc')[1].click()"
        modifier_confirm = f"('button')[0].click()"
        for index in indexlist:
            selector = f"document.querySelectorAll(`{row_selector}`)[{index}].querySelectorAll"
            modifier_js = selector + modifier
            self.com_selenium.execute_js(modifier_js)
            ipaddress_selector = f'//*[@id="pane-dnsrecord"]/div[3]/div[3]/table/tbody/tr[{index + 1}]/td[5]/div/span/div/input'
            ipaddress = self.com_selenium.find_element(ipaddress_selector)
            ipaddress.clear()
            ipaddress.send_keys(ip)
            modifier_confirm_js = selector + modifier_confirm
            self.com_selenium.execute_js(modifier_confirm_js)
        self.com_selenium.click('.el-button.el-button--primary.el-button--medium:first-child')

    def update_ip_towebsite(self, args=None, parse_record=None, headless=True):
        interval_second = 30
        self.com_util.print_info(f"listen ip_address change as interval-second {interval_second} and update to westIDC.")
        identification_index = 0
        while True:
            if identification_index > 3:
                #IP地址验证3次无效则重置
                self.__temp_ip = None
            if self.__temp_ip == None:
                self.__temp_ip = self.com_http.get_remote_ip(city="guizhousheng")
                # self.com_util.print_info(f"get prevIP {self.__temp_ip}.")
            if self.__temp_ip != None:
                identification_index += 1
                ip_identification = self.com_http.get_remote_ip(city="guizhousheng")
                # self.com_util.print_info(f"get secondIP {self.__temp_ip}.")
                if ip_identification == self.__temp_ip:
                    # self.com_util.print_info(f"prevIP {self.__temp_ip}, secondIP {ip_identification} as identification successfully.")
                    #IP地址验证成功则重置索引
                    identification_index = 0
                    self.__temp_ip = None
                    ip = ip_identification
                    if ip == None:
                        self.com_util.print_warn(f"ipAddress {ip} get error.")
                        time.sleep(interval_second)
                        continue
                    ip_temp = self.com_config.get_public('tampermonkey/ip_temp.txt')
                    preip = self.com_file.read(ip_temp)
                    if ip == preip:
                        self.com_util.print_info(f"ipAddress {ip} has been modified of westIDC.")
                        time.sleep(interval_second)
                        continue
                    self.com_util.print_info(f"new IP {ip}, preIP {preip},Changing to westIDC.")
                    self.analyze_domain(parse_record, ip=ip, headless=headless)
                    self.com_file.save(ip_temp, ip, overwrite=True)
                    time.sleep(interval_second)
                else:
                    # self.com_util.print_info(f"prevIP {self.__temp_ip}, secondIP {ip_identification} as identification failed.")
                    time.sleep(interval_second)

    def get_static_files(self, flask=None):
        file = flask.flask_request.args.get('file')
        content = None
        if file != None:
            file = self.com_file.get_template_dir(file)
            content = self.com_file.read(file)
        result = self.com_util.print_result(data=content)
        return result
