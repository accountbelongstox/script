
import zipfile

class File():
    def __init__(self):
        pass

    def zip_extract(self, file, member, o=None):
        if o == None:
            o = os.path.dirname(file)
        with zipfile(file) as f:
            f.extract(member, o)


    def zip_extractall(self, file, odir=None, member=None):
        if odir == None:
            odir = os.path.dirname(file)
        with zipfile.ZipFile(file) as f:
            f.extractall(odir, member)
        return odir