import os
from pycore.utils_linux import file

class Mock:
    def get_mock(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_data=file.read_json(os.path.join(current_dir,'mock_data.json'))
        print(json_data)
        return json_data

mock=Mock()