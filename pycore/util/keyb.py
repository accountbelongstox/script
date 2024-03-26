import keyboard
from pycore._base import Base

class Keyboard(Base):
    def __init__(self):
        self.added_shortcuts = set()

    def listen(self, shortcut, press_duration, callback_function):
        if shortcut in self.added_shortcuts:
            self.warn(f"Shortcut '{shortcut}' has already been added.")
        else:
            keyboard.add_hotkey(shortcut, callback_function, suppress=True, timeout=press_duration)
            self.added_shortcuts.add(shortcut)
            self.success(f"Shortcut '{shortcut}' added successfully.")

    def listen_group(self, key_group, callback, duration=1):
        if key_group in self.added_shortcuts:
            self.warn(f"Shortcut '{key_group}' has already been added.")
        else:
            keyboard.add_hotkey(key_group, callback, suppress=True, timeout=duration)
            self.added_shortcuts.add(key_group)
            self.success(f"Shortcut '{key_group}' added successfully.")
