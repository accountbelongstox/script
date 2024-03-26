import os
from pycore.practicals_linux import env as _env
from pycore.utils_linux import file
import platform

def get_os_info():
    os_name = platform.system()
    os_version = platform.release()
    if os_name == "Linux":
        distro_info = platform.linux_distribution()
        if distro_info[0] == "centos":
            return "CentOS", distro_info[1]
        elif distro_info[0] == "ubuntu":
            return "Ubuntu", distro_info[1]
        elif distro_info[0] == "debian":
            return "Debian", distro_info[1]
        else:
            return "Unsupported Linux distribution", ""
    else:
        return "Unsupported operating system", ""

systemname,systemversion = get_os_info()
print(systemname,systemversion)
_deploy_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_env.set_root_dir(_deploy_dir)
tmpdir = "/home/script/.tmp"
infodir = "/home/script/.info"
file.mkdir(tmpdir)
file.mkdir(infodir)
deploy_dir_file = os.path.join(infodir,".deploy_dir")
shells_dir_file = os.path.join(infodir,".shells_dir")
apps_dir_file = os.path.join(infodir,".apps_dir")
systeminfo_file = os.path.join(infodir,".systeminfo_dir")
script_dir_file = os.path.join(_deploy_dir, "shells")
env = _env
compose_env = _env.load(_deploy_dir, ".docker")
deploy_dir = _deploy_dir
base_dir = os.path.dirname(_deploy_dir)
apps_dir = base_dir
main_dir = "/www"
service_dir = os.path.join(main_dir, "service")
docker_main_dir = os.path.join(main_dir, "docker")
docker_data = os.path.join(main_dir, "data")
wwwroot_dir = os.path.join(main_dir, "wwwroot")

if not file.is_file(deploy_dir_file):
    file.save(deploy_dir_file,_deploy_dir)
if not file.is_file(shells_dir_file):
    file.save(deploy_dir_file,shells_dir)
if not file.is_file(apps_dir_file):
    file.save(deploy_dir_file,apps_dir)
if not file.is_file(script_dir_file):
    file.save(deploy_dir_file,apps_dir)



