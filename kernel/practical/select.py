import curses
from pycore.utils_linux import strtool
from pycore.base.base import Base


class Select(Base):
    edit_user_input = ""

    def __init__(self):
        self.selected_indices = set()
        self.current_index = 0

    def edit_str(self, edit_str="", setting_name="", show=False, init="str"): # init = str | pwd
        p_enter = strtool.to_yellow("<Enter>") if not show else strtool.to_blue("-------")
        p_skip = strtool.to_blue(" to skip  ") if not show else strtool.to_blue("--------")
        pre_str = strtool.to_blue("-------")
        skip_str = f"press{p_enter}{p_skip}{pre_str}"
        if setting_name:
            p_setting_name = strtool.to_blue(setting_name)
            print(f"{pre_str}  config:{p_setting_name}, {skip_str}")
        green_color = '\033[92m'
        end_color = '\033[0m'
        if init == "pwd":
            if not edit_str:
                edit_str = strtool.create_password(12)
        # p_key = strtool.extend(setting_name)
        input_nse = f"\n\t{skip_str}\n\tInput New?:" if show == False else ""
        prompt = f"\tvalues : {green_color}{edit_str}{end_color} {input_nse}"
        if not show:
            new_val = input(prompt).strip()
        else:
            print(prompt)
            new_val = ""
        if new_val and not show:
            edit_str = new_val
            p_key = strtool.to_red(setting_name)
            p_val = strtool.to_red(edit_str)
            print(f"The {p_key} has been set to {p_val}")
        print("\n")
        return edit_str

    def edit(self, init_str=""):
        self.init_str = init_str
        curses.wrapper(self._edit)
        return self.edit_user_input

    def _edit(self, stdscr):
        curses.echo()
        stdscr.clear()
        stdscr.addstr("Edit mode, press Enter to complete editing:\n")
        stdscr.refresh()

        if self.init_str:
            self.edit_user_input = self._edit_text(stdscr, self.init_str)
        else:
            stdscr.addstr("Enter something value:\n")
            stdscr.refresh()
            self.edit_user_input = self._edit_text(stdscr, "")

    def _edit_text(self, stdscr, text):
        if text == "":
            display_text = self.init_str
        else:
            display_text = text

        while True:
            stdscr.addstr(2, 0, display_text)
            stdscr.refresh()
            user_input = stdscr.getstr(3, 0).decode(encoding="utf-8")
            # stdscr.addstr(5, 0, f"The editing result is: {user_input}")
            stdscr.addstr(4, 0, "Confirm? (y/n)")
            stdscr.refresh()

            key = stdscr.getch()
            if key == 10 or key == ord('y') or key == ord('Y'):
                return user_input
            else:
                text = user_input
                stdscr.addstr(2, 0, " " * len(display_text))

    def by_list(self, options, name=""):
        self.options = options
        self.name = name
        curses.wrapper(self._main)
        return self.get_selected()

    def show_title(self, stdscr):
        stdscr.addstr(0, 0, f"select {self.name}, press Space-Key to select, and Enter to confirm.")

    def show_options(self, stdscr):
        max_y, max_x = stdscr.getmaxyx()
        for i, option in enumerate(self.options):
            label = f"[{i + 1}]"
            si = i + 1
            option = option[:max_x - len(label) - 5]
            if si < max_y:
                if i == self.current_index:
                    stdscr.addstr(si, 0, f"[>] {label} {option}", curses.color_pair(0))
                elif i in self.selected_indices:
                    stdscr.addstr(si, 0, f"[*] {label} {option}", curses.color_pair(1))
                else:
                    try:
                        stdscr.addstr(si, 0, f"[ ] {label} {option}", curses.color_pair(0))
                    except Exception as e:
                        pass
                        # self.warn(e)
            else:
                break

    def _main(self, stdscr):
        curses.curs_set(0)
        curses.start_color()
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        else:
            pass
        # stdscr.clear()
        self.show_title(stdscr)
        # stdscr.addstr(0, 0, f"select {self.name}, press Space-Key to select, and Enter to confirm.")
        max_y, _ = stdscr.getmaxyx()
        max_options = max_y - 2
        while True:
            self.show_options(stdscr)
            try:
                self._clear_confirm_selection(stdscr)
            except Exception as e:
                print(e)
            key = stdscr.getch()
            if key == curses.KEY_DOWN:
                self._move_cursor(1)
            elif key == curses.KEY_UP:
                self._move_cursor(-1)
            elif key == ord(' '):
                self._toggle_selection()
            elif key == 10:
                key_str, key_int = self._confirm_selection(stdscr)
                if key_str == 'y' or key_int == 10:
                    break
                else:
                    try:
                        self._clear_confirm_selection(stdscr)
                    except Exception as e:
                        print("len(self.options) + 2", len(self.options) + 2)
                        print(e)

                    continue
            stdscr.refresh()

    def _move_cursor(self, direction):
        self.current_index = (self.current_index + direction) % len(self.options)

    def _toggle_selection(self):
        if self.current_index in self.selected_indices:
            self.selected_indices.remove(self.current_index)
        else:
            self.selected_indices.add(self.current_index)

    def get_selected(self):
        return [self.options[i] for i in self.selected_indices]

    def get_confirm_str(self):
        return f"Confirm selection: {self.get_selected()}? (y/n)"

    def _confirm_selection(self, stdscr):
        # stdscr.clear()
        self.show_title(stdscr)
        self.show_options(stdscr)
        print("len(self.options) + 2", len(self.options) + 2)
        stdscr.addstr(len(self.options) + 2

                      , 0, self.get_confirm_str(), curses.color_pair(0))
        stdscr.refresh()
        key = stdscr.getch()
        return chr(key), key

    def _clear_confirm_selection(self, stdscr):
        str_len = len(self.get_confirm_str())
        str_len = " " * str_len
        try:
            stdscr.addstr(len(self.options) + 2, 0, str_len, curses.color_pair(0))
        except Exception as e:
            pass
            # self.warn(e)
