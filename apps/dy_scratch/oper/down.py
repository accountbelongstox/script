import os.path
import os
from datetime import datetime
import time
from pycore.utils import file,strtool
from pycore.utils import screen,oper
from apps.dy_scratch.provider.project_info import project_name
from pycore.practicals import cv2
from pycore._base import Base

class Down(Base):

    def __init__(self):
        pass

    def auto_save_click(self, title=None, attempts=5):
        offset = 73
        save_position = cv2.icon_match("save", project_name, matching_index=5)
        if save_position:
            center_x = save_position[0] + save_position[2] // 2
            center_y = save_position[1] + save_position[3] // 2
            center_y -= offset
            oper.single_click(center_x, center_y)
            oper.press_keys(['ctrl', 'a'])
            input_title = oper.cut()
            ext = file.get_ext(input_title)
            md5_title = strtool.md5(input_title)
            video_file = md5_title + ext
            oper.write_clipboard(video_file)
            oper.press_paste()
            oper.click_center(save_position)
            self.add_down_json(video_file, title)
            time.sleep(0.5)
            return video_file
        elif attempts > 0:
            print(f"Save position not found. Retrying... (attempts left: {attempts})")
            time.sleep(3)
            return self.auto_save_click(title=title, attempts=attempts - 1)
        else:
            print("Save position not found after multiple attempts.")
            return None

    def add_down_json(self, video_file, title):
        out_dir = os.path.join(file.get_root_dir(), "out")
        down_json_file = os.path.join(out_dir, "down_json.json")
        down_json = file.read_json(down_json_file)
        # Create a new entry with new_title, title, and current time (ctime)
        down_json[video_file] = {
            "video_file": video_file,
            "title": title,
            "ctime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        file.save_json(down_json_file, down_json)
        print(f"已经抓取到视频: {len(down_json)}")
        print(f"\t视频标题: {title}")
        print(f"\t视频文件保存名: {video_file}")
        print(f"\tApi样式")
        print(down_json[video_file])


down = Down()