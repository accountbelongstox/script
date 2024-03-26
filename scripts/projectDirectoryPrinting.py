import os

ignored_extensions = ['.log', '.woff2', '.txt', '.md', '.gz', '.gitkeep', '.map', '.vue', '.html', '.mmdb', '.ico']
ignored_directories = ['node_modules', 'build', '.git', '.vscode']

def scan_directory(dir, prefix='', include_files=False):
    output = ''
    entries = os.listdir(dir)

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1

        if os.path.isdir(os.path.join(dir, entry)) and entry not in ignored_directories:
            output += f"{prefix}{'└──' if is_last else '├──'} {entry}\n"
            output += scan_directory(
                os.path.join(dir, entry),
                f"{prefix}{'    ' if is_last else '│   '}",
                include_files
            )
        elif include_files and os.path.isfile(os.path.join(dir, entry)) and os.path.splitext(entry)[1] not in ignored_extensions:
            output += f"{prefix}{'└──' if is_last else '├──'} {entry}\n"

    return output

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../out')
if not os.path.exists(project_path):
    os.makedirs(project_path)
output_file_path = os.path.join(project_path, 'project_file_tree.txt')
output_dir_path = os.path.join(project_path, 'project_dir_tree.txt')

with open(output_dir_path, 'w', encoding='utf-8') as output_dir_file:
    output_dir_file.write(scan_directory(project_path))

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(scan_directory(project_path, '', True))

print(f"目录树已保存到文件：{output_file_path}")
print(f"目录树已保存到文件：{output_dir_path}")
