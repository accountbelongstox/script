import os
from apps.deploy.py_script.system.user_tools import user_tools
from pycore.utils_linux import file, plattools, arr
from pycore.base import Base
import subprocess

class Samba(Base):
    samba_config_file = "/etc/samba/smb.conf"

    def generate_share_name(self, share_dir, user):
        last_folder = os.path.basename(os.path.normpath(share_dir))
        return f"{last_folder}_by_{user}"

    def gen_config(self, samba_user, share_dir, comment=None,
                   writable=True, public=False,
                   read_only=False, create_mask="0777", directory_mask="0777"):
        config_name = self.generate_share_name(share_dir, samba_user)
        samba_config_name = f"[{config_name}]"
        samba_config = f"{samba_config_name}\n"
        comment = comment or f"{samba_user}'s Samba Share"
        samba_config += f"   comment = {comment}\n"
        samba_config += f"   path = {share_dir}\n"
        samba_config += f"   writable = {'yes' if writable else 'no'}\n"
        samba_config += f"   public = {'yes' if public else 'no'}\n"
        samba_config += f"   valid users = {samba_user},@samba\n"
        samba_config += f"   write list = {samba_user},@samba\n"
        samba_config += f"   read only = {'yes' if read_only else 'no'}\n"
        samba_config += f"   create mask = {create_mask}\n"
        samba_config += f"   directory mask = {directory_mask}\n"
        return samba_config

    def add(self, samba_user, share_dir):
        samba_config = self.gen_config(
            share_dir=share_dir,
            samba_user=samba_user,
        )
        self.delete_config(share_dir,samba_user,True)
        self.write_smb_conf(share_dir, samba_user, samba_config)

    def write_smb_conf(self, share_dir, username, samba_config):
        if not file.isfile(self.samba_config_file):
            self.error(f"Samba configuration file not found: {self.samba_config_file}")
            return
        exists, current_content_lines = self.samba_config_exists(share_dir, username)
        current_content_lines = arr.clear_empty(current_content_lines)
        if not exists:
            current_content_text = '\n'.join(current_content_lines)
            new_content = f"{current_content_text}\n{samba_config}\n"
            file.save(self.samba_config_file, new_content)
            self.info(f"Samba configuration added to {self.samba_config_file}")

    def samba_config_exists(self, share_dir, username):
        samba_config_name = self.generate_share_name(share_dir, username)
        current_content_lines = file.read_lines(self.samba_config_file)
        for line in current_content_lines:
            if line.strip().startswith(samba_config_name):
                return True, current_content_lines
        return False, current_content_lines

    def get_samba_config(self, samba_config_name, current_content_lines=None):
        current_content_lines = current_content_lines or file.read_lines(self.samba_config_file)
        start_index = -1
        end_index = len(current_content_lines)
        for i, line in enumerate(current_content_lines):
            if line.strip().startswith(samba_config_name):
                start_index = i
                break
        if start_index != -1:
            for i in range(start_index + 1, len(current_content_lines)):
                if not current_content_lines[i].strip().startswith(" "):
                    end_index = i
                    break
        return current_content_lines[start_index:end_index], (start_index, end_index), current_content_lines

    def delete_config(self, share_dir, user, info=False):
        samba_config_name = self.generate_share_name(share_dir, user)
        _, (start_index, end_index), current_content_lines = self.get_samba_config(samba_config_name)
        if start_index != -1:
            deleted_lines = current_content_lines[start_index:end_index]
            current_content_lines = current_content_lines[:start_index] + current_content_lines[end_index:]
            current_content_lines = arr.merge_consecutive(current_content_lines)
            new_content = '\n'.join(current_content_lines)
            file.save(self.samba_config_file, new_content)
            if info:
                deleted_lines_text = '\n'.join(deleted_lines)
                self.success(f"Samba configuration {samba_config_name} deleted. Deleted lines:\n{deleted_lines_text}")
        else:
            self.warn(f"Samba configuration {samba_config_name} not found. Nothing deleted.")

    def set_samba_password(self, username, password):
        process = subprocess.Popen(["sudo", "smbpasswd", "-a", username], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(input=f"{password}\n{password}\n")
        if process.returncode == 0:
            self.success(f"Samba password for user {username} set successfully.")
        else:
            self.error(f"Failed to set Samba password for user {username}. Error: {error}")
samba = Samba()
