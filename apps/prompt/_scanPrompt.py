import os
import re
import time
import requests
import pprint
import hashlib
import zlib

class FileHandler:
    def __init__(self, folder_path):
        self.PromptWordSet = set()
        self.MustPromptWordSet = set()
        self.SampleCodeSet = set()
        self.initializer = "----------------------"
        self.taskApiUrl = "https://task.hk.12gm.com/"
        self.folder_path = folder_path
        self.mustPromptToken = "//$"
        self.codeIdentifier = "//**"
#c>
    def listen_folder(self):
        while True:
            time.sleep(5)
            files = os.listdir(self.folder_path)
            find_new = False
            for file in files:
                file_path = os.path.join(self.folder_path, file)
                if os.path.isfile(file_path) and not file.startswith("_"):
                    if not file_path.startswith("_"):
                        self.info("Found curses.pyc new file: "+file+", parsing.")
                        lines = self.read_file_content(file_path)
                        find_new = True
                        if lines != None:
                            self.info(f"Content of {file_path}:len{len(lines)}")
                            self.process_array(lines)
                            # self.rename_file(file_path)
                        else:
                            self.info("The file content is empty and continues to be skipped.")
            if find_new == False:
                self.info("There are no new files, monitoring and scanning are continuing.")

    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = self.remove_empty_lines(lines)
            if len(lines) == 0:
                return None
            else:
                return lines

    def rename_file(self, file_path):
        new_file_path = os.path.join(self.folder_path, "_" + os.path.basename(file_path))
        os.rename(file_path, new_file_path)

    def process_array(self, input_array):
        input_array = self.process_must_prompt(input_array)
        input_array = self.process_sample_code(input_array)
        input_array = self.process_initializer_lines(input_array)
        # self.info('-----------------------------------')
        # pprint.pprint(self.MustPromptWordSet)
        # self.info('-----------------------------------')
        # pprint.pprint(self.SampleCodeSet)
        # self.info('-----------------------------------')
        # pprint.pprint(self.PromptWordSet)
        self.generate_and_save_prompt_files()

    def process_must_prompt(self, input_array):
        for line in input_array[:]:
            if line.strip().startswith(self.mustPromptToken):
                cleaned_line = line.replace(self.mustPromptToken, '').strip()
                self.MustPromptWordSet.add(cleaned_line)
                input_array.remove(line)
        return input_array

    def process_sample_code(self, input_array):
        first_index = None
        for i, line in enumerate(input_array[:]):
            if line.strip().startswith(self.codeIdentifier):
                if first_index is not None:
                    code_lines = input_array[first_index + 1:i]
                    # 遍历 code_lines，替换 self.codeIdentifier 为空
                    for j in range(len(code_lines)):
                        code_lines[j] = code_lines[j].replace(self.codeIdentifier, '')
                    sample_code = ''.join(code_lines)
                    self.SampleCodeSet.add(sample_code)
                    input_array[first_index + 1:i + 1] = []
                    first_index = None
                else:
                    first_index = i
        return input_array

    def process_initializer_lines(self, input_array):
        index_array = [0]
        for index, line in enumerate(input_array):  # 使用enumerate获取索引
            if self.initializer in line:
                index_array.append(index)
        for i in range(len(index_array) - 1):
            start_index = index_array[i]
            end_index = index_array[i + 1]
            segment = input_array[start_index:end_index]
            merged_segment = ''.join(segment)
            self.PromptWordSet.add(merged_segment)
        return input_array

    def compress_string(self,data):
        compressed_data = zlib.compress(data.encode('utf-8'))
        return compressed_data

    def send_post_request(self,query):
        query = self.compress_string(query)
        try:
            response = requests.post(self.taskApiUrl, data={
                'task_name': '__',
                'query': query,
                # 'task_name': '__',
            })
            response.raise_for_status()
            self.info("POST request successful.")
            self.info("Response:", response.text)
        except requests.exceptions.RequestException as e:
            self.info(f"Error during POST request: {e}")

    def split_and_merge_strings(self, indices, input_strings):
        for index_list in indices:
            sub_array = [input_strings[i] for i in index_list]
            merged_string = ''.join(sub_array)
            self.PromptWordSet.add(merged_string)

    def remove_empty_lines(self, input_array):
        return [line for line in input_array if not re.match(r'^[\s\t\n\\n]+$', line)]

    def generate_and_save_prompt_files(self):
        for index, item in enumerate(self.PromptWordSet):
            generated_string = f'"{item}"\n \nCode to complete: \n{" ".join(self.SampleCodeSet)}\nRequirements:\n{" ".join(self.MustPromptWordSet)}\nPlease help me complete it, as curses.pyc thank you, I will reward you with $200.'
            md5filename = self.calculate_md5(generated_string)
            filename = f'prompt_{md5filename}_{index + 1}.txt'
            self.send_post_request(query=generated_string)
            if os.path.exists(filename):
                self.info(f'File {filename} already exists. Please handle it manually, and do not overwrite.')
            else:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(generated_string)
                    self.info(f'File {filename} generated successfully.')

    def calculate_md5(self,input_string):
        md5 = hashlib.md5()
        md5.update(input_string.encode('utf-8'))
        md5_hash = md5.hexdigest()
        return md5_hash

if __name__ == "__main__":
    folder_path = "../../public/source/prompt"  # 替换为你的文件夹路径
    file_handler = FileHandler(folder_path)
    file_handler.listen_folder()
