from pycore.base import *
import time
import math
from queue import Queue
# import asyncio
import os
import re
import json
import requests
from urllib import request, parse
import googletrans
from googletrans import Translator
# import azure.cognitiveservices.speech as speechsdk

threadQueue = Queue()
threadAddVoiceQueue = Queue()

pyttsx_engine = None

googletanslator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.com.hk',
    # 'translate.google.cn',
])

class BingDict(Base):
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

    def is_transincludeimages(self, translation):
        sample_images = translation.get('sample_images')
        if isinstance(sample_images, dict):
            if len(sample_images.keys()) > 0:
                return True
        return False

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

    def get_trans_val(self, put_word, file_val):
        if file_val == None:
            return put_word
        for key, val in file_val.items():
            save_filename = val.get('save_filename')
            full_filename = self.com_file.get_template_dir(save_filename, fulllink=True)
            put_word[save_filename] = self.com_file.read_file_bytes(full_filename)
        return put_word
