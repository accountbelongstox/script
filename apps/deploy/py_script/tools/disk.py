import os
from pycore.utils_linux import strtool, plattools, file
from pycore.base import Base
from apps.deploy.py_script.provider.deployenv import env, compose_env
import re


class Disk(Base):
    def __init__(self):
        pass

    def create_main_dir(self):
        main_dir = env.get_env("MAIN_DIR")
        if not file.isdir(main_dir):
            file.mkdir(main_dir)
        self.mount_main_dir(main_dir)
        return main_dir

    def get_local_mount_dir(self):
        MOUNT_DIR = env.get_env("MOUNT_DIR")
        if not MOUNT_DIR:
            MOUNT_DIR = "/home/www"
        if not file.isdir(MOUNT_DIR):
            file.mkdir(MOUNT_DIR)
        return MOUNT_DIR

    def is_partitioned(self, disk_path):
        result = plattools.exec_cmd(f"blkid {disk_path}", info=False)
        return "not partitioned" not in result

    def backup_fstab(self):
        returncode = plattools.cmd("sudo cp /etc/fstab /etc/fstab.backup")
        if returncode == True:
            self.success("/etc/fstab backup created successfully.")
        else:
            self.warn(f"Failed to create backup: /etc/fstab")

    def check_disk_count(self):
        result = plattools.exec_cmd("lsblk -d --noheadings | wc -l", info=False)
        disk_count = int(result.strip())
        return disk_count

    def get_disk_list(self):
        disks = []
        for root, dirs, files in os.walk('/dev'):
            for name in files:
                if name.startswith('sd') or name.startswith('hd'):
                    disks.append(os.path.join(root, name))
        return disks

    def show_list_disks(self):
        plattools.exec_cmd("lsblk")

    def is_mounted(self, dir_path):
        fstab = self.get_fstab()
        print(fstab)
        for entry in fstab:
            if len(entry) >= 2 and entry[1] == dir_path:
                return True
        return False

    def get_fstab(self):
        fstabinfo = plattools.exec_cmd("cat /etc/fstab")
        lines = fstabinfo.split('\n')
        fstab_array = [line.split() for line in lines if line]
        return fstab_array

    def get_disk_info(self):
        result = plattools.exec_cmd(['lsblk', '-d', '-o', 'NAME,SIZE'], info=False)
        output_lines = result.strip().split('\n')[1:]
        disk_info_list = []
        for line in output_lines:
            name, size = line.split()
            size = size.strip()
            name = name.strip()
            disk_info_list.append({"name": name, "size": size})
        disk_info_list = sorted(disk_info_list, key=lambda x: self.convert_to_bytes(x["size"]))
        return disk_info_list

    def convert_to_bytes(self, size_str):
        size_str = size_str.lower()
        value = strtool.get_number(size_str)
        unit = strtool.get_letter(size_str)
        unit = unit.lower()
        units = {'kb': 1024, 'k': 1024, 'mb': 1024 ** 2, 'm': 1024 ** 2, 'gb': 1024 ** 3, 'g': 1024 ** 3,
                 'tb': 1024 ** 4, 't': 1024 ** 4}
        if unit not in units:
            print(f"Invalid unit: {unit}")
            return 0
        return int(float(value) * units[unit])

    def get_largest_disk(self):
        disk_info = self.get_disk_info()
        if disk_info:
            largest_disk = disk_info[-1]
            return largest_disk["name"]
        else:
            return None

    def format_disk(self, disk_path):
        partition_cmd = f"(echo o; echo n; echo p; echo 1; echo; echo; echo w) | fdisk {disk_path}"
        plattools.exec_cmd(partition_cmd)
        format_cmd = f"mkfs.ext4 {disk_path}1"
        plattools.exec_cmd(format_cmd)

    def get_disk_names(self, disk_list=None):
        disk_info_list = disk_list or self.get_disk_info()
        formatted_disk_info = "|".join([disk["name"].replace('/dev/', '') for disk in disk_info_list])
        return formatted_disk_info

    def mount_main_dir(self, main_dir):
        disk_info_list = self.get_disk_info()
        if len(disk_info_list) > 1:
            if self.is_mounted(main_dir):
                self.warn(f"{main_dir} is already mounted.")
                return
            self.backup_fstab()
            self.info(f"{main_dir} mounting.")
            self.show_list_disks()
            largest_disk = self.get_largest_disk()
            p_main_dir = strtool.to_yellow(main_dir)
            p_largest_disk = strtool.to_red(largest_disk)
            disk_names = self.get_disk_names(disk_info_list)
            m_disk = input(f"Mount {p_main_dir} to {p_largest_disk}, change Disk: ( {disk_names} )")
            if m_disk == "":
                m_disk = largest_disk
            disk_path = f"/dev/{m_disk}"
            if not self.is_partitioned(disk_path):
                sure_partition = strtool.to_red(
                    f"Disk {m_disk} is not partitioned. Are you sure you want to partition and format it? 'yes' to confirm: ")
                confirmation = input(sure_partition)
                if confirmation.lower() == "yes":
                    self.warn(f"Partitioning and formatting {m_disk}...")
                    self.format_disk(f"(echo o; echo n; echo p; echo 1; echo; echo; echo w) | fdisk {disk_path}")
                    self.success(f"Disk {m_disk} has been partitioned and formatted as ext4.")
            self.mount_disk(disk_path, main_dir)
        else:
            disk_path = self.get_local_mount_dir()
            self.bind_disk(disk_path, main_dir)

    def get_uuid(self, src_dir):
        is_dev_path = src_dir.startswith(src_dir)
        if not is_dev_path:
            return None
        info = plattools.exec_cmd(["sudo", "lsblk", "-no", "UUID", src_dir], info=False)
        return info.strip()

    def get_filesystem_type(self, src_dir, is_dev_path=True):
        fs_type = "ext4"
        if is_dev_path:
            fs_type_cmd = plattools.exec_cmd(["sudo", "lsblk", "-no", "FSTYPE", src_dir], info=False)
            fs_type = fs_type_cmd.strip() or "ext4"
        return fs_type

    def mount_disk(self, src_dir, target_dir):
        file.mkbasedir(target_dir)
        fs_type = self.get_filesystem_type(src_dir)
        disk_uuid = self.get_uuid(src_dir)
        if not disk_uuid:
            print("UUID not found or not required, using path for mounting")
            fstab_entry = f"{src_dir} {target_dir} {fs_type} defaults 0 2"
        else:
            print(f"Using UUID {disk_uuid} for mounting")
            fstab_entry = f"UUID={disk_uuid} {target_dir} {fs_type} defaults 0 2"
        self.mount_to_fstab(fstab_entry)

    def mount_to_fstab(self, fstab_entry):
        with open('/etc/fstab', 'w') as fstab_file:
            fstab_file.write(f"{fstab_entry}\n")
        mount_cmd = plattools.cmd(['mount', '-a'], info=False)
        if mount_cmd == True:
            print("Mounting successful.")
        else:
            print("Mounting failed. Removing fstab entry.")
            with open('/etc/fstab', 'r') as fstab_file:
                lines = fstab_file.readlines()
            with open('/etc/fstab', 'w') as fstab_file:
                for line in lines:
                    if line.strip() != fstab_entry.strip():
                        fstab_file.write(line)
        print("Removed the fstab entry. Reloading system.")
        plattools.cmd(['systemctl', 'daemon-reload'])

    def bind_disk(self, src_dir, target_dir):
        file.mkbasedir(target_dir)
        disk_uuid = self.get_uuid(src_dir)
        if not disk_uuid:
            print("UUID not found or not required, using path for binding")
            fstab_entry = f"{src_dir} {target_dir} none bind 0 0"
        else:
            print(f"Using UUID {disk_uuid} for binding")
            fstab_entry = f"UUID={disk_uuid} {target_dir} none bind 0 0"
        self.mount_to_fstab(fstab_entry)


disk = Disk()
