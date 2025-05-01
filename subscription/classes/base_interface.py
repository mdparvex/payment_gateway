from abc import ABC, abstractmethod

class VendorInterface(ABC):
    # def load_data_source(self, path: str, file_name: str) -> str:
    #     """Load in the file for extracting text."""
    @abstractmethod
    def create(self, custom_var=None):
        pass
    
    def custom(self, argument):
        pass
    def custom(self, *arg, **kwargs):
        pass
    def webhook(self, *arg, **kwargs):
        pass