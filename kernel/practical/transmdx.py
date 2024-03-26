from kernel.base.base import *
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

class Trans(Base):
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
