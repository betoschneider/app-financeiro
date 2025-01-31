# src/models/item.py
from dataclasses import dataclass

@dataclass
class Item:
    id: int | None = None
    name: str = ""
    category: str = ""