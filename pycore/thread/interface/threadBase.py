from abc import ABC, abstractmethod

class ThreadBase(ABC):
    @abstractmethod
    def is_running(self):
        """Check if the thread is running"""
        pass
