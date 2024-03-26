import os.path
import cv2
import numpy as np
import os
from pycore.utils import file
from apps.automation.lib.oper.screen import Screen
from apps.automation.lib.ctrler.operation_keys import get_operate_code
from pycore._base import Base

screen = Screen()


class Cv2cognize(Base):
    showDebug = False
    current_screen_file = None

    def __init__(self, capture_interval=60):
        self.last_capture_time = 0
        #
        self.capture_interval = capture_interval
        self.default_dir = os.path.join(file.get_root_dir(), "out/screen")
        file.mkdir(self.default_dir)

    def find_position_no_best(self, operate_code=None, threshold=0.7, new_screenshot=True):
        img_path = file.resolve_path(operate_code, "out/screen")
        if new_screenshot or screen.get_cache_screen() == None:
            screen.capture_screen()
        current_screen_file = screen.get_cache_screen()
        default_dir = screen.get_default_dir()
        img_rgb = cv2.imread(current_screen_file)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(img_path, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        x = loc[0]
        y = loc[1]
        if len(x) and len(y):
            found = []
            for pt in zip(*loc[::-1]):
                fx = pt[0]
                fy = pt[1]
                found.append([fx, fy, w, h])
                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)
                result = os.path.join(default_dir, "result.png")
                cv2.imwrite(result, img_rgb)
                self.info('Found the template in screen', [fx, fy, w, h])
            return found
        else:
            self.info('Template not found in screen')
            return []

    def process_operate_code(self, operate_name):
        operate_codes = []
        if isinstance(operate_name, str):
            operate_code, threshold = get_operate_code(operate_name)
            operate_codes.append({
                "threshold": threshold,
                "operate_code": operate_code,
            })
        else:
            for oper_name in operate_name:
                operate_code, threshold = get_operate_code(oper_name)
                operate_codes.append({
                    "threshold": threshold,
                    "operate_code": operate_code,
                })
        return operate_codes

    def find_operate_position_one(self, operate_name):
        operate_codes = self.process_operate_code(operate_name)
        new_screenshot = True
        best_location_match = []
        for oper_item in operate_codes:
            operate_code = oper_item.get("operate_code")
            threshold = oper_item.get("threshold")
            image_path = file.resolve_path(operate_code, "out/screen")
            best_location, locations, best_scale = self.find_operate_code_position(small_image_path=image_path,
                                                                                   threshold=threshold,
                                                                                   new_screenshot=new_screenshot)
            if new_screenshot:
                new_screenshot = False
            best_location_match = best_location
        return best_location_match

    def find_operate_position(self, operate_name):
        operate_codes = self.process_operate_code(operate_name)
        new_screenshot = True
        best_location_match = []
        for oper_item in operate_codes:
            operate_code = oper_item.get("operate_code")
            threshold = oper_item.get("threshold")
            image_path = file.resolve_path(operate_code, "out/screen")
            best_location, locations, best_scale = self.find_operate_code_position(small_image_path=image_path,
                                                                                   threshold=threshold,
                                                                                   new_screenshot=new_screenshot)
            if new_screenshot:
                new_screenshot = False
            best_location_match += locations
        return best_location_match

    def find_operate_code_position(self, small_image_path, threshold=0.9, new_screenshot=True):
        small_image = cv2.imread(small_image_path, cv2.IMREAD_GRAYSCALE)
        if new_screenshot or screen.get_cache_screen() == None:
            screen.capture_screen()
        current_screen_file = screen.get_cache_screen()
        default_dir = screen.get_default_dir()
        large_image = cv2.imread(current_screen_file, cv2.IMREAD_GRAYSCALE)
        img_rgb = cv2.imread(current_screen_file)
        best_scale = 1
        locations = []
        best_location = []
        max_correlation = 0
        w, h = small_image.shape[::-1]
        result_png = os.path.join(default_dir, "result.png")
        for scale in np.linspace(0.5, 1.5, 20):
            resized_small_image = cv2.resize(small_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            if resized_small_image.shape[0] > large_image.shape[0] or resized_small_image.shape[1] > large_image.shape[
                1]:
                continue
            result = cv2.matchTemplate(large_image, resized_small_image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > max_correlation:
                if max_correlation >= threshold:
                    best_location = max_loc
                    locations.append([max_loc[0], max_loc[1], w, h])
                best_scale = scale
                self.info("max_match: " + str(max_correlation) + " by " + os.path.basename(small_image_path),show=self.showDebug)
                max_correlation = max_val
                cv2.rectangle(img_rgb, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 255), 2)
                cv2.imwrite(result_png, img_rgb)
        if best_location:
            cv2.rectangle(img_rgb, best_location, (best_location[0] + w, best_location[1] + h), (0, 0, 255), 2)
            cv2.imwrite(result_png, img_rgb)
            best_location = [best_location[0], best_location[1], w, h]
        locations = locations[::-1]
        return best_location, locations, best_scale

