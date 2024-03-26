from kernel.base.base import Base
from kernel.utils_prune import file, arr, strtool
# from kernel.practicals_prune import yml
from deploy.py_script.provider.deployenv import env  # , deploy_dir, base_dir
# from deploy.py_script.env.docker_info import docker_info
# import os
import re

class Nginx(Base):
    annotation_symbol = "#"
    template_dir = ""

    def __init__(self):
        pass

    def set_val(self, key, val=None, file_path=None, comment=True, content=None):
        if not content:
            if file.is_file(file_path):
                lines = file.read_lines(file_path)
            else:
                lines = file_path
        else:
            lines = content
        for i, item in enumerate(lines):
            raw_key = item[0]
            trim_key = raw_key.strip()
            if key == trim_key:
                if comment:
                    if raw_key.startswith(self.annotation_symbol):
                        raw_key = " ".join([self.annotation_symbol, raw_key])
                    lines[i][0] = raw_key
                if val != None:
                    if len(item) > 1:
                        lines[i][1] = val
                    else:
                        lines[i].append(val)
        if file.is_file(file_path):
            self.save_conf(file_path, lines)
        return lines

    def keep_last_newline(self, item_text):
        last_newline_index = item_text.rfind('\n')
        if last_newline_index != -1:
            result = item_text[:last_newline_index + 1]
        else:
            result = item_text
        return result

    def conf_to_text(self,  content_list):
        if not isinstance(content_list,list):
            return content_list
        texts = []
        for item in content_list:
            item_text = " ".join(item)
            item_text = self.keep_last_newline(item_text)
            item_text_strip = item_text.strip()
            if item_text_strip != "":
                texts.append(item_text)
        texts = arr.remove_empty_lines(texts)
        content = "\n".join(texts)
        return content

    def save_conf(self, file_path, content):
        if isinstance(content, list):
            content = self.conf_to_text(content)
        file.save(file_path, content, overwrite=True)

    def comment(self, key, content):
        if file.is_file(content):
            content = file.read_lines(content)
        else:
            content = strtool.to_array_by_newline(content)
        content = self.read_conf(content)
        content = self.set_val(key, None, content=content)
        return content

    def read_conf(self, file_path):
        result = []
        if isinstance(file_path, str):
            if file.is_file(file_path):
                lines = file.read_lines(file_path)
            else:
                lines = file_path
        else:
            lines = file_path
        for line in lines:
            parts = re.split(r'\b\s+(?!\s)', line, maxsplit=1)
            result.append(parts)
        return result

    def replace_wwwroot(self, content):
        # web_dir = env.get_env("WEB_DIR")
        # content = content.replace("/etc/nginx/conf.d/*.conf", "/etc/nginx/*.conf")
        content = content.replace("/etc/nginx/vhost/nginx/tcp/*.conf", "/etc/nginx/tcp/*.conf")
        # content = content.replace("/var/run/nginx.pid;", "/home/nginx.pid")
        content = content.replace("/www/server/nginx/proxy_temp_dir", "/home/tmp/proxy_temp_dir")
        content = content.replace("/www/server/nginx/proxy_cache_dir", "/home/tmp/proxy_cache_dir")
        content = content.replace("/usr/share/nginx/html", "/home/tmp/proxy_cache_dir")
        # content = self.comment("pid", content)
        content = self.conf_to_text(content)
        return content




nginx = Nginx()
