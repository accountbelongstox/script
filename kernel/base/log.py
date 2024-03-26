import os
# import shutil
from datetime import datetime

class Log:
    def write_log(self, log_text, log_type="info", max_total_size_mb=500, log_filename=None, max_file=5, cwd="."):
        max_size = max_total_size_mb * 1024 * 1024
        log_dir = os.path.join(cwd, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"{log_type}_{log_filename}" if log_filename else log_type
        log_obj = self.generate_log_file(log_filename, log_dir, max_size)
        log_filename = log_obj["logfile"]
        if log_obj["logcount"] > max_file:
            self.reduce_logs(log_dir, max_size)
        log_entry = f"[{datetime.utcnow().isoformat()}] [{log_type}] {log_text}\n"
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

    def count_log_lines(self, log_file, log_dir):
        log_files = self.get_logs(log_file, log_dir)
        total_lines = 0
        for log_file_path in log_files:
            with open(os.path.join(log_dir, log_file_path), "r", encoding="utf-8") as file:
                total_lines += sum(1 for _ in file)
        return total_lines

    def get_logs(self, log_file, log_dir):
        return [file for file in os.listdir(log_dir) if file.startswith(f"{log_file}_") and file.endswith(".log")]

    def get_last_logfile(self, log_file, log_dir):
        log_files = self.get_logs(log_file, log_dir)
        log_count = len(log_files)
        if log_count > 0:
            log_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]), reverse=True)
            last_log_file = os.path.join(log_dir, log_files[0])
            last_log_size = os.path.getsize(last_log_file)
            return {"path": last_log_file, "size": last_log_size, "logcount": log_count}
        else:
            return None

    def generate_log_file(self, log_file, log_dir, max_size):
        last_log = self.get_last_logfile(log_file, log_dir)
        log_count = last_log["logcount"] if last_log else 0
        if last_log:
            last_log_file = last_log["path"]
            if last_log["size"] > max_size:
                new_index = int(last_log_file.split('_')[-1].split('.')[0]) + 1
                new_log_file = os.path.join(log_dir, f"{log_file}_{new_index}.log")
                open(new_log_file, "w").close()  # Create an empty log file
                log_file = new_log_file
            else:
                log_file = last_log_file
        else:
            initial_log_file = os.path.join(log_dir, f"{log_file}_1.log")
            open(initial_log_file, "w").close()  # Create an initial log file
            log_file = initial_log_file
        return {"logfile": log_file, "logcount": log_count}

    def reduce_logs(self, log_dir, max_size):
        log_files = [file for file in os.listdir(log_dir) if file.endswith(".txt")]
        for log_file in log_files:
            file_path = os.path.join(log_dir, log_file)
            file_size = os.path.getsize(file_path)
            if os.path.isfile(file_path) and file_size > max_size:
                self.trim_log_file(file_path)

    def trim_log_file(self, file_path):
        output_file_path = f"{file_path}_trimmed.txt"
        with open(file_path, "r", encoding="utf-8") as read_stream, open(output_file_path, "w", encoding="utf-8") as write_stream:
            lines = read_stream.readlines()
            half_index = len(lines) // 2
            second_half = "".join(lines[half_index:])
            write_stream.write(second_half)
        os.remove(file_path)
        os.rename(output_file_path, file_path)
        print(f"Trimmed {file_path}. Kept the second half of lines.")


