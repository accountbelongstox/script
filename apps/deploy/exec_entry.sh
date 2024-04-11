
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
install_sh=$1
if [ -z "$1" ]; then
    PS3="Select install type (1: server, 2: pve, 3: local): "
    options=("server" "pve" "local")
    select install_sh in "${options[@]}"; do
        if [ -n "$install_type" ]; then
            break
        else
            echo "Invalid option. Please select a number between 1 and ${#options[@]}."
        fi
    done
else
    install_sh=$1
fi

install_for_version() {
    local version=$1
    local script_path="$BASE_DIR/shells/$version/$install_sh"

    if [ -x "$script_path" ]; then
        echo "Executing install script for $version..."
        "$script_path"
    else
        echo "Install script not found for $version by $script_path."
    fi
}

if [ -e /etc/debian_version ]; then
    echo "Detected Debian"
    debian_version=$(grep "VERSION_ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')
    case "$debian_version" in
        9|10|11|12)
            echo "Debian 9 detected."
            install_for_version "debian_$debian_version"
            ;;
        *)
            echo "Unsupported Debian version."
            exit 1
            ;;
    esac

elif [ -e /etc/centos-release ]; then
    echo "Detected CentOS"
    centos_version=$(grep "CentOS" /etc/centos-release | awk '{print $4}' | cut -d '.' -f1)
    case "$centos_version" in
        7|8|9)
            echo "CentOS $centos_version detected."
            install_for_version "centos_$centos_version"
            ;;
        *)
            echo "Unsupported CentOS version $centos_version."
            exit 1
            ;;
    esac

elif [ -e /etc/os-release ]; then
    echo "Detected Ubuntu"
    ubuntu_version=$(grep "VERSION_ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')
    case "$ubuntu_version" in
        18|19|20|21|22|23)
            echo "Ubuntu $ubuntu_version detected."
            install_for_version "ubuntu_$ubuntu_version"
            ;;
        *)
            echo "Unsupported Ubuntu version."
            exit 1
            ;;
    esac
else
    echo "Unsupported operating system."
    exit 1
fi
