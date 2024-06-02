import subprocess
import re
import sys
from datetime import datetime, timedelta
import os

# Command:
# python .\added_code.py ./ 2 2024-3-1 2024-6-2
# Parameter 1: Path
# Parameter 2: Mode
# Parameter 3: Start date
# Parameter 4: End date



class GitLogProcessor:
    current_dir = os.getcwd()
    total_lines = 0
    total_price = 0
    added_price = 0
    roles = ["developer", "tester", "architect"]

    def __init__(self, cwd=".", since=None, until=None,lv=1,role="developer",mode=2):
        self.rules = {
            "include": {
                "folders": {"enabled": True, "values": [ "pycore", "csharp"]},
                "filenames": {"enabled": True, "values": []},
                "file_starts": {"enabled": True, "values": []},
                "file_ends": {"enabled": True, "values": []},
                "folder_starts": {"enabled": True, "values": ["apps/deploy/shells/debian_12","apps/deploy/py_script"]},
                "folder_ends": {"enabled": True, "values": []},
                "any_subdir": {"enabled": True, "values": []}
            },
            "exclude": {
                "folders": {"enabled": True, "values": ["public", "__rm__"]},
                "filenames": {"enabled": True, "values": ["yarn.lock", "package-lock.json", "pnpm-lock.yaml"]},
                "file_starts": {"enabled": True, "values": ["temp", "test"]},
                "file_ends": {"enabled": True, "values": ["_backup", "_old", ".txt", ".bin", ".po",
                                                          ".sln",
                                                          ".pot",
                                                          ".cache",
                                                          ".assets.json",
                                                          ".csproj"
                                                          ]},
                "folder_starts": {"enabled": True, "values": ["tmp", "cache"]},
                "folder_ends": {"enabled": True, "values": ["_data", "_archive"]},
                "any_subdir": {"enabled": True,
                               "values": ["node_modules", ".vs", "build", "bin", "stylesheet", "_misc", "webfonts",
                                          "static",
                                          "nginx_ui", "nvm_node", "pm2_node18", "nvm_node", "__rm__",
                                          "openai_assistant", "pm2", "php", "nginx", "bt_template", "nut", "library",
                                          "laravel", "prompt", "ncss", "momo", "dy_scratch",
                                          "prompt",
                                          "Debug",
                                          "Release",
                                          "prompt",
                                          "thread"
                                          ]}
            }
        }

        for rule_type in self.rules:
            for rule_name, rule_data in self.rules[rule_type].items():
                rule_data["matches"] = []
                rule_data["non_matches"] = []

        time_due = self.getDates("%Y-%m-%d", [since, until], 2)
        self.since = time_due[0]
        self.until = time_due[1]
        self.cwd = self.getPath(cwd)
        # Mode switch: 0 = include, 1 = exclude, 2 = both
        int_params = self.get_params(int)
        self.mode = int_params[0] if int_params and len(int_params) > 0 else mode
        self.level = int_params[1] if int_params and len(int_params) > 1 else lv
        self.role = self.getRole(role)
        self.unitPrice = self.getUnitPrice()
        self.init_rules_enable()
        self.print_mode_logic()
        self.added_lines = 0
        self.removed_lines = 0

        self.green_group = []
        self.yellow_group = []
        self.red_group = []

    def organize_logic(self):
        result = {
            "added_lines": self.added_lines,
            "removed_lines": self.removed_lines,
            "total_lines": self.total_lines,
            "total_price": self.total_price,
            "added_price": self.added_price,
        }
        os.chdir(self.cwd)
        git_isok = self.check_git_directory()
        if git_isok == True:
            git_log_command = self.get_git_log_command()
            cmdresult = subprocess.run(git_log_command, capture_output=True, text=True)
            for line in cmdresult.stdout.splitlines():
                if line:
                    lines = line.split()
                    add = lines[0]
                    remove = lines[1]
                    fpath = self.normalize_path(lines[2])
                    path_parts = re.split(r'[\\/]+', fpath)

                    if add == '-' or remove == '-':
                        continue

                    add = int(add)
                    remove = int(remove)
                    folder = path_parts[0]
                    filename = path_parts[-1]

                    if self.mode == 0:
                        should_include = self.match_include_rules(fpath, folder, filename, path_parts)
                        if should_include:
                            self.apply_rule_logic(add, remove, fpath, folder)

                    elif self.mode == 1:
                        should_exclude = self.match_exclude_rules(fpath, folder, filename, path_parts)
                        if not should_exclude:
                            self.apply_rule_logic(add, remove, fpath, folder)

                    elif self.mode == 2:
                        should_include = self.match_include_rules(fpath, folder, filename, path_parts)
                        should_exclude = self.match_exclude_rules(fpath, folder, filename, path_parts)
                        if should_include and not should_exclude:
                            self.apply_rule_logic(add, remove, fpath, folder)

            self.total_lines = self.added_lines - self.removed_lines
        os.chdir(self.current_dir)
        self.print_group_info(self.green_group, self.Colors.GREEN)
        self.print_group_info(self.yellow_group, self.Colors.YELLOW)
        self.print_group_info(self.red_group, self.Colors.RED)
        self.print_rules_info()
        self.added_price = self.calculate_total_price(self.added_lines,"added_price")
        self.total_price = self.calculate_total_price(self.total_lines,"total_price")
        self.print_info(
            f"role\t: {self.role}\n" +
            f"level\t: {self.level}\n" +
            f"added lines\t: {self.added_lines}\n" +
            f"added price\t: {self.added_price} (¥)\n" +
            f"removed lines\t: {self.removed_lines}\n" +
            f"total lines\t: {self.total_lines}\n" +
            f"total price\t: {self.total_price} (¥)\n",
            self.Colors.GREEN)
        return result

    def calculate_total_price(self,total_lines,calculate_name = "total"):
        statistical_unit = self.unitPrice[0]
        thousand_price = self.unitPrice[1]
        per_price = thousand_price / statistical_unit
        thousands_count = total_lines // statistical_unit
        num_thousands = thousands_count * statistical_unit
        remainder_lines = total_lines - num_thousands
        thousands_price = thousands_count * thousand_price
        remainder_price = remainder_lines * per_price
        total_price = thousands_price + remainder_price
        print()
        print(f"-----------------{calculate_name}---------------\t")
        print("total_lines\t",total_lines)
        print("thousands_count\t",thousands_count)
        print("per_thousand_price\t",thousand_price)
        print("thousands_price\t",thousands_price)
        print("-\t")
        print("remainder_lines\t",remainder_lines)
        print("per_line_price\t",per_price)
        print("remainder_price\t",remainder_price)
        print("-\t")
        print("total_price\t",total_price)
        print("---------------------------------------\t")
        return total_price

    def getUnitPrice(self):
        base_price = 1000.00
        increments = {
            "developer": 10.00,
            "tester": 15.00,
            "architect": 20.00
        }
        base_developer_price = 50.00
        base_tester_price = 50.00
        base_architect_price = 50.00

        dev_price = base_developer_price + increments["developer"] * (self.level - 1)
        tester_price = base_tester_price + increments["tester"] * (self.level - 1)
        architect_price = base_architect_price + increments["architect"] * (self.level - 1)

        prices = (base_price, dev_price, tester_price, architect_price)

        if self.role == "developer":
            price = prices[1]
        elif self.role == "tester":
            price = prices[2]
        elif self.role == "architect":
            price = prices[3]
        else:
            price = 0

        return (prices[0], price)

    def check_git_directory(self):
        if not os.path.exists('.git'):
            self.print_info("\nError: No '.git' directory found in the specified directory.\n", self.Colors.RED)
            return False
        try:
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                self.print_info("\nError: The '.git' directory seems to be corrupted or not properly configured.\n",
                                self.Colors.RED)
                return False
        except Exception as e:
            self.print_info(f"\nError: Unable to access or check the '.git' directory: {e}\n", self.Colors.RED)
            return False
        self.print_info("\nSuccess: The '.git' directory is properly configured.\n", self.Colors.GREEN)
        return True

    def get_git_log_command(self):
        return [
            "git", "log",
            f"--since={self.since}",
            f"--until={self.until}",
            "--pretty=tformat:",
            "--numstat"
        ]

    def init_rules_enable(self):
        include_folders_values = self.rules["include"]["folders"]["values"]
        include_folder_starts_values = self.rules["include"]["folder_starts"]["values"]
        include_folder_ends_values = self.rules["include"]["folder_ends"]["values"]
        include_filenames_values = self.rules["include"]["filenames"]["values"]
        include_file_starts_values = self.rules["include"]["file_starts"]["values"]
        include_file_ends_values = self.rules["include"]["file_ends"]["values"]
        include_rules_any_subdir_values = self.rules["include"]["any_subdir"]["values"]

        # self.rules["include"]["folders"]["enabled"] = bool(self.rules["include"]["folders"]["enabled"]) and bool(
        #     include_folders_values)
        # self.rules["include"]["folder_starts"]["enabled"] = bool(
        #     self.rules["include"]["folder_starts"]["enabled"]) and bool(include_folder_starts_values)
        # self.rules["include"]["folder_ends"]["enabled"] = bool(
        #     self.rules["include"]["folder_ends"]["enabled"]) and bool(include_folder_ends_values)
        # self.rules["include"]["filenames"]["enabled"] = bool(self.rules["include"]["filenames"]["enabled"]) and bool(
        #     include_filenames_values)
        # self.rules["include"]["file_starts"]["enabled"] = bool(
        #     self.rules["include"]["file_starts"]["enabled"]) and bool(include_file_starts_values)
        # self.rules["include"]["file_ends"]["enabled"] = bool(self.rules["include"]["file_ends"]["enabled"]) and bool(
        #     include_file_ends_values)
        # self.rules["include"]["any_subdir"]["enabled"] = bool(self.rules["include"]["any_subdir"]["enabled"]) and bool(
        #     include_rules_any_subdir_values)

        exclude_folders_values = self.rules["exclude"]["folders"]["values"]
        exclude_folder_starts_values = self.rules["exclude"]["folder_starts"]["values"]
        exclude_folder_ends_values = self.rules["exclude"]["folder_ends"]["values"]
        exclude_filenames_values = self.rules["exclude"]["filenames"]["values"]
        exclude_file_starts_values = self.rules["exclude"]["file_starts"]["values"]
        exclude_file_ends_values = self.rules["exclude"]["file_ends"]["values"]
        exclude_rules_any_subdir_values = self.rules["exclude"]["any_subdir"]["values"]

        # self.rules["exclude"]["folders"]["enabled"] = bool(self.rules["exclude"]["folders"]["enabled"]) and bool(
        #     exclude_folders_values)
        # self.rules["exclude"]["folder_starts"]["enabled"] = bool(
        #     self.rules["exclude"]["folder_starts"]["enabled"]) and bool(exclude_folder_starts_values)
        # self.rules["exclude"]["folder_ends"]["enabled"] = bool(
        #     self.rules["exclude"]["folder_ends"]["enabled"]) and bool(exclude_folder_ends_values)
        # self.rules["exclude"]["filenames"]["enabled"] = bool(self.rules["exclude"]["filenames"]["enabled"]) and bool(
        #     exclude_filenames_values)
        # self.rules["exclude"]["file_starts"]["enabled"] = bool(
        #     self.rules["exclude"]["file_starts"]["enabled"]) and bool(exclude_file_starts_values)
        # self.rules["exclude"]["file_ends"]["enabled"] = bool(self.rules["exclude"]["file_ends"]["enabled"]) and bool(
        #     exclude_file_ends_values)
        # self.rules["exclude"]["any_subdir"]["enabled"] = bool(self.rules["exclude"]["any_subdir"]["enabled"]) and bool(
        #     exclude_rules_any_subdir_values)

    def match_include_rules(self, fpath, folder, filename, path_parts):
        should_include = False

        include_folders_enabled = self.rules["include"]["folders"]["enabled"]
        include_folder_starts_enabled = self.rules["include"]["folder_starts"]["enabled"]
        include_folder_ends_enabled = self.rules["include"]["folder_ends"]["enabled"]
        include_filenames_enabled = self.rules["include"]["filenames"]["enabled"]
        include_file_starts_enabled = self.rules["include"]["file_starts"]["enabled"]
        include_file_ends_enabled = self.rules["include"]["file_ends"]["enabled"]
        include_rules_any_subdir_enabled = self.rules["include"]["any_subdir"]["enabled"]

        is_include_rules_any_subdir = False if include_rules_any_subdir_enabled else True
        is_include_folders = False if include_folders_enabled else True
        is_include_folder_starts = False if include_folder_starts_enabled else True
        is_include_folder_ends = False if include_folder_ends_enabled else True
        is_include_filenames = False if include_filenames_enabled else True
        is_include_file_starts = False if include_file_starts_enabled else True
        is_include_file_ends = False if include_file_ends_enabled else True

        if include_rules_any_subdir_enabled:
            for part in path_parts:
                if (part in self.rules["include"]["any_subdir"]["values"]):
                    is_include_rules_any_subdir = True
                    break

        if include_folders_enabled:
            if folder in self.rules["include"]["folders"]["values"]:
                is_include_folders = True
                self.rules["include"]["folders"]["matches"].append(folder)
            else:
                self.rules["include"]["folders"]["non_matches"].append(folder)

        if include_folder_starts_enabled:
            for start in self.rules["include"]["folder_starts"]["values"]:
                if fpath.startswith(start):
                    is_include_folder_starts = True
                    self.rules["include"]["folder_starts"]["matches"].append(fpath)
                    break
            else:
                self.rules["include"]["folder_starts"]["non_matches"].append(fpath)

        if include_folder_ends_enabled:
            for end in self.rules["include"]["folder_ends"]["values"]:
                if fpath.endswith(end):
                    is_include_folder_ends = True
                    self.rules["include"]["folder_ends"]["matches"].append(fpath)
                    break
            else:
                self.rules["include"]["folder_ends"]["non_matches"].append(fpath)

        if include_filenames_enabled:
            if filename in self.rules["include"]["filenames"]["values"]:
                is_include_filenames = True
                self.rules["include"]["filenames"]["matches"].append(filename)
            else:
                self.rules["include"]["filenames"]["non_matches"].append(filename)

        if include_file_starts_enabled:
            for start in self.rules["include"]["file_starts"]["values"]:
                if filename.startswith(start):
                    is_include_file_starts = True
                    self.rules["include"]["file_starts"]["matches"].append(filename)
                    break
            else:
                self.rules["include"]["file_starts"]["non_matches"].append(filename)

        if include_file_ends_enabled:
            for end in self.rules["include"]["file_ends"]["values"]:
                if filename.endswith(end):
                    is_include_file_ends = True
                    self.rules["include"]["file_ends"]["matches"].append(filename)
                    break
            else:
                self.rules["include"]["file_ends"]["non_matches"].append(filename)

        if is_include_rules_any_subdir or is_include_folders or is_include_folder_starts or is_include_folder_ends \
                or is_include_filenames or is_include_file_starts or is_include_file_ends:
            should_include = True

        return should_include

    def match_exclude_rules(self, fpath, folder, filename, path_parts):
        should_exclude = False

        exclude_folders_enabled = self.rules["exclude"]["folders"]["enabled"]
        exclude_folder_starts_enabled = self.rules["exclude"]["folder_starts"]["enabled"]
        exclude_folder_ends_enabled = self.rules["exclude"]["folder_ends"]["enabled"]
        exclude_filenames_enabled = self.rules["exclude"]["filenames"]["enabled"]
        exclude_file_starts_enabled = self.rules["exclude"]["file_starts"]["enabled"]
        exclude_file_ends_enabled = self.rules["exclude"]["file_ends"]["enabled"]
        exclude_rules_any_subdir_enabled = self.rules["exclude"]["any_subdir"]["enabled"]

        is_exclude_rules_any_subdir = False if exclude_rules_any_subdir_enabled else True
        is_exclude_folders = False if exclude_folders_enabled else True
        is_exclude_folder_starts = False if exclude_folder_starts_enabled else True
        is_exclude_folder_ends = False if exclude_folder_ends_enabled else True
        is_exclude_filenames = False if exclude_filenames_enabled else True
        is_exclude_file_starts = False if exclude_file_starts_enabled else True
        is_exclude_file_ends = False if exclude_file_ends_enabled else True

        if exclude_rules_any_subdir_enabled:
            for part in path_parts:
                if part in self.rules["exclude"]["any_subdir"]["values"]:
                    is_exclude_rules_any_subdir = True
                    break

        if exclude_folders_enabled:
            if folder in self.rules["exclude"]["folders"]["values"]:
                is_exclude_folders = True
                self.rules["exclude"]["folders"]["matches"].append(folder)
            else:
                self.rules["exclude"]["folders"]["non_matches"].append(folder)

        if exclude_folder_starts_enabled:
            for start in self.rules["exclude"]["folder_starts"]["values"]:
                if fpath.startswith(start):
                    is_exclude_folder_starts = True
                    self.rules["exclude"]["folder_starts"]["matches"].append(fpath)
                    break
            else:
                self.rules["exclude"]["folder_starts"]["non_matches"].append(fpath)

        if exclude_folder_ends_enabled:
            for end in self.rules["exclude"]["folder_ends"]["values"]:
                if fpath.endswith(end):
                    is_exclude_folder_ends = True
                    self.rules["exclude"]["folder_ends"]["matches"].append(fpath)
                    break
            else:
                self.rules["exclude"]["folder_ends"]["non_matches"].append(fpath)

        if exclude_filenames_enabled:
            if filename in self.rules["exclude"]["filenames"]["values"]:
                is_exclude_filenames = True
                self.rules["exclude"]["filenames"]["matches"].append(filename)
            else:
                self.rules["exclude"]["filenames"]["non_matches"].append(filename)

        if exclude_file_starts_enabled:
            for start in self.rules["exclude"]["file_starts"]["values"]:
                if filename.startswith(start):
                    is_exclude_file_starts = True
                    self.rules["exclude"]["file_starts"]["matches"].append(filename)
                    break
            else:
                self.rules["exclude"]["file_starts"]["non_matches"].append(filename)

        if exclude_file_ends_enabled:
            for end in self.rules["exclude"]["file_ends"]["values"]:
                if filename.endswith(end):
                    is_exclude_file_ends = True
                    self.rules["exclude"]["file_ends"]["matches"].append(filename)
                    break
            else:
                self.rules["exclude"]["file_ends"]["non_matches"].append(filename)

        if is_exclude_rules_any_subdir or is_exclude_folders or is_exclude_folder_starts or is_exclude_folder_ends \
                or is_exclude_filenames or is_exclude_file_starts or is_exclude_file_ends:
            should_exclude = True
        return should_exclude

    def apply_rule_logic(self, add, remove, fpath, folder, should_include=True):
        if add <= 500:
            self.append_to_group(add, remove, fpath, folder, self.Colors.GREEN)
        elif 500 < add <= 1000:
            self.append_to_group(add, remove, fpath, folder, self.Colors.YELLOW)
        else:
            self.append_to_group(add, remove, fpath, folder, self.Colors.RED)

        self.added_lines += add
        self.removed_lines += remove

    def print_mode_logic(self):
        logic_description = {
            0: "Mode 0 (Include): Include files and folders based on the include rules. If a file/folder matches the include rules, it will be processed.",
            1: "Mode 1 (Exclude): Exclude files and folders based on the exclude rules. If a file/folder matches the exclude rules, it will not be processed.",
            2: "Mode 2 (Both): Include files and folders based on the include rules unless they also match the exclude rules. If a file/folder matches both include and exclude rules, it will not be processed."
        }
        des = logic_description.get(self.mode, 'Unknown mode')
        print(f"Current mode\t {self.mode} : {des}")
        print(f"Current dir\t {self.cwd}")
        print(f"Current level\t {self.level}")
        print(f"Current price\t {self.unitPrice}")
        print(f"Current role\t {self.role}")


    class Colors:
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        END = '\033[0m'

    def get_params(self, param_type=None):
        args = sys.argv[1:]
        params = []
        for arg in args:
            if param_type is None:
                params.append(arg)
            elif param_type == str:
                if self.is_param_str(arg):
                    params.append(arg)
            else:
                try:
                    value = param_type(arg)
                    params.append(value)
                except ValueError:
                    continue
        return params

    def is_param_str(self, input_value):
        if not isinstance(input_value, str):
            return False
        try:
            float_value = float(input_value)
            if float_value.is_integer():
                return False
            else:
                return False
        except ValueError:
            pass

        if input_value.lower() in ["true", "false", "null"]:
            return False

        return True

    def get_param(self, param_type=str, default_value=None):
        params = self.get_params(param_type)
        return params[0] if params else default_value

    def getDates(self, format_str="%Y-%m-%d", default_values=[], count=1):
        if not default_values:
            default_values = [datetime.now().strftime(format_str)] * count
        dates = []
        date_strs = self.get_params()
        if date_strs:
            for date_str in date_strs:
                try:
                    date_obj = datetime.strptime(date_str, format_str)
                    dates.append(date_obj.strftime(format_str))
                except ValueError:
                    continue

        while len(dates) < count:
            next_date = datetime.now()  # + timedelta(days=len(dates))
            dates.append(next_date.strftime(format_str))

        return dates or default_values or [datetime.now().strftime(format_str)]

    def getDate(self, format_str="%Y-%m-%d", default_value=None):
        if not default_value:
            default_value = datetime.now().strftime(format_str)
        return self.get_param(default_value=default_value) or datetime.now().strftime(format_str)

    def getPath(self, default_value="./"):
        args = sys.argv[1:]
        for arg in args:
            if re.search(r'[./\\]', arg):
                default_value = arg
                break
        if not os.path.isabs(default_value):
            default_value = os.path.abspath(os.path.join(os.path.dirname(__file__), default_value))
        return default_value

    def getRole(self,default_value="developer"):
        strs = self.get_params(str)
        for s in strs:
            if s.lower() in self.roles:
                return s.lower()
        return default_value

    def normalize_path(self, fpath):
        fpath = fpath.strip("'\"").strip()
        fpath = re.sub(r'^[\\/]+|[\\/]+$', '', fpath)
        fpath = re.sub(r'[\\/]+', '/', fpath)
        return fpath

    def print_info(self, msg, color):
        print(f"{color}{msg}{self.Colors.END}")

    def print_modify_info(self, add, remove, fpath, folder, color):
        self.print_info(f"New {add}\t remove {remove}\t {fpath}", color)

    def append_to_group(self, add, remove, fpath, folder, color):
        if color == self.Colors.GREEN:
            self.green_group.append((add, remove, fpath, folder))
        elif color == self.Colors.YELLOW:
            self.yellow_group.append((add, remove, fpath, folder))
        else:
            self.red_group.append((add, remove, fpath, folder))

    def print_group_info(self, group, color):
        display_count = 0
        hidden_count = 0

        if color == self.Colors.GREEN:
            if len(group) > 1000:
                threshold = 10
            elif len(group) > 100:
                threshold = 2
            else:
                threshold = 0

            for add, remove, fpath, folder in group:
                if int(add) >= threshold:
                    self.print_modify_info(add, remove, fpath, folder, color)
                    display_count += 1
                else:
                    hidden_count += 1

            if hidden_count > 0:
                self.print_info(f"Hidden {hidden_count} entries with add < {threshold} (Total entries: {len(group)})",
                                self.Colors.END)
        else:
            for add, remove, fpath, folder in group:
                self.print_modify_info(add, remove, fpath, folder, color)

    def print_rules_info(self):
        if self.mode in [0, 2]:
            print("Include Rules:")
            self.print_rule_info("Include Folders", self.rules["include"]["folders"]["enabled"],
                                 self.rules["include"]["folders"]["matches"],
                                 self.rules["include"]["folders"]["non_matches"])
            self.print_rule_info("Include Folder Starts", self.rules["include"]["folder_starts"]["enabled"],
                                 self.rules["include"]["folder_starts"]["matches"],
                                 self.rules["include"]["folder_starts"]["non_matches"])
            self.print_rule_info("Include Folder Ends", self.rules["include"]["folder_ends"]["enabled"],
                                 self.rules["include"]["folder_ends"]["matches"],
                                 self.rules["include"]["folder_ends"]["non_matches"])
            self.print_rule_info("Include Filenames", self.rules["include"]["filenames"]["enabled"],
                                 self.rules["include"]["filenames"]["matches"],
                                 self.rules["include"]["filenames"]["non_matches"])
            self.print_rule_info("Include File Starts", self.rules["include"]["file_starts"]["enabled"],
                                 self.rules["include"]["file_starts"]["matches"],
                                 self.rules["include"]["file_starts"]["non_matches"])
            self.print_rule_info("Include File Ends", self.rules["include"]["file_ends"]["enabled"],
                                 self.rules["include"]["file_ends"]["matches"],
                                 self.rules["include"]["file_ends"]["non_matches"])
            self.print_rule_info("Include Any Subdir", self.rules["include"]["any_subdir"]["enabled"],
                                 self.rules["include"]["any_subdir"]["matches"],
                                 self.rules["include"]["any_subdir"]["non_matches"])
        if self.mode in [1, 2]:
            print("\nExclude Rules:")
            self.print_rule_info("Exclude Folders", self.rules["exclude"]["folders"]["enabled"],
                                 self.rules["exclude"]["folders"]["matches"],
                                 self.rules["exclude"]["folders"]["non_matches"])
            self.print_rule_info("Exclude Folder Starts", self.rules["exclude"]["folder_starts"]["enabled"],
                                 self.rules["exclude"]["folder_starts"]["matches"],
                                 self.rules["exclude"]["folder_starts"]["non_matches"])
            self.print_rule_info("Exclude Folder Ends", self.rules["exclude"]["folder_ends"]["enabled"],
                                 self.rules["exclude"]["folder_ends"]["matches"],
                                 self.rules["exclude"]["folder_ends"]["non_matches"])
            self.print_rule_info("Exclude Filenames", self.rules["exclude"]["filenames"]["enabled"],
                                 self.rules["exclude"]["filenames"]["matches"],
                                 self.rules["exclude"]["filenames"]["non_matches"])
            self.print_rule_info("Exclude File Starts", self.rules["exclude"]["file_starts"]["enabled"],
                                 self.rules["exclude"]["file_starts"]["matches"],
                                 self.rules["exclude"]["file_starts"]["non_matches"])
            self.print_rule_info("Exclude File Ends", self.rules["exclude"]["file_ends"]["enabled"],
                                 self.rules["exclude"]["file_ends"]["matches"],
                                 self.rules["exclude"]["file_ends"]["non_matches"])
            self.print_rule_info("Exclude Any Subdir", self.rules["exclude"]["any_subdir"]["enabled"],
                                 self.rules["exclude"]["any_subdir"]["matches"],
                                 self.rules["exclude"]["any_subdir"]["non_matches"])

    def print_rule_info(self, rule_name, is_enabled, matches, non_matches):
        if is_enabled:
            self.print_info(f"{rule_name}: Enabled\t Matches: {len(matches)}\t Non-Matches: {len(non_matches)}",
                            self.Colors.GREEN)
        else:
            self.print_info(f"{rule_name}: Disabled", self.Colors.RED)


processor = GitLogProcessor(since="2024-03-01", until="2024-06-02")
processor.organize_logic()
