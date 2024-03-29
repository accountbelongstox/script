import sys
from pycore.util.getnode_lwj import getnode

# versions = getnode.compareFileSizes(r"https://nodejs.org/dist/node-v0.6.11.tar.gz",r"D:\programing\script\scripts\autogit.py")
versions=getnode.getNodeByVersion()
# versions=getnode.isWindows()
print(versions)

exit()

