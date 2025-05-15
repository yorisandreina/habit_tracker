from abc import ABC, abstractmethod
from typing import List, Optional
from .models import HabitEntity

class HabitRepository(ABC):
    """Abstract interface for habit persistance."""
    
    @abstractmethod
    def add(self, habit: HabitEntity) -> HabitEntity:
        ...
        
    @abstractmethod
    def get_all(self) -> List[HabitEntity]:
        ...
        
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[HabitEntity]:
        ...
        
    @abstractmethod
    def update(self, habit: HabitEntity) -> None:
        ...
        
    @abstractmethod
    def delete(self, id: int) -> None:
        ...
