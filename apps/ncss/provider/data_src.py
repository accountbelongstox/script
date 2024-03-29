# import os.path
from pycore.base.base import Base
from pycore.practicals import flasktool
from pycore.utils import file
from apps.ncss.provider.project_info import app_name

class DataSrc(Base):
    data=None
    counter = 0
    counter_file = "counter_file"
    full_counter = 0
    full_counter_file = "full_counter_file"

    def __init__(self):
        self.counter_file = file.get_source(f"{app_name}/{self.counter_file}")
        if file.isFile(self.counter_file):
            self.counter = int(file.read_text(self.counter_file))
        self.full_counter_file = file.get_source(f"{app_name}/{self.full_counter_file}")
        if file.isFile(self.full_counter_file):
            self.full_counter = int(file.read_text(self.full_counter_file))
        pass

    def get_search(self):
        full_data = file.get_source(f"{app_name}/full_data.txt")
        if file.isFile(full_data):
            lines = file.read_lines(full_data)
            self.full_counter += 1
            file.save(self.full_counter_file,f"{self.full_counter}",overwrite=True)
            if self.full_counter <= len(lines):
                next_line = lines[self.full_counter - 1].strip()
                return next_line
        return None

    def get_item(self):
        if self.data is None:
            self.data = self.get_data()  # Assuming you have a get_data method
        while self.counter < len(self.data):
            item = self.data[self.counter]
            self.counter += 1
            file.save(self.counter_file,f"{self.counter}",overwrite=True)
            validated_item = self.split_and_validate(item)

            if validated_item:
                return validated_item
            else:
                continue
        return None

    def split_and_validate(self, input_str):
        if not input_str:
            return None
        parts = input_str.split(',')
        if len(parts) == 3 and parts[0].isdigit():
            return parts
        else:
            return None
    def get_data(self):
        if not self.data:
            src_data = file.get_source(f"{app_name}/data.csv")
            self.data = file.read_lines(src_data)
        return self.data

data_src = DataSrc()