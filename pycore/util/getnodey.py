import time
from pycore.base.base import Base
from pycore.util.unit.ziptask_yj import zip_task_instance
import subprocess
import sys
import os
import platform
import urllib.parse
import re
import datetime
from datetime import datetime
import tarfile
from urllib import request
import requests


class Getnode(Base):
    def __init__(self, tmp_dir=None):
        super().__init__()

        self.tmp_dir_name = "nodes_autoinstaller"

        self.error = {}

        self.mirrors_url = "https://mirrors.tencent.com/npm/"

        self.node_dist_url = 'https://nodejs.org/dist/'

        self.node_dist_file = 'node_dist.html'

        self.retry_limit = 30

        self.retry_count = 0

        self.tmp_dir = tmp_dir

        self.version_number = ''

        self.node_install_dir = '/usr/node'

        self.down_url='https://nodejs.org/dist/v18.12.0/'
    def get_current_os(self):
        return platform.system()

    def is_windows(self):
        return self.get_current_os() == 'Windows'

    def is_linux(self):
        return self.get_current_os() == 'linux'

    def get_node_directory(self, n_path=None):
        current_os = self.get_current_os()
        tmp_dir = '/usr/nodes' if current_os != 'Windows' else 'D:/lang_compiler/nodes/'
        if n_path:
            tmp_dir = os.path.join(tmp_dir, n_path)
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir

    def get_local_dir(self, subpath=None):
        app_data_local_dir = os.getenv('LOCALAPPDATA') or os.path.join(os.getenv('APPDATA'), 'Local')

        if subpath:
            return os.path.join(app_data_local_dir, subpath)
        else:
            return app_data_local_dir

    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as error:
            print(f'Error reading file "{file_path}": {error}')
            return ''

    def get_temp_directory(self):
        current_os = self.get_current_os()
        tmp_dir = '/tmp/node' if current_os != 'Windows' else os.path.join(self.get_local_dir(), self.tmp_dir_name)
        self.mkdir(tmp_dir)
        return tmp_dir

    def get_download_directory(self, fpath=None):
        home_dir = os.path.expanduser('~')
        downloads_dir = os.path.join(home_dir, 'Downloads')
        current_os = self.get_current_os()
        tmp_dir = '/tmp/node/Downloads' if current_os != 'Windows' else os.path.join(downloads_dir, self.tmp_dir_name)
        self.mkdir(tmp_dir)
        if fpath:
            tmp_dir = os.path.join(tmp_dir, fpath)
        return tmp_dir

    def mkdir(self,dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as error:
            print(f'Error creating directory "{dir_path}": {error}')
            return False

    def download(self, down_url, down_name=None):
        download_dir = self.get_download_directory()
        if not down_name:
            down_name = down_url.split('/').pop()
        down_name = self.unescape_url(down_name)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        save_path = os.path.join(download_dir, down_name)

        self.down_file(down_url, save_path)

        return save_path

    def make_base_dir(self, directory_path):

        base_dir = os.path.dirname(directory_path)

        if base_dir and not os.path.exists(base_dir):
            os.makedirs(base_dir)

        return base_dir

    def down_file(self, down_url, dest):
        try:
            response = requests.get(down_url, stream=True)
            response.raise_for_status()
            with open(dest, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            if os.path.exists(dest):
                os.remove(dest)
        else:
            return dest

    def retry(self, down_url, dest):
        if self.retry_count < self.retry_limit:
            self.retry_count += 1
            print(f'Retry {self.retry_count} for file {dest}')
            return self.down_file(down_url, dest)
        else:
            print(f'Retry limit reached for file {dest}')
            raise Exception(f'Failed to download {dest}')

    def is_file(self, filename):
        if not filename or not isinstance(filename, str):
            return False
        if os.path.exists(filename):
            return os.path.isfile(filename)
        return False

    def compare_file_sizes(self, remote_url, local_path):
        if not self.is_file(local_path):
            return False
        try:
            remote_size = self.get_remote_file_size(remote_url)
            local_size = self.get_file_size(local_path)
            print(f"compareFileSizes : url:{remote_url},remoteSize:{remote_size},localPath:{local_path}")
            return remote_size == local_size
        except Exception as err:
            print("An error occurred:", err)
            return False

    def get_remote_file_size(self, remoteUrl):
        req = urllib.request.Request(remoteUrl, method='HEAD')
        with urllib.request.urlopen(req) as response:
            size = response.headers.get('Content-Length')
            if size:
                return int(size)
            else:
                return -1

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return -1
        try:
            return os.path.getsize(file_path)
        except Exception as error:
            print("An error occurred while getting file size:", error)
            return -1

    def unescape_url(self, url):
        return urllib.parse.unquote(url)

    def get_node_downloads(self):
        return {}

    def get_version(self):
        return float(platform.python_version())

    def get_version_full(self):
        return platform.python_version()

    def get_node_modules(self, app_path):
        return os.path.join(app_path, "node_modules")

    def extract_node_version(self, app_config):
        specified_node_version = app_config['package_json']['engines'][
            'node'] if 'package_json' in app_config and 'engines' in app_config['package_json'] and 'node' in \
                       app_config['package_json']['engines'] else None
        print(app_config['name'], specified_node_version)

        if specified_node_version:
            return [float(token)
                    for token in re.findall(r'\d+\.\d+', specified_node_version)
                    if token]
        else:
            return []

    def extract_versions_by_out(self, content):
        result = re.search(r'Expected version "([0-9 ||]+)"', content)
        return result.group(1).split(' || ') if result else None

    # 通过字符串提取错误
    def extract_errors_by_str(self, input_string):
        if input_string:
            errors = [line.strip() for line in input_string.split('\n') if 'error' in line]
            return errors if errors else None
        else:
            return None

    # 读取版本号
    def read_version_number(self):
        version_number = '18'
        return version_number

    def has_sudo(self):
        try:
            subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL)
            return True
        except subprocess.SubprocessError:
            return False

    def get_last_modified_time(self, file_path):
        try:
            stats = os.stat(file_path)
            return stats.st_mtime
        except Exception as error:
            print(f'Error getting last modified time for file "{file_path}": {error}')
            return None

    def get_node_dist_html(self):
        node_dist_html_path = os.path.join(self.get_download_directory(), 'node_dist.html')
        re_download = False
        if self.is_file(node_dist_html_path):
            last_modified_time = self.get_last_modified_time(node_dist_html_path)
            if last_modified_time:
                diff_in_sec = time.time() - last_modified_time
                if diff_in_sec > (24 * 60 * 60):
                    re_download = True
            else:
                re_download = True
        else:
            re_download = True
        if re_download:
            self.download_node_dist_html()
        return node_dist_html_path

    def get_local_versions_list(self):
        dist_html = self.get_node_dist_html()
        content = self.read_file(dist_html)

        version_pattern = re.compile(r'v\d+\.\d+\.\d+')
        versions_list = re.findall(version_pattern, content)

        return versions_list
        # if versions_list:
        #     latest_versions_list = self.get_latest_version_from_list(versions_list)
        #     major_number = self.read_version_number()
        #     try:
        #         major_number = int(major_number)
        #         resolved_value = self.get_latest_version_by_major(major_number, latest_versions_list)
        #         print(resolved_value)
        #         version = resolved_value
        #
        #     except ValueError:
        #         print('ERROR')
        #
        #
        # else:
        #     print('No versions found in the file.')

    def get_latest_version_from_list(self, versions_list=None):
        if not versions_list:
            versions_list = self.get_local_versions_list()

        latest_versions_map = {}

        for version in versions_list:
            version_number = version.replace('v', '')
            major, minor, patch = map(int, version_number.split('.'))
            current_major = latest_versions_map.get(major)

            if not current_major or minor > current_major['minor'] or (
                    minor == current_major['minor'] and patch > current_major['patch']):
                latest_versions_map[major] = {'minor': minor, 'patch': patch, 'version': version}

        latest_versions = [v['version'] for v in latest_versions_map.values()]
        return latest_versions

    def download_node_dist_html(self):
        self.download(self.node_dist_url, self.node_dist_file)

    def get_latest_version_by_number(self, version_number, versions_list):
        max_version = None

        for version in versions_list:
            if version.startswith(version_number):
                if not max_version or self.compare_versions(version, max_version) > 0:
                    max_version = version

        return max_version

    def get_latest_version_by_major(self, major_number, latest_versions_list):
        for version in latest_versions_list:
            version_number = version.replace('v', '')
            major, _, _ = map(int, version_number.split('.'))
            if major == major_number:
                return version

        return None

    def compare_versions(self, version_a, version_b):
        parts_a = list(map(int, version_a.split('.')))
        parts_b = list(map(int, version_b.split('.')))

        if len(parts_a) < len(parts_b):
            parts_a += [0] * (len(parts_b) - len(parts_a))
        elif len(parts_b) < len(parts_a):
            parts_b += [0] * (len(parts_a) - len(parts_b))

        for part_a, part_b in zip(parts_a, parts_b):
            if part_a != part_b:
                return part_a - part_b

        return 0

    def install_node(self, version):
        node_install_dir = "/usr/node"
        node_dir = os.path.join(node_install_dir, version)

        if os.path.exists(node_dir):
            print(f"Node version {version} is already installed at {node_dir}")
            return

        try:
            os.makedirs(node_install_dir, exist_ok=True)
            os.makedirs(node_dir, exist_ok=True)

            download_url = f"https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.gz"
            download_path = os.path.join(node_install_dir, f"node-{version}-linux-x64.tar.gz")

            print(f"Downloading Node.js {version} from {download_url}...")
            urllib.request.urlretrieve(download_url, download_path)
            print(f"Node.js {version} downloaded successfully.")

            print(f"Extracting Node.js {version} to {node_dir}...")
            with tarfile.open(download_path, "r:gz") as tar:
                tar.extractall(path=node_dir)
            print(f"Node.js {version} extracted successfully.")

            print(f"Node.js {version} installed successfully at {node_dir}")
        except Exception as e:
            print(f"Error installing Node.js {version}: {e}")


    def extract_file(self, src, dest_dir):
        try:
            subprocess.run(["tar", "-xzf", src, "-C", dest_dir], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return False

    def get_node_executable(self):
        return 'node' if self.is_linux() else 'node.exe'

    def get_npm_executable(self):
        return 'npm' if self.is_linux() else 'npm.cmd'

    def get_npx_executable(self):
        return 'npx' if self.is_linux() else 'npx.cmd'

    def get_yarn_executable(self):
        return 'yarn' if self.is_linux() else 'yarn.cmd'

    def get_pm2_executable(self):
        return 'pm2' if self.is_linux() else 'pm2.cmd'

    def get_file_name_without_extension(self, file_name):
        last_dot_index = file_name.rfind('.')
        if last_dot_index != -1:
            return file_name[:last_dot_index]
        else:
            return file_name

    def find_node_version_by_platform(self, node_href_versions, version):
        match_roles = ['v{}.'.format(version), 'win', 'x64', '.7z']
        if self.is_linux():
            match_roles = ['v{}.'.format(version), 'linux', 'x64', '.gz']
        match_roles_copy = match_roles[:]
        while match_roles_copy:
            for ver in node_href_versions:
                if all(role in ver for role in match_roles_copy):
                    return ver
            match_roles_copy.pop()
        return None

    def extract_node_href_versions(self, node_html_content):
        lines = node_html_content.split('\n')
        href_values = []
        for line in lines:
            href_match = re.search('href="(.*?)"', line)
            if href_match:
                href_values.append(href_match.group(1))

        return href_values

    def install_node_and_yarn(self, node_path, npm_path, node_install_file_dir):
        print(f"Node.js version: {node_path}")
        print(f"Npm version: {npm_path}")

        try:
            node_version = subprocess.check_output(f"{node_path} -v", shell=True, encoding='utf-8')
            npm_version = subprocess.check_output(f"{npm_path} -v", shell=True, encoding='utf-8')
            print(f"Node.js version: {node_version}")
            print(f"Npm version: {npm_version}")

            cmd = f'{npm_path} config set prefix "{node_install_file_dir}"'
            if self.is_linux() and self.has_sudo():
                cmd = f'sudo {cmd}'
            print(cmd)
            out = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            print(out)

            cmd = f'{npm_path} config set registry {self.mirrors_url}'
            if self.is_linux() and self.has_sudo():
                cmd = f'sudo {cmd}'
            print(cmd)
            out = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            print(out)

            cmd = f'{npm_path} install -g yarn'
            if self.is_linux() and self.has_sudo():
                cmd = f'sudo {cmd}'
            print(cmd)
            out = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            print(out)

            cmd = f'{npm_path} install -g pm2'
            if self.is_linux() and self.has_sudo():
                cmd = f'sudo {cmd}'
            print(cmd)
            out = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            print(out)

            print('Node.js installation completed.')
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

    def get_node_by_version(self, version="18"):
        node_dir = self.get_node_directory()
        node_href_versions = os.listdir(node_dir)
        matching_version = self.find_node_version_by_platform(node_href_versions, version)
        node_exe = self.get_node_executable()

        if not self.is_file(os.path.join(self.get_node_directory(matching_version), node_exe)):
            latest_version_from_list = self.get_latest_version_from_list()
            matched_version = next((version_string for version_string in latest_version_from_list if
                                    version_string.startswith(f"v{version}.")), None)
            if matched_version:
                node_detail_html = f"{matched_version}.html"
                node_detail_download_file = self.get_download_directory(node_detail_html)
                if not self.is_file(node_detail_download_file):
                    node_detail_url = f"{self.node_dist_url}{matched_version}/"
                    node_detail_download_file = self.download(node_detail_url, node_detail_html)
                node_html_content = self.read_file(node_detail_download_file)
                node_href_versions = self.extract_node_href_versions(node_html_content)
                matching_version = self.find_node_version_by_platform(node_href_versions, version)
                if matching_version:
                    matching_version_download_file = self.get_download_directory(matching_version)
                    if not self.is_file(matching_version_download_file):
                        node_download_url = f"{self.node_dist_url}{matched_version}/{matching_version}"
                        matching_version_download_file = self.download(node_download_url, matching_version)
                        matching_version = self.get_file_name_without_extension(matching_version)
                    zip_task_instance.put_unzip_task_promise(matching_version_download_file, node_dir)

        if matching_version:
            return os.path.join(self.get_node_directory(matching_version), node_exe)
        return None

    def getNpmByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
        yarnExec = os.path.join(nodeInstallPath, self.getYarnExecutable())
        print(f'yarnExec: {yarnExec}')
        if not self.isFile(yarnExec):
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return npmExec

    def getNpxByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        npxExec = os.path.join(nodeInstallPath, self.getNpxExecutable())
        return npxExec

    def getYarnByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        yarnExec = os.path.join(nodeInstallPath, self.getYarnExecutable())
        if not self.isFile(yarnExec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return yarnExec

    def getPm2ByNodeVersion(self, version):
        nodeExec = self.getNodeByVersion(version)
        nodeInstallPath = os.path.dirname(nodeExec)
        pm2Exec = os.path.join(nodeInstallPath, self.getPm2Executable())
        if not self.isFile(pm2Exec):
            npmExec = os.path.join(nodeInstallPath, self.getNpmExecutable())
            self.installNodeAndYarn(nodeExec, npmExec, nodeInstallPath)
        return pm2Exec

    def __str__(self):
        return '[class Getnode]'



getnode_instance = Getnode()

