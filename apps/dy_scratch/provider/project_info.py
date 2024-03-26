import os
from pycore.practicals_linux import env as _env

_project_dir = os.path.dirname(os.path.dirname(__file__))
_env.set_root_dir(_project_dir)

env = _env
compose_env = _env.load(_project_dir, ".docker")
project_dir = _project_dir
project_name = env.get_env("PROJECT_NAME")
applications_dir = os.path.dirname(project_dir)
