import pprint

from apps.prompt.mdous.usage_code.python_prompt_analyze import py_analyze
from apps.prompt.mdous.usage_code.golang_prompt_analyze import go_analyze
from apps.prompt.mdous.analyze.analyze import text_analyze
<<<<<<< HEAD
from kernel.base.base import Base
# from apps.prompt.mdous.usage_code.goUsageCode import goUsageCode
# from apps.prompt.mdous.usage_code.jsUsageCode import jsUsageCode
# from apps.prompt.mdous.usage_code.javaUsageCode import javaUsageCode
# from apps.prompt.mdous.usage_code.genericUsageCode import genericUsageCode


from kernel.utils import arr
=======
from pycore._base import Base
# from applications.prompt.mdous.usage_code.goUsageCode import goUsageCode
# from applications.prompt.mdous.usage_code.jsUsageCode import jsUsageCode
# from applications.prompt.mdous.usage_code.javaUsageCode import javaUsageCode
# from applications.prompt.mdous.usage_code.genericUsageCode import genericUsageCode


from pycore.utils import arr
>>>>>>> origin/main


# go_usage = goUsageCode()
# js_usage = jsUsageCode()
# java_usage = javaUsageCode()
# generic_usage = genericUsageCode()

class usageMain(Base):
    supported_lang = ["py", "go"]

    def __init__(self):
        pass

    def is_sopported(self, ext):
        return ext in self.supported_lang

    def generate_prompts(self, code_path):
        must_prompt = apis = code_usage = generic_prompt = code_comments = None
        text_text = ""
        text_raw_arr = text_pure_arr = []
        file_extension = code_path.split('.')[-1].lower()
        if file_extension in self.supported_lang:
            text_text, text_raw_arr, text_pure_arr = text_analyze.read_as_arr(code_path)
            # self.info("text_raw_arr",text_raw_arr)
            # self.info("text_pure_arr",text_pure_arr)
            if file_extension == 'py':
                must_prompt, remain_text_arr = py_analyze.extract_must_prompt(text_pure_arr)
                code_comments = py_analyze.split_comments(text_raw_arr)
                apis, remain_text_arr = py_analyze.extract_apis(remain_text_arr)
                code_usage, remain_text_arr = py_analyze.extract_usage(text_raw_arr, remain_text_arr, code_path)
                generic_prompt = py_analyze.generic_prompt(remain_text_arr)
            if file_extension == 'go':
                must_prompt, remain_text_arr = go_analyze.extract_must_prompt(text_pure_arr)
                code_comments = go_analyze.split_comments(text_raw_arr)
                apis, remain_text_arr = go_analyze.extract_apis(remain_text_arr)
                code_usage, remain_text_arr = go_analyze.extract_usage(text_raw_arr, remain_text_arr, code_path)
                generic_prompt = go_analyze.generic_prompt(remain_text_arr)
            else:
                self.warn(f"{file_extension} Supported languages that have not yet been implemented..")
        else:
            self.warn(f"Unsupported: ({file_extension}) This file type is not a supported language.")
        return must_prompt, apis, code_usage, generic_prompt, code_comments, text_text, text_raw_arr, text_pure_arr


usagemain = usageMain()
