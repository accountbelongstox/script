import os
import shutil
import zipfile
import tarfile
import subprocess  # 导入 subprocess 模块
import threading
from urllib.request import urlopen
from urllib.parse import urlparse


class Downloader:
    def __init__(self, remote_urls, target_directory):
        self.remote_urls = remote_urls
        self.target_directory = target_directory
        self.download_dir = self.get_user_download_directory()
        self.extract_to = os.path.join(self.target_directory)
        self.check_and_create_directory()
        self.download_and_extract_files()
        self.execute_commands()  # 添加执行命令的功能

    def get_user_download_directory(self):
        user_home = os.path.expanduser("~")
        if os.name == "posix":
            download_directory = os.path.join(user_home, "Downloads")
        elif os.name == "nt":
            download_directory = os.path.join(user_home, "Downloads")
        else:
            download_directory = None
        return download_directory

    def check_and_create_directory(self):
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory, exist_ok=True)
            print(f"目标目录 {self.target_directory} 创建成功。")
        else:
            print(f"目标目录 {self.target_directory} 已存在。")

    def download_file(self, remote_url):
        filename = self.get_filename_from_url(remote_url)
        local_file_path = os.path.join(self.download_dir, filename)
        try:
            with urlopen(remote_url) as response:
                with open(local_file_path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            print(f"文件成功下载到：{local_file_path}")
            return local_file_path
        except Exception as e:
            print(f"下载文件时出错：{e}")
            return None

    def extract_archive(self, archive_path, filename):
        if archive_path.endswith(".zip"):
            self.extract_zip(archive_path, filename)
        elif archive_path.endswith(".tar"):
            self.extract_tar(archive_path, filename)
        else:
            print(f"不支持的压缩文件格式：{archive_path}")

    def extract_zip(self, zip_path, filename):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                extract_to_path = os.path.join(self.extract_to, filename.split('.')[0])
                zip_ref.extractall(extract_to_path)
                node_exe_path = os.path.join(extract_to_path, "node.exe")
                npm_cmd_path = os.path.join(extract_to_path, "npm.cmd")
                print(f"Node.js路径: {node_exe_path}")
                print(f"NPM路径: {npm_cmd_path}")
            print(f"文件成功解压到：{extract_to_path}")
        except Exception as e:
            print(f"解压 ZIP 文件时出错：{e}")

    def extract_tar(self, tar_path, filename):
        try:
            with tarfile.open(tar_path, "r") as tar_ref:
                extract_to_path = os.path.join(self.extract_to, filename.split('.')[0])
                tar_ref.extractall(extract_to_path)
            print(f"文件成功解压到：{extract_to_path}")
        except Exception as e:
            print(f"解压 TAR 文件时出错：{e}")

    def get_filename_from_url(self, url):
        parsed_url = urlparse(url)
        return os.path.basename(parsed_url.path)

    def download_and_extract_files(self):
        threads = []
        for remote_url in self.remote_urls:
            thread = threading.Thread(target=self.download_and_extract, args=(remote_url,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def download_and_extract(self, remote_url):
        local_file_path = self.download_file(remote_url)
        if local_file_path:
            filename = self.get_filename_from_url(remote_url)
            self.extract_archive(local_file_path, filename)

    def execute_commands(self):
        # 执行命令
        try:
            subprocess.run(["node.exe", "-v"], check=True)  # 检查Node.js版本
            subprocess.run(["npm.cmd", "config", "set", "prefix", "%NodeinstallFileDir%"], check=True)  # 设置NPM前缀路径
            subprocess.run(["npm.cmd", "config", "set", "prefix", "%NodeinstallFileDir%"], check=True)  # 再次设置NPM前缀路径
            subprocess.run(["npm.cmd", "config", "set", "registry", "https://mirrors.tencent.com/npm/"],
                           check=True)  # 设置NPM镜像源
            subprocess.run(["npm.cmd", "install", "-g", "yarn"], check=True)  # 全局安装Yarn
            print("Node.js安装完成。")
        except subprocess.CalledProcessError as e:
            print(f"执行命令时出错: {e}")


if __name__ == "__main__":
    remote_urls = [
        "http://static.local.12gm.com:805/softlist/lang_compiler/environments.tar",
        "http://static.local.12gm.com:805/softlist/lang_compiler/Python39.zip",
        "https://nodejs.org/dist/v18.16.0/node-v18.16.0-win-x64.zip"
    ]
    target_directory = "D:\lang_compiler2"
    downloader = Downloader(remote_urls, target_directory)

#
# @echo off
# setlocal
#
# REM Define remote URLs and target directory
# set "remote_urls=http://static.local.12gm.com:805/softlist/lang_compiler/environments.tar http://static.local.12gm.com:805/softlist/lang_compiler/Python39.zip"
# set "target_directory=D:\lang_compiler2"
#
# REM Function to get user's download directory
# :get_user_download_directory
# set "download_directory="
# if "%OS%"=="Windows_NT" (
#     set "download_directory=%USERPROFILE%\Downloads"
# ) else (
#     REM Assuming POSIX
#     set "download_directory=%HOME%/Downloads"
# )
#
# REM Function to check and create target directory
# :check_and_create_directory
# if not exist "%target_directory%" (
#     mkdir "%target_directory%"
#     echo Target directory %target_directory% created successfully.
# ) else (
#     echo Target directory %target_directory% already exists.
# )
#
# REM Function to download file
# :download_file
# set "url=%~1"
# set "filename=%~nx1"
# set "local_file_path=%download_directory%\%filename%"
# curl -o "%local_file_path%" "%url%" --create-dirs --fail
# if %errorlevel% neq 0 (
#     echo Failed to download file from %url%.
#     goto :eof
# ) else (
#     echo File successfully downloaded to: %local_file_path%
# )
#
# REM Function to extract archive
# :extract_archive
# set "archive_path=%~1"
# set "filename=%~nx1"
# set "extract_to=%target_directory%\!filename:~0,-4!"
# if "%archive_path:~-4%"==".zip" (
#     powershell -Command "Expand-Archive -Path \"%archive_path%\" -DestinationPath \"%extract_to%\""
# ) else if "%archive_path:~-4%"==".tar" (
#     mkdir "%extract_to%"
#     tar -xf "%archive_path%" -C "%extract_to%" --strip-components=1
# ) else (
#     echo Unsupported compression file format: %archive_path%
# )
#
# REM Iterate through remote URLs
# for %%i in (%remote_urls%) do (
#     call :download_file "%%i"
#     if exist "%download_directory%\%%~nxi" (
#         call :extract_archive "%download_directory%\%%~nxi"
#     )
# )
#
# endlocal
