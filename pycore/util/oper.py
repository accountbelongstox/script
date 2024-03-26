import time
import random
import platform

class Oper:
    def __init__(self):
        self.is_windows = self.detect_windows()
        if self.is_windows:
            import pyautogui
            import pyperclip
            self.pyautogui = pyautogui
            self.pyperclip = pyperclip
            self.time = time
            self.random = random
        else:
            # 在 Linux 下不加载相关包
            pass

    def press_keys(self, keys):
        for key in keys:
            self.pyautogui.keyDown(key)

        for key in keys:
            self.pyautogui.keyUp(key)

    def backspace(self):
        self.pyautogui.press('backspace')
    def detect_windows(self):
        return platform.system().lower() == 'windows'
    def double_click(self, x, y):
        self.pyautogui.click(x, y, clicks=2, interval=0.1)

    def mouse_curve(self, end_point):
        start_point = (random.randint(0, self.pyautogui.size().width), random.randint(0, self.pyautogui.size().height))
        a = random.uniform(0.1, 0.5)
        b = random.uniform(0.1, 0.5)
        points = [(x, int(a * math.sin(b * x) + start_point[1])) for x in
                  range(int(start_point[0]), int(end_point[0]) + 1)]
        for point in points:
            self.pyautogui.moveTo(point[0], point[1])
            time.sleep(0.01)
        self.pyautogui.moveTo(end_point[0], end_point[1])

    def single_click(self, x, y):
        self.pyautogui.click(x, y)

    def right_click(self, x, y):
        self.pyautogui.rightClick(x, y)

    def scroll_up(self, x, y):
        self.pyautogui.scroll(1, x, y)

    def scroll_down(self, x, y):
        self.pyautogui.scroll(-1, x, y)

    def copy_to_clipboard(self, text):
        self.pyperclip.copy(text)

    def paste_from_clipboard(self):
        return self.pyperclip.paste()

    def write_clipboard(self, text):
        self.copy_to_clipboard(text)

    def press_paste(self):
        self.pyautogui.hotkey('ctrl', 'v')

    def paste(self):
        return self.paste_from_clipboard()

    def get_paste(self):
        return self.paste_from_clipboard()

    def cut(self):
        self.pyautogui.hotkey('ctrl', 'x')
        return self.pyperclip.paste()

    def input(self,text):
        self.copy_to_clipboard(text)
        self.simulate_paste()

    def send(self,text):
        self.copy_to_clipboard(text)
        self.simulate_paste()
        time.sleep(1)
        self.simulate_enter()

    def simulate_paste(self):
        self.pyautogui.keyDown('ctrl')
        self.pyautogui.press('v')
        self.pyautogui.keyUp('ctrl')

    def page_up(self):
        self.random_wait(0.2,1)
        self.pyautogui.press('pageup')

    def page_down(self):
        self.random_wait(0.2,1)
        self.pyautogui.press('pagedown')

    def press_continuously(self, key, min_value=1, max_value=2,):
        num_iterations = random.randint(min_value, max_value)
        for _ in range(num_iterations):
            self.pyautogui.press(key)
            self.random_wait(0.2, 1)

    def simulate_enter(self):
        self.pyautogui.press('enter')

    def random_wait(self,start=0.3, end=1.5):
        random_number = self.random_generate(start=start, end=end)
        time.sleep(random_number)

    def random_generate(self,start=0.3, end=1.5):
        random_number = random.uniform(start, end)
        return random_number

    def click_center(self,icon_position):
        x, y = self.generateRandomRectangle(icon_position[0], icon_position[1], icon_position[2], icon_position[3])
        self.random_wait(0.2,1)
        self.single_click(x, y)

    def generateRandomRectangle(self, x, y, w, h, safe=True):
        if safe == True:
            x, y, w, h = self.scaledDownRectangle(x, y, w, h, wMax=30, hMax=30, scale=10)
        print(x, y, w, h)
        random_x = random.randint(x, x + w)
        random_y = random.randint(y, y + h)
        return random_x, random_y

    def scaledDownRectangle(self, x, y, w, h, wMax=30, hMax=30, scale=10):
        if w > wMax:
            scaled_width = (scale / 100) * w
            new_width = w - (2 * scaled_width)
            w = new_width if new_width > 0 else wMax
            x = x + scaled_width
        if h > hMax:
            scaled_height = (scale / 100) * h
            new_height = h - (2 * scaled_height)
            h = new_height if new_height > 0 else hMax
            y = y + scaled_height
        return int(x), int(y), int(w), int(h)
