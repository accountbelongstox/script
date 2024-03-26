from abc import ABC, abstractmethod
class PromptAnalyzeInterface(ABC):
    @abstractmethod
    def get_code_mark_index(self, text):
        pass

    @abstractmethod
    def extract_apis(self, text):
        pass

    @abstractmethod
    def extract_must_prompt(self, text):
        pass

    @abstractmethod
    def get_code_start_marks(self, text):
        pass

    @abstractmethod
    def generic_prompt(self, text):
        pass

    @abstractmethod
    def get_code_end_marks(self, text):
        pass

    @abstractmethod
    def get_language_method_marks(self, text):
        pass

    @abstractmethod
    def mark_empty_default_start_line(self, text):
        pass

    @abstractmethod
    def mark_empty_default_end_line(self, text):
        pass

    @abstractmethod
    def extract_usage(self, text_raw_arr, text_pure_arr, code_path):
        pass

    @abstractmethod
    def split_comments(self, text_raw_arr):
        pass
