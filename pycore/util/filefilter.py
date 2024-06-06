import re
import os
from pycore.base.base import Base

default_rules = {
    "include": {
        "folders": {"enabled": True, "values": []},
        "filenames": {"enabled": True, "values": []},
        "file_starts": {"enabled": True, "values": []},
        "file_ends": {"enabled": True, "values": []},
        "folder_starts": {"enabled": True, "values": []},
        "folder_ends": {"enabled": True, "values": [
            ".py", ".js", ".java", ".c", ".cpp", ".cs", ".rb", ".php", ".swift", ".m", ".kt", ".go",
            ".rs", ".ts", ".html", ".css", ".sql", ".sh", ".pl", ".scala", ".hs", ".lua", ".m", ".r",
            ".vhd", ".v", ".pas", ".f90", ".adb", ".cbl", ".dart", ".elm", ".fs", ".erl", ".pl",
            ".lisp", ".scm", ".groovy", ".ml", ".st", ".sol", ".jl", ".asm", ".md", ".yaml", ".json",
            ".xml", ".tcl", ".vbs", ".bat", ".vue", ".jsx", ".tsx"
        ]},
        "any_subdir": {"enabled": True, "values": []}
    },
    "exclude": {
        "folders": {"enabled": True, "values": ["__rm__", ".git"]},
        "filenames": {"enabled": True, "values": []},
        "file_starts": {"enabled": True, "values": []},
        "file_ends": {"enabled": True, "values": [".bin", ".po", ".sln", ".pot", ".cache", ".assets.json", ".csproj"]},
        "folder_starts": {"enabled": True, "values": []},
        "folder_ends": {"enabled": True, "values": []},
        "any_subdir": {"enabled": True, "values": ["node_modules", ".vs", "__rm__", ".idea", ".vscode"]}
    }
}


