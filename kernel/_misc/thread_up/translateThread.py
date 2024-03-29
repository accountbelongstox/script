from pycore.base.base import *
import os
import re
import time
import threading

global_thread = {}


class TranslateThread(threading.Thread, Base):
    __info = True
    __count = 0
    __save_db = False
    __language = "zh-CN"
    __headless = True
    __debug = False
    __type = "translate"  # "voice
    __tick = 0
    __db = None
    __allow_executeintervalcallback = False
    callback = None
    __pre_surplus_awaittranswords = 0

    def __init__(self, args, group_queue=None, public_queue=None, thread_id=None, thread_name=None, daemon=False):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.task = args.get('task')
        self.result = args.get('result')
        self.thread_lock = args.get('thread_lock')
        if type(args) == dict:
            if "save_db" in args:
                self.__save_db = args["save_db"]
            if "type" in args:
                self.__type = args["type"]
            if "info" in args:
                self.__info = args["info"]
            if "language" in args:
                self.__language = args["language"]
            if "headless" in args:
                self.__headless = args["headless"]
            if "debug" in args:
                self.__debug = args["debug"]
            if "callback" in args:
                self.callback = args["callback"]
        self.thread_name = thread_name

    def main(self):
        pass

    def run(self):
        url = f'https://www.bing.com/dict?mkt={self.__language}'
        self.com_selenium.open(url, width=600, height=400, mobile=False, not_wait=True, headless=self.__headless,
                               wait=1200000)
        self.com_selenium.find_element_by_js_wait("#sb_form_q")
        thread_normal_sleep = 60
        thread_daily_sleep = 120
        while True:
            # 定时更新数据库
            worditem = self.get_itemandupdate()
            if worditem == None:
                time_now = self.com_util.create_time()
                # self.com_util.print_info(
                #     f"translate Thread {time_now} sleep {thread_normal_sleep} and tick:{self.__tick} 1_update.sh.")
                time.sleep(thread_normal_sleep)
            if type(worditem) == str:
                self.translate_word(worditem)
            elif type(worditem) == dict:
                self.update_wordvoice(worditem)
            elif type(worditem) in [list]:
                self.trans_tovoice(worditem)
            self.com_selenium.close_page()

    def translate_word(self, worditem):
        word = worditem.strip()
        qsize = self.task.qsize()
        self.com_util.print_info(f"task: {qsize},thread-id:{self.__thread_id}, word: {word} ")
        self.com_selenium.send_keys('#sb_form_q', word)
        self.com_selenium.click('#sb_form_go')
        time.sleep(0.2)
        word_trans = self.bing_engine_htmlextracttojson(word=word, debug=self.__debug)
        if self.__save_db:
            if word_trans.get("trans_status") == False or self.com_translate.is_onlywebtrans_and_noother(word,
                                                                                                         word_trans) == True:
                if word_trans.get("trans_status") == False:
                    trans_type = word_trans.get('trans_type')
                    self.com_util.print_warn(f"delete : {word} because trans_type ${trans_type}")
                elif self.com_translate.is_onlywebtrans_and_noother(word, word_trans) == True:
                    self.com_util.print_warn(
                        f"delete : {word} because is only web trans-result, and no some images,and no a native voice.")
                self.com_dictionary.delete_word(word, info=False)
            else:
                # 翻译成功则添加第三方音频
                word_trans = self.com_translate.add_third_voice(word, word_trans)
                self.com_util.print_info(f"\t{word} trans-successful,also {qsize} words that are not translated.")
                self.com_dictionary.update_word(word, {
                    "word_sort": self.com_translate.sort_word(word),
                    "translate_bing": word_trans
                })
            if qsize == 0:
                if self.__pre_surplus_awaittranswords > 0:
                    self.com_util.print_info(f"translate Queue success,sync words to dictionary map.")
                    self.com_dictionary.syncwordtomap()
            self.__pre_surplus_awaittranswords = qsize
        if self.callback != None:
            self.callback(word, word_trans)

    def trans_tovoice(self, worditem):
        speeds = [0.1, 0.5, 1.0]
        voice = {}
        sentence = worditem[0]
        md5 = worditem[1]
        # 语音获取
        for speed in speeds:
            save_name = f"{md5}-{speed}"
            voice_file = self.microsoft_azure_to_voice(sentence, speed=speed, save_name=save_name,
                                                       headless=self.__headless)
            voice[f"{speed}"] = voice_file

    def update_wordvoice(self, worditem):
        revolve_type = worditem.get('type')
        if revolve_type == "add_voice":
            word = worditem.get('word').strip()
            self.translate_word(word)

    def get_item(self):
        qsize = self.task.qsize()
        if qsize > 0:
            self.thread_lock.acquire()
            item = self.task.get()
            self.thread_lock.release()
            return item
        return None

    def get_itemandupdate(self):
        thread_message = self.receive_message()
        tick = thread_message.get('tick')
        if tick == None:
            tick = 1
        else:
            tick += 1
        self.__tick += 1
        self.send_message('tick', tick)

        worditem = self.get_item()
        tick_interval = 60 * 10

        remain = tick % tick_interval
        updatetranslateable = remain == 0
        if updatetranslateable:
            self.com_util.print_info(f'thread pool interval; True.')
            self.__allow_executeintervalcallback = updatetranslateable
        # else:
        #     self.com_util.print_info(f'thread pool interval; remain: {tick_interval - remain}')  # 每10分钟执行一次

        if worditem == None:
            if self.__tick % 2 == 0:
                self.com_translate.not_sentencevoice()
            else:
                self.com_translate.not_translatedtoqueue()
            worditem = self.get_item()
            if worditem == None:
                if self.__allow_executeintervalcallback:
                    self.__allow_executeintervalcallback = False
                    self.com_dictionary.update_translate()
                    worditem = self.get_item()

        return worditem

    def send_message(self, key, value, tid=None):
        group_queue = self.__group_queue
        if group_queue.qsize() == 0:
            message = {
                key: value
            }
            self.__group_queue.put(message)
        else:
            message = group_queue.get()
            message[key] = value
            self.__group_queue.put(message)

    def receive_message(self):
        group_queue = self.__group_queue
        if group_queue.qsize() == 0:
            message = {
            }
        else:
            message = group_queue.get()
        return message

    def qsize(self):
        return self.task.qsize()

    def update_taskqueue(self, worditem=None):
        if worditem == None:
            self.com_translate.not_translatedtoqueue()

    def is_computertranslate(self):
        computer_translate = self.com_selenium.find_element_by_js(".lf_area .smt_hw")
        return computer_translate

    def is_noresult(self):
        no_result = self.com_selenium.find_element_by_js(".no_results")
        return no_result

    def is_translation(self):
        strong = self.com_selenium.find_element_by_js(".hd_div strong")
        return strong

    def translate_type(self, wait_max=30):
        index = 0
        while index < wait_max:
            computer_translate = self.is_computertranslate()
            no_result = self.is_noresult()
            translation = self.is_translation()
            if no_result != None or index >= wait_max:
                return "no_result"
            if computer_translate != None:
                return "computer_translate"
            if translation != None:
                return "translation"
            time.sleep(1)

    def run_microsoftvoice(self):
        self.microsoft_azure_to_voice()

    def bing_engine_word(self, debug=False):
        word = self.com_selenium.find_value_by_js_wait('.hd_div strong', )
        if debug: self.com_util.pprint(f"{word}")
        return word

    def bing_engine_wrodtranslation(self, debug=False):
        word_translation = self.com_selenium.find_text_content_list('.qdef .hd_area', "", ".nextSibling.childNodes",
                                                                    html_split=True)
        if debug: self.com_util.pprint(f"\tword_translation {word_translation}")
        return word_translation

    def bing_engine_htmlextracttojson(self, word, debug=True):
        # trans_area = ".lf_area"
        translate_type = self.translate_type(wait_max=120)
        word_trans = {}

        if translate_type in ["no_result", "computer_translate"]:
            self.com_util.print_warn(f"\t{word} translate_type:{translate_type}")
            result = {
                "trans_status": False,
                "trans_type": translate_type,
            }
            return result

        word_trans["word"] = self.bing_engine_word(debug)
        word_trans["word_translation"] = self.bing_engine_wrodtranslation(debug)
        try:
            phonetics = self.com_selenium.find_html_by_js('.hd_area [lang]')
        except Exception as e:
            self.com_util.print_warn(f"\t{word} not found phonetic")
            self.com_util.print_warn(e)
            phonetics = None

        word_trans["phonetic_symbol"] = {
            "phonetic_us": None,
            "phonetic_us_sort": None,
            "phonetic_us_length": 0,
            "phonetic_uk": None,
            "phonetic_uk_sort": None,
            "phonetic_uk_length": 0,
        }
        if phonetics != None:
            temporary_separator = " -=- "
            pattern = re.compile(r"(?<=\]).+?(?=http)")
            phonetics = re.split(pattern, phonetics)
            phonetics = temporary_separator.join(phonetics)
            pattern = re.compile(r"(?<=mp3).+?>")
            phonetics = re.split(pattern, phonetics)
            phonetics = temporary_separator.join(phonetics)
            pattern = re.compile(r"<.+?>")
            phonetics = re.split(pattern, phonetics)
            phonetics = temporary_separator.join(phonetics)
            phonetics = phonetics.split(temporary_separator)
            phonetics = self.com_util.clear_value(phonetics)
            phonetic_dict = {}
            voices_srclist = []
            pre_phonetic = None
            for i in range(len(phonetics)):
                phonetic = phonetics[i]
                if self.com_http.is_url(phonetic) == False:
                    pre_phonetic = phonetic
                else:
                    phonetic_dict[phonetic] = {
                        "url": phonetic,
                        "phonetic": pre_phonetic
                    }
                    pre_phonetic = self.com_translate.format_phonetic(pre_phonetic)
                    phonetic_sort = self.com_translate.sort_phonetic(pre_phonetic)
                    phonetic_length = len(phonetic_sort)
                    if word_trans["phonetic_symbol"]["phonetic_us"] == None:
                        word_trans["phonetic_symbol"]["phonetic_us"] = pre_phonetic
                        word_trans["phonetic_symbol"]["phonetic_us_sort"] = phonetic_sort
                        word_trans["phonetic_symbol"]["phonetic_us_length"] = phonetic_length
                    else:
                        word_trans["phonetic_symbol"]["phonetic_uk"] = pre_phonetic
                        word_trans["phonetic_symbol"]["phonetic_uk_sort"] = phonetic_sort
                        word_trans["phonetic_symbol"]["phonetic_uk_length"] = phonetic_length
                    voices_srclist.append(phonetic)
        else:
            voices_srclist = []
            phonetic_dict = {}

        word_trans["is_native_voice"] = False
        voice_files = {}
        if len(voices_srclist) > 0:
            word_trans["is_native_voice"] = True
            for down_url in voices_srclist:
                download = self.com_selenium.down_file_inline(down_url)
                download = self.get_downs_staticfiles(word, download, file_iterate=phonetic_dict, file_type="voice")
                voice_files[down_url] = download
        word_trans["voice_files"] = voice_files
        word_trans["plural_form"] = self.com_selenium.find_text_content_list(".qdef .hd_if", "", html_split=True, )
        sample_image = self.com_selenium.find_text_content_list(".qdef .simg", "img", attribute="src")
        downs = {}
        down_image_index = 0
        if len(sample_image) > 0:
            for down_url in sample_image:
                download = self.com_selenium.down_file_inline(down_url)
                download = self.get_downs_staticfiles(word, download, file_type="images", index=down_image_index)
                down_image_index += 1
                downs[down_url] = download

        word_trans["sample_images"] = downs
        word_trans["synonyms_type"] = self.com_selenium.find_text_content_list('.wd_div .tb_div h2',
                                                                               deduplication=False)
        word_trans["synonyms"] = self.com_selenium.find_text_content_list('.wd_div .tb_div', "",
                                                                          ".nextSibling.childNodes", html_split=True,
                                                                          deduplication=False)
        word_trans["advanced_translate_type"] = self.com_selenium.find_text_content_list('.df_div .tb_div h2',
                                                                                         deduplication=False)
        word_trans["advanced_translate"] = self.com_selenium.find_text_content_list('.df_div .tb_div', "",
                                                                                    ".nextSibling.childNodes",
                                                                                    html_split=True,
                                                                                    deduplication=False)
        return word_trans

    def get_downs_staticfiles(self, word, downitem, file_iterate=None, file_type="voice", index=""):
        url = downitem.get('url')
        down_file = downitem.get("save_filename")
        if not down_file:
            return downitem
        file_ext = self.com_file.get_ext(down_file)
        file_iterate_name = self.com_util.get_dict_value(file_iterate, url, "")
        if 'phonetic' in file_iterate_name:
            file_iterate_name = file_iterate_name['phonetic']
            downitem["iterate_name"] = file_iterate_name
        file_iterate_name = re.sub(re.compile(r"\&.+$"), "", file_iterate_name)
        if index != "" and file_iterate_name == "":
            file_iterate_name = str(index)
        static_file = self.com_translate.bing_engine_get_static_file(word, index=file_iterate_name, file_ext=file_ext,
                                                                     file_type=file_type)
        try:
            self.com_file.cut(down_file, static_file)
        except Exception as e:
            self.com_util.print_warn("downitem")
            self.com_util.print_warn(downitem)
            self.com_util.print_warn(f"static_file {static_file}")
            self.com_util.print_warn(f"{word} downs_statistics error")
            self.com_util.print_warn(e)
        static_folder = self.com_config.get_global("flask_template_folder")
        static_folder = self.com_string.dir_normal(static_folder, linux=True)
        static_file = self.com_string.dir_normal(static_file, linux=True)
        save_name = static_file.split(static_folder)[1]
        save_name = self.com_string.dir_normal(save_name, linux=True)
        downitem["save_filename"] = save_name
        return downitem

    def microsoft_azure_to_voice(self, sentence="", speed=0.3, voice="en-US-JennyNeural", language="en-US",
                                 save_name=None, headless=True):
        if not sentence:
            print(f"Please pass the sentence or word before translation")
            return None

        if save_name == None:
            save_name = self.microsoft_azure_get_voice_file(sentence, speed)
        else:
            save_name = self.com_translate.microsoft_azure_voice_download_dir(save_name)
        if self.com_file.isfile(save_name):
            print(f"The audio files already exist, no need to download")
        return save_name
        self.com_selenium.open(
            f'https://azure.microsoft.com/{language.lower()}/products/cognitive-services/text-to-speech',
            not_wait=True, driver_type="edge", disable_gpu=True, headless=headless)
        # driver = self.com_selenium.is_exists_driver()
        # if driver == False:
        #     self.com_selenium.refresh()
        #     self.com_selenium.open(
        #         f'https://azure.microsoft.com/{language.lower()}/products/cognitive-services/text-to-speech',
        #         not_wait=True, driver_type="edge", disable_gpu=True, headless=headless)
        # else:
        #     driver.refresh()
        time.sleep(1)
        azure_speech_download_js_file = self.com_config.get_libs("azure_speech_download.js")
        azure_speech_download_js = self.com_file.read_file(azure_speech_download_js_file)
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
            return self.microsoft_azure_to_voice(language=language, speed=speed, sentence=sentence, save_name=save_name,
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
                return self.microsoft_azure_to_voice(language=language, speed=speed, sentence=sentence,
                                                     save_name=save_name, headless=headless)

    def microsoft_azure_voice_play(self):
        self.com_selenium.click("#playbtn")

    def microsoft_azure_voice_is_play(self, wait_second=3):
        play_show = self.com_selenium.is_show("#playbtn")
        time.sleep(wait_second)
        error = self.microsoft_azure_voice_error()
        if not play_show and not error:
            return True
        else:
            return False

    def microsoft_azure_voice_error(self):
        ##ttsstatus 加载此演示时发生错误，请重载并重试
        error_selector = "#ttsstatus"
        err_info = self.com_selenium.find_text_content_by_js(error_selector)
        err_info = err_info.find("error")
        if err_info == -1:
            return False
        else:
            return True

    def microsoft_azure_voice_fillintext(self, sentence=""):
        selector = f"#ttstext"
        textarea = self.com_selenium.find_element(selector)
        textarea.click()
        textarea.clear()
        textarea.send_keys(sentence)

    def microsoft_azure_voice_scrolllanguageandselect(self, language="en-US"):
        language_selector = f"#languageselect"
        offset_top = self.com_selenium.offset_scrolltowindow(language_selector)
        offset_top = offset_top + self.com_string.random_num(0, 100)
        self.com_selenium.scroll_to(0, offset_top)
        self.com_selenium.select_wait(language_selector, language)

    def microsoft_azure_voice_voiceselect(self, voice):
        language_selector = f"#voiceselect"
        self.com_selenium.select_wait(language_selector, voice)

    def microsoft_azure_voice_adjust_speed(self, speed=0.3):
        speed_selector = "#speed"
        offset_top = self.com_selenium.offset_towindow(speed_selector)
        offset_left = self.com_selenium.offset_left(speed_selector)
        element_width = self.com_selenium.element_width(speed_selector)
        element_height = self.com_selenium.element_height(speed_selector)
        speed = speed / 2  # 因为宽度是2倍的从中间切开
        # speed_pix = element_width / 300
        x = offset_left + element_width * speed
        y = (element_height / 1.5) + offset_top
        self.com_selenium.screen_click(x, y)

    def microsoft_azure_voice_downloadcomplete(self, ):
        optiondiv_selector = "#optiondiv"
        process_reg = re.compile("[^0-9\.]+")
        pre_process = None
        process_count = 0

        def process_query():
            global pre_process
            global process_count
            process_selector = f"document.querySelector(`{optiondiv_selector}`).nextSibling.nextSibling.innerHTML"
            process_html = self.com_selenium.execute_js_code(process_selector)
            process_html = re.sub(process_reg, "", process_html)
            process = float(process_html)
            if process != pre_process:
                pre_process = process
                process_count = 0
                return True
            else:
                process_count += 1
                return False

        complete = f"return document.querySelector(`{optiondiv_selector}`).nextSibling.innerHTML"
        max_wait = 50
        no_process_second = 20
        wait = 0

        complete_html = self.com_selenium.execute_js_wait(complete, deep=10)
        if not complete_html:
            print(f"I did not start downloading.")
            return False

        complete_reg = re.compile(r"(complete|\u5b8c\u6210)")
        # 如果10秒没有进展及没有查找到complete则停止
        while len(re.findall(complete_reg, self.com_selenium.execute_js_wait(complete,
                                                                             deep=10))) > 0 and wait < max_wait and process_count < no_process_second:
            print(f"Waiting for voice download has been waiting for {wait / 2} seconds")
            wait += 1
            process_query()
            time.sleep(0.5)
        if process_count >= no_process_second:
            print(f"No progress in {no_process_second / 2} seconds")
            return False
        if wait >= max_wait:
            print(f"Waiting for {wait / 2} timeout")
            return False
        else:
            return True

    def microsoft_azure_voice_extract_voicefile(self):
        download_dir = self.com_translate.microsoft_azure_voice_download_dir()
        index = 0
        timeout_second = 50
        while len(os.listdir(download_dir)) == 0 and index < timeout_second:
            print(f"Wait for the audio to download")
            time.sleep(1)
            index += 1
        if index >= timeout_second:
            print(f"Timeout download unfinished {index} second")
            return None
        download_file = os.listdir(download_dir)
        file = download_file[0]
        file = os.path.join(download_dir, file)
        file = self.com_file.rename_remove_space(file)
        return file

    def microsoft_azure_voice_close(self):
        self.com_selenium.quit()

    def microsoft_azure_get_voice_file(self, sentence, speed, file_suffix=".mp3"):
        static_file = f"{self.com_string.md5(sentence)}_speed_{speed}{file_suffix}"
        static_file = self.com_translate.microsoft_azure_voice_download_dir(static_file)
        return static_file

    def done(self):
        if self.task.qsize() == 0:
            return True
        else:
            return False

    def result(self):
        self.__count = 0
        result = self.resultList
        self.resultList = []
        return result
