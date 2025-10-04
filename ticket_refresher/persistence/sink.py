from abc import ABC, abstractmethod
from typing import Dict, Any

class Sink(ABC):
    @abstractmethod
    def persist(self, payload: Dict[str, Any]) -> None:
        ...
