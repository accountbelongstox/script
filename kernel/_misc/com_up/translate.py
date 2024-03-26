import time

import math
from queue import Queue
import asyncio

from pycore.base import *
import os
import re
import json
import requests
from urllib import request, parse

import googletrans
from googletrans import Translator
import azure.cognitiveservices.speech as speechsdk

threadQueue = Queue()
threadAddVoiceQueue = Queue()

pyttsx_engine = None

googletanslator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.com.hk',
    # 'translate.google.cn',
])


class Translate(Base):
    __db = None
    __tts_engine = None
    __third_voice_names = ['tts']
    __obsolete_third_voice_names = ['Yd']
    __voice_files = None
    MDX = None  # 用来解析mdx文件的字段

    def __init__(self, args):
        pass

    def main(self, args):
        pass

    def format_phonetic(self, phonetic, clean=None):
        phonetic = self.com_string.decode(phonetic).lower()
        baseclean = ["uk", "us", "[", "]", "'", '"']
        if clean != None:
            baseclean = baseclean + clean
        phonetic = self.com_string.clear_string(phonetic, baseclean)
        phonetic = self.com_string.encode(phonetic)
        return phonetic

    def sort_phonetic(self, phonetic):
        phonetic = self.format_phonetic(phonetic, ["(", ")", "ˈ", "ˌ", "ː", ".", ":", "ˈ", "ˌ", "ː", ":"])
        return phonetic

    def is_translation(self, translation):
        if type(translation) != dict:
            return False
        word_translation = translation.get('word_translation')
        if None == word_translation:
            return False
        advanced_translate = translation.get('advanced_translate')
        if None == advanced_translate:
            return False
        advanced_translate_type = translation.get('advanced_translate_type')
        if None == advanced_translate_type:
            return False
        plural_form = translation.get('plural_form')
        if None == plural_form:
            return False
        return True

    def get_third_voice_names(self):
        return self.__third_voice_names

    def is_voice(self, translation):
        voice_files = translation.get('voice_files')
        if voice_files == None or len(voice_files.keys()) == 0:
            return False
        return True

    def scan_voicefiles(self,copy=False):
        if self.__voice_files == None:
            flask_template_folder = self.com_config.get_global("flask_template_folder")
            control_dir = self.load_module.get_control_dir(flask_template_folder)
            voice_dir = os.path.join(control_dir, 'static/translate_wave/bing/voice')
            self.__voice_files = os.listdir(voice_dir)
        if copy:
            return self.__voice_files[:]
        else:
            return self.__voice_files

    def is_voicefile(self, translation, word, info=False, index=None,scan_voicefiles=None):
        self.scan_voicefiles()
        voice_files = translation.get('voice_files')
        if info == True:
            self.com_util.print_info(f"is_voicefile checked {index}")
        if voice_files != None:
            if len(voice_files.keys()) == 0:
                return False
            for key, val in voice_files.items():
                if not isinstance(val, dict):
                    return False
                save_filename = val.get('save_filename')
                if save_filename != None:
                    base_name = os.path.basename(save_filename)
                    if base_name not in self.__voice_files:
                        return False
                    else:
                        if scan_voicefiles != None:
                            if base_name in scan_voicefiles:
                                scan_voicefiles.remove(base_name)
        else:
            return False
        return True

    def delete_redundantvoicefiles(self,redundant_voicefiles):
        index = 0
        for file in redundant_voicefiles:
            file_name = self.bing_engine_voice_static_dir(file_type="voice",file_name=file)
            redundant_voice = self.bing_engine_voice_static_dir(file_type="redundant_voice",file_name=file)
            self.com_file.cut(file_name,redundant_voice)
            if index % 10000 == 0 and index > 0:
                self.com_util.print_info(f"delete  redundant voice file({index}): {file_name}.")
            index += 1

    def is_onlywebtrans_and_noother(self, word, translation=None):
        translate = self.is_wordtranslate(translation)
        if translate == True:
            only_web = self.is_onlywebtrans(translation)
            compound_word = self.is_compound_word(word)
            include_images = self.is_transincludeimages(translation)
            include_native_voice = self.include_native_voice(translation)
            if only_web == True \
                    and compound_word == False \
                    and include_native_voice == False \
                    and include_images == False:
                return True
            else:
                return False
        else:
            return True

    def is_incorrect_translate(self, word, translation):
        if not isinstance(word, str):
            return False
        compound_word = self.is_compound_word(word)
        include_images = self.is_transincludeimages(translation)
        include_native_voice = self.include_native_voice(translation)
        if compound_word or include_images or include_native_voice:
            return True
        else:
            return False

    def is_compound_word(self, word):
        is_hyphen = self.com_string.is_wordbetween(word, "-")
        if is_hyphen or word.isupper():
            return True
        else:
            return False

    def is_transincludeimages(self, translation):
        sample_images = translation.get('sample_images')
        if isinstance(sample_images, dict):
            if len(sample_images.keys()) > 0:
                return True
        return False

    def is_word_type(self, word_type):
        word_types = [
            "n.",
            "v.",
            "Web",
            "prep.",
            "abbr.",
            "n.",
            "adj.",
            "vt.",
            "adj.",
            "IDM",
            "pron.",
            "adv.",
            "etc.",
            "pron.",
        ]
        result = None
        for type_oneitem in word_types:
            word_type = word_type.lower().strip()
            if word_type.startswith(type_oneitem.lower()):
                result = word_type
                return result
        return result

    def is_wordtranslate(self, translation):
        if translation == None:
            return False
        word_translation = translation.get('word_translation')
        if isinstance(word_translation, list):
            return True
        else:
            return False

    def is_onlywebtrans(self, translation):
        word_translation = translation.get('word_translation')
        if len(word_translation) == 1:
            trans_item = word_translation[0]
            if isinstance(trans_item, list):
                trans_type = trans_item[0]
                if trans_type.lower() == 'web':
                    return True
        return False

    def is_third_voice(self, translation):
        voice_files = translation.get('voice_files')
        if voice_files == None:
            return False
        for key in voice_files.keys():
            if key in self.__third_voice_names:
                if isinstance(voice_files.get(key), dict):
                    return True
        return False

    def add_third_voice(self, word, translation, delete_obsolete=True):
        voice_files = translation.get('voice_files')
        if voice_files == None:
            translation['voice_files'] = {}
        tts_voice_file = self.to_voice_tts(word)
        tts_voice_oggfile = self.com_ffmpeg.convert_to_ogg(tts_voice_file,delete_old=True)

        self.com_util.print_info(f'tts_voice_file {tts_voice_oggfile}')
        tts_name = self.get_third_voice_names()[0]
        static_file = self.com_translate.bing_engine_get_static_file(word, index="0", file_ext='.mp3',
                                                                     file_type='voice', voice_type='tts')
        self.com_file.cut(tts_voice_oggfile, static_file)
        static_folder = self.com_config.get_global("flask_template_folder")
        static_folder = self.com_string.dir_normal(static_folder, linux=True)
        static_file = self.com_string.dir_normal(static_file, linux=True)
        save_name = static_file.split(static_folder)[1]
        save_name = self.com_string.dir_normal(save_name, linux=True)
        if delete_obsolete == True:
            for obsolete in self.__obsolete_third_voice_names:
                if translation['voice_files'].get(obsolete) != None:
                    del translation['voice_files'][obsolete]
        translation['voice_files'][tts_name] = {
            "save_filename": save_name,
            "url": tts_name,
            "dynamic_url": False,
        }
        self.com_util.pprint(translation['voice_files'])
        return translation

    def include_native_voice(self, translation):
        voice_files = translation.get('voice_files')
        if voice_files == None:
            return False
        native_voice = []
        for key in voice_files.keys():
            if key not in self.__third_voice_names and key not in self.__obsolete_third_voice_names:
                native_voice.append(key)
        return len(native_voice) > 0

    def set_default_val(self, data):
        if type(data) != list:
            data = [data]
        for word_item in data:
            self.set_addval(word_item, "last_time", self.com_string.create_time())
            self.set_addval(word_item, "read", 0)
        return data

    def get_thread_translatemax(self, qsize, default=None):
        if default != None:
            return default
        max_thread = 4
        min_thread = 1
        max_processing_per_thread = 1000
        thread_n = min_thread
        if self.load_module.is_windows():
            if qsize > max_processing_per_thread:
                thread_n = int(qsize / max_processing_per_thread)
                if thread_n > max_thread:
                    thread_n = max_thread
        return thread_n

    def set_addval(self, word, key, value):
        if key not in word:
            word[key] = value
        return word

    def translate(self, word, from_is="en", to="zh-cn", engine="google_cn", callback=None, timeout=None):
        is_file = self.com_file.isfile(word)
        if is_file:
            word = self.com_file.open(word)
        if type(word) is list:
            words = word
        else:
            if type(word) is not str:
                word = self.com_string.byte_to_str(word)
            words, exists_words, exclude_words, word_frequency = self.count_document_words(word)
        if from_is in words:
            words = words[from_is]
        if engine == "bing":
            return self.translate_from_bing(words)

        per_thread_solve_word_num = 30
        words_len = len(words)
        words_split = words_len / per_thread_solve_word_num
        max_thread = math.ceil(words_split)
        # 最大调用线程数
        if max_thread > 60:
            max_thread = 60

        threads = []
        for i in range(max_thread):
            start_point = i * per_thread_solve_word_num
            end_point = i * per_thread_solve_word_num + per_thread_solve_word_num
            fragment_translation = words[start_point:end_point]
            fragment_word_translateobject_list = []
            for index in range(len(fragment_translation)):
                word = fragment_translation[index]
                translateobject = self.word_to_translateobject(word, from_is=from_is, to=to, engine=engine,
                                                               callback=callback, index=index)
                fragment_word_translateobject_list.append(translateobject)
            th = self.com_thread.create_thread("translate", args=fragment_word_translateobject_list)
            th.start()
            threads.append(th)

        time_count = 0
        # 如果线程全部结束则返回结果
        while (self.thread_translation_has_ended(threads) != True):
            if self.is_timeout(time_count, timeout):
                print(f'translation timed out')
                break
            time.sleep(1)
            time_count += 1
        result = self.get_thread_result(threads)
        if callback is not None:
            return callback(result)
        else:
            return result

    def get_trans_val(self, put_word, file_val):
        if file_val == None:
            return put_word
        for key, val in file_val.items():
            save_filename = val.get('save_filename')
            full_filename = self.com_file.get_template_dir(save_filename, fulllink=True)
            put_word[save_filename] = self.com_file.read_file_bytes(full_filename)
        return put_word

    def document_extract_en(self, doc):
        splits_symbol = re.compile(r'[^curses.pyc-zA-Z]+')
        doc_words = re.split(splits_symbol, doc)
        doc_words = list(
            set(doc_words)
        )
        return doc_words

    def modify_word(self, word):
        # Abb 形式单词
        pattern = re.compile(r"^[A-Z][curses.pyc-z]+")
        if re.match(pattern, word):
            word = word.lower()
        # 云除'号
        word = word.strip("'").strip()
        # 将单词编码
        word = self.com_string.encode(word)
        return word

    def count_document_words(self, doc):
        exclude_words = []
        normal_words = []
        if isinstance(doc, list):
            orgin_words = doc
        else:
            splits_symbol = re.compile(r'[^curses.pyc-zA-Z\'\-\_]+')
            orgin_words = re.split(splits_symbol, doc)

        for word in orgin_words:
            is_english = self.is_english(word)
            if is_english == True:
                normal_words.append(self.modify_word(word))
            else:
                if word not in exclude_words:
                    exclude_words.append(word)

        word_frequency = self.count_word_frequency_tolist(normal_words)
        words = self.com_util.deduplication_list(normal_words)
        exists_words = self.com_util.arr_diff(normal_words, words)
        return words, exists_words, exclude_words, word_frequency

    def is_chinese(self, word):
        pattern = re.compile(r"^([\u4e00-\u9fa5]|[\ufe30-\uffa0]|[\u4e00-\uffa5])+")
        if re.search(pattern, word) != None:
            return True
        return False

    def is_english(self, word):
        if isinstance(word, str):
            word = word.strip()
            pattern = r'^[curses.pyc-zA-Z\-\']+$'
            if re.match(pattern, word):
                pattern = r'^[curses.pyc-zA-Z]+$'
                first = word[0]
                tail_alphabet = word[-1]
                if re.match(pattern, first) and re.match(pattern, tail_alphabet):
                    return True
                    # word_lower = word.lower()
                    # word_len = len(word)
                    # if word_len == 1:
                    #     if word in ['curses.pyc', 'I', 'O', 'x', 'y']:
                    #         return True
                    # elif word_len == 2:
                    #     double_words = [
                    #         'aa', 'ab', 'ad', 'ae', 'ag', 'ah', 'ai', 'al', 'am', 'an', 'ar', 'as', 'at', 'aw', 'ax',
                    #         'ay',
                    #         'ba', 'be', 'bi', 'bo', 'by',
                    #         'ch',
                    #         'da', 'de', 'di', 'do',
                    #         'ea', 'ed', 'ee', 'ef', 'eh', 'el', 'em', 'en', 'er', 'es', 'et', 'ex',
                    #         'fa', 'fe', 'fy',
                    #         'gi', 'go',
                    #         'ha', 'he', 'hi', 'hm', 'ho',
                    #         'id', 'if', 'in', 'is', 'it',
                    #         'jo',
                    #         'ka', 'ki', 'ko',
                    #         'la', 'li', 'lo',
                    #         'ma', 'me', 'mi', 'mm', 'mo', 'mu', 'my',
                    #         'na', 'ne', 'no', 'nu',
                    #         'od', 'oe', 'of', 'oh', 'oi', 'ok', 'om', 'on', 'op', 'or', 'os', 'ow', 'ox', 'oy',
                    #         'pa', 'pe', 'pi', 'po',
                    #         'qi', 'ms', 'pm', 'vt',
                    #         're',
                    #         'sh', 'si', 'so',
                    #         'ta', 'ti', 'to',
                    #         'uh', 'um', 'un', 'up', 'ur', 'us', 'ut',
                    #         'we', 'wo',
                    #         'xi', 'xu',
                    #         'ya', 'ye', 'yo',
                    #         'za'
                    #     ]
                    #     if word_lower in double_words:
                    #         return True
                    # else:
                    #     if word_len >= 3:
            return False
        else:
            return False

    def count_word_frequency(self, word_list):
        word_count = {}
        for word in word_list:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
        return word_count

    def count_word_frequency_tolist(self, word_frequency):
        if isinstance(word_frequency, list):
            word_frequency = self.count_word_frequency(word_frequency)
        sorted_list = [{key: value} for key, value in
                       sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)]
        return sorted_list

    def google_translate_language(self):
        language = googletrans.LANGUAGES
        return language

    def translate_to_html(self, word, from_is="en", to="zh-cn", engine="google_cn", callback=None):
        result = self.translate(word, from_is=from_is, to=to, engine=engine, callback=callback)
        return result

    def to_html(self, result):
        for item in result:
            print(item)

    def to_text(self, result):
        for item in result:
            print(item)

    def is_timeout(self, time_count, timeout):
        if timeout == None:
            return False
        if (time_count >= timeout):
            return True
        else:
            return False

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

    def translate_from_google(self, word, dest="en", src="zh-CN", ):
        out = googletanslator.translate(word, dest, src)
        voice = None
        result = {
            "origin": word,
            "text": out.text,
            "src": out.src,
            "dest": out.dest,
            "pronunciation": voice,
        }
        return result

    def bing_engine_get_static_file(self, word, index="", file_ext="", file_type="voice", voice_type=""):
        if index != "":
            index = f"_{index}"
        if file_ext != "":
            if not file_ext.startswith("."):
                file_ext = f".{file_ext}"
        if voice_type != "":
            voice_type = f"_{voice_type}"
        word_file = self.com_file.sanitize_filename(word)
        md5 = self.com_string.md5(word)
        filename_file = f"{word_file}{voice_type}_{md5}{index}{file_ext}"
        static_dir = self.bing_engine_voice_static_dir(file_type=file_type)
        static_file = os.path.join(static_dir, filename_file)
        static_file = self.com_string.dir_normal(static_file)
        return static_file

    def bing_engine_voice_static_dir(self, file_type="voice",file_name=''):
        static_folder = self.get_static()
        down_dir = self.load_module.get_control_dir(f"{static_folder}/bing/{file_type}")
        if file_name != "":
            down_dir = os.path.join(down_dir,file_name)
            down_dir = self.com_string.dir_normal(down_dir)
        return down_dir

    def bing_engine_htmlshell(self, htmls):
        self.com_selenium.remove('.se_div')
        self.com_selenium.remove('.b_footer')
        self.com_selenium.remove('.sidebar')
        self.com_selenium.remove('#b_header')
        self.com_selenium.html('.lf_area', '')
        bing_engine_htmlshell = self.com_selenium.get_html()
        file_name = self.com_file.create_file_name(prefix='bing_html', suffix='.html')
        self.com_file.save(file_name, bing_engine_htmlshell, overwrite=True)
        while len(htmls) > 0:
            html = htmls.pop(0)
            self.com_selenium.before('.lf_area', html)
        result_html = self.com_selenium.get_html()
        file_name = self.com_file.create_file_name(prefix='bing', suffix='.html')
        file_name = self.com_file.save(file_name, result_html, overwrite=True)
        return file_name

    def get_static(self):
        static_folder = self.com_config.get_global("flask_static_folder")
        static_folder = os.path.join(static_folder, 'translate_wave')
        return static_folder

    def translate_from_mdx(self, word, from_is=None, to=None):
        if self.MDX is not None:
            from readmdict import MDX, MDD
            from pyquery import PyQuery as pq
            import pyquery
            self.MDX = MDX
            self.MDD = MDD
            self.pyquery = pyquery
        '''
        # 如果是windows环境，运行提示安装python-lzo，但
        > pip install python-lzo
        报错“please set LZO_DIR to where the lzo source lives” ，则直接从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#_python-lzo 下载 "python_lzo‑1.12‑你的python版本.whl" 
        > pip install xxx.whl 
        装上就行了，免去编译的麻烦
        '''
        mdx_file = "mdx/oxford.mdx"
        # 加载mdx文件
        mdx_dir = self.com_config.get_public(mdx_file)
        filename = mdx_dir
        headwords = [*self.MDX(filename)]  # 单词名列表
        items = [*self.MDX(filename).items()]  # 释义html源码列表
        if len(headwords) == len(items):
            print(f'加载成功：共{len(headwords)}条')
        else:
            print(f'【ERROR】加载失败{len(headwords)}，{len(items)}')

        # 查词，返回单词和html文件
        wordIndex = headwords.index(word.encode())
        query_word, html = items[wordIndex]
        query_word, html = query_word.decode(), html.decode()
        # print(word, html)

        # 从html中提取需要的部分，这里以the litte dict字典为例。到这一步需要根据自己查询的字典html格式，自行调整了。
        doc = self.pyquery(html)
        self.com_file.save(doc)
        coca2 = doc('div[class="coca2"]').text().replace('\n', '')
        print(coca2)
        meaning = doc("""div[class="dcb"]""").text()

    def youdao_engine_us_voice_file(self, sentence):
        if len(sentence) > 1000:
            return None

        youdao_api = f"https://dict.youdao.com/dictvoice?type=0&audio="
        r = requests.get(f'{youdao_api}{sentence}')  # 发送请求
        # 保存
        voiceDownloadDir = self.com_config.get_public("downfile")
        filename = self.com_string.md5(sentence)
        filename = os.path.join(f'{voiceDownloadDir}/{filename}_us.wav')
        with open(f'{filename}', 'wb+') as f:
            f.write(r.content)
            f.close()
            # print(f"[voice_engine_youdao]:{filename}")
            return filename

    def to_voice_youdao(self, word):
        voice_type = "us"
        voice_code = 0
        if voice_type == "us":
            voice_code = 0
        if voice_type == "en":
            voice_code = 1

        youdao_api = f"https://dict.youdao.com/dictvoice?type={voice_code}&audio={word}"
        content = self.com_http.get(youdao_api, to_string=False)
        voiceDownloadDir = self.com_config.get_public("downfile")
        filename = self.com_string.md5(word)
        word_filename = self.com_file.sanitize_filename(word)
        filename = os.path.join(f'{voiceDownloadDir}/{word_filename}_Yd_{filename}.wav')
        with open(f'{filename}', 'wb+') as f:
            f.write(content)
            f.close()
            return filename

    def to_voice_tts(self, word):
        global pyttsx_engine
        if self.com_util.is_windows():
            if pyttsx_engine == None:
                import pyttsx3
                pyttsx_engine = pyttsx3.init()

            if self.__tts_engine == None:
                pyttsx_engine.setProperty('rate', 125)
                voices = pyttsx_engine.getProperty('voices')
                pyttsx_engine.setProperty('voice', voices[1].id)
                self.__tts_engine = pyttsx_engine

            voiceDownloadDir = self.com_config.get_public("downfile")
            filename = self.com_string.md5(word)
            word_filename = self.com_file.sanitize_filename(word)
            filename_path = os.path.join(voiceDownloadDir, f'{word_filename}_tts_{filename}.mp3')
            self.__tts_engine.save_to_file(word, filename_path)
            self.__tts_engine.runAndWait()
            time.sleep(1)
            return filename_path
        else:
            self.com_util.print_warn('Not support Linux.')
            return None

    def encoding_to(self, translate_dir):
        self.com_file.dir_to(translate_dir)
        return translate_dir

    def get_docsentencemd5(self, doc, filetype="doc"):
        exclude_sentence = []
        # if filetype == "srt":
        #     sentence_list = self.com_file.srt(doc)
        # else:
        sentence_list, exclude_sentence = self.analyze_doc_to_sentence(doc)
        sentence = []
        for line in sentence_list:
            if self.sentence_filter(line) == True:
                line = self.sentence_modify(line)
                sentence.append({
                    "sentence": line,
                    "md5": self.com_string.md5(line)
                })
            else:
                if line not in exclude_sentence:
                    exclude_sentence.append(line)
        return sentence, exclude_sentence

    def trim_word_left(self, s):
        form = re.compile(r'^[^curses.pyc-zA-Z]+')
        s = re.sub(form, '', s)
        s = s.strip()
        return s

    def sentence_filter(self, simple):
        # 句子过长
        if len(simple) > 1000:
            return False

        # 含有中文
        if self.com_string.is_chinese(simple) == True:
            return False

        # 清除空格,开头不是字母
        simple = self.trim_word_left(simple)

        # F = 形式清除掉
        form = re.compile(r'^[curses.pyc-zA-Z]*\s+[^0-9a-zA-Z]+\s*')
        while form.search(simple) != None:
            simple = re.sub(form, '', simple)
        #  = Ed. 形式清除掉
        form = re.compile(r'\s*[^0-9a-zA-Z]+\s+[curses.pyc-zA-Z]+[^0-9a-zA-Z]*')
        while form.search(simple) != None:
            simple = re.sub(form, '', simple)

        #  f heb. 形式清除掉
        form = re.compile(r'^\s*[^aAiI]{1}\s+[curses.pyc-zA-Z]+[^0-9a-zA-Z]*$')
        simple = re.sub(form, '', simple)

        # 清除空格,开头不是字母
        simple = self.trim_word_left(simple)

        alphabet = re.compile(r'[curses.pyc-zA-Z]')
        numbers = re.compile(r"\d")
        all_numbers = re.compile(r'^\d+$')
        alph_len = len(alphabet.findall(simple))

        # axx axx axx 形式
        first_alphabets = list(set(re.compile(r'^[curses.pyc-zA-Z]{1}|(?<=\s)[curses.pyc-zA-Z]{1}').findall(simple)))
        for first_alphabet in first_alphabets:
            form = re.compile(
                r'(^|\s)' + first_alphabet + r'[curses.pyc-z]*\s+' + first_alphabet + r'[curses.pyc-z]*\s+' + first_alphabet + r'[curses.pyc-z]*',
                re.IGNORECASE)
            if form.search(simple) != None:
                return False

        # 没有字母,或字母只有1个
        if alph_len <= 1:
            return False

        # 没有空格
        no_space = re.compile(r'\s')
        if len(no_space.findall(simple)) == 0:
            return False

        # 数字与字母比不协调
        num_len = len(numbers.findall(simple))
        if num_len > 0:  # 有数字的情况下进行比较
            rate = (num_len / alph_len) * 100
            # print(f"rate {rate}")
            if rate > 20:
                return False

        #  00. 0. s 形式
        form = re.compile(r'[\d]\.\s')
        if form.search(simple) != None:
            return False

        # xxx !0 xxx形式清除
        words = re.compile(r'[^curses.pyc-zA-Z0-9]+').split(simple)
        words = self.com_util.unique_list(words)
        if len(words) < 4:
            for word in words:
                if all_numbers.search(word) != None:
                    return False
        # 最后返回True
        return True

    def sentence_modify(self, sentence):
        # 00 And 形式
        form = re.compile(r'^\d+\s+(?=[A-Z])')
        if form.search(sentence) != None:
            sentence = re.sub(form, '', sentence)
        # 从开头起有没有闭合的]
        sentence = re.sub(r'^[^]]*\]', '', sentence)
        # 至结尾有没有闭合的[
        sentence = re.sub(r'\[[^[]*$', '', sentence)
        # 在句中有完整闭合的[]
        sentence = re.sub(r'\[[^\]]*\]', '', sentence)
        # 开头不是字母
        sentence = self.trim_word_left(sentence)
        return sentence

    def analyze_doc_to_sentence(self, doc):
        exclude_sentence = []
        p = re.compile(r'\r+')  # 将换行去除,连成完整的句子
        doc = re.sub(p, "", doc)
        p = re.compile(r'\n+')  # 将换行去除,连成完整的句子
        doc = re.sub(p, " ", doc)
        p = re.compile(r'\s+')  # 将多余的空格去除,分格成普通句子
        doc = re.sub(p, " ", doc)

        theComma = re.compile(r"[\,\，]+")
        doc = re.sub(theComma, ",\n", doc)

        theColon = re.compile(r"[\;\；]+")
        doc = re.sub(theColon, ";\n", doc)

        theQuestionMark = re.compile(r"[\?\？]+")
        doc = re.sub(theQuestionMark, "?\n", doc)

        theDatIsNotFloat = re.compile(r"(?<=[^\d])\.(?=[^\d])")
        doc = re.sub(theDatIsNotFloat, ".\n", doc)

        theFullStopAsChinese = re.compile(r"[\。]+")
        doc = re.sub(theFullStopAsChinese, ".\n", doc)

        theShiftLine = re.compile(r"\n+")
        sentence = re.split(theShiftLine, doc)

        new_sentence = []
        for simple in sentence:
            is_add_sentence = False
            if self.sentence_filter(simple) == True:
                simple = self.sentence_modify(simple)
                if simple:
                    is_add_sentence = True
                    new_sentence.append(simple)
            if is_add_sentence == False:
                exclude_sentence.append(simple)
        return new_sentence, exclude_sentence

    def doc_towordlist(self, doc):
        if isinstance(doc, list):
            return doc
        else:
            words, exists_words, exclude_words, word_frequency = self.count_document_words(doc)
            return words

    def not_sentencevoice(self, sentence=[]):
        global threadQueue

        exclude_sentence = []
        if type(sentence) == str: sentence = [sentence]
        sentence = sentence + self.com_db.read(self.com_dbbase.get_tablename("translation_voices"), {
            # "voice": "",
            "md5": "778b96a8168d3574d1dad943f9471db7",
        }, limit=None, select="sentence,md5")
        for i in range(len(sentence)):
            item = sentence[i]
            line = item.get('sentence')
            if self.sentence_filter(line) == True:
                line = self.sentence_modify(line)
                if len(item) > 1:
                    md5 = item.get('md5')
                else:
                    md5 = self.com_string.md5(line)
                sentence[i] = [line, md5]
            else:
                if line not in exclude_sentence:
                    exclude_sentence.append(line)
        return sentence, exclude_sentence

    def sort_word(self, word):
        if word in [None, ""]:
            return ""
        word = self.com_string.sort(word, lower=True, filter="""-+."'""")
        notalphabet = re.compile(r"[^curses.pyc-z]", re.IGNORECASE)
        word = re.sub(notalphabet, "", word)
        return word

    def translate_from_baidu(self, content):
        """
        作废的翻译连接
        :param content:
        :return:
        """
        url = "http://fanyi.baidu.com/sug"
        data = parse.urlencode({"kw": content})  # 将参数进行转码
        headers = {
            'User-Agent': 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10'
        }
        req = request.Request(url, data=bytes(data, encoding="utf-8"), headers=headers)
        r = request.urlopen(req)
        # print(r.code) 查看返回的状态码
        html = r.read().decode('utf-8')
        # json格式化
        html = json.loads(html)
        for k in html["data"]:
            print(k["k"], k["v"])
        return html["data"]

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
        # 主要意思
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
                    # 这是例句
                    if info_type is None:
                        # is generic 类型
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

    def translate_from_youdao(self, word="", from_is='zh', to='en'):
        while True:
            print('欲翻译文本 => %s' % (word))
            if word.strip() == '':
                return None
            data = {
                'q': word,
                'from': to,
                'to': from_is
            }
            print(f'translate_from_youdao : {from_is} to {to}')
            result = self.com_http.post_as_json('https://github.com/visionmedia/debug/issues/797', data)
            errorCode = result['errorCode']
            if errorCode != '0':
                print('出现错误！返回的状态码为：%s' % (errorCode))
                break
            else:
                print(result)
            query = result['query']
            translation = result['translation']

            return translation

    def to_voice(self, sentence, engin="azure"):
        if (engin == "azure"):
            return self.to_voice_azure(sentence)
        elif (engin == "youdao"):
            return self.to_voice_youdao(sentence)
        elif (engin == "youdao_us"):
            return self.youdao_engine_us_voice_file(sentence)
        else:
            self.com_util.print_warn(f"engine not supported")
            return None

    def to_voice_azure(self, sentence="", speed=0.3, voice="en-US-JennyNeural", language="en-US",
                       save_name=None, headless=True):
        if not sentence:
            print(f"Please pass the sentence or word before translation")
            return None

        if save_name == None:
            save_name = self.microsoft_azure_get_voice_file(sentence, speed)
        else:
            save_name = self.com_dictionary.microsoft_azure_voice_download_dir(save_name)
        if self.com_file.isfile(save_name):
            print(f"The audio files already exist, no need to download")
            return save_name
        self.com_selenium.open(
            f'https://azure.microsoft.com/{language.lower()}/products/cognitive-services/text-to-speech',
            not_wait=True, driver_type="chrome", disable_gpu=True, headless=headless)
        # driver = self.com_selenium.is_exists_driver()
        # if driver == False:
        #     self.com_selenium.refresh()
        #     self.com_selenium.open(
        #         f'https://azure.microsoft.com/{language.lower()}/products/cognitive-services/text-to-speech',
        #         not_wait=True, driver_type="edge", disable_gpu=True, headless=headless)
        # else:
        #     driver.refresh()
        time.sleep(1)
        language_selector = f"#languageselect"
        self.com_selenium.find_element_wait(language_selector, deep=False)
        azure_speech_download_js_file = self.com_config.get_libs("azure_speech_download.js")
        azure_speech_download_js = self.com_file.read_file(azure_speech_download_js_file)
        time.sleep(30)
        self.com_selenium.execute_js(azure_speech_download_js)
        self.microsoft_azure_voice_scrolllanguageandselect(language)
        self.microsoft_azure_voice_voiceselect(voice)
        self.microsoft_azure_voice_adjust_speed(speed)
        self.microsoft_azure_voice_fillintext(sentence)
        self.microsoft_azure_voice_play()
        wait_second = 4
        while wait_second > 0 and self.microsoft_azure_voice_is_play(1) == False:
            print("Waiting for voice playback.")
            wait_second -= 1
            time.sleep(0.5)
        if self.microsoft_azure_voice_error():
            print(f"Voice reading is unsuccessful")
            return self.to_voice_azure(language=language, speed=speed, sentence=sentence,
                                       save_name=save_name,
                                       headless=headless)
        else:
            tampermonkey_downloadselector = "#donwloadli button"
            self.com_selenium.click(tampermonkey_downloadselector)
            voice_complete = self.microsoft_azure_voice_downloadcomplete()
            if voice_complete:
                self.com_file.cut(save_name, save_name)
                return save_name
            else:
                print(f"The voice download failed, re -translated.")
                return self.to_voice_azure(language=language, speed=speed, sentence=sentence,
                                           save_name=save_name, headless=headless)

    def read_not_translated(self, engine="bing", condition=None):
        if condition == None:
            condition = {
                f"translate_{engine}": "",
            }
        words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), condition,
                                 limit=None,
                                 select="word",
                                 )
        if type(words) == list:
            words = [self.com_string.decode(word.get('word')) for word in words]
        else:
            words = []
        # sentence_list = self.com_db.read("translation_voices", {
        #     # "voice": "",
        #     "md5": "778b96a8168d3574d1dad943f9471db7",
        # }, limit=None, select="sentence,md5")
        #
        # if type(sentence_list) == list:
        #     for i in range(len(sentence_list)):
        #         sentence = sentence_list[i]
        #         word_sentence = sentence.get('sentence')
        #         sentence_decode = self.com_string.decode(word_sentence)
        #         if len(sentence) > 1:
        #             md5 = sentence.get('md5')
        #         else:
        #             md5 = self.com_string.md5(sentence_decode)
        #         sentence_list[i] = [sentence_decode, md5]
        # else:
        #     sentence_list = []
        # return words + sentence_list
        return words

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

    def correct_translate(self):
        words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {
            'is_delete': 1
        }, limit=None, select="*", read_delete=True)
        restorewords = []
        for word_item in words:
            word = word_item.get('word')
            translate_bing = word_item.get('translate_bing')
            translation = self.com_string.to_json(translate_bing)
            if isinstance(translation, dict):
                if self.is_incorrect_translate(word, translation) == True:
                    restorewords.append(word)
                    continue
        self.com_util.print_info(f"restorewords words :{len(restorewords)},incorrectly.")
        return restorewords

