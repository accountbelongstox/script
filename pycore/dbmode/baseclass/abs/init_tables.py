from abc import ABC, abstractmethod

class DBInit(ABC):
    @abstractmethod
    def init_database(self):
        pass


