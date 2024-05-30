from abc import ABC, abstractmethod

class DBCommon(ABC):
    @abstractmethod
    def connect(self):
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
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def set_engine_to_global(self):
        pass

    @abstractmethod
    def set_session_to_global(self):
        pass

    @abstractmethod
    def set_table_map_to_global(self):
        pass