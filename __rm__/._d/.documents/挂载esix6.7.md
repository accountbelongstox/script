UI界面开启SSH
ls -l /dev/disks
厂商ID 设备ID 默认值 默认值
8086  1c02  d3d0     default    
vi /etc/vmware/passthru.map 

服务器
disk="t10.ATA_____ST4000NM00332D9ZM170_________________________________Z1Z93KP3"
datastore="datastore1"
vmdkname="ZzzBuzzPassthruSSD"

黑群
ATA_____Hitachi_HUS724040ALE641_________________PCHHV0ZB____________
ATA_____HGST_HMS5C4040BLE640__________________________PL1331LAH1J2EH

vmkfstools -z "/vmfs/devices/disks/t10.ATA_____ST4000NM00332D9ZM170_________________________________Z1Z93KP3" "/vmfs/volumes/datastore1/ServerHHD.vmdk"

vmkfstools -z "/vmfs/devices/disks/t10.ATA_____Hitachi_HUS724040ALE641_________________PCHHV0ZB____________" "/vmfs/volumes/datastore1/Synology/SynologyHHD_A.vmdk"
vmkfstools -z "/vmfs/devices/disks/t10.ATA_____HGST_HMS5C4040BLE640__________________________PL1331LAH1J2EH" "/vmfs/volumes/datastore1/Synology/SynologyHHD_B.vmdk"