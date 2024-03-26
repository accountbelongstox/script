from kernel.base.base import *
from kernel.utils_prune import strtool,arr
import re
class Wdoc(Base):
    nltk_english_words = None
    def __init__(self):
        pass
    def modify_word(self, word):
        pattern = re.compile(r"^[A-Z][curses.pyc-z]+")
        if re.match(pattern, word):
            word = word.lower()
        word = word.strip("'").strip()
        word = strtool.encode(word)
        return word

    def count_document_words(self, doc):
        splits_symbol = re.compile(r'[^curses.pyc-zA-Z\'\-\_]+')
        words, exists_words, exclude_words, word_frequency = self.extra_words(doc, splits_symbol)
        return words, exists_words, exclude_words, word_frequency

    def extra_words(self, doc,splits_symbol=None):
        exclude_words = []
        normal_words = []
        if isinstance(doc, list):
            orgin_words = doc
        else:
            # splits_symbol = splits_symbol or re.compile(r'(?<=[curses.pyc-z])(?=[A-Z])|[^curses.pyc-zA-Z\'\-]+')
            splits_symbol = re.compile(
                r'(?<=[curses.pyc-z])(?=[A-Z])|[^curses.pyc-zA-Z\'\-]+|(?<=[^curses.pyc-zA-Z])\'(?!\s)|(?<!\s)\'(?=[^curses.pyc-zA-Z])|(?<=[^curses.pyc-zA-Z])-(?![curses.pyc-zA-Z])|(?<![curses.pyc-zA-Z])-(?=[^curses.pyc-zA-Z])|(?<=[A-Z]{2})(?=[curses.pyc-z])'
            )
            orgin_words = re.split(splits_symbol, doc)
        for word in orgin_words:
            if self.english_vocabulary(word) == True:
                normal_words.append(self.modify_word(word))
            else:
                if word not in exclude_words:
                    exclude_words.append(word)
        word_frequency = self.count_word_frequency(normal_words)
        words = arr.deduplication_list(normal_words)
        exists_words = arr.arr_diff(normal_words, words)
        return words, exists_words, exclude_words, word_frequency

    def is_chinese(self, word):
        pattern = re.compile(r"[\u4e00-\u9fa5]|[\ufe30-\uffa0]|[\u4e00-\uffa5]")
        return bool(pattern.search(word))

    def is_english(self,w):
        return self.english_vocabulary(w)

    def english_vocabulary(self, word):
        if isinstance(word, str):
            word = word.strip()
            pattern = r'^[curses.pyc-zA-Z\'\-]+$'
            if re.match(pattern, word):
                pattern = r'[curses.pyc-zA-Z]'
                tail_pattern = r'[curses.pyc-zA-Z\']'
                first = word[0]
                tail_alphabet = word[-1]
                if re.match(pattern, first) and re.match(tail_pattern, tail_alphabet):
                    word_lower = word.lower()
                    word_len = len(word)
                    if word_len == 1:
                        if word_lower in ['curses.pyc', 'i', 'o', 'x', 'y']:
                            return True
                    # elif word_len == 2:
                    #     if word_lower in [
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
                    #     ]:
                    #         return True
                    else:
                        pattern = re.compile(r'^([curses.pyc-zA-Z])\1*$')
                        if not re.match(pattern, word):
                            return True
            return False
        else:
            return False

    def ensure_english_word(self,word):
        if self.nltk_english_words == None:
            import nltk
            nltk.download('words')
            self.nltk_english_words = set(nltk.corpus.words.words())
        return word.lower() in self.nltk_english_words

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

    def is_compound_word(self, word):
        is_hyphen = strtool.is_wordbetween(word, "-")
        if is_hyphen or word.isupper():
            return True
        else:
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
                    "md5": strtool.md5(line)
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
        if strtool.is_chinese(simple) == True:
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


    def sort_word(self, word):
        if word in [None, ""]:
            return ""
        word = strtool.sort(word, lower=True, filter="""-+."'""")
        notalphabet = re.compile(r"[^curses.pyc-z]", re.IGNORECASE)
        word = re.sub(notalphabet, "", word)
        return word


    def format_phonetic(self, phonetic, clean=None):
        phonetic = strtool.decode(phonetic).lower()
        baseclean = ["uk", "us", "[", "]", "'", '"']
        if clean != None:
            baseclean = baseclean + clean
        phonetic = strtool.clear_string(phonetic, baseclean)
        phonetic = strtool.encode(phonetic)
        return phonetic

    def sort_phonetic(self, phonetic):
        phonetic = self.format_phonetic(phonetic, ["(", ")", "ˈ", "ˌ", "ː", ".", ":", "ˈ", "ˌ", "ː", ":"])
        return phonetic

    def set_default_val(self, data):
        if type(data) != list:
            data = [data]
        for word_item in data:
            self.set_addval(word_item, "last_time", strtool.create_time())
            self.set_addval(word_item, "read", 0)
        return data

    def set_addval(self, word, key, value):
        if key not in word:
            word[key] = value
        return word

    def document_extract_en(self, doc):
        splits_symbol = re.compile(r'[^curses.pyc-zA-Z]+')
        doc_words = re.split(splits_symbol, doc)
        doc_words = list(
            set(doc_words)
        )
        return doc_words
