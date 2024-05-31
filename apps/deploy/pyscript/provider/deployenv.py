import os
from pycore.practicals_linux import env as _env
from pycore.globalvar.gdir import gdir
from pycore.utils_linux import file
import platform
import re
import subprocess
import sys

def get_distro_release():
    debian_codenames = {
        '8': 'jessie',
        '9': 'stretch',
        '10': 'buster',
        '11': 'bullseye',
        '12': 'bookworm'
    }

    try:
        # Try to use `lsb_release -cs`
        codename = subprocess.check_output(['lsb_release', '-cs'], universal_newlines=True).strip()
        return codename
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Read `/etc/os-release`
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('VERSION_CODENAME='):
                    return line.strip().split('=')[1]
    except FileNotFoundError:
        pass

    try:
        # Read `/etc/lsb-release`
        with open('/etc/lsb-release') as f:
            for line in f:
                if line.startswith('DISTRIB_CODENAME='):
                    return line.strip().split('=')[1]
    except FileNotFoundError:
        pass

    try:
        # Read `/etc/issue`
        with open('/etc/issue') as f:
            issue_content = f.read().strip()
            # A simple regex to match common codename patterns in `/etc/issue`
            match = re.search(r'Ubuntu (\w+)', issue_content)
            if match:
                return match.group(1)
            # Add other distribution patterns here if needed
    except FileNotFoundError:
        pass

    try:
        # Use os module as a last resort
        if os.path.exists('/etc/debian_version'):
            with open('/etc/debian_version') as f:
                debian_version = f.read().strip()
                # Map the Debian version to codename
                if debian_version in debian_codenames:
                    return debian_codenames[debian_version]
    except Exception as e:
        pass

    # Use platform module as the final fallback
    try:
        dist_name, version, codename = platform.linux_distribution()
        if codename:
            return codename
        elif 'debian' in dist_name.lower():
            # Map the Debian version to codename
            major_version = version.split('.')[0]
            if major_version in debian_codenames:
                return debian_codenames[major_version]
    except Exception as e:
        pass

    return None


LSB_RELEASE = get_distro_release()
PYTHON_EXECUTABLE = sys.executable
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
APPS_DIR = os.path.join(SCRIPT_DIR, "apps")
DEPLOY_DIR = os.path.join(APPS_DIR, "deploy")
SHELLS_DIR = os.path.join(DEPLOY_DIR, "shells")
PYTHON_MAIN_SCRIPT_NAME = "main.py"
PYTHON_MAIN_SCRIPT = os.path.join(SCRIPT_DIR, PYTHON_MAIN_SCRIPT_NAME)

_env.set_root_dir(DEPLOY_DIR)
env = _env
ENV = _env

TMP_INFO_DIR = gdir.getLocalDir()
MAIN_DIR = "/www"
SERVICE_DIR = os.path.join(MAIN_DIR, "service")
WWWROOT_DIR = os.path.join(MAIN_DIR, "wwwroot")

file.mkdir(MAIN_DIR)
file.mkdir(SERVICE_DIR)
file.mkdir(WWWROOT_DIR)

COMPOSE_ENV = _env.load(DEPLOY_DIR, ".docker")






