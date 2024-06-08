import os
import re
import datetime
from pycore.base.base import Base
from pycore.utils_linux import file, filefilter, strtool
from pycore.practicals_linux import gittool
from pycore.globalvar.lang_types import lang_types
from pycore.threads import ziptask
import time
JOB_REMOTE_DIR = "\\\\192.168.100.5\\web\\jobs"
PUBLISH_REMOTE_DIR = f"{JOB_REMOTE_DIR}\\tasks"
include_folders = ["script"]
        
class Release(Base):
    TASK_KEYWORD = "#TODO"
    max_file_max = 10 #mb

    def contains_task_keyword(self, content):
        return self.TASK_KEYWORD in content

    def get_task_language(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        for lang, details in lang_types.items():
            if details["ext"] == ext:
                return lang
        return ""

    def extract_tasks(self, content, file_path,rootDir):
        tasks = []
        lines = content.split('\n')
        task_block = []
        inside_task_block = False

        def get_task_info(task_block):
            task_info = {
                'number': 999,
                'description': '',
                'file': file_path,
                'relative_file': os.path.relpath(file_path,rootDir),
                'language': self.get_task_language(file_path),
                'release_date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            }
            first_line = task_block[0]
            match = re.search(rf'{self.TASK_KEYWORD}\s*(\d*)\s*(.*)', first_line)
            if match:
                task_info['number'] = int(match.group(1)) if match.group(1).isdigit() else 999
                task_info['description'] = match.group(2).strip()
            task_info['description'] += '\n'.join(task_block[1:])
            return task_info

        for line in lines:
            if self.TASK_KEYWORD in line:
                if task_block:
                    tasks.append(get_task_info(task_block))
                    task_block = []
                inside_task_block = True
            if inside_task_block:
                task_block.append(line)
                if not re.match(r'^[\u4e00-\u9fa5]', line):
                    inside_task_block = False

        if task_block:
            tasks.append(get_task_info(task_block))


        return tasks

    def get_framework(self):
        return ""

    def publis_link_task_quest_markers(self,task_info):
        task_batch = task_info["task_batch"]
        task_batch_id = task_info["task_batch_id"]
        task_quest_markers_file = f"{JOB_REMOTE_DIR}/task_quest_markers.json"
        task_quest_markers = file.read_json(task_quest_markers_file)
        links = task_quest_markers.get("links")
        if not links:
            task_quest_markers = {
                "links":{}
            }
        task_quest_markers["links"][task_batch_id] = task_batch
        file.save_json(task_quest_markers_file,task_quest_markers)


    def publis_remote(self,publish_dir,task_info):
        task_batch = task_info["task_batch"]
        remote_dir = f"{PUBLISH_REMOTE_DIR}/{task_batch}"
        task_filename = f"{task_batch}.zip"
        task_zip = f"{remote_dir}/{task_filename}"
        task_info["task_filename"] =task_filename
        task_info_file = os.path.join(remote_dir, "task_info.json")
        self.warn("Waiting for git initialization to complete...")
        time.sleep(5)
        os.makedirs(remote_dir, exist_ok=True)
        ziptask.add_task(publish_dir,task_zip,is_compress=True)
        file.save_json(task_info_file,task_info)
        self.publish_task_id(remote_dir, task_info)
        self.publis_link_task_quest_markers(task_info)

    def publish_clear(self):
        pass

    def publish_tasks(self, task_info):
        task_name = task_info["task_name"]
        task_batch = task_info["task_batch"]
        task_batch_id = task_info["task_batch_id"]
        task_list = task_info["task_list"]
        publish_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        publish_dir = f"D:/temp/TaskReleaseDirectory/{task_batch}"
        git_dir = f"{publish_dir}/{task_name}"

        for task in task_list:
            relative_path = task['relative_file']
            target_path = os.path.join(publish_dir, relative_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            file.copy(task['file'], target_path)


        gittool.initialize_git_repo(git_dir,True)
        gittool.git_add_and_commit(git_dir)

        self.publish_task_id(publish_dir,task_info)
        self.publis_remote(publish_dir,task_info)

    def publish_task_id(self,publish_dir,task_info):

        task_batch_id = task_info["task_batch_id"]
        task_batch_id_file = os.path.join(publish_dir, f"Task-ID_{task_batch_id}")
        chinese_task_batch_id_file = os.path.join(publish_dir, f"任务-ID_{task_batch_id}")
        file.save(task_batch_id_file,f"ID:\n{task_batch_id}")
        file.save(chinese_task_batch_id_file,f"ID:\n{task_batch_id}")


    def start(self, rootDir="D:/programing"):
        filtered_files = filefilter.filter(rootDir, include_folders=include_folders)

        num_files = len(filtered_files)
        self.info(f"Found {num_files} files")
        self.info("Preparing to publish tasks.")

        relative_files = [os.path.relpath(f, rootDir) for f in filtered_files]
        self.info(f"A total of {len(relative_files)} files were found")
        grouped_files = {}
        all_task_queue = []

        for relative_file in relative_files:
            parts = relative_file.split(os.path.sep)
            group_name = parts[0]

            if group_name not in grouped_files:
                grouped_files[group_name] = []
            grouped_files[group_name].append(relative_file)

        for group_name, paths in grouped_files.items():
            self.info(f"Group name: {group_name},files:{len(paths)}")
            group_task_queue = []
            for path in paths:
                absolute_path = os.path.join(rootDir, path)
                file_size = file.get_size(absolute_path,"m")
                if file_size > self.max_file_max:
                    self.info(f"Skip Big file : {file_size} Mb / {absolute_path}")
                    continue
                try:
                    content = file.read_text(absolute_path)
                    if self.contains_task_keyword(content):
                        self.info(f"File contains keyword '{self.TASK_KEYWORD}': {absolute_path}")
                        tasks = self.extract_tasks(content, absolute_path,rootDir)
                        self.success(f"extract_tasks Extraction successful")
                        for task in tasks:
                            group_task_queue.append(task)
                            all_task_queue.append(task)
                        self.success(f"The task unit queue was added successfully")
                except Exception as e:
                    self.info(f"Error reading file {absolute_path}: {e}")

            group_task_queue.sort(key=lambda x: x['number'])
            task_batch = f"{group_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            task_info = {
                "task_list": group_task_queue,
                "task_name": group_name,
                "task_batch": task_batch,
                "task_id": strtool.md5(group_name),
                "task_batch_id": strtool.md5(task_batch),
                "task_release_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "task_language": list(set(task['language'] for task in group_task_queue)),
                "framework": self.get_framework(),
                "total_tasks": len(group_task_queue),
                "estimated_code_generation": sum(len(task['description']) for task in group_task_queue) * 1,
                "task_zip": "",
                "task_claim": {
                    "claim_records": {},
                    "claim_statistics": 0,
                    "last_claim_time": None,
                },
                "task_submit": {
                    "submit_records": {},
                    "submit_statistics": 0,
                    "last_submit_time": None,
                },
                "task_review": {
                    "review_records": {},
                    "review_statistics": 0,
                    "last_review_time": None,
                }
            }
            self.pprint(task_info)
            self.publish_tasks(task_info)
        all_task_queue.sort(key=lambda x: x['number'])
        return grouped_files

release = Release()