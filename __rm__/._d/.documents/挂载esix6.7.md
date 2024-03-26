UI界面开启SSH
ls -l /dev/disks
厂商ID 设备ID 默认值 默认值
8086  1c02  d3d0     default    
vi /etc/vmware/passthru.map 

disk="t10.ATA_____ST4000NM00332D9ZM170_________________________________Z1Z93KP3"
datastore="datastore1"
vmdkname="ZzzBuzzPassthruSSD"

vmkfstools -z "/vmfs/devices/disks/t10.ATA_____ST4000NM00332D9ZM170_________________________________Z1Z93KP3" "/vmfs/volumes/datastore1/ST4000DATA.vmdk"