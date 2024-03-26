
import filetype
import chardet

class File():
    def __init__(self):
        pass

    def file_type(self, filename):
        if self.isfile(filename) == False:
            return ""
        kind = filetype.guess(filename)
        if kind is not None:
            if kind.extension != None:
                return kind.extension
        return None


    def check_encode(self, file):
        with open(file, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']
            return encoding
