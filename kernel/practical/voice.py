from kernel.base.base import *
import time
from queue import Queue
# import math
# from queue import Queue
# import asyncio
import os
# import re
# import json
import requests
# from urllib import request, parse
# import googletrans
# from googletrans import Translator
# import azure.cognitiveservices.speech as speechsdk
threadAddVoiceQueue = Queue()

class Voice(Base):
    def delete_redundantvoicefiles(self,redundant_voicefiles):
        index = 0
        for file in redundant_voicefiles:
            file_name = self.bing_engine_voice_static_dir(file_type="voice",file_name=file)
            redundant_voice = self.bing_engine_voice_static_dir(file_type="redundant_voice",file_name=file)
            self.com_file.cut(file_name,redundant_voice)
            if index % 10000 == 0 and index > 0:
                self.com_util.print_info(f"delete  redundant voice file({index}): {file_name}.")
            index += 1


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

    def is_third_voice(self, translation):
        voice_files = translation.get('voice_files')
        if voice_files == None:
            return False
        for key in voice_files.keys():
            if key in self.__third_voice_names:
                if isinstance(voice_files.get(key), dict):
                    return True
        return False


    def include_native_voice(self, translation):
        voice_files = translation.get('voice_files')
        if voice_files == None:
            return False
        native_voice = []
        for key in voice_files.keys():
            if key not in self.__third_voice_names and key not in self.__obsolete_third_voice_names:
                native_voice.append(key)
        return len(native_voice) > 0

    def bing_engine_voice_static_dir(self, file_type="voice",file_name=''):
        static_folder = self.get_static()
        down_dir = self.load_module.get_control_dir(f"{static_folder}/bing/{file_type}")
        if file_name != "":
            down_dir = os.path.join(down_dir,file_name)
            down_dir = self.com_string.dir_normal(down_dir)
        return down_dir

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