import sys
from pycore.util.getnode_wj import getnode
from pycore.util.unit.ziptask_wj import zip_task
# # versions = getnode.compareFileSizes(r"https://nodejs.org/dist/node-v0.6.11.tar.gz",r"D:\programing\script\scripts\autogit.py")
versions=getnode.getNodeByVersion(14)
# # versions=getnode.isWindows()
print(versions)
# result = zip_task.putUnZipTaskPromise(r"C:\Users\ppcda\Downloads\nodes_autoinstaller\node-v16.20.2-win-x64.7z",
#                                       r"D:\lang_compiler")
# print(result)
exit()
