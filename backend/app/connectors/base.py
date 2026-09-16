from abc import ABC, abstractmethod
from typing import Any


class DataConnector(ABC):

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def fetch(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def transform(self, data: Any) -> Any:
        pass