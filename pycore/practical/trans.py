from pycore.base import Base
import time
# import math
from queue import Queue
# import asyncio
# import os
import re
import json
# import requests
from urllib import request, parse
import googletrans
from googletrans import Translator as GTrans
# import azure.cognitiveservices.speech as speechsdk
threadQueue = Queue()
gEngine = GTrans(service_urls=[
    'translate.google.com',
    'translate.google.com.hk',
    # 'translate.google.cn',
])

class Trans(Base):
    def __init__(self):
        pass

    def google(self, word, dest="en", src="auto", ):
        out = gEngine.translate(word, dest, src)
        result = {
            "origin": word,
            "text": out.text,
            "src": out.src,
            "dest": out.dest,
        }
        return result

    def to_english(self, text):
        result = self.google(text, dest="en", src="auto", )
        return result

    def to_chinese(self, text):
        result = self.google(text, dest="zh-CN", src="auto", )
        return result

    def putQueue(self, word):
        if isinstance(word, list):
            for item in word:
                threadQueue.put(item)
        else:
            threadQueue.put(word)

    def get_language(self):
        language = googletrans.LANGUAGES
        return language

    def get_thread_result(self, threads):
        result = []
        for th in threads:
            result_of_th = th.result()
            while result_of_th.qsize() > 0:
                result.append(result_of_th.get())
        result.sort(key=lambda item: item["index"])
        return result

    def thread_translation_has_ended(self, threads):
        for th in threads:
            if th.done() == False:
                return False
        return True


    def translate_from_google_cn(self, word, from_is="en", to="zh-cn", callback=None):
        # 返回形式
        # auxiliary verb 助动词
        # prefix 前缀
        # pronounce 发音
        # pronounce_to 译文发音
        # phonetic_symbol 音标
        # phonetic_symbol_to 译文音标
        # adverb 副词
        # preposition 介词
        # conjunction 连词
        # adverb 副词
        request_time = time.strftime("%Y-%m-%d", time.localtime())
        url = f'https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute'
        data = {
            "rpcids": "MkEWBc",
            "source-path": "/",
            "f.sid": "3528615277044966264",
            "bl": f"boq_translate-webserver_{request_time}.17_p0",
            "hl": to,
            "soc-app": "1",
            "soc-platform": "1",
            "soc-device": "1",
            "_reqid": "5445720",
            "rt": "c",
            'f.req': f'[[["MkEWBc","[[\\"{word}\\",\\"{from_is}\\",\\"{to}\\",true],[null]]",null,"generic"]]]'
        }
        res = self.com_http.post(url, data=data)
        res = res.decode('utf-8')
        # Google翻译是以数字+换行作为响应分隔符的，故以以下正则分割。
        res = re.split(re.compile(r"\d+\n"), res)
        res = res[1]
        # 去除google干扰字符
        res = res.replace('"[', '[')
        res = res.replace(']"', ']')
        res = res.replace('\\"', '"')
        # 替换空值，以便于eval转码
        res = res.replace('true', 'True')
        res = res.replace('false', 'False')
        res = res.replace('null', 'None')
        # 将字符串里的unicode码查出
        unicode_code = re.findall(re.compile(r"\\\\u.{4}"), res)
        while len(unicode_code) > 0:
            # 并将unicode码转码后替换成字符串
            unicode = unicode_code.pop()
            trans_code = unicode[1:].encode().decode('unicode_escape')
            res = res.replace(unicode, trans_code)
        # 解析成一个对象
        rough = eval(res)
        rough_machining = rough[0]
        shelled = []
        for item in rough_machining:
            if type(item) is list:
                shelled = item
                break
        result = {}
        result["word"] = word
        result["phonetic_symbol"] = shelled[0][0]
        result["from_is"] = shelled[2]
        result["pronounce"] = None
        result["pronounce_to"] = None
        main_mean = self.com_util.extract_list(shelled[1][0])
        main_mean = self.com_util.split_list(main_mean)
        main_mean = self.com_util.extract_list(main_mean[1])
        main_mean = self.com_util.split_list(main_mean)
        example_key = f"example"
        synonym_key = f"synonym"
        generic_key = f"generic"
        mean_key = "mean"
        for item in main_mean:
            if mean_key not in result:
                result[mean_key] = []
            result[mean_key].append(item[2])
        result[example_key] = []
        main_trans_result = shelled[1]
        result["to"] = main_trans_result[1]
        trans_to = main_trans_result[0]
        for trans_item in trans_to:
            if "phonetic_symbol_to" not in result:
                result["phonetic_symbol_to"] = trans_item[1]
        main_trans_result = self.com_util.extract_list(main_trans_result[0])
        main_trans_result = self.com_util.split_list(main_trans_result, start=1, split_symbol=[None, False, True])
        main_trans_result = self.com_util.extract_list(main_trans_result)
        mean = main_trans_result[0]
        self.com_util.add_to_dict(result, mean_key, mean)
        try:
            main_info = shelled[3]
        except:
            if callback is not None:
                return callback(result)
            else:
                return result
        for trans_item in main_info:
            if type(trans_item) is list:
                info_of_trans = trans_item[0]
                for info in info_of_trans:
                    info_type = info[0]
                    try:
                        info_detail = info[1]
                    except:
                        self.com_util.pprint(info)
                        return
                    if info_type is None:
                        if type(info_detail) is list:
                            if generic_key in result:
                                info_label = f"{generic_key}_mothertongue"
                                result[info_label] = result[generic_key]
                            result[generic_key] = {}
                            info_detail = self.com_util.extract_list(info_detail)
                            info_detail = self.com_util.split_list(info_detail, split_symbol=[None, False, True])
                            means = info_detail[0]
                            result[generic_key][mean_key] = means
                            if len(info_detail) > 1:
                                synonym = info_detail[1]
                            else:
                                synonym = []
                            result[generic_key][synonym_key] = synonym

                        else:
                            result[example_key].append(info_detail)
                    else:
                        for detail_item in info_detail:

                            if info_type == "abbreviation":
                                self.com_util.add_to_dict(result, info_type, detail_item[0])
                            elif info_type in ["adverb", "noun", "adjective", "exclamation", "article", "pronoun",
                                               "pronoun", "pronoun", "pronoun", "pronoun", "pronoun"]:

                                # 如果项目已经存在,而说明需要将前一个替换为母语翻译
                                if info_type in result:
                                    info_label = f"{info_type}_mothertongue"
                                    result[info_label] = result[info_type]
                                result[info_type] = {}
                                result[info_type][example_key] = []
                                result[info_type][synonym_key] = []
                                # 需要进行例句判断
                                mean = detail_item[0]
                                self.com_util.add_to_dict(result[info_type], mean_key, mean)
                                add_to_example = True
                                query_synonym = False
                                synonym = []
                                for i in range(len(detail_item)):
                                    item = detail_item[i]
                                    if item in [None, False, True]:
                                        add_to_example = False
                                        query_synonym = True
                                    if i > 0 and type(item) is str and add_to_example:
                                        # 例句添加
                                        result[info_type][example_key].append(item)
                                    if i > 0 and query_synonym and type(item) is list:
                                        synonym = item
                                while len(synonym) > 0 and type(synonym[0][0]) == list:
                                    synonym = synonym[0]
                                for item in synonym:
                                    if type(item) == list:
                                        item = item[0]
                                    self.com_util.add_to_dict(result[info_type], synonym_key, item)
                            else:  # 其他未识别
                                result[info_type] = {}
                                for detail in detail_item:
                                    if type(detail) is str:  # 例句
                                        # self.com_util.add_to_dict(result[info_type], example_key, detail)
                                        self.com_util.add_to_dict(result[info_type], mean_key, detail)
                                    if type(detail) is list:  # 同义词
                                        detail_list = detail
                                        while type(detail_list[0][0]) is list:
                                            detail_list = detail_list[0]
                                        for item in detail_list:
                                            while type(item[0][0]) is list:
                                                item = item[0]
                                            if type(item[0]) is list:
                                                verb = item[0][0]
                                            else:
                                                verb = item
                                            if type(verb) is list:
                                                verb = verb[0]
                                            self.com_util.add_to_dict(result[info_type], synonym_key, verb)
        if callback is not None:
            return callback(result)
        else:
            return result

    def not_translatedtoqueue(self, words=None, condition=None):
        global threadQueue
        if isinstance(words, str):
            words = [words]
        elif words == None:
            words = self.read_not_translated(condition=condition)
        self.com_thread.update_queue(threadQueue, words)
        update_time = self.com_string.create_time()
        qsize = threadQueue.qsize()
        if qsize < 3:
            pass
        else:
            self.com_util.print_info(
                f'no-translated:{len(words)} words add to tasks and qsize:{qsize},update_time {update_time}')
        return threadQueue

    def start_translate_thread(self, words=None, condition=None, wait=False, save_db=True, headless=True, debug=False,
                               callback=None, max_thread=4):
        if words == None:
            words = self.read_not_translated()
        threadQueue = self.not_translatedtoqueue(words=words, condition=condition)
        qsize = threadQueue.qsize()
        tasks_per_thread = int(qsize / max_thread)
        min_processing_per_thread = 10
        if tasks_per_thread < min_processing_per_thread:
            tasks_per_thread = min_processing_per_thread
        thread_args = {
            "task": threadQueue,
            "save_db": save_db,
            # "save_db":False,
            "info": False,
            "headless": headless,
            "debug": debug,
            "callback": callback,
            "tasks_per_thread": tasks_per_thread,
        }
        self.com_thread.create_thread_pool("translate", args=thread_args, wait=wait, max_thread=max_thread, )
