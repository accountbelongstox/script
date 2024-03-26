import html
import json
import base64
from cryptography.fernet import Fernet
# import xml.dom.minidom
import random
import string
import re
import time
import hashlib
# import sys
# from turtle import width
import cv2
# from PIL import Image
import numpy as np
import zlib
from datetime import datetime, date, time as datatime_time

class Img():

    def img_to_text(self, img_fname, save_fname=None):
        img = cv2.imread(img_fname)
        height, width, _ = img.shape
        text_list = []
        for h in range(height):
            for w in range(width):
                R, G, B = img[h, w]
                if R | G | B == 0:
                    break
                idx = (G << 8) + B
                text_list.append(chr(idx))
        content = "".join(text_list)
        if save_fname == None:
            save_fname = self.file_suffix(img_fname, "txt")
            self.com_util.print_info(f"text to image at {save_fname}")
        # self.com_file.save(content,save_fname)

    def text_to_img(self, txt_fname, save_fname=None):
        content = self.com_file.read(txt_fname)
        text_len = len(content)
        img_w = 1000
        img_h = 1680
        img = np.zeros((img_h, img_w, 3))
        x = 0
        y = 0
        for each_text in content:
            idx = ord(each_text)
            rgb = (0, (idx & 0xFF00) >> 8, idx & 0xFF)
            img[y, x] = rgb
            if x == img_w - 1:
                x = 0
                y += 1
            else:
                x += 1
        if save_fname == None:
            save_fname = self.file_suffix(txt_fname, "jpg")
            self.com_util.print_info(f"text to image at {save_fname}")
        cv2.imwrite(save_fname, img)
