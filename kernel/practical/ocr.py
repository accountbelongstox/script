# import pytesseract
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from PIL import Image
# from paddleocr import PaddleOCR, draw_ocr
from pycore.utils import file
# from urllib.parse import urlparse
import os
import sys
import time
# from paddleocr import PaddleOCR, draw_ocr
# from urllib.parse import urlparse

class Ocr:
    enocr = None
    zhocr = None
    def __init__(self):
        pass
    # def find_str_by_img(self, image_url, lang):
    #     im = Image.open(image_url)
    #     im = im.convert('L')
    #     im_str = pytesseract.image_to_string(im, lang=lang)
    #     return im_str
    #
    # def find_str_by_img_use_paddleorc(self, img_path, lang="chi_sim"):  # lang='chi_sim'# lang eng
    #     # unbuntu
    #     # sudo apt-get install tesseract-ocr
    #     # export PATH=$PATH:/usr/local/bin/tesseract
    #     image_path = os.path.join(os.getcwd(), img_path)
    #     text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
    #     return text

    def get_ocr(self,lang="en"):
        from paddleocr import PaddleOCR, draw_ocr
        if lang == "en":
            if self.enocr == None:
                self.enocr = PaddleOCR(use_angle_cls=True, lang=lang)
            return self.enocr
        if lang == "zh":
            if self.zhocr == None:
                self.zhocr = PaddleOCR(use_angle_cls=True, lang=lang)
            return self.zhocr

    def is_text(self, img_path, target_text):
        recognized_texts = self.recognize_texts(img_path)
        target_text_lower = target_text.lower()
        return any(target_text_lower in text.lower() for text in recognized_texts)

    def recognize_texts(self, img_path,lang="en"):
        from paddleocr import PaddleOCR, draw_ocr
        ocr = self.get_ocr(lang=lang)
        result = ocr.ocr(img_path, cls=True)
        texts = []
        for idx, res in enumerate(result):
            print(f"Page {idx + 1}:")
            for line in res:
                box, (text, confidence) = line
                texts.append(text)
                print(f"Bounding Box: {box}, Text: {text}, Confidence: {confidence}")
            print("\n")
            image = Image.open(img_path).convert('RGB')
            boxes = [line[0] for line in res]
            txts = [line[1][0] for line in res]
            scores = [line[1][1] for line in res]
            current_time = time.time()
            result_img = self.resolve_path(f'result_page_{idx + 1}_{current_time}.jpg',"out/recognize")
            im_show = draw_ocr(image, boxes, txts, scores)
            im_show = Image.fromarray(im_show)
            file.mkbasedir(result_img)
            im_show.save(result_img)
        return texts

    def recognize(self, img_path,lang="en"):
        result = self.ocr.ocr(img_path, cls=True)
        recognized_texts = []
        for idx, res in enumerate(result):
            page_texts = []
            for line in res:
                box, (text, confidence) = line
                page_texts.append({
                    'text': text,
                    'confidence': confidence,
                    'bounding_box': box
                })
                print(f"Bounding Box: {box}, Text: {text}, Confidence: {confidence}")
            recognized_texts.append(page_texts)
            print("\n")
            image = Image.open(img_path).convert('RGB')
            boxes = [line[0] for line in res]
            txts = [line[1][0] for line in res]
            scores = [line[1][1] for line in res]
            current_time = time.time()
            result_img = self.resolve_path(f'result_page_{idx + 1}_{current_time}.jpg', "out/recognize")
            im_show = draw_ocr(image, boxes, txts, scores)
            im_show = Image.fromarray(im_show)
            im_show.save(result_img)
        return recognized_texts

    def resolve_path(self, path, relative_path=None,resolve=True):
        if resolve == False:
            return path
        if not os.path.isabs(path):
            if os.path.exists(path):
                return path
            root_path = self.get_root_dir()
            if relative_path != None:
                root_path = os.path.join(root_path, relative_path)
            path = os.path.join(root_path, path)
        return path
    def get_root_dir(self):
        main_file_path = os.path.abspath(sys.argv[0])
        root_path = os.path.dirname(main_file_path)
        return root_path
    #
    # def recognize_chinese_text(self, image_path):
    #     result = ocr.ocr(image_path, cls=True, lang='ch')
    #     chinese_texts = [word_info[-1] for line in result for word_info in line]
    #     return chinese_texts
    #
    # def recognize_english_text(self, image_path):
    #     result = ocr.ocr(image_path, cls=True, lang='en')
    #     english_texts = [word_info[-1] for line in result for word_info in line]
    #     return english_texts