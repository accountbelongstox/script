import os
import sys

class QTBase:
    def __getattr__(self, item):
        return self.__dict__.get(item)
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    def __set__(self, instance, value):
        self.__dict__[instance] = value
    def __get__(self, item):
        return self.__dict__.get(item)

    def getcwd(self,file=None,suffix=""):
        if file == None:
            cwd = __file__.split('pycore')[0]
        else:
            cwd = os.path.dirname(file)
        cwd = os.path.join(cwd,suffix)
        return cwd
