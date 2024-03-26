from pycore.base.base import *
import numpy as np


class Numpy(Base):
    def __init__(self, args):
        pass

    def array_diff(self, arr1, arr2):
        diff = np.setdiff1d(arr1, arr2)
        return diff
