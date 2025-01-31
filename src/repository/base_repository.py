# src/repository/base_repository.py
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    def __init__(self, conn):
        self.conn = conn
    
    @abstractmethod
    def add(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> T:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass