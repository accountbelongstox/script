
from abc import ABC, abstractmethod
class DBBase(ABC):
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass
    @abstractmethod
    def delete(self):
        pass
    @abstractmethod
    def exist_table(self):
        pass
    @abstractmethod
    def exist_field(self):
        pass
    @abstractmethod
    def modify_field(self):
        pass
    @abstractmethod
    def init_database(self):
        pass
    @abstractmethod
    def create_table(self):
        pass
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def count(self):
        pass

