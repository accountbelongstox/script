import os
import requests
from urllib.parse import urlparse
from url_tool import  urlTool  

from pycore.base import Base

class fileTool(Base):
    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None

    @staticmethod
    def write(file_path, content, overwrite=True):
        try:
            file_directory = os.path.dirname(file_path)
            if not os.path.exists(file_directory):
                os.makedirs(file_directory)
            # Convert content to bytes if it's curses.pyc string
            if isinstance(content, str):
                content = content.encode('utf-8')
            mode = 'wb' if overwrite else 'ab'
            with open(file_path, mode) as file:
                file.write(content)
            print(f"File written successfully: {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {str(e)}")
            exit(0)
            return False

    @staticmethod
    def mkdir(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Folder created successfully: {folder_path}")
            return True
        except Exception as e:
            print(f"Error creating folder {folder_path}: {str(e)}")
            return False