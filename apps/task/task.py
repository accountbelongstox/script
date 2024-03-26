import hashlib
# import json
import os
from time import time
from datetime import datetime
from pycore.base.base import Base
from pycore.utils import http, file,strtool
from pycore.practicals import env

class TaskManager(Base):
    task_name = "ai"
    task_list = {}
    namespace = "official"
    default_api_url = "https://task.local.12gm.com:905/task"
    complete_task_list = {}
    current_prompt = None
    current_key = None

    def __init__(self):
        self.default_backup_dir = file.resolve_path("out/prompt_automation/")
        self.task_cache_dir = file.resolve_path("out/task_cache/")
        self.task_done_cache_dir = file.join(self.task_cache_dir, "done")
        file.mkdir(self.default_backup_dir)
        file.mkdir(self.task_cache_dir)
        pass

    def task_is_empty(self):
        return not bool(self.task_list)

    def get_api_url(self):
        api_url = env.get_env("TASK_URL")
        if api_url == "":
            return self.default_api_url
        return api_url

    def post(self, action, data=None):
        api_url = self.get_api_url()
        response = http.post(api_url, {
            "action": action,
            **data
        }, json=True)
        return response

    def task_len(self):
        return len(self.task_list)

    def fetch_task(self):
        task_data = {
            "task_name": self.task_name,
            "namespace": self.namespace,
        }
        result = self.post(action="get_tasks", data=task_data)
        try:
            status = result.get("status")
            if status == "success":
                tasks_object = result.get("task")
                tasks = tasks_object.get("list")
                if tasks:
                    new_task_count = 0
                    for key, item in tasks.items():
                        if key not in self.task_list:
                            self.task_list[key] = item
                            new_task_count += 1
                            self.success(f"Get a task as {key}")
                    self.task_list = dict(sorted(self.task_list.items(), key=lambda x: x[1]['group']))
                    self.success(f"Some tasks({str(new_task_count)}) have been obtained and sorted by group.")
                else:
                    self.warn(f"Not fetch a few new tasks.")
            else:
                self.warn(f"Failed to get tasks.")
        except Exception as e:
            # Handle any unexpected exceptions
            self.warn(f"An unexpected error occurred: {str(e)}")

    def print_task_groups(self):
        sorted_tasks = sorted(self.task_list.values(), key=lambda x: x['group'])
        self.info("The tasks order of the current group is.:")
        for task in sorted_tasks:
            self.success(task['group'])

    def put_task(self, code_pathname, content, group="default"):
        tid = hashlib.md5(str(code_pathname).encode()).hexdigest()
        cache_file_path = os.path.join(self.task_cache_dir, "task_cache.json")
        cache_file_path = file.resolve_path(cache_file_path)
        cached_data = file.read_json(cache_file_path)
        group = group or "default"
        if tid in cached_data:
            self.success(f"Task with tid {tid} already submitted. Skipping.")
            return
        task_data = {
            "action": "add",
            "task_name": self.task_name,
            "group": group,
            "name": tid,
            "namespace": self.namespace,
            "task_content": content,
            "task_path": code_pathname,
            "id": tid,
        }
        result = self.post(action="add", data=task_data)
        status = result.get("status")
        message = result.get("message")
        if status == "success":
            submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cached_data[tid] = {
                "submission_time": submission_time,
                "submitted": True,
                "task_entity": task_data,
            }
            file.save_json(cache_file_path, cached_data)
            self.success(message)
        else:
            self.warn(message)

    def save_done_to_cache(self, filename, content,task_entity=None):
        if filename == None:
            filename = strtool.md5(content)
        filename = filename+".json"
        new_filename = os.path.join(self.task_done_cache_dir, filename)
        file.save_json(new_filename, content)
        self.success(f"Save the task-complete. Content length:{len(strtool.to_str(content))}. direct : {new_filename}.")

    def get_done_from_cache(self, filename):
        filename = filename+".json"
        file_path = os.path.join(self.task_done_cache_dir, filename)
        if os.path.exists(file_path):
            return file.read_json(file_path)
        else:
            self.warn(f"File '{filename}' not found in cache.")
            return None

    def pop_task(self):
        if self.task_list:
            for key, item in self.task_list.items():
                return key, item
        else:
            return None, None

    def print_remaining_tasks(self):
        remaining_tasks = len(self.task_list)
        return remaining_tasks

    def get_current_key(self):
        return self.current_key

    def set_current_key(self, key):
        self.current_key = key

    def get_current_prompt(self):
        return self.current_prompt

    def set_current_prompt(self, prompt):
        self.current_prompt = prompt

    def set_complete_task(self, complete_content):
        key = self.get_current_key()
        if key in self.task_list:
            self.task_list[key]["complete_content"] = complete_content
            self.success(f'Task "{key}" marked as complete with content: {complete_content}')
        else:
            self.warn(f'Task "{key}" not found. Unable to mark as complete.')
        task_entity = self.task_list.get(key)
        self.save_done_to_cache(key, complete_content, task_entity)

    def put_complete_and_pop(self, key):
        completed_task = self.task_list.pop(key)
        self.save_prompt_complete_content(completed_task)
        self.info("completed_task")
        self.info(completed_task)
        self.post("complete", completed_task)
        return True

    def is_complete(self, key):
        complete_content = self.task_list[key].get("complete_content")
        if complete_content is not None:
            return True
        return False

    def get_task_details(self, task_id):
        md5_id = hashlib.md5(str(task_id).encode()).hexdigest()
        data = {
            "action": "get_task",
            "id": md5_id,
        }
        response = self.post(data=data)
        return response.get("details")

    def save_prompt_complete_content(self, complete_task):
        complete_content = complete_task.get("complete_content")
        id = complete_task.get("id")
        namespace = complete_task.get("namespace")
        name = complete_task.get("name")
        prompt = self.get_current_prompt()
        md5_id = hashlib.md5(str(prompt).encode()).hexdigest()
        timestamp = int(time())
        prompt_filename = f"{md5_id}_prompt_{timestamp}.json"
        content_filename = f"{md5_id}_complete_content_{timestamp}.json"
        prompt_path = os.path.join(self.default_backup_dir, prompt_filename)
        content_path = os.path.join(self.default_backup_dir, content_filename)
        file.save(prompt_path, prompt)
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


task = TaskManager()
