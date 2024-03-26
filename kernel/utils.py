from pycore.util.arg import Arg
from pycore.util.arr import Arr
from pycore.util.file import File
from pycore.util.oper import Oper
from pycore.util.http import Http
from pycore.util.strtool import Strtool
from pycore.util.tool import Tool
from pycore.util.keyb import Keyboard
from pycore.util.sysarg import SysArg
from pycore.util.plattools import Plattools
from pycore.util.screen import Screen

arg = Arg()
arr = Arr()
file = File()
oper = Oper()
http = Http()
strtool = Strtool()
tool = Tool()
keyb = Keyboard()
sysarg = SysArg()
plattools = Plattools()
screen = Screen()

# from types import ModuleType
# this_module = globals()
# for class_name, class_instance in class_instances.items():
#     setattr(this_module, class_name, class_instance)