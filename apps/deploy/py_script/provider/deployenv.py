import os
from pycore.practicals_prune import env as _env

_deploy_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_env.set_root_dir(_deploy_dir)

env = _env
compose_env = _env.load(_deploy_dir, ".docker")
deploy_dir = _deploy_dir
base_dir = os.path.dirname(_deploy_dir)
main_dir = "/www"
service_dir = os.path.join(main_dir, "service")
docker_main_dir = os.path.join(main_dir, "docker")
docker_data = os.path.join(main_dir, "data")
wwwroot_dir = os.path.join(main_dir, "wwwroot")
