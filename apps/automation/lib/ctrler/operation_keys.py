from pycore.utils import file
from pycore.practicals import env
from pycore.base import Base
import os
DEFAULT_THRESHOLD = 0.9
autoEnv = env.load("apps/automation")

evnfile = autoEnv.get_local_env_file()
class OperCode(Base):
    icons_env_checked = False

    def check_icons_env(self, icons_dir):
        need_set_variables = []
        try:
            if self.icons_env_checked:
                return
            file_list = os.listdir(icons_dir)
            for file_name in file_list:
                file_path = os.path.join(icons_dir, file_name)
                if os.path.isfile(file_path):
                    env_name = os.path.splitext(file_name)[0]
                    env_val = autoEnv.get_env(env_name)
                    if env_val == "":
                        need_set_variables.append(env_name)
            self.icons_env_checked = True
            if need_set_variables:
                warning_message = "Environment variable(s) need to be set:"
                for env_name in need_set_variables:
                    warning_message += f"\n{env_name}={DEFAULT_THRESHOLD}"
                self.warn(warning_message)
        except Exception as e:
            self.warn(f"Error: {e}")

    def get_operate_code(self,key, mode='dark', ):
        GPT_MODE = autoEnv.get_env("GPT_MODE")
        if GPT_MODE != "":
            mode = GPT_MODE
        return self.find_key(mode, key)

    def find_key(self,mode, image_name):
        image_dir = file.resolve_path(mode, "apps/automation/icons/")
        self.check_icons_env(image_dir)
        if not os.path.exists(image_dir):
            self.info("The specified directory does not exist", image_dir)
            return None
        for root, _, files in os.walk(image_dir):
            for filename in files:
                if filename == f"{image_name}.png":
                    threshold = autoEnv.get_env(image_name)
                    if not threshold:
                        threshold = autoEnv.get_env("DEFAULT_THRESHOLD") or DEFAULT_THRESHOLD
                        self.warn(f"You need to define {image_name} environment variable for the key in the {evnfile}.")
                    return os.path.join(root, filename), float(threshold)
        self.info(f"Image named {image_name}.png not found")
        return None
oper_code = OperCode()
get_operate_code = oper_code.get_operate_code