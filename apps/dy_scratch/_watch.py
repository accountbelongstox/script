import os
# import re
import time
# import pprint
from datetime import datetime, timedelta
from apps.prompt.mdous.save.prompt_map import prompt_map_file
from apps.prompt.mdous.usage_code.code_prompts import usagemain
from apps.prompt.config.config import pConfig
<<<<<<< HEAD
# from apps.prompt.mdous.analyze.analyze import analyze
from kernel.utils import arg
from kernel.utils import file, arr, keyb
from kernel.threads import ComThread
from kernel.base.base import Base
=======
# from applications.prompt.mdous.analyze.analyze import analyze
from pycore.utils import arg
from pycore.utils import file, arr, keyb
from pycore.threads import ComThread
from pycore._base import Base
>>>>>>> origin/main

class promptMain(Base):
    def __init__(self):
        self.root_dir = file.get_root_dir()
        self.start_time = datetime.now()
        self.reset_time = datetime.now()
        self.threads = {}

    def watch(self):
        config = pConfig.get_config()
        maximum_running_seconds_per_day = config.get("maximum_running_seconds_per_day", 86400)
        maximum_per_account_per_day = config.get("maximum_per_account_per_day", 600)
        while True:
            if self.is_time_to_reset():
                self.reset_time = datetime.now()
                self.check_and_stop_threads()

            remaining_time = self.calculate_remaining_time(maximum_running_seconds_per_day)
            self.info(f"Remaining time: {remaining_time}")
            time.sleep(1)

    def is_time_to_reset(self,):
        config = pConfig.get_config()
        maximum_running_seconds_per_day = config.get("maximum_running_seconds_per_day", 86400)
        current_time = datetime.now()
        time_difference = current_time - self.reset_time
        return time_difference.total_seconds() >= maximum_running_seconds_per_day

    def calculate_remaining_time(self, maximum_running_seconds_per_day):
        current_time = datetime.now()
        elapsed_time = current_time - self.reset_time
        remaining_time = max(maximum_running_seconds_per_day - elapsed_time.total_seconds(), 0)
        return str(timedelta(seconds=remaining_time))

    def check_and_stop_threads(self):
        for thread_name, thread_instance in self.threads.items():
            if thread_instance.is_alive():
                thread_instance.stop()
                self.info(f"Thread '{thread_name}' forcibly stopped.")

    def start(self):
        keyb.listen_group("ctrl+`", self.print, 1)
        th = ComThread(target=self.watch)
        self.threads["main_run"] = th
        th.start()

    def scan_project_root(self):
        pprojects = pConfig.get_pprojects()
        common_projects = pprojects.get("common")
        for project in common_projects:
            if isinstance(project, dict) and "root" in project:
                root_path = project["root"]
                language = project.get("language")
                framework = project.get("framework")
                if not file.is_absolute_path(root_path):
                    self.warn(f"Warning: '{root_path}' is not an absolute path.")
                self.info(f"Root Path: {root_path}")
                self.resolve_project(root_path)
            else:
                self.info("Invalid project format or missing 'root' attribute.")

    def resolve_project(self, path):
        folder_path = file.resolve_path(path)
        base_dir = folder_path
        config = pConfig.get_config(base_dir)
        filter_file_starts_with = config.get("filterFileStartsWith", [])
        filter_folder_starts_with = config.get("filterFolderStartsWith", [])
        filter_prompt_extension = config.get("filterExtension", [])
        default_prompts_dir = config.get("default_prompts_dir", [])
        prompts_dir = os.path.join(base_dir, default_prompts_dir)
        filter_folder = config.get("filterFolder", [])
        gpt_config = config.get("gpt", {})
        for root, dirs, files in os.walk(folder_path):
            for folder_name in list(dirs):
                folder_path = os.path.join(root, folder_name)
                if self.should_skip(folder_name, filter_folder_starts_with, filter_folder):
                    folder_name = os.path.basename(folder_path)
                    self.info(f"Skipping folder: {folder_name}, as  {folder_path}")
                    dirs.remove(folder_name)
                    continue
            for file_name in list(files):
                file_path = os.path.join(root, file_name)
                if self.should_skip(file_name, filter_file_starts_with):
                    file_name = os.path.basename(file_path)
                    self.info(f"Skipping file-name: {file_name}, as {file_path}")
                    continue
                file_extension = os.path.splitext(file_name)[1]
                if self.should_skip(file_extension, filter_prompt_extension):
                    self.info(f"Skipping extension: {file_extension}, as : {file_path}")
                    continue
                code_path = file_path
                # self.info(file_path)
                must_prompt, apis, code_usage, generic_prompt, code_comments = usagemain.generate_prompts(code_path)
                if code_comments != None:
                    code_comments = arr.to_2d_list(code_comments)
                    code_pathname = file.remove_path(base_dir, code_path)
                    ext = file.get_not_dot_ext(code_pathname)
                    prompt_map_file.save_comment(prompts_dir, code_pathname, code_comments, ext, gpt_config)

                    # TODO
                    # self.info("code_comments:",code_comments)

    def should_skip(self, item, starts_with_filters, exact_match_filters=None):
        exact_match_filters = exact_match_filters or []
        for filter_item in starts_with_filters:
            if item.startswith(filter_item):
                return True
        if item in exact_match_filters:
            return True
        return False

    def analize_path(self, code_path=None):
        if code_path == None:
            arg.init([
                ('--path', str, "Get the file path that needs to be parsed."),
            ])
            code_path = arg.get_str_arg("path")
        if code_path == None:
            self._warn("Please provide curses.pyc valid file path using the '--path' argument.")
        return usagemain.generate_prompts(code_path)

    def listen_folder(self):
        while True:
            time.sleep(5)
            files = os.listdir(self.folder_path)
            find_new = False
            for file in files:
                file_path = os.path.join(self.folder_path, file)
                if os.path.isfile(file_path) and not file.startswith("_"):
                    if not file_path.startswith("_"):
                        self.info("Found curses.pyc new file: " + file + ", parsing.")
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

    def _warn(self, msg):
        self.info(f"\033[91mWarning: {msg}\033[0m")

    def _success(self, msg):
        self.info(f"\033[92mSuccess: {msg}\033[0m")
