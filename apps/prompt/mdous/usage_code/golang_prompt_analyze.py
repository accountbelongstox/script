from apps.prompt.bc.interface.prompt_analyze import PromptAnalyzeInterface
import re
# import pprint
from pycore.utils import arr
from pycore.base.base import Base

class golangPromptAnalyze(PromptAnalyzeInterface,Base):
    def __init__(self):
        self.empty_default_start_line = 0
        self.empty_default_max_line = 50
        self.codeIdentifier = "//c"
        self.mustPromptIdentifier = "//p"
        self.apiIdentifier = "//curses.pyc"
        self.apiListIdentifier = "//"
        self.language_method_index = []
        self.language_method_mark = "func"
        self.initializer_pre = ""
        self.initializer = "//-"
        self.max_line = 100

    def extract_must_prompt(self, text_pure_arr):
        must_prompt_index = []
        for i, line in enumerate(text_pure_arr):
            if self.mustPromptIdentifier in line:
                must_prompt_index.append(i)
        code_arr = []
        if len(must_prompt_index) > 0:
            index = 0
            end_point = must_prompt_index[index]
            while end_point < len(text_pure_arr) and index < len(must_prompt_index):
                start_point = must_prompt_index[index]
                if start_point < end_point:
                    # self.info("continue-end_point", end_point)
                    index += 1
                    continue
                while end_point < len(text_pure_arr) - 1:
                    end_point += 1
                    if not (text_pure_arr[end_point].startswith(self.apiListIdentifier) or
                            text_pure_arr[end_point].startswith((self.apiIdentifier, self.initializer))):
                        end_point -= 1
                        break
                end_point += 1
                segment = text_pure_arr[start_point:end_point]
                text_pure_arr = arr.fill(text_pure_arr, start_point, end_point, None)
                code_arr += segment
                index += 1
        remain_arr = arr.filter_value(text_pure_arr, None)
        code_arr = arr.filter_value(code_arr, self.apiIdentifier)
        return code_arr, remain_arr

    def extract_apis(self, text_pure_arr):
        api_index = []
        for i, line in enumerate(text_pure_arr):
            if self.apiIdentifier in line:
                api_index.append(i)
        code_arr = []
        if len(api_index) > 0:
            index = 0
            end_point = api_index[index]
            while end_point < len(text_pure_arr) and index < len(api_index):
                start_point = api_index[index]
                if start_point < end_point:
                    # self.info("continue-end_point", end_point)
                    index += 1
                    continue
                while end_point < len(text_pure_arr) - 1:
                    end_point += 1
                    if not (text_pure_arr[end_point].startswith(self.apiListIdentifier) or
                            text_pure_arr[end_point].startswith((self.apiIdentifier, self.initializer))):
                        end_point -= 1
                        break
                end_point += 1
                segment = text_pure_arr[start_point:end_point]
                text_pure_arr = arr.fill(text_pure_arr, start_point, end_point, None)
                code_arr += segment
                index += 1
        remain_arr = arr.filter_value(text_pure_arr, None)
        code_arr = arr.filter_value(code_arr, self.apiIdentifier)
        return code_arr, remain_arr

    def generic_prompt(self, text_pure_arr) -> list:
        initializer = self.initializer_pre + self.initializer
        chinese_index = []
        code_arr = []
        is_initializer = False
        is_chinese_prompt = False
        for i, line in enumerate(text_pure_arr):
            if initializer in line:
                is_initializer = True
            if re.match(r"[\u4e00-\u9fa5]", line):
                is_chinese_prompt = True
                chinese_index.append(i)
        if is_initializer == False:
            if is_chinese_prompt == False:
                if len(text_pure_arr) <= self.max_line:
                    processed_row = arr.filter_value(text_pure_arr, initializer)
                    code_arr.append(processed_row)
                    return code_arr
                else:
                    i = 0
                    """
                    将该数组根据的self.max_line 长度距离。 按每 self.max_line 分割,直到分割完成。
                    """
                    while i * self.max_line < len(text_pure_arr):
                        start_index = i * self.max_line
                        end_index = min((i + 1) * self.max_line, len(text_pure_arr))
                        segment = text_pure_arr[start_index:end_index]
                        segment = arr.filter_value(segment, initializer)
                        code_arr.append(segment)
                        i += 1
                    return code_arr
            else:
                """
                # split_start  split_end
                # 然后从start_point向text_pure_arr的数组开头依次递减查找到0, 直到连续查找到两个以self.language_method_mark 开头的字符串,并根据该字符串的Index设置为split_start。
                # 然后从end_point向text_pure_arr的数组开头依次递增查找直到数组结尾, 直到连续查找到第一个以self.language_method_mark 开头的字符串,,并根据该字符串的Index设置为split_end。
                # 遍历 text_pure_arr 。 根据Sprint store或Springdale的值。 区间的数据添加到segment_prompt_new_arr。
                # split_start  split_end
                """
                index = 0
                end_point = chinese_index[index]
                while end_point < len(text_pure_arr) and index < len(chinese_index):
                    ch_index = chinese_index[index]
                    """当前位置已经查找过"""
                    if ch_index < end_point:
                        self.info("continue-start_point", start_point)
                        self.info("continue-end_point", end_point)
                        index += 1
                        continue
                    """数据已经遍历结束"""
                    start_point = ch_index
                    # self.info("ch_index", ch_index)
                    while start_point > 0:
                        start_point -= 1
                        if text_pure_arr[start_point] == None:
                            break
                        if text_pure_arr[start_point].startswith(self.language_method_mark):
                            break
                    while end_point < len(text_pure_arr) - 1:
                        end_point += 1
                        if text_pure_arr[end_point].startswith(self.language_method_mark):
                            end_point -= 1
                            break
                    end_point += 1
                    # self.info("start_point", start_point)
                    # self.info("end_point", end_point)
                    segment = text_pure_arr[start_point:end_point]
                    text_pure_arr = arr.fill(text_pure_arr, start_point, end_point, None)
                    # self.info("text_pure_arr", text_pure_arr)
                    code_arr.append(segment)
                    index += 1
                # self.info("code_arr", code_arr)
                return code_arr
        else:
            index_array = [0]
            for index, line in enumerate(text_pure_arr):
                if initializer in line:
                    index_array.append(index)
            index_array.append(len(text_pure_arr))
            index_array = arr.unique_list(index_array)
            generic_prompt_arr = []
            for i in range(len(index_array) - 1):
                start_index = index_array[i]
                end_index = index_array[i + 1]
                segment = text_pure_arr[start_index:end_index]
                generic_prompt_arr.append(segment)
            for row in generic_prompt_arr:
                processed_row = arr.filter_value(row, initializer)
                if len(processed_row) > 0:
                    code_arr.append(processed_row)
            return code_arr

    def get_language_method_marks(self, text_arr):
        pattern = f"^\s*{self.language_method_mark}"
        indices = []
        for i, line in enumerate(text_arr):
            if re.match(pattern, line):
                indices.append(i)
        return indices

    def get_code_mark_index(self, text_arr):
        index_arr = []
        for i, line in enumerate(text_arr):
            if line.strip().startswith(self.codeIdentifier):
                index_arr.append(i)
        return index_arr

    def get_code_start_marks(self):
        return self.codeIdentifier

    def get_code_end_marks(self):
        return self.codeIdentifier

    def mark_empty_default_start_line(self):
        return self.empty_default_start_line

    def mark_empty_default_end_line(self, text_pure_arr):
        language_method_marks = self.get_language_method_marks(text_pure_arr)
        default_line = len(text_pure_arr)
        if len(language_method_marks) > 2:
            default_line = language_method_marks[2]
        if default_line > self.empty_default_max_line:
            default_line = self.empty_default_max_line
        return default_line

    def split_comments(self, raw_arr):
        code_arr = []
        current_line = []
        for element in raw_arr:
            current_line.append(element)
            if len(current_line) == self.max_line:
                code_arr.append(current_line)
                current_line = []
        if current_line:
            code_arr.append(current_line)

        return code_arr

    def extract_usage(self, text_raw_arr, text_pure_arr, code_path):
        remain_text_arr = arr.copy(text_pure_arr)
        index_arr = self.get_code_mark_index(text_pure_arr)
        processed_arr = []
        if len(index_arr) > 1:
            for i in range(0, len(index_arr) - 1):
                start_index = index_arr[i]
                end_index = index_arr[i + 1]
                s_start = start_index
                s_end = end_index
                processed_arr.append(text_pure_arr[s_start:s_end])
                remain_text_arr = arr.fill(remain_text_arr, s_start, s_end, None)
                # self.info(f"extract_usage : {s_start} {s_end}")
        elif len(index_arr) == 0:
            s_start, s_end = self.mark_empty_default_start_line(), self.mark_empty_default_end_line(
                text_pure_arr)
            remain_text_arr = arr.fill(remain_text_arr, s_start, s_end, None)
            processed_arr.append(text_pure_arr[s_start:s_end])
        else:
            if index_arr[0] != 0:
                index_arr = [0] + index_arr
            else:
                """
                # 代码标记位置在 0 的情况
                """
                code_identi_index = index_arr[0]
                while code_identi_index < len(text_pure_arr) - 1:
                    code_identi_index += 1
                    if code_identi_index >= self.empty_default_max_line:
                        code_identi_index = self.empty_default_max_line
                        break
                    if text_pure_arr[code_identi_index].startswith(self.language_method_mark):
                        break
                index_arr.append(code_identi_index)
            s_start, s_end = index_arr[0], index_arr[1]
            processed_arr.append(text_pure_arr[s_start:s_end])
            remain_text_arr = arr.fill(remain_text_arr, s_start, s_end, None)
            # self.info(f"extract_usage : {s_start} {s_end}")
        processed_arr = arr.filter_value(processed_arr, self.codeIdentifier)
        code_usage = []
        for row in processed_arr:
            processed_row = arr.filter_value(row, self.codeIdentifier)
            if len(processed_row) > 0:
                code_usage.append(processed_row)
        remain_text_arr = arr.filter_value(remain_text_arr, self.codeIdentifier)
        remain_text_arr = arr.filter_value(remain_text_arr, None)
        return code_usage, remain_text_arr


go_analyze = golangPromptAnalyze()
