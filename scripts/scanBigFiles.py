import os

def scan_directory(current_directory, skip_folders=[], min_file_size=0):
    items = os.listdir(current_directory)

    for item in items:
        item_path = os.path.join(current_directory, item)

        if os.path.isdir(item_path):
            if item in skip_folders:
                # print(f"Skipping folder: {item}")
                continue

            # print(f"Entering folder: {item}")
            scan_directory(item_path, skip_folders, min_file_size)
        else:
            file_size_bytes = os.path.getsize(item_path)

            # 转换文件大小为MB
            file_size_mb = file_size_bytes / (1024 * 1024)

            if file_size_mb > min_file_size:
                print(f"File larger than {min_file_size} MB: {item_path} ({file_size_mb:.2f} MB)")

current_directory = os.path.dirname(os.getcwd())
print(f"current_directory {current_directory}")
common_skip_folders = ['node_modules', '.git', '.vscode', '__pycache__',"venv"]

min_file_size_mb = 1  # 1MB

scan_directory(current_directory, common_skip_folders, min_file_size_mb)
