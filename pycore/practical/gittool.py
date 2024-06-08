from pycore.base.base import Base
from pycore.utils_linux import strtool,plattools,file
from pycore.globalvar.src import src
from pycore.globalvar.gdir import gdir
import os
import subprocess
import re
import sys
from datetime import datetime, timedelta
import time

class GitTool(Base,):

    def __init__(self):
        pass

# Command:
# python .\added_code.py ./ 2 2024-3-1 2024-6-2 architect author:accountbelongstox
# Parameter 1: Path
# Parameter 2: Mode
# Parameter 3: Start date
# Parameter 4: End date
# Parameter 5: Role
# Parameter 6: Author

    current_dir = os.getcwd()
    total_lines = 0
    total_price = 0
    added_price = 0

    def initialize_git_repo(self, path, force=False):
        git_executable = src.get_git_executable()
        command_a = f'{git_executable} -C "{path}" init '
        self.run_exe(command_a)


    def git_add_and_commit(self,path, ):
        git_executable = src.get_git_executable()

        self.info(f"Git Add and Commit by {path}")
        timestamp = time.strftime('%Y_%m_%d_%H_%M_%S')

        command_text = f'{git_executable} -C "{path}" add "{path}"\r\n'
        command_text = command_text+f'{git_executable} -C "{path}" commit -m "{timestamp}"\n'

        command_name = f"git_{timestamp}.bat"
        command_file = gdir.getTempFile(command_name)
        self.info(f"command_file {command_file}")

        file.save(command_file,command_text)
        command_a = f'{git_executable} -C "{path}" add "{path}"'
        self.run_exe(command_a)
        command_b = f'{git_executable} -C "{path}" commit -m "{timestamp}"'
        self.run_exe(command_b)


        # php = src.get_php_executable()
        # php_dir = gdir.getLibraryRootDir("scripts/php")
        # php_script = f"{php_dir}/exec.php"
        # self.run_exe([php,php_script,command_file])
        print(f"Changes committed with message: '{timestamp}'")


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

    def get_all_authors(self):
        if self.author != None:
            return [self.author]
        result = subprocess.run(['git', 'log', '--format=%aN'], capture_output=True, text=True)
        authors = set(result.stdout.splitlines())
        return authors

    def get_git_log_command(self):
        command = [
            "git", "log",
            f"--since={self.since}",
            f"--until={self.until}",
            "--pretty=tformat:",
            "--numstat"
        ]
        if self.author != None:
            command.insert(2, f"--author={self.author}")
        return command

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
        if git_isok:
            authors = self.get_all_authors()
            for author in authors:
                self.added_lines = 0
                self.removed_lines = 0
                self.green_group = []
                self.yellow_group = []
                self.red_group = []

                git_log_command = self.get_git_log_command()
                cmdresult = subprocess.run(git_log_command, capture_output=True, text=True)
                for line in cmdresult.stdout.splitlines():
                    if line:
                        lines = line.split()
                        add = lines[0]
                        remove = lines[1]
                        fpath = self.normalize_path(lines[2])

                        if add == '-' or remove == '-':
                            continue

                        add = int(add)
                        remove = int(remove)
                        folder = re.split(r'[\\/]+', fpath)[0]

                        if self.mode == 0:
                            should_include = self.match_include_rules(fpath, folder, lines[2],
                                                                      re.split(r'[\\/]+', fpath))
                            if should_include:
                                self.apply_rule_logic(add, remove, fpath, folder)

                        elif self.mode == 1:
                            should_exclude = self.match_exclude_rules(fpath, folder, lines[2],
                                                                      re.split(r'[\\/]+', fpath))
                            if not should_exclude:
                                self.apply_rule_logic(add, remove, fpath, folder)

                        elif self.mode == 2:
                            should_include = self.match_include_rules(fpath, folder, lines[2],
                                                                      re.split(r'[\\/]+', fpath))
                            should_exclude = self.match_exclude_rules(fpath, folder, lines[2],
                                                                      re.split(r'[\\/]+', fpath))
                            if should_include and not should_exclude:
                                self.apply_rule_logic(add, remove, fpath, folder)

                self.total_lines = self.added_lines - self.removed_lines
                self.print_group_info(self.green_group, self.Colors.GREEN)
                self.print_group_info(self.yellow_group, self.Colors.YELLOW)
                self.print_group_info(self.red_group, self.Colors.RED)
                self.print_rules_info()
                self.added_price = self.calculate_total_price(self.added_lines, "added_price")
                self.total_price = self.calculate_total_price(self.total_lines, "total_price")
                self.print_info(
                    f"Author\t: {author}\n" +
                    f"role\t: {self.role}\n" +
                    f"level\t: {self.level}\n" +
                    f"added lines\t: {self.added_lines}\n" +
                    f"added price\t: {self.added_price} (¥)\n" +
                    f"removed lines\t: {self.removed_lines}\n" +
                    f"total lines\t: {self.total_lines}\n" +
                    f"total price\t: {self.total_price} (¥)\n",
                    self.Colors.GREEN)
        os.chdir(self.current_dir)
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


    def getRole(self,default_value="developer"):
        strs = self.get_params(str)
        for s in strs:
            if s.lower() in self.roles:
                return s.lower()
        return default_value

    def getAuthor(self, default_value=None):
        strs = self.get_params(str)
        for s in strs:
            if s.lower().startswith("author:"):
                return s[len("author:"):].strip()
        return default_value

    def normalize_path(self, fpath):
        fpath = fpath.strip("'\"").strip()
        fpath = re.sub(r'^[\\/]+|[\\/]+$', '', fpath)
        fpath = re.sub(r'[\\/]+', '/', fpath)
        return fpath