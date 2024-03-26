import os
import shutil
import zipfile
import tarfile
import subprocess
import threading
from urllib.request import urlopen
from urllib.parse import urlparse
import os.path
import time
import urllib.parse
import urllib.request
#最新
class FileDownloader:
    def __init__(self):
        self.remote_url = "http://static.local.12gm.com:805/softlist/static_src/software_installer/workplatform.py"
        # Get the last modified time of the local file and the remote file
        self.local_last_modified_time = self.get_last_modified_time()
        self.remote_last_modified_time = self.get_remote_last_modified_time()
        # Print the last modified time of the local file and the remote file
        print(f"Local file last modified time: {self.local_last_modified_time}")
        print(f"Remote file last modified time: {self.remote_last_modified_time}")
        # Generate the URL for updating the local file
        self.generated_url = self.generate_url(self.local_last_modified_time)

        self.remote_urls = [
            "http://static.local.12gm.com:805/softlist/lang_compiler/environments.tar",
            "http://static.local.12gm.com:805/softlist/lang_compiler/Python39.zip",
            "https://nodejs.org/dist/v18.16.0/node-v18.16.0-win-x64.zip"
        ]
        self.target_directory = "D:\lang_compiler2"

        self.download_dir = self._get_user_download_directory()
        self.extract_to = os.path.join(self.target_directory)
        self._check_and_create_directory()
        self._download_and_extract_files()
        self._execute_commands()

    def get_last_modified_time(self):
        file_path = os.path.realpath(__file__)  # Get the absolute path of the current file
        file_stat = os.stat(file_path)  # Get file status
        last_modified_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.localtime(file_stat.st_mtime))  # Format the last modified time
        return last_modified_time

    # Get the last modified time of the remote file
    def get_remote_last_modified_time(self):
        try:
            response = urllib.request.urlopen(self.remote_url)
            headers = response.headers
            last_modified = headers.get('Last-Modified')  # Get the Last-Modified header field
            return last_modified
        except urllib.error.URLError as e:
            print(f"An error occurred: {e}")
            return None

    # Generate the update URL
    def generate_url(self, last_modified_time):
        base_url = "http://static.local.12gm.com:805/softlist/static_src/software_installer/update.php?local_time="
        encoded_time = urllib.parse.quote(last_modified_time)  # Encode the last modified time
        return base_url + encoded_time

    # Download the remote file
    def download_file(self):
        if self.remote_last_modified_time and self.remote_last_modified_time > self.local_last_modified_time:
            try:
                response = urllib.request.urlopen(self.remote_url)
                if response.code == 200:
                    with open("workplatform.py", "wb") as f:
                        f.write(response.read())  # Write the file content to the local file
                    print("File downloaded successfully.")
                else:
                    print(f"Failed to download file. Status code: {response.code}")
            except urllib.error.URLError as e:
                print(f"An error occurred: {e}")
        else:
            print("The local file is already up to date, no need to download.")

    def _get_user_download_directory(self):
        user_home = os.path.expanduser("~")
        if os.name == "posix":
            download_directory = os.path.join(user_home, "Downloads")
        elif os.name == "nt":
            download_directory = os.path.join(user_home, "Downloads")
        else:
            download_directory = None
        return download_directory

    def _check_and_create_directory(self):
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory, exist_ok=True)
            print(f"Target directory {self.target_directory} created successfully.")
        else:
            print(f"Target directory {self.target_directory} already exists.")

    def _download_file(self, remote_url):
        filename = self._get_filename_from_url(remote_url)
        local_file_path = os.path.join(self.download_dir, filename)
        try:
            with urlopen(remote_url) as response:
                with open(local_file_path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            print(f"File downloaded successfully to: {local_file_path}")
            return local_file_path
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    def _extract_archive(self, archive_path, filename):
        if archive_path.endswith(".zip"):
            self._extract_zip(archive_path, filename)
        elif archive_path.endswith(".tar"):
            self._extract_tar(archive_path, filename)
        else:
            print(f"Unsupported compression format: {archive_path}")

    def _extract_zip(self, zip_path, filename):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                extract_to_path = os.path.join(self.extract_to, filename.split('.')[0])
                zip_ref.extractall(extract_to_path)
                node_exe_path = os.path.join(extract_to_path, "node.exe")
                npm_cmd_path = os.path.join(extract_to_path, "npm.cmd")
                print(f"Node.js path: {node_exe_path}")
                print(f"NPM path: {npm_cmd_path}")
            print(f"Files successfully extracted to: {extract_to_path}")
        except Exception as e:
            print(f"Error extracting ZIP file: {e}")

    def _extract_tar(self, tar_path, filename):
        try:
            with tarfile.open(tar_path, "r") as tar_ref:
                extract_to_path = os.path.join(self.extract_to, filename.split('.')[0])
                tar_ref.extractall(extract_to_path)
            print(f"Files successfully extracted to: {extract_to_path}")
        except Exception as e:
            print(f"Error extracting TAR file: {e}")

    def _get_filename_from_url(self, url):
        parsed_url = urlparse(url)
        return os.path.basename(parsed_url.path)

    def _download_and_extract_files(self):
        threads = []
        for remote_url in self.remote_urls:
            thread = threading.Thread(target=self._download_and_extract, args=(remote_url,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def _download_and_extract(self, remote_url):
        local_file_path = self._download_file(remote_url)
        if local_file_path:
            filename = self._get_filename_from_url(remote_url)
            self._extract_archive(local_file_path, filename)

    def _execute_commands(self):
        try:
            subprocess.run(["node.exe", "-v"], check=True)
            subprocess.run(["npm.cmd", "config", "set", "prefix", "%NodeinstallFileDir%"], check=True)
            subprocess.run(["npm.cmd", "config", "set", "prefix", "%NodeinstallFileDir%"], check=True)
            subprocess.run(["npm.cmd", "config", "set", "registry", "https://mirrors.tencent.com/npm/"],
                           check=True)
            subprocess.run(["npm.cmd", "install", "-g", "yarn"], check=True)
            print("Node.js installation completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing commands: {e}")


if __name__ == "__main__":
    url_handler = FileDownloader()
    url_handler.download_file()
    downloader = FileDownloader()  # Centralized the code into a class
