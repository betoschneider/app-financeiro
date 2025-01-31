# src/models/transaction.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    id: int | None = None
    item_id: int = 0
    value: float = 0.0
    type: str = "D"  # D para débito, C para crédito
    is_completed: bool = False
    is_recurring: bool = False  # Nova coluna
    date: datetime = datetime.now()