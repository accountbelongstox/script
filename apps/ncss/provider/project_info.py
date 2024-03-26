import os
from pycore.practicals_linux import env as _env
from pycore.utils import file

_project_dir = os.path.dirname(os.path.dirname(__file__))
_env.set_root_dir(_project_dir)

env = _env
compose_env = _env.load(_project_dir, ".docker")
project_dir = _project_dir
project_name = os.path.basename(project_dir)
app_name = project_name
applications_dir = os.path.dirname(project_dir)
current_script_dir = os.path.dirname(os.path.abspath(__file__))
