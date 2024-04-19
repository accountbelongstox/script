from abc import ABC, abstractmethod

class DBBase(ABC):
    @abstractmethod
    def exist_table(self):
        pass

    @abstractmethod
    def exist_field(self):
        pass

    @abstractmethod
    def modify_field(self):
        pass