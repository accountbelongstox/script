import os.path
from pycore.utils import arr, file, strtool
from pycore.base.base import Base
from apps.prompt.mdous.resolve_prompt.create_prompt import create_prompt
from apps.tasks.task import task
from pycore.practicals import wdoc

# from apps.prompt.mdous.analyze.config_weights import config_weights

class promptMapFile(Base):

    def __init__(self, ):
        self.commentStyles = ["//", "#"]
        self.maxCommentCodeLong = 100

    def apply_API_list(self, path):
        api_list_path = self.generate_APIFile(path)
        file.save(api_list_path, "")

    def save_comment(self, prompts_dir, code_pathname, code_comments, prompt_comments, p_config, com_config, lang_map):
        prompt_comment_result = create_prompt.replace_and_join(prompt_comments, lang_map)
        group = create_prompt.create_prompt_group(com_config, lang_map)
        for index, code_comment in enumerate(code_comments):
            prompts_file = create_prompt.create_prompt_filename(prompts_dir, code_pathname, ".comments_", index)
            code_wrap = create_prompt.wrap_code(code_comment)
            content = code_wrap + "\n" + prompt_comment_result
            file.save(prompts_file, content, overwrite=True)
            task.put_task(code_pathname, content, group=group)
        return code_pathname

    def save_translate(self, prompts_dir, code_pathname, text_text, gpt_config):
        words, exists_words, exclude_words, word_frequency = wdoc.extra_words(text_text)
        prompts_ext = ".trans.json"
        prompts_pathname = code_pathname + prompts_ext

        def initialize_map(map, key):
            if map.get(key) is None:
                map[key] = []

        def update_word_list(word_list, new_words):
            for word in new_words:
                if word not in word_list:
                    word_list.append(word)

        translate_dir = os.path.join(prompts_dir, ".translate")
        translate_dir = os.path.join(translate_dir, ".app")
        translate_file = os.path.join(translate_dir, prompts_pathname)
        trans_map = file.read_json(translate_file)

        initialize_map(trans_map, "words")
        initialize_map(trans_map, "exclude_words")

        words_json = os.path.join(prompts_dir, ".translate/words.json")
        words_map = file.read_json(words_json)

        initialize_map(words_map, "words")
        initialize_map(words_map, "exclude_words")

        update_word_list(trans_map["words"], words)
        update_word_list(trans_map["exclude_words"], exclude_words)

        update_word_list(words_map["words"], words)
        update_word_list(words_map["exclude_words"], exclude_words)

        file.save_json(translate_file, trans_map)
        file.save_json(words_json, words_map)

        # trans_words_prompt = gpt_config.get("transPromptByWord")
        # words_prompt = ""
        # words_prompt = "\n".join(trans_words_prompt)
        # if trans_words_prompt != None:
        #     words_prompt = "\n".join(trans_words_prompt)
        #     words, exists_words, exclude_words, word_frequency = wdoc.extra_words(text_text)
        #     words_map["words"].append(words)
        # words_text = ",".join(words)
        # words_text = "(" + words_text + ")"
        # replace_map = {}
        # replace_map["words"] = words_text
        # words_prompt = strtool.replace_template(words_prompt, replace_map)

    def save_apis(self, prompts_dir, code_pathname, apis, ext, gpt_config):
        promptapis = gpt_config.get("promptapis", [])
        for index, code_comment in enumerate(promptapis):
            prompts_ext = ".apis_" + str(index) + ".txt"
            # pathname = file.replace_ext(pathname,prompts_ext, resolve=False)
            prompts_pathname = code_pathname + prompts_ext
            self.info("prompts_pathname", prompts_pathname)
            code = "\n".join(code_comment)
            code = '"""\n' + code + '\n"""'
            prompts_file = os.path.join(prompts_dir, prompts_pathname)
            self.info("pathname", prompts_pathname)
            self.info("prompts_file", prompts_file)
            self.info("prompts_dir", prompts_dir)
            promptapis = []

    def generate_APIFile(self, path):
        path = file.file_add(path, "APIs", resolve=True)
        path = file.replace_ext(path, "md", resolve=True)
        return path

    def is_APIFile_exists(self, path):
        api_list_path = self.generate_APIFile(path)
        return file.isFile(api_list_path)

    def remove_comments(self, lines):
        result_lines = []
        in_triple_quotes = False
        start_triple_quotes_line = None
        for i, line in enumerate(lines):
            if in_triple_quotes:
                if '"""' in line:
                    in_triple_quotes = False
                    for j in range(start_triple_quotes_line, i + 1):
                        result_lines.append(None)
                else:
                    result_lines.append(None)
            elif line.strip().startswith(tuple(self.commentStyles)):
                result_lines.append(None)
            elif '"""' in line:
                in_triple_quotes = True
                start_triple_quotes_line = i
                result_lines.append(line.split('"""', 1)[-1].strip())
            else:
                result_lines.append(line)
        result_lines = arr.filter_value(result_lines, None)
        return result_lines

    def segment_code(self, code):
        segments = []
        current_segment = ""
        for line in code.splitlines():
            if len(current_segment) + len(line) <= self.maxCommentCodeLong:
                current_segment += line + "\n"
            else:
                segments.append(current_segment.strip())
                current_segment = line + "\n"
        if current_segment.strip():
            segments.append(current_segment.strip())
        return segments

    def _warn(self, msg):
        self.info(f"\033[91mWarning: {msg}\033[0m")

    def _success(self, msg):
        self.info(f"\033[92mSuccess: {msg}\033[0m")


prompt_map_file = promptMapFile()
