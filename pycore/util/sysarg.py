import sys, re


class SysArg:
    def __init__(self):
        self.python_version = sys.version
        self.platform = sys.platform
        self.command_line_args = sys.argv[1:]

    def get_python_version(self):
        return self.python_version

    def get_platform(self):
        return self.platform

    def get_arg(self, name):
        if isinstance(name, int):
            name = name + 1
            if len(sys.argv) > name:
                return sys.argv[name]
            else:
                return None
        for i, arg in enumerate(self.command_line_args):
            if re.match(r"^[\-]*" + re.escape(name) + r"($|=|-|:)", arg):
                if f"{name}:" in arg:
                    return arg.split(":")[1]
                elif arg == f"--{name}" or arg == f"-{name}" or re.match(r"^-{0,1}\*{1}" + re.escape(name), arg):
                    if i + 1 < len(self.command_line_args):
                        return self.command_line_args[i + 1]
                    else:
                        return None
                elif arg == name:
                    if i + 1 < len(self.command_line_args) and not self.command_line_args[i + 1].startswith("-"):
                        return self.command_line_args[i + 1]
                    else:
                        return ""
        return None

    def is_arg(self, name):
        return self.get_arg(name) != None

    def get_args(self):
        return self.command_line_args
