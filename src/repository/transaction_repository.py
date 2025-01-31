# src/repository/transaction_repository.py
import os
import sys
from typing import List

# Adiciona o diretório raiz ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from src.repository.base_repository import BaseRepository
from src.models.transaction import Transaction

class TransactionRepository(BaseRepository[Transaction]):
    def add(self, transaction: Transaction) -> Transaction:
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO transactions 
               (item_id, value, type, is_completed, is_recurring, date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (transaction.item_id, transaction.value, transaction.type,
             transaction.is_completed, transaction.is_recurring, transaction.date)
        )
        self.conn.commit()
        transaction.id = cursor.lastrowid
        return transaction
    
    def get_all(self) -> List[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, item_id, value, type, is_completed, is_recurring, date 
            FROM transactions
        """)
        return [Transaction(*row) for row in cursor.fetchall()]
    
    def get_by_id(self, id: int) -> Transaction:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, item_id, value, type, is_completed, is_recurring, date 
            FROM transactions WHERE id = ?
        """, (id,))
        row = cursor.fetchone()
        return Transaction(*row) if row else None
    
    def update(self, transaction: Transaction) -> Transaction:
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE transactions 
               SET item_id = ?, value = ?, type = ?, is_completed = ?, 
                   is_recurring = ?, date = ?
               WHERE id = ?""",
            (transaction.item_id, transaction.value, transaction.type,
             transaction.is_completed, transaction.is_recurring, 
             transaction.date, transaction.id)
        )
        self.conn.commit()
        return transaction
    
    def delete(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0