import time
from apps.automation.lib.oper.cv2cognize import Cv2cognize, screen
<<<<<<< HEAD
from kernel.utils import oper
from kernel.utils import arr
from kernel.base.base import Base
from kernel.practicals import ocr
=======
from pycore.utils import oper
from pycore.utils import arr
from pycore._base import Base
from pycore.practicals import ocr
>>>>>>> origin/main

cv2cognize = Cv2cognize()


class Operation(Base):
    last_failure_time = 0
    last_normal_time = None
    process_running_time = 0
    code_cache_list = []

    def __init__(self):
        self.start_time = time.time()
        pass

    def start(self):
        result = self.is_chat_bottom()
        self.info("result")
        self.info(result)

    def is_chrome_open(self):
        icon_position = cv2cognize.find_operate_position_one("task_chrome_icon")
        return icon_position is not None

    def open_chrome(self):
        if self.is_chrome_open():
            self.warn("Chrome browser is already open")
            return
        icon_position = cv2cognize.find_operate_position_one("start_chrome")
        if not icon_position:
            self.warn("Chrome is not currently installed on the computer or the Chrome icon is blocked by the icon.")
            return False
        x, y = arr.generateRandomRectangle(icon_position[0], icon_position[1], icon_position[2], icon_position[3])
        oper.double_click(x, y)
        use_time = 0
        time_out = 300
        while not self.is_chrome_open() and use_time < time_out:
            self.success(f"Google Chrome is starting. use_time: {use_time}s")
            use_time += 5
            time.sleep(5)
        if use_time >= time_out:
            self.warn(f"Google Chrome opening error. Trying again.")
            return self.open_chrome()
        return True

    def is_open_openai(self):
        icon_positions = cv2cognize.find_operate_position("gtp_chrome_tab")
        return bool(icon_positions)

    def open_openai(self):
        if self.is_chrome_open():
            self.open_chrome()
        if self.is_open_openai():
            self.success("OpenAI, Have opened.")
            return
        while not self.is_open_openai():
            self.warn("OpenAI, open. Please use manual opening.")
            time.sleep(5)
        icon_positions = cv2cognize.find_operate_position("gtp_chrome_tab")
        if not icon_positions:
            self.open_url_by_chrome("https://chat.openai.com")

    def open_url_by_chrome(self, url):
        operate_code = "chrome_url_input"
        icon_position = cv2cognize.find_operate_position_one(operate_code)
        while not icon_position:
            self.warn("Chrome tab not found.")
            self.open_new_chrome_tab()
            icon_position = cv2cognize.find_operate_position_one(operate_code)
            time.sleep(5)
        x, y = arr.offsetRectangle(icon_position[0], icon_position[1], icon_position[2], icon_position[3], 0, 20)
        oper.single_click(x, y)
        oper.copy_to_clipboard(url)
        oper.simulate_paste()
        time.sleep(1)
        oper.simulate_enter()

    def is_chrome_open_with_url(self):
        operate_code = "history_area_bottom"
        icon_positions = cv2cognize.find_operate_position(operate_code)
        return bool(icon_positions)

    def open_new_chrome_tab(self):
        operate_code = "chrome_new_tab"
        icon_position = cv2cognize.find_operate_position_one(operate_code)
        if not icon_position:
            self.warn("Chrome tab not found.")
            return False
        random_point = arr.generateRandomRectangle(icon_position[0], icon_position[1], icon_position[2],
                                                   icon_position[3])
        self.info("open_new_chrome_tab-random_point", random_point)
        oper.single_click(random_point[0], random_point[1])
        exit(0)

    def is_new_chat_created(self):
        operate_code = "new_chat_interface"
        icon_positions = cv2cognize.find_operate_position(operate_code)
        if not icon_positions:
            self.create_new_chat()
        else:
            return True

    def is_chat_enable(self):
        operation.check_status()
        operate_code = "prompt_input"
        icon_positions = cv2cognize.find_operate_position_one(operate_code)
        if icon_positions:
            return True
        operate_code = "wait_chat"
        self.info("wait_chat")
        self.info("wait_chat", operate_code)
        icon_positions = cv2cognize.find_operate_position_one(operate_code)
        self.info("icon_positions", icon_positions)
        if not icon_positions:
            return False
        x = icon_positions[0]
        y = icon_positions[1]
        width = icon_positions[2]
        height = icon_positions[3]
        screen_offset = screen.capture_screen_offset(0, y, 2000, height)
        is_message = ocr.is_text(screen_offset, "message")
        if is_message:
            return True
        return False

    def chat_input(self, text):
        operate_code = "prompt_input"
        icon_position = cv2cognize.find_operate_position_one(operate_code)
        self.info("icon_position", icon_position)
        if icon_position:
            x, y, w, h = arr.offsetRectangle(icon_position[0], icon_position[1], icon_position[2], icon_position[3], 0,
                                             5)
            oper.single_click(x, y)
            oper.send(text)
            time.sleep(1)
            chat_send = "chat_send"
            chat_send_position = cv2cognize.find_operate_position_one(chat_send)
            if chat_send_position:
                oper.click_center(chat_send_position)
            while not self.is_chat_returned():
                self.check_status()
                self.success("GTP is currently being generated...")
                time.sleep(2)
            return True
        operate_code = "wait_chat"
        icon_positions = cv2cognize.find_operate_position_one(operate_code)
        if not icon_positions:
            return False
        x = icon_positions[0]
        y = icon_positions[1]
        width = icon_positions[2]
        height = icon_positions[3]
        screen_offset = screen.capture_screen_offset(0, y, 2000, height)
        is_message = ocr.is_text(screen_offset, "message")
        if is_message:
            return True
        return False

    def check_status(self):
        cloudflare = "cloudflare"
        cloudflare_position = cv2cognize.find_operate_position_one(cloudflare)
        if cloudflare_position:
            cloudflare_verify = "cloudflare_verify"
            cloudflare_verify_position = cv2cognize.find_operate_position_one(cloudflare_verify)
            while not cloudflare_verify_position:
                cloudflare_verify_position = cv2cognize.find_operate_position_one(cloudflare_verify)
                self.warn("Waiting for crowd flower's verification.")
            self.success(cloudflare_verify_position)
            x, y = arr.calculateRectangleCenter(cloudflare_verify_position)
            target_point = [x, y]
            oper.mouse_curve(target_point)
            time.sleep(1)
            oper.single_click(x, y)
        operate_code = "network_err"
        err_position = cv2cognize.find_operate_position_one(operate_code)
        while err_position:
            self.last_failure_time = time.time()
            self.warn("Network error, try creating curses.pyc new chat.")
            operate_code = "new_chat"
            icon_position = cv2cognize.find_operate_position_one(operate_code)
            if icon_position:
                oper.click_center(icon_position)
                self.success("The new chat was charged successfully and is waiting for retry status.")
            time.sleep(2)
            err_position = cv2cognize.find_operate_position_one(operate_code)

        operate_code = "re_generate"
        regenerate_position = cv2cognize.find_operate_position_one(operate_code)
        while regenerate_position:
            self.last_failure_time = time.time()
            self.warn("Network delay, need to regenerate the attempt to create curses.pyc regenerate.")
            oper.click_center(regenerate_position)
            self.success("Reproduction successful. Waiting for retry status.")
            time.sleep(2)
            regenerate_position = cv2cognize.find_operate_position_one(operate_code)
        current_time = time.time()
        total_running_time = current_time - self.start_time
        time_since_last_failure = current_time - self.last_failure_time
        self.info(
            f"GTP Normal status: {total_running_time} seconds,Last failure time: {self.last_failure_time},Time since last failure: {time_since_last_failure} seconds")

    def is_chat_returned(self):
        chat_enable = self.is_chat_enable()
        if not chat_enable:
            return False
        return True

    def is_chat_bottom(self):
        operate_code = "chat_bottom"
        icon_position = cv2cognize.find_operate_position(operate_code)
        if icon_position:
            return True
        return False

    def to_chat_bottom(self):
        operate_code = "chat_bottom"
        icon_position = cv2cognize.find_operate_position(operate_code)
        if icon_position:
            return True
        while not icon_position:
            oper.press_continuously("pagedown", 3, 10)
            icon_position = cv2cognize.find_operate_position(operate_code)
            self.warn("Waiting to get content. Drag the chat to the end.")
            time.sleep(0.5)
        return True

    def is_chat_segments(self):
        operate_code = "chat_segments"
        icon_position = cv2cognize.find_operate_position(operate_code)
        if icon_position:
            return True
        return False

    def to_chat_segments(self):
        operate_code = "chat_segments"
        icon_position = cv2cognize.find_operate_position(operate_code)
        while not icon_position:
            self.info("Now on, slide to the chat line.")
            oper.page_up()
            icon_position = cv2cognize.find_operate_position(operate_code)
            if icon_position:
                self.success("chat line position.", icon_position)

    def fetch_content(self):
        operate_code = "copy_code"
        code_segments = "code_segments"
        copy_icon_positions = cv2cognize.find_operate_position(operate_code)
        chat_segment = "chat_segments"
        logo_position = self.get_3_5_logo_position()
        if not logo_position:
            self.warn("Gpt logo not found.")
            return
        chat_segment_position = cv2cognize.find_operate_position(chat_segment)
        wait_chat = "wait_chat"
        wait_chat_position = cv2cognize.find_operate_position(wait_chat)
        sx = logo_position[0]
        sy = logo_position[1]
        sw = chat_segment_position[2]
        sh = chat_segment_position[3]
        sx = sx + sw
        sy = sy + sh

        wx = wait_chat_position[0]
        wy = wait_chat_position[1]
        ww = wait_chat_position[2]
        wh = wait_chat_position[3]
        wy = wy - 20

        if copy_icon_positions:
            cx = copy_icon_positions[0]
            cy = copy_icon_positions[1]

            code_segments_positions = cv2cognize.find_operate_position(code_segments)

        while not self.is_chat_bottom():
            self.copy_code()
            oper.page_down()
            g1img = screen.capture_screen_scope(sx, sy, wx, wy)
            ocr.recognize_texts(g1img)
        if not copy_icon_positions:
            random_point = screen.generate_random_point(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
            oper.single_click(random_point[0], random_point[1])

    def copy_code(self):
        operate_code = "copy_code"
        icon_positions = cv2cognize.find_operate_position(operate_code)
        if icon_positions:
            self.success("Found new code content being copied.")
            oper.click_center(icon_positions)
            code_content = oper.paste()
            self.add_code_cache_list(code_content)

    def get_3_5_logo_position(self):
        operate_code = "gtp_3_5_logo"
        icon_positions = cv2cognize.find_operate_position(operate_code)
        return icon_positions

    def add_code_cache_list(self, code_content):
        if code_content not in self.code_cache_list:
            self.code_cache_list.append(code_content)
            self.success(f"{code_content} added to code list.")
        else:
            self.warn(f"{code_content} is already in code list.")

    def get_current_chat_content(self):
        """
        获取当前聊天内容。
        """
        operate_code = "copy_code"
        icon_positions = cv2cognize.find_operate_position(operate_code)
        for coordinates in icon_positions:
            random_point = screen.generate_random_point(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
            oper.single_click(random_point[0], random_point[1])

    def scroll_chat_to_position(self):
        """
        滚动聊天到指定位置。
        :param position: 要滚动到的位置。
        """
        # 获取滚动区域的操作代码
        scroll_area_operate_code = "scroll_area"

        # 在屏幕中查找滚动区域的位置
        scroll_area_position = cv2cognize.find_operate_position(scroll_area_operate_code)

        if scroll_area_position:
            # 如果找到滚动区域，您可以根据需要滚动到特定位置，假设您要滚动到坐标 (x_target, y_target)
            x_target = ...  # 指定目标横坐标
            y_target = ...  # 指定目标纵坐标

            # 计算滚动的距离
            x_scroll_distance = x_target - scroll_area_position[0]
            y_scroll_distance = y_target - scroll_area_position[1]

            # 使用滚动操作来滚动聊天到指定位置
            oper.scroll_down(x_scroll_distance, y_scroll_distance)  # 可能需要根据实际情况选择是向上滚动还是向下滚动
        else:
            # 如果未找到滚动区域，您可以处理找不到的情况
            self.info("未找到滚动区域")

    def create_new_chat(self):
        operate_code = "new_chat"
        icon_positions = cv2cognize.find_operate_position_one(operate_code)
        if not icon_positions:
            return False
        else:
            random_point = arr.generateRandomRectangle(icon_positions[0], icon_positions[1], icon_positions[2],
                                                       icon_positions[3])
            # self.info("icon_positions",icon_positions)
            oper.single_click(random_point[0], random_point[1])

    def get_chat_history(self):
        """
        获取聊天历史记录。
        """
        pass

    def navigate_to_chat_history(self):
        """
        跳转到聊天历史记录。
        """
        pass

    def refresh_chat(self):
        """
        刷新聊天。
        """
        pass

    def resend_chat_message(self, message):
        """
        重新发送聊天消息。
        :param message: 要重新发送的消息内容。
        """
        pass


operation = Operation()
