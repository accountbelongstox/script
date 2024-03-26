from pycore.utils import arr, strtool, tool
from apps.prompt.config.lang_config import lang_config
from apps.prompt.mdous.analyze.config_weights import config_weights
import os
# from pycore.utils import file

class CreatePrompt:
    _pre = "#"
    initializer = "-"

    def get_prompt(self, prompt_config_name, p_config, com_config, lang_map, default_lang="en"):
        prompt_by_config = config_weights.get_by_extend(prompt_config_name, p_config, com_config, lang_map)
        prompts = []
        for prompt in prompt_by_config:
            if isinstance(prompt, dict):
                prompt = prompt.get(default_lang)
                if isinstance(prompt, list):
                    prompts = prompts + prompt
                else:
                    prompts.append(prompt)
            elif isinstance(prompt, list):
                prompts = prompts + prompt
            else:
                prompts.append(prompt)
        return prompts

    def replace_prompt(self, prompt, ext, replace_map={}):
        if isinstance(ext, str):
            lang_map = lang_config.get_langconfig(ext)
        else:
            lang_map = ext
        lang_map = tool.deep_update(lang_map, replace_map)
        prompt = strtool.replace_template(prompt, lang_map)
        return prompt

    def replace_and_join(self, prompt_comments,lang_map):
        prompt_comment = "\n".join(prompt_comments)
        prompt_comment_result = create_prompt.replace_prompt(prompt_comment, lang_map)
        return  prompt_comment_result

    def wrap_code(self,code_partition):
        if isinstance(code_partition,list):
            code_partition = "\n".join(code_partition)
        wrap_code = '```\n' + code_partition + '\n```\n'
        return wrap_code

    def create_prompt_filename(self,prompts_dir,code_pathname,pre_name,index):
        prompts_ext = pre_name + str(index) + ".txt"
        prompts_pathname = code_pathname + prompts_ext
        prompts_pathname = os.path.join(prompts_dir, prompts_pathname)
        return prompts_pathname

    def create_prompt_group(self,com_config,lang_map=None):
        name_space = com_config.get("name_space") or "default"
        lang = ""
        if lang_map != None:
            lang = lang_map.get("lang")
        if lang != "":
            lang = "-"+lang
        prompt_group = name_space+lang
        return prompt_group


    def generic_prompt(self, text_pure_arr) -> list:
        initializer = self._pre + self.initializer
        index_array = [0]
        for index, line in enumerate(text_pure_arr):
            if initializer in line:
                index_array.append(index)
        generic_prompt_arr = []
        for i in range(len(index_array) - 1):
            start_index = index_array[i]
            end_index = index_array[i + 1]
            segment = text_pure_arr[start_index:end_index]
            generic_prompt_arr.append(segment)
        code_arr = []
        for row in generic_prompt_arr:
            processed_row = arr.filter_value(row, initializer)
            if len(processed_row) > 0:
                code_arr.append(processed_row)
        return code_arr


create_prompt = CreatePrompt()
