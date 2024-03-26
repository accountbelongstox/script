import json
import hashlib
from kernel.utils import http, file, arr
import os
from time import time

class TextAnalyze:
    task_name = "__"
    task_list = []
    default_backup_dir = file.resolve_path("out/prompt_automation/")

    def __init__(self):
        pass

    def read_as_arr(self, code_path):
        text_text = file.read_text(code_path)
        text_raw_arr = arr.text_to_lines(text_text)
        text_pure_arr = arr.remove_empty_lines(text_raw_arr)
        return text_text, text_raw_arr, text_pure_arr

    def save_prompt_content(self, complete_prompt, complete_content, task_id):
        md5_id = hashlib.md5(str(task_id).encode()).hexdigest()
        timestamp = int(time())
        prompt_filename = f"prompt_{md5_id}_{timestamp}.txt"
        content_filename = f"content_{md5_id}_{timestamp}.txt"
        prompt_path = os.path.join(self.default_backup_dir, prompt_filename)
        content_path = os.path.join(self.default_backup_dir, content_filename)
        file.save(prompt_path, complete_prompt)
        file.save(content_path, complete_content)

    def retrieve_prompt_content(self, task_id):
        md5_id = hashlib.md5(str(task_id).encode()).hexdigest()
        prompt_files = [f for f in os.listdir(self.default_backup_dir) if f.startswith(f"prompt_{md5_id}")]
        content_files = [f for f in os.listdir(self.default_backup_dir) if f.startswith(f"content_{md5_id}")]
        if prompt_files and content_files:
            prompt_files.sort()
            content_files.sort()
            latest_prompt_path = os.path.join(self.default_backup_dir, prompt_files[-1])
            latest_content_path = os.path.join(self.default_backup_dir, content_files[-1])
            complete_prompt = file.open(latest_prompt_path)
            complete_content = file.open(latest_content_path)
            return complete_prompt, complete_content
        else:
            return None, None



text_analyze = TextAnalyze()
