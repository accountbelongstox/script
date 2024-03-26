import os
from kernel.utils_prune import file, arr, sysarg
from kernel.base.base import Base

class Env(Base):
    main_env_file = None
    local_env_file = None
    root_dir = ""
    annotation_symbol = "#"
    example_env_file = ""

    def __init__(self, root_dir=None, env_name=".env", delimiter="="):
        if root_dir == None:
            root_dir = file.get_root_dir()
        else:
            root_dir = file.resolve_path(root_dir)
        self.set_root_dir(root_dir, env_name, delimiter=delimiter)

    def set_delimiter(self, delimiter="="):
        self.delimiter = delimiter

    def example_to(self, example_path):
        env_file = example_path.replace("-example", "")
        env_file = env_file.replace("_example", "")
        env_file = env_file.replace(".example", "")
        self.merge_env(env_file, example_path)

    def set_root_dir(self, root_dir, env_name=".env", delimiter="="):
        self.set_delimiter(delimiter)
        self.root_dir = root_dir
        self.local_env_file = os.path.join(self.root_dir, env_name)
        example_env_file = os.path.join(self.root_dir, env_name + '_example')
        if not file.is_file(example_env_file):
            example_env_file = os.path.join(self.root_dir, env_name + '-example')
        if not file.is_file(example_env_file):
            example_env_file = os.path.join(self.root_dir, env_name + '.example')
        self.example_env_file = example_env_file
        self.get_local_env_file()

    def load(self, root_dir, env_name=".env", delimiter="="):
        return Env(root_dir=root_dir, env_name=env_name, delimiter=delimiter)

    def get_local_env_file(self):
        if not file.isFile(self.local_env_file):
            file.save(self.local_env_file, "")
        self.merge_env(self.local_env_file, self.example_env_file)
        return self.local_env_file

    def get_env_file(self):
        return self.local_env_file

    def merge_env(self, env_file, example_env_file):
        if file.is_file(example_env_file) == False:
            return
        example_arr = self.read_env(example_env_file)
        local_arr = self.read_env(env_file)
        added_keys = []
        example_dict = arr.arr_to_dict(example_arr)
        local_dict = arr.arr_to_dict(local_arr)
        for key, value in example_dict.items():
            if key not in local_dict:
                local_dict[key] = value
                added_keys.append(key)
        if len(added_keys) > 0:
            self.success(f"Env-Update env: {env_file}")
            local_arr = arr.dict_to_arr(local_dict)
            self.save_env(local_arr, env_file)
        for added_key in added_keys:
            self.success(f"Env-Added key: {added_key}")

    def read_key(self, key):
        with open(self.main_env_file, 'r') as file:
            for line in file:
                k, v = line.partition(self.delimiter)[::2]
                if k.strip() == key:
                    return v.strip()
        return None

    def replace_or_add_key(self, key, val):
        updated = False
        lines = []
        with open(self.main_env_file, 'r') as file:
            for line in file:
                k, v = line.partition(self.delimiter)[::2]
                if k.strip() == key:
                    line = f"{key}{self.delimiter}{val}\n"
                    updated = True
                lines.append(line)

        if not updated:
            lines.append(f"{key}{self.delimiter}{val}\n")
        content = "\n".join(lines)
        file.save(self.main_env_file, content, overwrite=True)

    def read_env(self, file_path=None):
        if file_path is None:
            file_path = self.local_env_file
        result = []
        lines = file.read_lines(file_path)
        for line in lines:
            line_values = [value.strip() for value in line.split(self.delimiter)]
            result.append(line_values)
        return result

    def get_envs(self, file_path=None):
        return self.read_env(file_path=file_path)

    def save_env(self, env_arr, file_path=None):
        if file_path == None:
            file_path = self.local_env_file
        filtered_env_arr = [subarr for subarr in env_arr if len(subarr) == 2]
        formatted_lines = [f'{subarr[0]}{self.delimiter}{subarr[1]}' for subarr in filtered_env_arr]
        result_string = '\n'.join(formatted_lines)
        file.save(file_path, result_string, overwrite=True)

    def set_env(self, key, value, file_path=None):
        if file_path is None:
            file_path = self.local_env_file
        env_arr = self.read_env(file_path=file_path)
        key_exists = False
        for subarr in env_arr:
            if subarr[0] == key:
                subarr[1] = value
                key_exists = True
                break
        if not key_exists:
            env_arr.append([key, value])
        self.save_env(env_arr, file_path)

    def is_env(self, key, file_path=None):
        is_arg = sysarg.is_arg("is_env")
        val = self.get_env(key=key, file_path=file_path)
        if val == "":
            if is_arg == True:
                print("False")
            return False
        if is_arg == True:
            print("True")
        return True

    def get_env(self, key, file_path=None):
        # is_arg = sysarg.is_arg("get_env")
        if file_path is None:
            file_path = self.local_env_file
        env_arr = self.read_env(file_path=file_path)
        for subarr in env_arr:
            if subarr[0] == key:
                return subarr[1]
        return ""
