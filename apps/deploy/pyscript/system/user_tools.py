import os
import crypt
import spwd
import grp
import getpass
from apps.deploy.pyscript.tools.choice import choice
from pycore.base.base import Base

class UserTools(Base):
    def valid_user_and_pwd(self, username, password):
        is_user = self.is_user(username)
        if is_user:
            stored_password = spwd.getspnam(username).sp_pwd
            encrypted_password = crypt.crypt(password, stored_password)
            if encrypted_password == stored_password:
                return True
            else:
                return False
        else:
            return False
        
    def ensuer_username(self,samba_username):
        current_username = self.get_current_username()
        while not self.is_user(samba_username):
            self.error("Incorrect SAMBA username.")
            samba_username = choice.get_input("Please enter your SAMBA username",current_username)
        return samba_username

    def is_user(self, username):
        try:
            spwd.getspnam(username)
            return True
        except KeyError:
            return False

    def is_user_in_group(self, username, group_name):
        try:
            groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
            return group_name in groups
        except KeyError:
            return False

    def add_user_to_group(self, username, group_name):
        try:
            os.system(f"sudo usermod -aG {group_name} {username}")
            self.info(f"User {username} added to the group {group_name}.")
        except Exception as e:
            self.error(f"Error adding user to group: {e}")

    def get_current_username(self):
        return getpass.getuser()

    def get_correct_password(self,samba_username):
        password = choice.get_input("Please enter your SAMBA password", allow_empty=False)
        while not self.valid_user_and_pwd(samba_username, password):
            self.error("Incorrect SAMBA password.")
            password = choice.get_input("Please enter your SAMBA password", allow_empty=False)
        return password

    def confirm_password(self):
        while True:
            password1 = choice.get_input("Please enter password", allow_empty=False)
            password2 = choice.get_input("confirm password", allow_empty=False)
            if password1 == password2:
                return password1
            else:
                self.warn("Passwords do not match. Please try again.")

user_tools = UserTools()
