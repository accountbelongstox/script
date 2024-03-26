from pycore.requirement_fn.auto_install import auto_install

if __name__ == "__main__":
    auto_install.start()

    import os
    import json
    import re
    import pprint

    from pycore.practicals import down, wdoc
    from pycore.utils import file

    filelist = {}
    fileurls = []


    def extract_info_and_download(folder_path):
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if filename.endswith('.json'):
                json_data = file.read_json(filepath)
                task_path = json_data.get('task_path', '')
                task_id = json_data.get('id', '')
                if task_path:
                    if '.html' not in task_path and "." in task_path:
                        file_extension = os.path.splitext(task_path)[1]
                        # task_path = os.path.splitext(task_path)[0]
                        id_suffix = task_id.split('_')[0]
                        save_file = id_suffix + file_extension
                        if wdoc.is_chinese(save_file) and save_file not in filelist:
                            filelist[save_file] = task_path
                            fileurls.append(task_path)
                        # print("filelist: ", len(filelist))
                        # pprint.pprint(filelist)
                        # down.down_file(url=task_path, save_path=save_file, overwrite=True)


    # folder_path = '\\\\192.168.100.5/web/task.local.12gm.com/laravel/storage/app/.tasks/doclist/ov_bak'
    # extract_info_and_download(folder_path)
    # jsonFile = file.save_json(data=filelist)
    # print(jsonFile)

    jsonFile = "D:/local_server_programing/script/out/tmp/2023_12_25_22_46_17_065000v69r6x62e2"
    jsonFile2 = "D:/local_server_programing/script/out/tmp/2023_12_25_22_54_50_alxxgbldanp5likq"
    download_dir = "D:/迅雷下载"
    output_folder = file.platform_path("D", "programing/script/out/tmp/txt")
    filelist = {}
    # keylist = {}
    j = file.read_json(jsonFile)
    j2 = file.read_json(jsonFile)
    for key, val in j.items():
        val = os.path.basename(val)
        if val not in filelist:
            filelist[val] = (val, key)
    for key, val in j2.items():
        val = os.path.basename(val)
        if val not in filelist:
            filelist[val] = (val, key)

    # for key, val in filelist.items():
    #     basename = os.path.basename(val)
    #     basename = os.path.join(download_dir, basename)
    #     if file.is_file(basename):
    #         file.rename(basename)

    def is_empty_file(file_path):
        return os.path.getsize(file_path) == 0

    def is_all_lines_empty(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return all(line.strip() == '' for line in lines)

    def process_files_in_folder(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                if is_empty_file(file_path):
                    print(f"Empty file: {file_path}")
                elif os.path.getsize(file_path) <= 2048 and is_all_lines_empty(file_path):
                    print(f"File with size <= 2K and all lines are empty: {file_path}")


    process_files_in_folder(output_folder)

    for filename in os.listdir(download_dir):
        if filename in filelist:
            # filekey = os.path.splitext(filename)[0]
            fileobj = filelist.get(filename)
            src = fileobj[0]
            toFile = fileobj[1]
            download_file = os.path.join(download_dir, src)
            file.rename(download_file,toFile)
