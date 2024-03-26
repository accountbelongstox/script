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
from kernel.utils import file, arr, keyb, tool
from kernel.threads import ComThread
from kernel.practicals import watch
from kernel.base.base import Base
=======
# from applications.prompt.mdous.analyze.analyze import analyze
from pycore.utils import arg
from pycore.utils import file, arr, keyb, tool
from pycore.threads import ComThread
from pycore.practicals import watch
from pycore._base import Base
>>>>>>> origin/main
from apps.prompt.mdous.analyze.config_weights import config_weights
from apps.prompt.config.lang_config import lang_config
from apps.prompt.mdous.resolve_prompt.create_prompt import create_prompt

class promptMain(Base):
    watch_instances = {}
    scan_project = False

    def __init__(self):
        self.root_dir = file.get_root_dir()
        self.start_time = datetime.now()
        self.reset_time = datetime.now()
        self.threads = {}

    def start(self):
        keyb.listen_group("ctrl+`", self.scan_project_root, 1)
        th = ComThread(target=self.watch)
        self.threads["main_run"] = th
        th.start()

    def watch(self):
        while True:
            if self.scan_project:
                self.warn("Scanning in progress. Waiting 2 seconds...")
            else:
                self.scan_project_root()
            time.sleep(10)

    def scan_project_root(self):
        if self.scan_project:
            self.warn("Scanning in progress. Waiting 2 seconds...")
            time.sleep(2)
        self.scan_project = True
        pprojects = pConfig.get_pprojects()
        common_projects = pprojects.get("common")
        for com_config in common_projects:
            if isinstance(com_config, dict) and "root" in com_config:
                root_path = com_config["root"]
                language = com_config.get("language")
                framework = com_config.get("framework")
                if file.is_absolute_path(root_path):
                    p_config = pConfig.get_config(root_path)
                    if root_path not in self.watch_instances:
                        all_filters = config_weights.get_all_filters(root_path, p_config, com_config)
                        watch_instance = watch(folder_path=root_path, all_filters=all_filters, scan_interval_seconds=5)
                        self.watch_instances[root_path] = watch_instance
                    else:
                        watch_instance = self.watch_instances[root_path]
                    is_changed = watch_instance.start_monitoring()
                    changes = None
                    if is_changed == watch_instance.FIRST_SCAN:
                        changes = watch_instance.get_files()
                    elif is_changed == True:
                        changes = watch_instance.get_changes()
                    if changes != None:
                        self.resolve_project(root_path, changes, com_config, p_config)
                else:
                    self.warn(f"Warning: '{root_path}' is not an absolute path.")
            else:
                self.info("Invalid project format or missing 'root' attribute.")
        self.scan_project = False

    def resolve_project(self, root_path, code_paths, com_config, p_config=None):
        root_path = file.resolve_path(root_path)
        base_dir = root_path
        p_config = p_config or pConfig.get_config(root_path)
        default_prompts_dir = p_config.get("default_prompts_dir", "")
        prompts_dir = os.path.join(base_dir, default_prompts_dir)
        gpt_config = p_config.get("gpt", {})
        for code_path, modify_time in code_paths.items():
            must_prompt, apis, code_usage, generic_prompt, code_comments, text_text, text_raw_arr, text_pure_arr = usagemain.generate_prompts(
                code_path)
            code_pathname = file.remove_path(base_dir, code_path)
            ext = file.get_not_dot_ext(code_pathname)
            lang_map = lang_config.get_langconfig(ext)
            if code_comments != None:
                code_comments = arr.to_2d_list(code_comments)
                prompt_comments = create_prompt.get_prompt("promptCodeComments",p_config, com_config, lang_map,default_lang="zh")
                prompt_map_file.save_comment(prompts_dir, code_pathname, code_comments, prompt_comments,p_config,com_config, lang_map)
                # prompt_map_file.summarize(prompts_dir, code_pathname, code_comments, ext, gpt_config)
            if text_text != None:
                prompt_map_file.save_translate(prompts_dir, code_pathname, text_text, gpt_config)
            # if text_text != None:
            #     prompt_map_file.save_translate(prompts_dir, code_pathname, text_text, gpt_config)

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

prompt_main = promptMain()