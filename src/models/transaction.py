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
    is_recurring: bool = False
    date: datetime = datetime.now()

    @staticmethod
    def format_date(date_str: str) -> datetime:
        """Converte string de data para datetime"""
        if isinstance(date_str, datetime):
            return date_str
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.now()