class FileFilter(Base):
    def set_rules(self, rules):
        if rules is None:
            return default_rules
        updated_rules = default_rules.copy()
        for rule_type, rule_set in rules.items():
            if rule_type not in updated_rules:
                updated_rules[rule_type] = rule_set
            else:
                for rule_name, rule_data in rule_set.items():
                    if rule_name not in updated_rules[rule_type]:
                        updated_rules[rule_type][rule_name] = rule_data
                    else:
                        if 'enabled' in rule_data:
                            updated_rules[rule_type][rule_name]['enabled'] = rule_data['enabled']
                        if 'values' in rule_data:
                            updated_rules[rule_type][rule_name]['values'] = list(
                                set(updated_rules[rule_type][rule_name]['values'] + rule_data['values'])
                            )
        return updated_rules

    def filter(self, cwd, rules=None, mode=2):
        rules = self.set_rules(rules)
        for rule_type in rules:
            for rule_name, rule_data in rules[rule_type].items():
                rule_data["matches"] = []
                rule_data["non_matches"] = []
        rules = self.init_rules_enable(rules)
        self.print_rules_info(mode, rules)
        return
        result = []
        for root, dirs, files in os.walk(cwd):
            for file in files:
                fpath = os.path.join(root, file)
                fpath = self.normalize_path(fpath)
                relative_path = os.path.relpath(fpath, cwd)
                path_parts = re.split(r'[\\/]+', relative_path)
                folder = re.split(r'[\\/]+', relative_path)[0]
                filename = os.path.basename(fpath)
                if mode == 0:
                    should_include = self.match_include_rules(fpath, folder, filename, path_parts, rules)
                    if should_include:
                        result.append(fpath)

                elif mode == 1:
                    should_include = self.match_exclude_rules(fpath, folder, filename, path_parts, rules)
                    if not should_include:
                        result.append(fpath)

                elif mode == 2:
                    should_include = self.match_include_rules(fpath, folder, filename, path_parts, rules)
                    should_exclude = self.match_exclude_rules(fpath, folder, filename, path_parts, rules)

                    # self.info(f"{fpath}\tinclude:{should_include},exclude:{should_exclude}")
                    if should_include and not should_exclude:
                        self.info(fpath)
                        result.append(fpath)

        return result

    def match_include_rules(self, fpath, folder, filename, path_parts, rules):
        should_include = False

        include_folders_enabled = rules["include"]["folders"]["enabled"]
        include_folder_starts_enabled = rules["include"]["folder_starts"]["enabled"]
        include_folder_ends_enabled = rules["include"]["folder_ends"]["enabled"]
        include_filenames_enabled = rules["include"]["filenames"]["enabled"]
        include_file_starts_enabled = rules["include"]["file_starts"]["enabled"]
        include_file_ends_enabled = rules["include"]["file_ends"]["enabled"]
        include_rules_any_subdir_enabled = rules["include"]["any_subdir"]["enabled"]

        is_include_rules_any_subdir = False if include_rules_any_subdir_enabled else None
        is_include_folders = False if include_folders_enabled else None
        is_include_folder_starts = False if include_folder_starts_enabled else None
        is_include_folder_ends = False if include_folder_ends_enabled else None
        is_include_filenames = False if include_filenames_enabled else None
        is_include_file_starts = False if include_file_starts_enabled else None
        is_include_file_ends = False if include_file_ends_enabled else None

        #当  is_include 全部产石关闭时，包含为True

        print("is_include_rules_any_subdir",is_include_rules_any_subdir)
        if include_rules_any_subdir_enabled:
            for part in path_parts:
                if part in rules["include"]["any_subdir"]["values"]:
                    is_include_rules_any_subdir = True
                    break

        if include_folders_enabled:
            if folder in rules["include"]["folders"]["values"]:
                is_include_folders = True
                rules["include"]["folders"]["matches"].append(folder)
            else:
                rules["include"]["folders"]["non_matches"].append(folder)

        if include_folder_starts_enabled:
            for start in rules["include"]["folder_starts"]["values"]:
                if fpath.startswith(start):
                    is_include_folder_starts = True
                    rules["include"]["folder_starts"]["matches"].append(fpath)
                    break
            else:
                rules["include"]["folder_starts"]["non_matches"].append(fpath)

        if include_folder_ends_enabled:
            for end in rules["include"]["folder_ends"]["values"]:
                if fpath.endswith(end):
                    is_include_folder_ends = True
                    rules["include"]["folder_ends"]["matches"].append(fpath)
                    break
            else:
                rules["include"]["folder_ends"]["non_matches"].append(fpath)

        if include_filenames_enabled:
            if filename in rules["include"]["filenames"]["values"]:
                is_include_filenames = True
                rules["include"]["filenames"]["matches"].append(filename)
            else:
                rules["include"]["filenames"]["non_matches"].append(filename)

        if include_file_starts_enabled:
            for start in rules["include"]["file_starts"]["values"]:
                if filename.startswith(start):
                    is_include_file_starts = True
                    rules["include"]["file_starts"]["matches"].append(filename)
                    break
            else:
                rules["include"]["file_starts"]["non_matches"].append(filename)

        if include_file_ends_enabled:
            for end in rules["include"]["file_ends"]["values"]:
                if filename.endswith(end):
                    is_include_file_ends = True
                    rules["include"]["file_ends"]["matches"].append(filename)
                    break
            else:
                rules["include"]["file_ends"]["non_matches"].append(filename)

        if is_include_rules_any_subdir or is_include_folders or is_include_folder_starts or is_include_folder_ends \
                or is_include_filenames or is_include_file_starts or is_include_file_ends:
            should_include = True

        return should_include

    def match_exclude_rules(self, fpath, folder, filename, path_parts, rules):
        should_exclude = False

        exclude_folders_enabled = rules["exclude"]["folders"]["enabled"]
        exclude_folder_starts_enabled = rules["exclude"]["folder_starts"]["enabled"]
        exclude_folder_ends_enabled = rules["exclude"]["folder_ends"]["enabled"]
        exclude_filenames_enabled = rules["exclude"]["filenames"]["enabled"]
        exclude_file_starts_enabled = rules["exclude"]["file_starts"]["enabled"]
        exclude_file_ends_enabled = rules["exclude"]["file_ends"]["enabled"]
        exclude_rules_any_subdir_enabled = rules["exclude"]["any_subdir"]["enabled"]

        is_exclude_rules_any_subdir = False
        is_exclude_folders = False
        is_exclude_folder_starts = False
        is_exclude_folder_ends = False
        is_exclude_filenames = False
        is_exclude_file_starts = False
        is_exclude_file_ends = False

        if exclude_rules_any_subdir_enabled:
            for part in path_parts:
                if part in rules["exclude"]["any_subdir"]["values"]:
                    is_exclude_rules_any_subdir = True
                    break

        if exclude_folders_enabled:
            if folder in rules["exclude"]["folders"]["values"]:
                is_exclude_folders = True
                rules["exclude"]["folders"]["matches"].append(folder)
            else:
                rules["exclude"]["folders"]["non_matches"].append(folder)

        if exclude_folder_starts_enabled:
            for start in rules["exclude"]["folder_starts"]["values"]:
                if fpath.startswith(start):
                    is_exclude_folder_starts = True
                    rules["exclude"]["folder_starts"]["matches"].append(fpath)
                    break
            else:
                rules["exclude"]["folder_starts"]["non_matches"].append(fpath)

        if exclude_folder_ends_enabled:
            for end in rules["exclude"]["folder_ends"]["values"]:
                if fpath.endswith(end):
                    is_exclude_folder_ends = True
                    rules["exclude"]["folder_ends"]["matches"].append(fpath)
                    break
            else:
                rules["exclude"]["folder_ends"]["non_matches"].append(fpath)

        if exclude_filenames_enabled:
            if filename in rules["exclude"]["filenames"]["values"]:
                is_exclude_filenames = True
                rules["exclude"]["filenames"]["matches"].append(filename)
            else:
                rules["exclude"]["filenames"]["non_matches"].append(filename)

        if exclude_file_starts_enabled:
            for start in rules["exclude"]["file_starts"]["values"]:
                if filename.startswith(start):
                    is_exclude_file_starts = True
                    rules["exclude"]["file_starts"]["matches"].append(filename)
                    break
            else:
                rules["exclude"]["file_starts"]["non_matches"].append(filename)

        if exclude_file_ends_enabled:
            for end in rules["exclude"]["file_ends"]["values"]:
                if filename.endswith(end):
                    is_exclude_file_ends = True
                    rules["exclude"]["file_ends"]["matches"].append(filename)
                    break
            else:
                rules["exclude"]["file_ends"]["non_matches"].append(filename)

        if is_exclude_rules_any_subdir or is_exclude_folders or is_exclude_folder_starts or is_exclude_folder_ends \
                or is_exclude_filenames or is_exclude_file_starts or is_exclude_file_ends:
            should_exclude = True

        return should_exclude

    def print_mode_logic(self, mode, cwd, level, unit_price, role):
        logic_description = {
            0: "Mode 0 (Include): Include files and folders based on the include rules. If a file/folder matches the include rules, it will be processed.",
            1: "Mode 1 (Exclude): Exclude files and folders based on the exclude rules. If a file/folder matches the exclude rules, it will not be processed.",
            2: "Mode 2 (Both): Include files and folders based on the include rules unless they also match the exclude rules. If a file/folder matches both include and exclude rules, it will not be processed."
        }
        des = logic_description.get(mode, 'Unknown mode')
        print(f"Current mode\t {mode} : {des}")
        print(f"Current dir\t {cwd}")

    def print_modify_info(self, add, remove, fpath, folder, color, colors):
        self.success(f"New {add}\t remove {remove}\t {fpath}", )

    def append_to_group(self, add, remove, fpath, folder, color, green_group, yellow_group, red_group):
        if color == Colors.GREEN:
            green_group.append((add, remove, fpath, folder))
        elif color == Colors.YELLOW:
            yellow_group.append((add, remove, fpath, folder))
        else:
            red_group.append((add, remove, fpath, folder))

    def print_group_info(self, group, color, colors):
        display_count = 0
        hidden_count = 0

        if color == colors.GREEN:
            if len(group) > 1000:
                threshold = 10
            elif len(group) > 100:
                threshold = 2
            else:
                threshold = 0

            for add, remove, fpath, folder in group:
                if int(add) >= threshold:
                    print_modify_info(add, remove, fpath, folder, color, colors)
                    display_count += 1
                else:
                    hidden_count += 1

            if hidden_count > 0:
                self.success(f"Hidden {hidden_count} entries with add < {threshold} (Total entries: {len(group)})")
        else:
            for add, remove, fpath, folder in group:
                print_modify_info(add, remove, fpath, folder, color, colors)

    def init_rules_enable(self, rules):
        include_folders_values = rules["include"]["folders"]["values"]
        include_folder_starts_values = rules["include"]["folder_starts"]["values"]
        include_folder_ends_values = rules["include"]["folder_ends"]["values"]
        include_filenames_values = rules["include"]["filenames"]["values"]
        include_file_starts_values = rules["include"]["file_starts"]["values"]
        include_file_ends_values = rules["include"]["file_ends"]["values"]
        include_rules_any_subdir_values = rules["include"]["any_subdir"]["values"]

        rules["include"]["folders"]["enabled"] = bool(rules["include"]["folders"]["enabled"]) and bool(
            include_folders_values)
        rules["include"]["folder_starts"]["enabled"] = bool(
            rules["include"]["folder_starts"]["enabled"]) and bool(include_folder_starts_values)
        rules["include"]["folder_ends"]["enabled"] = bool(
            rules["include"]["folder_ends"]["enabled"]) and bool(include_folder_ends_values)
        rules["include"]["filenames"]["enabled"] = bool(rules["include"]["filenames"]["enabled"]) and bool(
            include_filenames_values)
        rules["include"]["file_starts"]["enabled"] = bool(
            rules["include"]["file_starts"]["enabled"]) and bool(include_file_starts_values)
        rules["include"]["file_ends"]["enabled"] = bool(rules["include"]["file_ends"]["enabled"]) and bool(
            include_file_ends_values)
        rules["include"]["any_subdir"]["enabled"] = bool(rules["include"]["any_subdir"]["enabled"]) and bool(
            include_rules_any_subdir_values)

        exclude_folders_values = rules["exclude"]["folders"]["values"]
        exclude_folder_starts_values = rules["exclude"]["folder_starts"]["values"]
        exclude_folder_ends_values = rules["exclude"]["folder_ends"]["values"]
        exclude_filenames_values = rules["exclude"]["filenames"]["values"]
        exclude_file_starts_values = rules["exclude"]["file_starts"]["values"]
        exclude_file_ends_values = rules["exclude"]["file_ends"]["values"]
        exclude_rules_any_subdir_values = rules["exclude"]["any_subdir"]["values"]

        rules["exclude"]["folders"]["enabled"] = bool(rules["exclude"]["folders"]["enabled"]) and bool(
            exclude_folders_values)
        rules["exclude"]["folder_starts"]["enabled"] = bool(
            rules["exclude"]["folder_starts"]["enabled"]) and bool(exclude_folder_starts_values)
        rules["exclude"]["folder_ends"]["enabled"] = bool(
            rules["exclude"]["folder_ends"]["enabled"]) and bool(exclude_folder_ends_values)
        rules["exclude"]["filenames"]["enabled"] = bool(rules["exclude"]["filenames"]["enabled"]) and bool(
            exclude_filenames_values)
        rules["exclude"]["file_starts"]["enabled"] = bool(
            rules["exclude"]["file_starts"]["enabled"]) and bool(exclude_file_starts_values)
        rules["exclude"]["file_ends"]["enabled"] = bool(rules["exclude"]["file_ends"]["enabled"]) and bool(
            exclude_file_ends_values)
        rules["exclude"]["any_subdir"]["enabled"] = bool(rules["exclude"]["any_subdir"]["enabled"]) and bool(
            exclude_rules_any_subdir_values)
        return rules

    def print_rules_info(self, mode, rules):
        self.pprint(rules)
        if mode in [0, 2]:
            print("Include Rules:")
            self.print_rule_info("folders", rules["include"])
            self.print_rule_info("folder_starts", rules["include"])
            self.print_rule_info("folder_ends", rules["include"])
            self.print_rule_info("filenames", rules["include"])
            self.print_rule_info("file_starts", rules["include"])
            self.print_rule_info("file_ends", rules["include"])
            self.print_rule_info("any_subdir", rules["include"])

        if mode in [1, 2]:
            print("\nExclude Rules:")
            self.print_rule_info("folders", rules["exclude"])
            self.print_rule_info("folder_starts", rules["exclude"])
            self.print_rule_info("folder_ends", rules["exclude"])
            self.print_rule_info("filenames", rules["exclude"])
            self.print_rule_info("file_starts", rules["exclude"])
            self.print_rule_info("file_ends", rules["exclude"])
            self.print_rule_info("any_subdir", rules["exclude"])

    def print_rule_info(self, rule_name, rules_category):
        is_enabled = rules_category[rule_name]["enabled"]
        matches = rules_category[rule_name]["matches"]
        non_matches = rules_category[rule_name]["non_matches"]
        if is_enabled:
            self.success(f"{rule_name}: Enabled\t Matches: {len(matches)}\t Non-Matches: {len(non_matches)}")
        else:
            self.warn(f"{rule_name}: Disabled")

    def normalize_path(self, fpath):
        fpath = fpath.strip("'\"").strip()
        fpath = re.sub(r'^[\\/]+|[\\/]+$', '', fpath)
        fpath = re.sub(r'[\\/]+', '/', fpath)
        return fpath
