# import os
from pycore.utils_linux import strtool
from apps.deploy.pyscript.provider.deployenv import env, compose_env,main_dir,wwwroot_dir
from pycore.base import Base

class Choice(Base):
    relative_settings = {}

    def __init__(self):
        pass

    def get_envs(self):
        return self.collection_settings()

    def collection_settings(self, settings=None, setting_name=""):
        if settings:
            self.relative_settings[setting_name] = settings

    def set_and_collection_envs(self, settings, setting_name="", show=False):
        if not settings:
            return
        self.collection_settings(settings, setting_name)
        if setting_name != "":
            p_setting_name = strtool.to_blue(setting_name)
            p_enter = strtool.to_yellow("<Enter>") if not show else strtool.to_blue("-------")
            p_skip = strtool.to_blue(" to skip  ") if not show else strtool.to_blue("--------")
            pre_str = strtool.to_blue("-------")
            print(f"\n{pre_str}  config:{p_setting_name}, press{p_enter}{p_skip}{pre_str}")
        green_color = '\033[92m'
        end_color = '\033[0m'
        for item in settings:
            key = item[0]
            val = env.get_env(key)
            if val == "":
                val = item[1] if len(item) > 1 else ""
            if key.upper().endswith(('PWD', 'PASSWORD', 'PASSWORD')):
                if not val:
                    val = strtool.create_password(12)

            p_key = strtool.extend(key)
            input_nse = ",Input New?:" if show == False else ""
            prompt = f"{p_key}\t:{green_color}{val}{end_color} {input_nse}"
            if not show:
                new_val = input(prompt).strip()
            else:
                print(prompt)
                new_val = ""
            if new_val != "":
                val = new_val
                p_key = strtool.to_red(p_key)
                p_val = strtool.to_red(val)
                print(f"The {p_key} has been set to {p_val}")
            env.set_env(key, val)

    def get_input(self, prompt, default_value="", original_value="", allow_empty=True):
        green_color = '\033[92m'
        red_color = '\033[91m'
        end_color = '\033[0m'
        
        skip_text = ""
        if allow_empty and default_value != "":
            skip_text = "Press Enter to skip."
            skip_text = strtool.to_red(skip_text)
            new_value = default_value
            
        default_value_alerttext = ""
        if default_value:
            default_text = strtool.to_green(default_value)
            default_value_alerttext = f" [Default: {default_text}]"
        
        input_text = f"{prompt} {default_value_alerttext}{skip_text}: "
        new_value = input(input_text).strip()


        while not allow_empty and new_value == "":
            self.info("Value cannot be empty.")
            new_value = self.get_input(prompt, default_value, original_value, allow_empty)

        if original_value and new_value != original_value:
            new_value = red_color + new_value + end_color

        return new_value

        

    

choice = Choice()
