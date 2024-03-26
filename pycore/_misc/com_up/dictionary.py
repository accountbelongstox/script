from pycore._base import *
import os
import re


class Dictionary(Base):
    __loadlocalgroup = None

    def __init__(self, args):
        pass

    def main(self, args):
        pass

    def start_threadtranslate(self, words=None, wait=False, condition=None, debug=False, headless=True, save_db=True,
                              callback=None, put_remote=False, max_thread=4):
        notTranslateWords = self.com_graphql.queryNotTranslate()
        if put_remote == True:
            callback = self.put_remoteword
        if self.__loadlocalgroup == None:
            self.__loadlocalgroup = True
            self.load_localgroups()
            self.update_translate()
        self.com_translate.start_translate_thread(words=words, condition=condition, wait=wait, save_db=save_db,
                                                  headless=headless,
                                                  debug=debug,
                                                  callback=callback, max_thread=max_thread)

    def load_localgroups(self, user=None):
        translate_dir = self.com_config.get_public('translate_file')
        if not self.com_file.isdir(translate_dir):
            self.com_file.mkdir(translate_dir)
        translate_types = os.listdir(translate_dir)
        word_acount = {
            'loaded': 0,
            'info': [],
        }
        groups = self.com_db.read("translation_group", {})
        for file in translate_types:
            file = os.path.join(translate_dir, file)
            if self.com_file.isfile(file):
                file = self.com_file.rename_remove_space(file)
                t_group = os.path.basename(file)
                if self.is_group(t_group, groups) == False:
                    self.com_util.print_info(f"add group {t_group}.")
                    file_type = self.com_file.get_suffix(file)
                    file_content = self.com_file.read_file(file)
                    result = self.put_group(None, file_content, t_group=t_group, user_id=0, file_type=file_type,
                                            start_thread=False)

                    word_acount['info'].append(f"group: {t_group} - {result}")
                else:
                    self.com_util.print_info(f"group {t_group} exists.")
        result = self.com_util.print_result(data=word_acount)
        return result

    def add_word(self, words):
        wordmap = self.get_wordmap()
        if not wordmap:
            wordmap = self.syncwordtomap()

        ids_text = wordmap.get('wordids')
        words_text = wordmap.get('words')
        words_list = words_text.split(",")

        language = "en"
        en_words = self.com_translate.doc_towordlist(words)
        words_set = set(words_list)
        not_exist = set(en_words) - words_set
        not_existwords = list(not_exist)

        if len(not_existwords) > 0:
            self.com_util.print_info(f'save {len(not_existwords)} words')
            save_words = []
            for word in not_existwords:
                save_words.append({
                    "language": language,
                    "word": word,
                    "word_sort": self.com_translate.sort_word(word),
                    "word_length": len(word),
                })
            count = 0
            tabname = self.com_dbbase.get_tablename("translation_dictionary")

            save_ids = {}
            for word in save_words:
                save_id = self.com_db.save(tabname, word)
                if save_id and len(save_id) > 0:
                    count += 1
                    save_ids[word.get("word")] = save_id[0]

            self.com_util.print_info(f"A total of {count} words are saved to the database.")

            ids_list = ids_text.split(",")
            orgin_idslen = len(ids_list)
            for save_success_word, save_success_id in save_ids.items():
                if save_success_id not in ids_list:
                    ids_list.append(str(save_success_id))
                    words_list.append(save_success_word)
            add_idslen = len(ids_list)
            if orgin_idslen != add_idslen:
                idsText = ",".join(ids_list)
                wordText = ",".join(words_list)
                save_wordmap = {
                    "wordids": idsText,
                    "words": wordText,
                    "ids_count": len(ids_list),
                    "words_count": len(words_list),
                    "count": len(ids_list),
                }
                self.syncwordtomap()
                self.set_wordmap(save_wordmap)

    def get_wordmap(self):
        dictionarymap = self.com_dbbase.get_tablename("translation_dictionarymap")
        maps = self.com_db.read(dictionarymap, limit=(0, 1), result_object=True)
        if len(maps) > 0:
            return maps[0]
        else:
            return None

    def set_wordmap(self, save_wordmap, maps=None):
        dictionarymap = self.com_dbbase.get_tablename("translation_dictionarymap")
        if not maps:
            maps = self.get_wordmap()
        ids_count = save_wordmap.get('ids_count')
        words_count = save_wordmap.get('words_count')
        count = save_wordmap.get('count')
        if None in [ids_count, words_count, count]:
            if ids_count == None or count == None:
                wordids = save_wordmap.get('wordids')
                wordids = wordids.split(',')
                save_wordmap["ids_count"] = len(wordids)
                save_wordmap["count"] = len(wordids)
            if words_count == None:
                words = save_wordmap.get('words')
                words = words.split(',')
                save_wordmap["words_count"] = len(words)
        if isinstance(maps, list) and len(maps) == 0:
            ids = self.com_db.save(dictionarymap, save_wordmap)
        else:
            ids = self.com_db.update(dictionarymap, save_wordmap, {
                "id": 1,
            })
        return ids

    def syncwordtomap(self):
        dictionary = self.com_dbbase.get_tablename("translation_dictionary")
        dictionarymap = self.com_dbbase.get_tablename("translation_dictionarymap")
        c = self.com_db.count(dictionary)
        maps = self.com_db.read(dictionarymap, limit=(0, 1), result_object=True)
        if len(maps) > 0:
            read_item = maps[0]
            result = maps[0]
            read_ids = read_item.get('wordids')
            before_ids = read_ids.split(",")
        else:
            before_ids = maps
        if len(before_ids) != c:
            dictionary = self.com_db.read(dictionary, select="id,word", limit=None)
            ids = []  # []#
            words_list = []
            for item in dictionary:
                ids.append(item.get('id'))
                words_list.append(item.get('word'))
            ids_list = [str(item) for item in ids]
            idsText = ",".join(ids_list)
            wordText = ",".join(words_list)
            save_wordmap = {
                "wordids": idsText,
                "words": wordText,
                "ids_count": len(ids_list),
                "words_count": len(words_list),
                "count": len(ids_list),
            }
            self.com_util.print_info(f"syncwordtomap ids: {len(ids_list)} words: {len(words_list)}")
            if len(maps) == 0:
                self.com_db.save(dictionarymap, save_wordmap)
            else:
                self.com_db.update(dictionarymap, save_wordmap, {
                    "id": 1,
                })
            result = save_wordmap
        else:
            result = result
        return result

    def update_word(self, word, update, not_execute=False):
        update["is_delete"] = 0
        update["last_time"] = self.com_string.create_time()
        phonetic_symbol_key = "phonetic_symbol"
        if phonetic_symbol_key in update:
            phonetic_symbol = update[phonetic_symbol_key]
            keys = ["phonetic_us", "phonetic_us_sort", "phonetic_us_length", "phonetic_uk", "phonetic_uk_sort",
                    "phonetic_uk_length"]
            for key in keys:
                if update.get(key) == None and key in phonetic_symbol:
                    update[key] = phonetic_symbol[key]

        res = self.com_db.update(self.com_dbbase.get_tablename("translation_dictionary"), update, {
            "word": word,
        })
        return res

    def delete_word(self, word, info=True):
        translation_dictionary = self.com_dbbase.get_tablename("translation_dictionary")
        condition = {"word": word}
        if info == True:
            self.com_util.print_warn(f"not translated {word} and delete one.")
        self.com_db.delete(translation_dictionary, condition, physical=False)

    def delete_sentence(self, sentence, info=True, not_execute=False):
        table = self.com_dbbase.get_tablename("translation_voices")
        if info == True:
            self.com_util.print_warn(f"delete: {sentence}")
        if self.com_string.is_number(sentence) == True:
            condition = {"id": sentence}
        else:
            condition = {"sentence": self.com_string.encode(sentence)}
        self.com_db.delete_physical(table, condition, not_execute)

    def update_sentence(self, update, id, not_execute=False):
        update["time"] = self.com_string.create_time()
        res = self.com_db.update(self.com_dbbase.get_tablename("translation_voices"), update, {
            "id": id,
        }, not_execute=not_execute)
        return res

    def clear_wordparameter(self, word):
        where = ""
        if word != None:
            where = "where word=%s" % word
        sql = f"update translation_dictionary set word_sort = NULL,phonetic_us=NULL,phonetic_us_sort=NULL,phonetic_uk=NULL,phonetic_uk_sort=NULL {where}"
        self.com_db.execute(sql)

    def update_translatesetwordsort(self, word, update_word, translation, force=False):
        original_word_sort = translation.get("word_sort")
        if original_word_sort in [None, ""]:
            translation["word_sort"] = self.com_translate.sort_word(word)
            update_word["word_sort"] = translation["word_sort"]
            update_word["word_length"] = len(translation["word_sort"])
            update_word["translate_bing"] = translation
        else:
            if force == True:
                translation["word_sort"] = self.com_translate.sort_word(word)
                update_word["word_sort"] = translation["word_sort"]
        return update_word

    def update_thirdvoice(self, word, update_word=None, translation=None, delete_obsolete=True, info=False, index=None):
        if update_word == None:
            update_word = {}
        if translation == None:
            words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {
                'word': word,
            }, limit=(0, 1), select="*", read_delete=True)
            if len(words) > 0:
                word_item = words[0]
                word = word_item.get('word')
                translate_bing = word_item.get('translate_bing')
                translation = self.com_string.to_json(translate_bing)
        if translation != None:
            if self.com_translate.is_third_voice(translation) == False:
                translation = self.com_translate.add_third_voice(word, translation, delete_obsolete=delete_obsolete)
                update_word["translate_bing"] = translation
                if info:
                    self.com_util.print_info(f"update_third voice {index}:{word}")
            return update_word, translation
        else:
            return {}, {}

    def update_translatephoneticandvoice(self, update_word, translation, phonetic_us, phonetic_us_sort, phonetic_uk,
                                         phonetic_uk_sort):
        if self.com_string.is_realNones([phonetic_us, phonetic_uk, phonetic_us_sort, phonetic_uk_sort]):
            voice_files = translation.get('voice_files')
            for ik, iv in voice_files.items():
                if isinstance(iv, dict):
                    iterate_name = iv.get('iterate_name')
                    if type(iterate_name) == str:
                        iterate_name = self.com_string.decode(iterate_name).lower()
                        phonetic = self.com_translate.format_phonetic(iterate_name)
                        if translation.get("phonetic_symbol") == None:
                            translation["phonetic_symbol"] = {}
                        us_key = None
                        if iterate_name.startswith('us'):
                            us_key = "us"
                            update_word["translate_bing"] = translation
                        elif iterate_name.startswith('uk'):
                            us_key = "uk"
                        if us_key != None:
                            update_word["translate_bing"] = translation
                            update_word[f"phonetic_{us_key}"] = phonetic
                            sort_phonetic = self.com_translate.sort_phonetic(phonetic)
                            len_phonetic = len(sort_phonetic)
                            update_word[f"phonetic_{us_key}_sort"] = sort_phonetic
                            update_word[f"phonetic_{us_key}_length"] = len_phonetic
                            translation["phonetic_symbol"][f"phonetic_{us_key}"] = update_word[f"phonetic_{us_key}"]
                            translation["phonetic_symbol"][f"phonetic_{us_key}_sort"] = update_word[
                                f"phonetic_{us_key}_sort"]
                            translation["phonetic_symbol"][f"phonetic_{us_key}_length"] = len_phonetic
        return update_word

    def update_translate(self):
        words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {
            'is_delete': 0
        }, limit=None, select="*")

        update_count = 0
        re_transwordsnottranslation = []
        re_transwordsnotvoicefile = []
        re_transwordincorrectlytrans = []
        re_transwordsnotvoice = []

        skipped = []
        index = 0
        is_check_voicefile = self.com_util.is_time_between("5", "7")  # 5点到7点更新音频库
        redundant_voicefiles = self.com_translate.scan_voicefiles(copy=True) if is_check_voicefile else []

        for word_item in words:
            id = word_item.get('id')
            word = word_item.get('word')
            phonetic_us = word_item.get('phonetic_us')
            phonetic_uk = word_item.get('phonetic_uk')
            phonetic_us_sort = word_item.get('phonetic_us_sort')
            phonetic_uk_sort = word_item.get('phonetic_uk_sort')
            translate_bing = word_item.get('translate_bing')
            translation = self.com_string.to_json(translate_bing)
            if index % 10000 == 0 and index > 0:
                self.com_util.print_info(f"redundant_voicefiles :{len(redundant_voicefiles)} delete.")
                show_info = True
            else:
                show_info = False
            if self.com_translate.is_translation(translation) == False:
                re_transwordsnottranslation.append(word)
                continue
            if self.com_translate.is_voice(translation) == False:
                re_transwordsnotvoice.append(word)
                continue
            if is_check_voicefile:
                if self.com_translate.is_voicefile(translation, word, info=show_info, index=index,
                                                   scan_voicefiles=redundant_voicefiles) == False:
                    re_transwordsnotvoicefile.append(word)
                    continue
            if self.com_translate.is_onlywebtrans_and_noother(word, translation) == True:
                re_transwordincorrectlytrans.append(word)
                continue
            update_word = {}
            update_word = self.update_translatesetwordsort(word, update_word, translation, force=False)
            update_word = self.update_translatephoneticandvoice(update_word, translation, phonetic_us, phonetic_us_sort,
                                                                phonetic_uk, phonetic_uk_sort)

            update_word, translation = self.update_thirdvoice(word, update_word, translation, info=show_info,
                                                              index=index)
            if len(update_word.keys()) > 0:
                self.update_word(word, update_word)
                update_count += 1
            else:
                skipped.append(id)
            index += 1

        self.com_util.print_info(f"re-translate words :{len(re_transwordsnotvoicefile)},not voice-file.")
        self.com_util.print_info(f"re-translate words :{len(re_transwordsnotvoice)},not voice-trans.")
        self.com_util.print_info(f"re-translate words :{len(re_transwordsnottranslation)},not translation.")
        self.com_util.print_info(
            f"re-translate words :{len(re_transwordincorrectlytrans)},is_onlywebtrans and no-delete.")
        self.com_util.print_info(f"skip-words :{len(skipped)}")
        re_transwords = re_transwordsnottranslation + re_transwordsnotvoice + re_transwordsnotvoicefile + re_transwordincorrectlytrans
        self.com_translate.not_translatedtoqueue(re_transwords)
        self.com_util.print_info(f"update_translate :{update_count} updated.")
        self.com_util.print_info(f"redundant_voicefiles :{len(redundant_voicefiles)} delete.")
        restorewords = self.com_translate.correct_translate()
        if len(restorewords) > 0:
            for word in restorewords:
                self.update_word(word, {
                    'is_delete': 0
                })
        self.com_translate.delete_redundantvoicefiles(redundant_voicefiles)
        # 暂时关闭,等待开发完成音频翻译功能再开启
        # self.update_sentencetranslate()

    def redundant_voicefiles(self):
        words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {}, limit=None, select="*",
                                 read_delete=True)
        redundant_voicefiles = self.com_translate.scan_voicefiles()
        for word_item in words:
            translate_bing = word_item.get('translate_bing')
            translation = self.com_string.to_json(translate_bing)
            voice_files = translation.get('voice_files')
            if voice_files != None:
                for key, val in voice_files.items():
                    if not isinstance(val, dict):
                        return False
                    save_filename = val.get('save_filename')
                    base_name = os.path.basename(save_filename)
                    if base_name in redundant_voicefiles:
                        redundant_voicefiles.remove(base_name)

        self.com_util.print_info(redundant_voicefiles)
        self.com_util.print_info(f"redundant voicefiles :{len(redundant_voicefiles)} files.")

    def update_sentencetranslate(self):
        sentences = self.com_db.read(self.com_dbbase.get_tablename("translation_voices"), {
            "voice": "",
        }, limit=None, select="*", info=False)
        # 句子分析
        update_list = []
        disuse_sentence = []
        update_info = []
        for item in sentences:
            id = item.get('id')
            sentence = item.get('sentence')
            if self.com_translate.sentence_filter(sentence) == False:
                update_sql = self.delete_sentence(id, info=False, not_execute=True)
                disuse_sentence.append(f"{id} {sentence}")
            else:
                new_sentence = self.com_translate.sentence_modify(sentence)
                update_info.append(f"{new_sentence} by {sentence}")
                update_sentence = {
                    "sentence": new_sentence,
                }
                update_sql = self.update_sentence(update_sentence, id, not_execute=True)
            if update_sql not in [None, False]:
                update_list.append(update_sql)
        self.com_db.exec(update_list)
        self.com_util.print_warn(f"delete_sentence :{' '.join(disuse_sentence[0:60])}")
        self.com_util.print_warn(f"update_detail :{' '.join(update_info[0:60])}")
        self.com_util.print_info(f"update_sentences :{len(update_list)} updated.")

    def sava_to_db(self, data, tabname="word", db_key="word"):
        if tabname == "word":
            tabname = self.com_dbbase.get_tablename("translation_dictionary")
        elif tabname == "group":
            tabname = self.com_dbbase.get_tablename("translation_group")
        if type(data) == str:
            data = {
                db_key: data,
            }
        data = self.com_translate.set_default_val(data)
        result = self.com_db.save(tabname, data)
        return result

    def get_words_db(self, limit=(1000, 0), group_n=None):
        words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {}, limit=limit)
        return words

    def group_link_word(self, flask, group_n=None, words=None):
        if group_n == None:
            group_n = flask.flask_request.args.get("group_n")
        condition = self.get_idcondition(group_n)
        group_query_words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {"word": words},
                                             limit=None,
                                             select="id,word", )
        group_line_word = [str(sid.get('id')) for sid in group_query_words]
        group_valid_words = [sid.get('word') for sid in group_query_words]
        invalid_words = self.com_util.arr_diff(words, group_valid_words)
        group_line_word = self.com_util.shuffle_list(group_line_word)
        linked_count = len(group_line_word)
        self.com_util.print_info(f'add {group_n} linked {linked_count} ids; {",".join(group_line_word[0:3])}...')
        group_line_word = ",".join(group_line_word)
        self.com_db.update(self.com_dbbase.get_tablename("translation_group"), {
            "valid_words": ','.join(group_valid_words),
            "valid_words_count": len(group_valid_words),
            "invalid_words": ','.join(invalid_words),
            "invalid_words_count": len(invalid_words),
            "link_words": group_line_word,
            "count": linked_count,
        }, condition)

        self.save_groupinfofile(group_n, "invalid_words", invalid_words)
        self.save_groupinfofile(group_n, "valid_words", group_valid_words)
        group_info = f"success {linked_count} linked."
        result = self.com_util.print_result(data=group_info)
        return result

    def group_link_sentences(self, t_group, file_content, file_type):
        sentence_list, exclude_sentence = self.com_translate.get_docsentencemd5(file_content, file_type)
        sentence_md5 = []
        insert_list = []
        sentences_list = []
        for line in sentence_list:
            md5value = line.get("md5")
            sentence_md5.append(md5value)
            sentence = line.get("sentence")
            insert_list.append({
                "md5": md5value,
                "sentence": sentence,
            })
            sentences_list.append(sentence)
        self.com_db.save(self.com_dbbase.get_tablename("translation_voices"), insert_list)
        self.com_util.print_info(f"{t_group} insert {len(insert_list)}sentence.")
        self.group_link_sentence(group_id=t_group, sentence_md5=sentence_md5)

    def group_link_sentence(self, group_id=None, sentence_md5=None):
        condition = self.get_idcondition(group_id)
        links = self.com_db.read(self.com_dbbase.get_tablename("translation_voices"), {
            "md5": sentence_md5
        }, limit=None, select="id")
        links = [str(item.get('id')) for item in links]
        count = len(links)
        if count == 0:
            result = f"not {count} sentence linked."
        else:
            links = ",".join(links)
            self.com_db.update(self.com_dbbase.get_tablename("translation_group"), {
                "sentence": links
            }, condition)
            result = f"success {count} sentence linked."
        result = self.com_util.print_result(data=result)
        return result

    def get_trans_words(self, flask):
        try:
            limit = flask.flask_request.args.get("limit")
        except:
            limit = (0, 1000)
        words = self.get_words_db(limit)
        result = self.com_util.print_result(data=words)
        return result

    def put_translate_words(self, flask):
        doc = flask.flask_request.form.get("doc")
        t_group = flask.flask_request.form.get("t_group")
        message = "no form %s parameter"
        if not doc:
            message = message % "doc"
            return self.com_util.print_info(message)
        if not t_group:
            message = message % "t_group"
            return self.com_util.print_info(message)

        result = self.add_word(doc)
        # 启动线程翻译
        result = self.com_util.print_info(result)
        # 启动一个线程用于翻译
        return result

    def add_voice(self, flask):
        words = flask.flask_request.form.get("words")
        words, exists_words, exclude_words, word_frequency = self.com_translate.count_document_words(words)
        if words == None:
            result = f"no {words} need by add_voice"
            result = self.com_util.print_result(data=result)
            return result
        words = [{"word": word, "type": "add_voice"} for word in words]
        self.com_translate.not_translatedtoqueue(words)
        result = f"{words} add to get_voice-tasks"
        result = self.com_util.print_result(data=result)
        return result

    def trans_word(self, flask, word=None, trans=None, image=None, voice=None):
        result = f"{word} has been submitted for background translation"
        sample_images = None
        voice_files = None
        if word == None:
            word = flask.flask_request.form.get("word")
            trans = flask.flask_request.form.get("trans")
            sample_images = flask.flask_request.form.get("sample_images", None)
            voice_files = flask.flask_request.form.get("voice_files", None)
        word = self.com_string.clear_string(word)
        if word == "" or word == None:
            message = "Need curses.pyc word"
            return self.com_util.print_info(message)
        if trans == None:
            self.delete_word(word)
        # self.com_dictionary.update_word(word,{
        #     "translate_bing": trans,
        # })
        for key, val in flask.flask_request.form.items():
            print(type(val), val)
        # print(trans)
        # if sample_images != None:
        #     print(sample_images)
        # if voice_files != None:
        #     print(voice_files)
        return result

    def put_bing_translation_field(self, flask):
        try:
            word = flask.flask_request.form.get("word")
            translate_field = flask.flask_request.form.get("translate_field")
            mobile = flask.flask_request.form.get("mobile")
        except:
            return None
        update = {
            "translate_bing": translate_field,
        }
        result = self.update_word(word, update)
        result = self.com_util.print_info(result)
        return result

    def get_word(self, flask, word=None):
        if word == None:
            word = flask.flask_request.args.get("word")
        word_trans = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {
            'word': word
        })
        result = self.com_util.print_result(data=word_trans)
        return result

    def get_usermap(self, flask):
        userid = self.com_flask.get_request(flask, "userid")
        user_gtu_map = self.com_dbbase.get_tablename("user_gtu_map")
        condition = {f"userid": userid}
        result = self.com_db.read(user_gtu_map, condition, select="sort_map", limit=(1, 0),
                                  # print_sql=True
                                  )
        # def resolve(arr):
        #     for i in range(len(arr)):
        #         arr[i] = int(arr[i])
        #     return arr

        if len(result) > 0:
            result = result[0]
            result = result[0]
            result = self.com_util.mapstrtolist(result)
        else:
            result = None
        return result

    def result_notice(self, notice="No user", unread_count=None, group_words=None, ):
        info = {
            "unread_count": unread_count,
            "group_words": group_words,
            "message": notice,
        }
        return self.com_util.print_result(data=info)

    # 函数名：get_wordsbygroup
    #
    # 功能：根据group_id获取对应的单词列表，并返回包含单词列表和group_map的字典对象
    #
    # 参数说明：
    #
    # flask_router: Flask对象，用于接收HTTP请求
    # group_id: int类型，指定需要获取单词列表的组别ID
    # load_eudic: bool类型，是否需要同时加载欧陆词典中的单词
    # limit: tuple类型，指定返回结果的数量限制，格式为(limit, offset)，默认为(1000, 0)
    # selector: str类型，指定从translation_dictionary表中查询的列，缺省为
    # "*"
    # compress: bool类型，是否需要压缩返回结果的JSON格式
    # wordids: list类型，指定需要查询的单词ID列表
    # 返回值说明：
    #
    # 返回包含单词列表和group_map的字典对象
    # 是否必须：是，但参数load_eudic和wordids可以不传入
    def get_wordsbygroup(self, flask=None, group_id=None, load_eudic=None, limit=(1000, 0), selector="*",
                         compress=False, wordids=None):
        limit = self.com_flask.get_request(flask, "limit", limit)
        compress = self.com_flask.get_request(flask, "compress", compress)
        # userid = self.com_flask.get_request(flask_router, "userid")
        group_id = self.com_flask.get_request(flask, "group_id", group_id)
        group_map = self.get_groupmap(flask)
        if len(group_map) == 0:
            return self.result_notice(f"group map not found by groud_id is {group_id}")

        sort_group_map = self.sort_groupmap(flask, group_map, sort="ASC", sort_key="read_time", limit=limit)
        link_words = self.get_linkbygroupmap(flask, sort_group_map)
        group_words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {'id': link_words},
                                       select=selector, result_object=True)
        diff = False
        link_diff = []
        if len(group_words) < len(link_words):
            diff = True
            gid = self.get_linkbygroupmap(flask, group_words)
            link_diff = self.com_util.arr_diff(link_words, gid)

        result = {
            "is_diff": diff,
            "diff": link_diff,
            "group_map": group_map,
            "group_words": group_words,
        }
        if compress != False:
            result = self.com_util.compress_json(result)

        result = self.com_util.print_result(data=result)
        return result

    def get_linkbygroup(self, flask):
        group_id = self.com_flask.get_request(flask, "group_id", None)
        if group_id == None:
            return None
        group_table = self.com_dbbase.get_tablename("translation_group")
        group_links = self.com_db.read(group_table, {'id': group_id}, select="link_words", result_object=True)
        if len(group_links) == 0:
            return None
        group_link = group_links[0]
        link_words = group_link.get('link_words')
        links = link_words.split(',')
        return links

    def get_linkbygroupmap(self, flask, groupmap):
        links = [d.get("id") for d in groupmap]
        links = self.com_util.list_toint(links)
        return links

    def get_review(self, flask, read_time=None):
        read_time = self.com_flask.get_request(flask, "read_time")
        userid = self.com_flask.get_request(flask, "userid")
        compress = self.com_flask.get_request(flask, "compress")
        limit = self.com_flask.get_request(flask, "limit", (0, 100))
        dtu_table = self.com_dbbase.get_tablename("user_dtu_map")
        read_time = self.com_string.to_date(read_time)
        condition = {
            'userid': userid,
            'read_time': read_time,
        }
        wordids = self.com_db.read(dtu_table, condition, select="wordid", limit=limit, sort={"read_time": "ASC", },
                                   print_sql=True)
        wordids = [x[0] for x in wordids]
        group_words = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {'id': wordids},
                                       select="*", limit=limit)
        if compress != False:
            result = self.com_util.compress_json(group_words)
        result = self.com_util.print_result(data=group_words)
        return result

    def get_review_count(self, flask, group_id=None):
        userid = self.com_flask.get_request(flask, "userid")
        user_gtu_haveread = self.com_dbbase.get_tablename("user_gtu_haveread")
        read_time = flask.flask_request.args.get("read_time")
        read_time = self.com_string.to_datetime(read_time)
        condition = {
            'read_time_day': read_time,
            "userid": userid,
        }
        result = self.com_db.read(user_gtu_haveread, condition)

        count = 0
        if len(result) > 0:
            haveread = result[0]
            read_text = haveread.get('read_ids')
            read_ids = read_text.split(',')
            count = len(read_ids)
        result = self.com_util.print_result(data=count)
        return result

    def get_idcondition(self, idname, default_key="group_n", user=None):
        is_num = re.compile(r'^\d+$')
        if is_num.search(idname) != None:
            condition = {
                "id": idname
            }
        else:
            condition = {
                default_key: idname
            }
        if self.com_string.is_number(user):
            condition["uid"] = self.com_string.to_int(user)
        return condition

    def is_group(self, t_group, user=None, groups=None):
        condition = self.get_idcondition(t_group, user=user)
        if groups == None:
            groups = self.com_db.read("translation_group", conditions=condition, )
        if len(groups) == 0:
            return False
        group_ns = [item.get('group_n') if isinstance(item, dict) else item for item in groups]
        return t_group in group_ns

    def put_word(self, flask, words=None, group_id=None, group_name=None, reference_url=None):
        user_id = self.com_flask.get_request(flask, "user_id")
        group_id = self.com_flask.get_request(flask, "group_id", group_id)
        group_name = self.com_flask.get_request(flask, "group_name", group_name)
        reference_url = self.com_flask.get_request(flask, "reference_url", reference_url)
        words = self.com_flask.get_request(flask, "words", words)
        condition = {}
        if group_id != None:
            condition = {
                "id": group_id,
            }
        if group_id != None:
            condition = {
                "group_n": group_name,
            }
        self.is_group()
        if not group_nameid:
            message = f"no group_nameid,group_nameid {group_nameid}"
            message = self.com_util.print_result(data=message)
            return message
        result = self.update_oraddgroup(group_nameid, word)
        if not (type(result) == str and result.find("is existing") != -1):
            self.put_notebook(None, word, reference_url)
        notebook_count = self.notebook_count(inline=True)
        if type(result) == str:
            result = {
                "message": result[0:60]
            }
        result["notebook_count"] = notebook_count
        result = self.com_util.print_result(data=result)
        return result

    def notebook_count(self, flask=None, group_id=None, userid=None, reference_url=None, inline=False):
        if flask != None:
            reference_url = flask.flask_request.args.get("reference_url")
            group_id = flask.flask_request.args.get("group_id")
            userid = flask.flask_request.args.get("userid")
        notebook_count = self.com_db.count(self.com_dbbase.get_tablename("translation_notebook"), {
            "time": f'%{self.com_string.create_time("%Y-%m-%d")}%',
            "group_id": group_id,
            "user_id": userid,
        })
        if inline == True:
            return notebook_count
        result = self.com_util.print_result(data=notebook_count)
        return result

    def get_readcount(self, flask):
        user_id = self.com_flask.get_request(flask, "userid")
        user_gtu_readcount = self.com_dbbase.get_tablename("user_gtu_readcount")
        if not self.com_string.is_number(user_id):
            return self.result_notice(f"get_readcount not userid, userid: {user_id}")
        readcount = self.com_db.read(user_gtu_readcount, {
            "userid": user_id,
        })
        if len(readcount) > 0:
            readmap_json = readcount[0]
            read_map = readmap_json.get('read_map')
            readmap_json["read_map"] = self.com_string.to_json(read_map)
            readcount[0] = readmap_json
        result = self.com_util.print_result(data=readcount)
        return result

    def put_readcount(self, flask, words=None):
        user_id = self.com_flask.get_request(flask, "userid")
        words = self.com_flask.get_request(flask, "words", words)
        if words == None or not self.com_string.is_number(user_id):
            return self.result_notice(f"get_readcount not words or userid, words: {words} userid: {user_id}")

        words = self.com_translate.doc_towordlist(words)
        user_gtu_readcount = self.com_dbbase.get_tablename("user_gtu_readcount")
        readcount_data = self.get_readcount(flask)
        readcount = readcount_data.get('data')
        save_read = {}
        timestamp = self.com_util.create_timestamp()
        read_count = 1
        if len(readcount) == 0:
            for word in words:
                save_read[word] = {
                    "last_time": timestamp,
                    "count": read_count,
                }
            readmap = {
                "read_map": self.com_string.json_tostring(save_read),
                "userid": user_id,
            }
            save_id = self.com_db.save(user_gtu_readcount, readmap)
        else:
            readmap_text = readcount[0]
            readmap_json = self.com_string.to_json(readmap_text)
            readmapwords_text = readmap_json.get('read_map')
            readmapwords = self.com_string.to_json(readmapwords_text)

            for word in words:
                if readmapwords.get(word) != None:
                    readmapwords[word]["count"] += read_count
                    readmapwords[word]["last_time"] = timestamp
                else:
                    readmapwords[word] = {
                        "last_time": timestamp,
                        "count": read_count,
                    }

            readmap = {
                "read_map": self.com_string.json_tostring(readmapwords),
            }
            save_id = self.com_db.update(user_gtu_readcount, readmap, {"userid": user_id})
        result = self.com_util.print_result(data=save_id)
        return result

    def put_notebook(self, flask, word=None, reference_url=None, group_id=None, userid=None):
        if word == None:
            word = flask.flask_request.args.get("word")
            reference_url = flask.flask_request.args.get("reference_url")
            group_id = flask.flask_request.args.get("group_id")
            userid = flask.flask_request.args.get("userid")

        local_word = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {"word": word})
        if local_word == None or len(local_word) == 0:
            message = f"'{word}' does not exist in the dictionary"
            self.com_util.print_warn(message)
            message = self.com_util.print_result(data=message)
            return message
        else:
            word_id = local_word[0][0]

            notebook = {
                "group_id": group_id,
                "user_id": userid,
                "word_id": word_id,
                "reference_url": reference_url,
            }
            self.com_db.save(self.com_dbbase.get_tablename("translation_notebook"), notebook)
            message = f"'{word}' add to notebook"
            self.com_util.print_info(message)
            message = self.com_util.print_result(data=message)
            return message

    def save_groupinfofile(self, group_file, savetype, context):
        if type(context) == list:
            for i in range(len(context)):
                text = context[i]
                if not isinstance(text, str):
                    text = str(text)
                context[i] = self.com_string.decode(text)
            dict_file = self.com_file.change_ext(f"{savetype}_{len(context)}_{group_file}", ".txt")
            context = "\n".join(context)
        elif type(context) == dict:
            dict_file = self.com_file.change_ext(f"{savetype}_{len(context.keys())}_{group_file}", ".txt")
            context = self.com_string.json_tostring(context)
        else:
            context = str(context)
            dict_file = self.com_file.change_ext(f"{savetype}_{group_file}", ".txt")
        dict_file = self.com_config.get_public(f'translate_file/.group_info/{dict_file}')
        self.com_file.save(dict_file, context)

    def update_oraddgroup(self, t_group, file_content, file_type="doc", user_id=0):
        if file_type == None:
            file_type = "doc"
        group = self.is_group(t_group)
        words, doc_exists_words, exclude_words, word_frequency = self.com_translate.count_document_words(file_content)
        self.com_util.print_info(f'update_oraddgroup {len(words)} group {group}')
        group_table = self.com_dbbase.get_tablename("translation_group")
        if group != False:
            translation_dictionary = self.com_dbbase.get_tablename("translation_dictionary")
            link_words = group.get('link_words')
            link_words = link_words.split(',')
            link_words = self.com_util.list_toint(link_words)
            exists_words = self.com_db.read(translation_dictionary, {
                "id": link_words,
            }, select="word")
            exists_words = [w.get('word') for w in exists_words]
            words = words + exists_words
            words = list(set(words))
            t_group = group.get('group_n')
            group_data = {
                "count": len(words),
                "last_time": self.com_string.create_time(),
            }
            self.com_util.print_info(f"update {t_group} of group")
            condition = self.get_idcondition(t_group)
            self.com_db.update(group_table, group_data, conditions=condition)
        else:
            group_data = {
                "group_type": file_type,
                "group_n": t_group,
                "uid": user_id,
                "language": "en",
                "count": len(words),
                "include_words": ",".join(words),
                "include_words_count": len(words),
                "word_frequency": self.com_string.json_tostring(word_frequency),
                "origin_text": file_content,
                "last_time": self.com_string.create_time(),
            }
            self.com_util.print_info(f"add {t_group} inserting of ({len(words)})words")
            self.com_db.save(group_table, group_data)
            self.com_util.print_info(f"add {t_group} ({len(words)})word save-to-database success.")

        self.save_groupinfofile(t_group, "include_words", words)
        self.save_groupinfofile(t_group, "word_frequency", word_frequency)
        # self.save_groupinfofile(t_group, "sentences", sentences_list)
        self.save_groupinfofile(t_group, "exclude_words", exclude_words)
        self.save_groupinfofile(t_group, "exists_words", doc_exists_words)

        self.add_word(words)
        result = self.group_link_word(flask=None, group_n=t_group, words=words)
        # self.group_link_sentences(t_group,file_content,file_type)
        return result

    def put_group(self, flask, file_content=None, t_group=None, user_id=0, file_type="doc", start_thread=True):
        t_group = self.com_flask.get_request(flask, "group_name", t_group)
        file_content = self.com_flask.get_request(flask, "doc", file_content)
        file_type = self.com_flask.get_request(flask, "type", file_type)
        user_id = self.com_flask.get_request(flask, "user_id", user_id)
        if t_group == None or file_content == None:
            message = f"group_name {t_group} error or doc content."
            result = self.com_util.print_result(data=message)
            return result
        t_group = self.com_string.clear_string(t_group)

        result = self.update_oraddgroup(t_group, file_content, file_type, user_id)
        result = self.com_util.print_result(data=result)
        return result

    # 函数名称: get_groups(self, flask_router=None, compress=False, groupmap=True)
    # 功能：获取指定用户的所有单词组信息。
    #
    # 实现逻辑：
    # - 从flask请求中获取compress和userid参数。
    # - 根据userid参数从translation_group表中查询指定用户的所有单词组信息。
    # - 返回查询到的单词组信息。
    #
    # 参数说明：
    # - flask_router: Flask应用程序实例。
    # - compress: 是否启用压缩JSON功能，默认为False。
    # - groupmap: 是否获取单词组映射表，默认为True。
    # - uid: 用户ID。
    #
    # 返回值说明：
    # - 返回一个JSON对象，包含查询到的单词组信息。
    #
    def get_groups(self, flask=None, compress=False, groupmap=True):
        compress = self.com_flask.get_request(flask, "compress")
        uid = self.com_flask.get_request(flask, "userid")
        print(self.com_db)
        groups = self.com_db.read(self.com_dbbase.get_tablename("translation_group"),
                                  select="id,group_n,language,last_time,time,count,link_words",
                                  sort={
                                      "id": "ASC"
                                  },
                                  result_object=True,
                                  )
        result = {
            "groups": groups,
        }
        if compress != False:
            result = self.com_util.compress_json(result)
        result = self.com_util.print_result(data=result)
        return result

    # 函数名称: haveread(self, flask_router)
    #
    # 参数：
    # - self: 对象本身
    # - flask_router: Flask应用程序实例
    #
    # 返回值：result，包含已读单词的id列表。
    #
    # 功能：将单词标记为已读并保存到数据库中。
    #
    # 实现逻辑：
    # - 从flask请求中获取wordids, words, group_id, userid参数。
    # - 将wordids转换为int类型的列表。
    # - 获取user_gtu_haveread表，并根据userid和read_time_day进行筛选。
    # - 如果找到相关的已读单词数据，则将已读单词id列表转换为int类型，并与新读取的单词id列表进行比较，得到需要更新的单词id列表。
    # - 如果没有找到相关的已读单词数据，则说明用户第一次阅读，更新所有单词id列表。
    # - 将更新后的单词id列表保存到数据库中，并更新groupmap表。
    # - 返回已读单词的id列表。
    #
    # 参数说明：
    # - wordids：已读单词的id列表，可以为int类型或逗号分隔的字符串。
    # - words: 单词列表。
    # - group_id: 单词组ID。
    # - userid: 用户ID。
    #
    # 返回值说明：
    # - result：包含已读单词的id列表。
    def haveread(self, flask, wordids=None):
        wordids = self.com_flask.get_request(flask, "wordids", wordids)
        words = self.com_flask.get_request(flask, "words")
        group_id = self.com_flask.get_request(flask, "group_id")
        userid = self.com_flask.get_request(flask, "userid")
        if not isinstance(wordids, list):
            if isinstance(wordids, int):
                wordids = [wordids]
            else:
                wordids = wordids.split(",")
        wordids = self.com_util.list_toint(wordids)

        if len(wordids) > 0:
            user_gtu_haveread = self.com_dbbase.get_tablename("user_gtu_haveread")
            read_time = self.com_string.create_time()
            read_time_day = read_time.split(' ')[0]
            result = self.com_db.read(user_gtu_haveread,
                                      {
                                          "read_time_day": read_time_day,
                                          "userid": userid,
                                      }
                                      )
            read_ids = []
            if len(result) > 0:
                havereaddata = result[0]
                read_ids = havereaddata.get('read_ids')
                read_ids = read_ids.split(",")
                read_ids = self.com_util.list_toint(read_ids)
                read_ids = list(set(read_ids))

                update_ids = [int(w) for w in wordids if w not in read_ids]
            else:
                update_ids = wordids

            if len(update_ids) > 0:
                save_wordids = read_ids + wordids
                save_wordids = [str(w) for w in save_wordids if w != ""]
                username = self.com_userinfo.get_current_user(flask)
                self.com_util.print_info(f'user: {username}, haveread {len(save_wordids)} words : {read_time}')
                save_wordids = ",".join(save_wordids)
                self.put_readcount(flask, words)
                if len(result) > 0:
                    data = {
                        "read_ids": save_wordids,
                    }
                    self.com_db.update(user_gtu_haveread, data, {"read_time_day": read_time_day, })
                else:
                    data = {
                        "read_time": read_time,
                        "read_time_day": read_time_day,
                        "read_ids": save_wordids,
                        "userid": userid,
                    }
                    self.com_db.save(user_gtu_haveread, data)
                self.set_groupmap(flask, update_ids, read_time, read_time_day)
        else:
            wordids = []
        result = self.com_util.print_result(data=wordids)
        return result

    # 函数名称: get_likebyphonetic(self, flask_router)
    #
    # 功能：根据音标的最大长度和音标的前缀，从字典中查询相应的单词信息。
    #
    # 实现逻辑：
    # - 从flask请求中获取phonetic_maxlength和phonetic_trim参数。
    # - 根据phonetic_trim和phonetic_maxlength参数从translation_dictionary表中查询相应的单词信息。
    # - 返回查询到的单词信息。
    #
    # 参数说明：
    # - flask_router: Flask应用程序实例。
    # - phonetic_maxlength: 音标的最大长度。
    # - phonetic_trim: 音标的前缀。
    #
    # 返回值说明：
    # - 返回一个JSON对象，包含查询到的单词信息。
    def get_likebyphonetic(self, flask):
        phonetic_maxlength = flask.flask_request.args.get("phonetic_maxlength")
        phonetic_trim = flask.flask_request.args.get("phonetic_trim")
        if None in [phonetic_maxlength, phonetic_trim]:
            message = f"No parameter as phonetic_length,phonetic_sortlength,phonetic_trim,word_length,word_sortlength,word_trim"
            return self.com_util.print_result(message)
        word_trans = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"), {
            'phonetic_us_sort': f"{phonetic_trim}%",
            'phonetic_us_length': f"< {phonetic_maxlength}",
        }, print_sql=False)
        result = self.com_util.print_result(data=word_trans)
        return result

    def get_likebyword(self, flask):
        word_maxlength = flask.flask_request.args.get("word_maxlength")
        word_trim = flask.flask_request.args.get("word_trim")
        if None in [word_maxlength, word_trim]:
            message = f"No parameter as phonetic_length,phonetic_sortlength,phonetic_trim,word_length,word_sortlength,word_trim"
            return self.com_util.print_result(message)
        word_trans = self.com_db.read(self.com_dbbase.get_tablename("translation_dictionary"),
                                      {
                                          'word': f"{word_trim}%",
                                          'word_length': f"< {word_maxlength}",
                                      },
                                      print_sql=False
                                      )
        result = self.com_util.print_result(data=word_trans)
        return result

    def debug(self, flask):
        print(self.com_selenium.get_current_url())
        return {"debug": True}

    def get_group(self, flask):
        group_id = self.com_flask.get_request(flask, 'group_id')
        groupinfo = self.com_db.read(self.com_dbbase.get_tablename('translation_group'), {
            "id": group_id
        }, result_object=True)
        result = self.com_util.print_result(data=groupinfo)
        return result

    def create_dtuword(self, link, group_map=None):
        wordmap = None
        if group_map != None:
            wordmap = group_map.get(link)
        if wordmap == None:
            wordmap = {
                "id": link,
                "read_time": 0,
                "read_count": 0,
            }
        return wordmap

    def sort_groupmap(self, flask, groupmap, sort="ASC", sort_key="read_time", limit=(0, 100)):
        limit = self.com_dbbase.gen_limit_sql(limit)
        offset = limit[1]
        limit_len = offset + limit[0]

        if sort == "ASC":
            groupmap = sorted(groupmap, key=lambda x: x[sort_key])
        else:
            groupmap = sorted(groupmap, key=lambda x: x[sort_key], reverse=True)
        groupmap = groupmap[offset:limit_len]
        # self.com_util.pprint(groupmap)
        # print('limit_len',limit_len)
        return groupmap

    # 函数名称: get_groupmap(self, flask_router)
    #
    # 返回值：groupmap，单词组映射表。
    #
    # 功能：获取指定用户在指定单词组中的单词映射表。
    #
    # 实现逻辑：
    # - 从flask请求中获取group_id和userid参数。
    # - 根据group_id和userid参数从user_gtu_map表中查询相应的单词组映射表。
    # - 如果查询到相应的单词组映射表，则返回单词组映射表。
    # - 如果没有查询到相应的单词组映射表，则根据group_id参数从translation_group表中查询相应的单词组信息，并将其中的link_words参数解析为单词id列表，然后根据单词id列表创建单词组映射表。
    # - 将创建的单词组映射表保存到user_gtu_map表中，并返回该单词组映射表。
    #
    # 参数说明：
    # - flask_router: Flask应用程序实例。
    # - group_id: 单词组ID。
    # - userid: 用户ID。
    #
    # 返回值说明：
    # - groupmap: 单词组映射表。
    def get_groupmap(self, flask):
        empty_groupmap = []
        group_id = self.com_flask.get_request(flask, 'group_id', None)
        userid = self.com_flask.get_request(flask, 'userid', None)
        if group_id == None or userid == False or userid == None:
            return empty_groupmap

        user_gtu_map = self.com_dbbase.get_tablename('user_gtu_map')
        condition = {
            "group_id": group_id,
            "userid": userid,
        }
        result = self.com_db.read(user_gtu_map, condition, result_object=True)
        # print("result",result)

        if isinstance(result, list) and len(result) > 0:
            groupdict = result[0]
            groupmap = groupdict.get('group_map')
            groupmap = self.com_string.to_json(groupmap)
            return groupmap
        else:
            group = self.get_group(flask)
            group_list = group.get('data')
            if len(group_list) > 0:
                group_dict = group_list[0]
                link_words = group_dict.get('link_words')
                # group_n = group_dict.get('group_n')
                linked = link_words.split(',')
                linked = self.com_util.list_toint(linked)
                group_map = []
                for link in linked:
                    group_map.append(self.create_dtuword(link))
                dtuword = {
                    "userid": userid,
                    "group_id": group_id,
                    "group_map": self.com_string.to_json(group_map),
                }
                result = self.com_db.save(self.com_dbbase.get_tablename('user_gtu_map'), dtuword)
                self.com_util.print_info(f'update grouptuser map,result:{result},userid:{userid}')
                return group_map
            else:
                return empty_groupmap

    # 函数名称: set_groupmap(self, flask_router, wid=None, read_time=None, read_time_day=None)
    #
    # 功能：更新指定用户在指定单词组中的单词映射表。
    #
    # 实现逻辑：
    # - 从flask请求中获取group_id和userid参数。
    # - 从flask请求中获取wordids参数。
    # - 如果read_time参数为None，则创建当前时间，并将其转换为时间戳和日期字符串。
    # - 将wordids参数转换为单词ID列表。
    # - 从user_gtu_map表中获取指定用户在指定单词组中的单词映射表。
    # - 遍历单词组映射表和单词ID列表，将单词组映射表中单词ID对应的单词信息的read_time和read_time_day字段更新为指定的时间戳和日期字符串。
    # - 将更新后的单词组映射表保存到user_gtu_map表中。
    # - 返回更新单词组映射表的结果。
    #
    # 参数说明：
    # - flask_router: Flask应用程序实例。
    # - group_id: 单词组ID。
    # - userid: 用户ID。
    # - wid: 单词ID。
    # - read_time: 阅读时间。
    # - read_time_day: 阅读日期。
    #
    # 返回值说明：
    # - result: 更新单词组映射表的结果。
    def set_groupmap(self, flask, wid=None, read_time=None, read_time_day=None):
        group_id = self.com_flask.get_request(flask, 'group_id', None)
        userid = self.com_flask.get_request(flask, 'userid', None)
        if group_id == None or userid == False:
            return None
        wid = self.com_flask.get_request(flask, 'wordids', wid)
        if read_time == None:
            read_time = self.com_string.create_time()
            read_time_day = read_time.split(" ")[1]
        if isinstance(wid, str):
            wid = wid.split(",")
        if isinstance(wid, str) or isinstance(wid, int):
            wids = [wid]
        else:
            wids = wid

        groupmap = self.get_groupmap(flask)

        wids = self.com_util.list_toint(wids)
        for i in range(len(groupmap)):
            map = groupmap[i]
            for wid in wids:
                if self.com_string.to_int(map.get("id")) == wid:
                    map["read_time"] = self.com_util.totimestamp(read_time)
                    map["read_time_day"] = self.com_util.totimestamp(read_time_day)
                    groupmap[i] = map

        user_gtu_map = self.com_dbbase.get_tablename('user_gtu_map')

        result = self.com_db.update(user_gtu_map, {
            "group_map": groupmap
        }, {
                                        "userid": userid,
                                        "group_id": group_id,
                                    })
        self.com_util.print_info("set_groupmap", result)
        result = self.com_util.print_result(data=result)
        return result
