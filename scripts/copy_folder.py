import os
import shutil

class FileCopyHandler:
    def __init__(self):
        self.success_count = 0
        self.success_milestone = 10000

    def warn(self, msg):
        print(f"\033[91m{msg}\033[0m")

    def overall_progress(self):
        if self.success_count % self.success_milestone == 0:
            print(f"\033[92mSuccessfully copied {self.success_count // self.success_milestone}0,000 files.\033[0m")

    def detailed_success(self, src_item, dest_item):
        # Uncomment the line below if you want to print each success message
        # print(f"\033[92mCopying file: {src_item} to {dest_item}\033[0m")
        pass

    def success(self, src_item, dest_item):
        self.success_count += 1
        self.overall_progress()
        self.detailed_success(src_item, dest_item)

    def copy_folder(self, src_folder, dest_folder, skip_folders=[], skip_extensions=[]):
        try:
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            for item in os.listdir(src_folder):
                src_item = os.path.join(src_folder, item)
                dest_item = os.path.join(dest_folder, item)
                if any(skip_folder.lower() in src_item.lower() for skip_folder in skip_folders):
                    self.warn(f"Skipping folder: {src_item}")
                    continue
                if os.path.isdir(src_item):
                    self.copy_folder(src_item, dest_item, skip_folders, skip_extensions)
                else:
                    _, file_extension = os.path.splitext(src_item)
                    if file_extension.lower() in skip_extensions:
                        self.warn(f"Skipping file: {src_item}")
                        continue

                    shutil.copy2(src_item, dest_item)
                    self.success(src_item, dest_item)
        except Exception as e:
            self.warn(f"Error occurred: {e}")

if __name__ == "__main__":
    source_folder = r"\\192.168.100.6/softlist"
    destination_folder = r"\\192.168.100.5/root/softlist"
    skip_folders = ["#recycle"]
    skip_extensions = []
    handler = FileCopyHandler()
    handler.copy_folder(source_folder, destination_folder, skip_folders, skip_extensions)
    print("Copy completed!")
