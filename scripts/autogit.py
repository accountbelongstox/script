import os

class DirectoryScanner:
    def __init__(self, start_dir):
        self.start_dir = start_dir
        self.skip_folders = ['node_modules', 'venv']
        self.skip_startswith = ['.']
        self.skip_endswith = ['*']

    def getWinGitCommandBefore(self):
        return """
@echo off
setlocal
for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set datetime=%%a
set "year=%datetime:~0,4%"
set "month=%datetime:~4,2%"
set "day=%datetime:~6,2%"
set "hour=%datetime:~8,2%"
set "minute=%datetime:~10,2%"
set "second=%datetime:~12,2%"
set "timestamp=%year%-%month%-%day% %hour%:%minute%:%second%"
"""

    def scan_directories(self):
        for dirpath, dirnames, filenames in os.walk(self.start_dir):
            dirnames[:] = [d for d in dirnames if d not in self.skip_folders and not any(d.startswith(s) for s in self.skip_startswith) and not any(d.endswith(e) for e in self.skip_endswith)]
            # if '.git' in dirnames:
            print(f"Found .git folder in: {dirpath}")

if __name__ == "__main__":
    start_directory = os.getcwd()
    scanner = DirectoryScanner(start_directory)
    scanner.scan_directories()
