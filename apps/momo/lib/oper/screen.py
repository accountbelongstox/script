import os.path
import pyautogui
import time
import os
from pycore.utils import file
from pycore.base import Base
import re
import datetime

# # Example usage:
# capturer = ScreenCapturer(default_dir='./screenshots')
# capturer.capture_screen()
# capturer.capture_lower_half()
# capturer.capture_upper_half()
# capturer.capture_left_half()
# capturer.capture_right_half()
# capturer.capture_quadrant(1)
# capturer.capture_quadrant(2)
# capturer.capture_quadrant(3)
# capturer.capture_quadrant(4)

class Screen(Base):
    current_screen_file = None
    showDebug = False

    def __init__(self, capture_interval=60):
        self.last_capture_time = 0
        self.capture_interval = capture_interval
        self.default_dir = os.path.join(file.get_root_dir(), "out/screen")
        file.mkdir(self.default_dir)

    def get_cache_screen(self):
        return self.current_screen_file

    def get_default_dir(self):
        return self.default_dir

    def auto_capture_screen(self):
        current_time = time.time()
        if current_time - self.last_capture_time > self.capture_interval:
            self.last_capture_time = current_time
            self.capture_screen()

    def cleanimg(self):
        current_time = datetime.datetime.now()
        pattern = r'\d{10}'
        for filename in os.listdir(self.default_dir):
            match = re.search(pattern, filename)
            if match:
                timestamp = int(match.group())
                file_time = datetime.datetime.fromtimestamp(timestamp)
                time_difference = current_time - file_time
                if time_difference.total_seconds() > 120:
                    file_path = os.path.join(self.default_dir, filename)
                    os.remove(file_path)
                    self.info(f"delete：{filename}")

    def capture_screen(self, screen_name="full_screen"):
        screen_file, img_path = self.genescreenfile(screen_name)
        screenshot = pyautogui.screenshot()
        self.cleanimg()
        screenshot.save(img_path)
        self.current_screen_file = img_path
        self.success(f'Full screen screenshot at {screen_file}')
        return img_path

    def capture_screen_offset(self, x, y, width, height, left_offset=0, right_offset=0, screen_name="partial_screen"):
        screen_file, img_path = self.genescreenfile(screen_name)
        x_left = max(0, x - left_offset)
        x_right = x + width + right_offset
        y_top = max(0, y)
        y_bottom = y + height
        screenshot = pyautogui.screenshot(region=(x_left, y_top, x_right - x_left, y_bottom - y_top))
        screenshot.save(img_path)
        self.success(f'Partial screenshot at {screen_file}')
        return img_path

    def capture_screen_scope(self, ax, ay, bx, by, screen_name="partial_screen"):
        screen_file, img_path = self.genescreenfile(screen_name)
        x_left = min(ax, bx)
        x_right = max(ax, bx)
        y_top = min(ay, by)
        y_bottom = max(ay, by)
        width = x_right - x_left
        height = y_bottom - y_top
        screenshot = pyautogui.screenshot(region=(x_left, y_top, width, height))
        screenshot.save(img_path)
        self.success(f'Partial screenshot at {screen_file}')
        return img_path

    def genescreenfile(self, screen_name="screen"):
        current_time = time.time()
        screen_file = f"{screen_name}_{current_time}.png"
        img_path = os.path.join(self.default_dir, screen_file)
        return screen_file, img_path

    def start_capture_screen(self, ):
        if file.isFile(self.default_dir) == None or self.current_screen_file == None:
            self.capture_screen()

    def capture_lower_half(self, screen_name="lower_half"):
        screen_file, img_path = self.genescreenfile(screen_name)
        screen_width, screen_height = pyautogui.size()
        region = (0, screen_height // 2, screen_width, screen_height // 2)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(img_path)
        self.current_screen_lower_half = img_path
        self.success(f'Half screen at {screen_file}')
        return img_path

    def capture_upper_half(self, screen_name="upper_half"):
        screen_file, img_path = self.genescreenfile(screen_name)
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width, screen_height // 2)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(img_path)
        self.current_screen_file = img_path
        self.success(f'Upper half  at {screen_file}')
        return img_path

    def capture_left_half(self, screen_name="left_half"):
        screen_file, img_path = self.genescreenfile(screen_name)
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width // 2, screen_height)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(img_path)
        self.current_screen_file = img_path
        self.success(f'Left half screen at {screen_file}')
        return img_path

    def capture_right_half(self, screen_name="right_half"):
        screen_file, img_path = self.genescreenfile(screen_name)
        screen_width, screen_height = pyautogui.size()
        region = (screen_width // 2, 0, screen_width // 2, screen_height)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(img_path)
        self.current_screen_file = img_path
        self.success(f'Right half screen at {screen_file}')
        return img_path

    def capture_quadrant(self, quadrant, screen_name="quadrant_"):
        screen_file, img_path = self.genescreenfile(f"{screen_name}{quadrant}")
        screen_width, screen_height = pyautogui.size()
        if quadrant == 1:
            region = (0, 0, screen_width // 2, screen_height // 2)
        elif quadrant == 2:
            region = (screen_width // 2, 0, screen_width // 2, screen_height // 2)
        elif quadrant == 3:
            region = (0, screen_height // 2, screen_width // 2, screen_height // 2)
        elif quadrant == 4:
            region = (screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2)
        else:
            raise ValueError("Invalid quadrant number")
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(img_path)
        self.current_screen_file = img_path
        self.success(f'Quadrant screen {quadrant} at {screen_file}')
        return img_path
