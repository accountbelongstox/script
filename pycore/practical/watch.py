import os
import time
from datetime import datetime
from pycore.base import Base

class Watch(Base):
    modify_src_time_map = None
    FIRST_SCAN = "FIRST_SCAN"
    def __init__(self, folder_path, all_filters={}, scan_interval_seconds=5):
        self.folder_path = folder_path
        self.scan_interval_seconds = scan_interval_seconds
        self.file_filters = all_filters.get('file_filters', [])
        self.file_start_filters = all_filters.get('file_start_filters', [])
        self.file_end_filters = all_filters.get('file_end_filters', [])
        self.extension_filters = all_filters.get('extension_filters', [])
        self.folder_filters = all_filters.get('folder_filters', [])
        self.folder_start_filters = all_filters.get('folder_start_filters', [])
        self.folder_end_filters = all_filters.get('folder_end_filters', [])
        self.last_scan_time = None
        self.file_changes = {}
        self.is_monitoring = False

    def start_monitoring(self):
        start_time = time.time()
        if self.modify_src_time_map is None:
            self.modify_src_time_map = self.scan_folder()
            if not self.file_changes:
                self.success("Current folder was scanned for the first time, and no new or modified files were found.")
            return self.FIRST_SCAN
        else:
            new_modify_src_time_map = self.scan_folder()
            differing_files = {}
            for path, new_time in new_modify_src_time_map.items():
                if path not in self.modify_src_time_map or self.modify_src_time_map[path] != new_time:
                    differing_files[path] = new_time
            end_time = time.time()
            total_time = end_time - start_time
            total_time = total_time * 10
            if differing_files:
                self.file_changes = differing_files
                self.warn(f"Detected changes {len(differing_files)} file(s), use time {total_time:.2f} seconds..")
                for path, new_time in differing_files.items():
                    if path in self.modify_src_time_map:
                        old_time = self.modify_src_time_map[path]
                        time_difference = new_time - old_time
                        self.warn(f"File: {path} Time diff: {time_difference:.2f} seconds.")
            else:
                self.success(f"No changes detected in files, use time {total_time:.2f} seconds..")
            self.modify_src_time_map = new_modify_src_time_map
            return bool(differing_files)

    def stop_monitoring(self):
        self.is_monitoring = False

    def get_changes(self):
        changes = self.file_changes.copy()
        self.file_changes.clear()
        return changes

    def get_files(self):
        return self.modify_src_time_map

    def scan_folder(self, directory=None, show=False,modify_src_time_map=None):
        modify_src_time_map = modify_src_time_map or {}
        try:
            if directory is None:
                directory = self.folder_path
            items = os.listdir(directory)
            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    if any(item.endswith(end_filter) for end_filter in self.folder_end_filters):
                        self.warn("Skipped Folder (End Filter): " + item_path, show=show)
                        continue
                    if any(item.startswith(start_filter) for start_filter in self.folder_start_filters):
                        self.warn("Skipped Folder (Start Filter): " + item_path, show=show)
                        continue
                    if any(filter_text in item for filter_text in self.folder_filters):
                        self.warn("Skipped Folder (Filter): " + item_path, show=show)
                        continue
                    self.success("Scanned Folder: " + item_path, show=show)
                    modify_src_time_map.update(self.scan_folder(item_path, show=show,modify_src_time_map=modify_src_time_map))
                else:
                    if any(item.endswith(end_filter) for end_filter in self.file_end_filters):
                        self.warn("Skipped File (End Filter): " + item_path, show=show)
                        continue
                    if any(item.startswith(start_filter) for start_filter in self.file_start_filters):
                        self.warn("Skipped File (Start Filter): " + item_path, show=show)
                        continue
                    if any(filter_text in item for filter_text in self.file_filters):
                        self.warn("Skipped File (Filter): " + item_path, show=show)
                        continue
                    _, extension = os.path.splitext(item)
                    if any(extension.endswith(ext_filter) for ext_filter in self.extension_filters):
                        self.warn("Skipped File (Extension Filter): " + item_path, show=show)
                        continue
                    try:
                        modification_time = os.path.getmtime(item_path)
                        modify_src_time_map[item_path] = modification_time
                        self.success("File: " + item_path, show=show)
                    except Exception as e:
                        self.warn(f"Failed to read modification time for file {item_path}. Error: {str(e)}")
        except Exception as e:
            self.warn(f"Error while scanning folder {directory}. Error: {str(e)}")
        return modify_src_time_map

# watch = Watch()