import os

class FolderScanner:
    def __init__(self, exclude_folders=None, min_file_size_mb=1):
        if exclude_folders is None:
            exclude_folders = []
        self.exclude_folders = exclude_folders
        self.min_file_size_bytes = min_file_size_mb * 1024 * 1024

    def convert_bytes_to_mb(self, bytes):
        return bytes / (1024 * 1024)

    def scan_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_folders]
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size > self.min_file_size_bytes:
                    file_size_mb = self.convert_bytes_to_mb(file_size)
                    print(f"{file_path}: {file_size_mb:.2f} MB")
            skipped_folders = [d for d in dirs if d in self.exclude_folders]
            if skipped_folders:
                print(f"Skipped folders in {root}: {skipped_folders}")

exclude_folders = ["__pycache__", ".vscode", ".idea", ".git", "venv", ".svn", "debug"]
scanner = FolderScanner(exclude_folders=exclude_folders)

scanner.scan_folder('../')
