# src/repository/transaction_repository.py
import os
import sys
from typing import List
from datetime import datetime

# Adiciona o diretório raiz ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from src.repository.base_repository import BaseRepository
from src.models.transaction import Transaction

class TransactionRepository(BaseRepository[Transaction]):
    def add(self, transaction: Transaction) -> Transaction:
        cursor = self.conn.cursor()
        date_str = transaction.date.strftime("%Y-%m-%d") if isinstance(transaction.date, datetime) else transaction.date
        
        cursor.execute(
            """INSERT INTO transactions 
               (item_id, value, type, is_completed, is_recurring, date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (transaction.item_id, transaction.value, transaction.type,
             transaction.is_completed, transaction.is_recurring, date_str)
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
        return [
            Transaction(
                id=row[0],
                item_id=row[1],
                value=row[2],
                type=row[3],
                is_completed=bool(row[4]),
                is_recurring=bool(row[5]),
                date=Transaction.format_date(row[6])
            )
            for row in cursor.fetchall()
        ]
    
    def get_by_id(self, id: int) -> Transaction:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, item_id, value, type, is_completed, is_recurring, date 
            FROM transactions WHERE id = ?
        """, (id,))
        row = cursor.fetchone()
        if row:
            return Transaction(
                id=row[0],
                item_id=row[1],
                value=row[2],
                type=row[3],
                is_completed=bool(row[4]),
                is_recurring=bool(row[5]),
                date=Transaction.format_date(row[6])
            )
        return None
    
    def update(self, transaction: Transaction) -> Transaction:
        cursor = self.conn.cursor()
        date_str = transaction.date.strftime("%Y-%m-%d") if isinstance(transaction.date, datetime) else transaction.date
        
        cursor.execute(
            """UPDATE transactions 
               SET item_id = ?, value = ?, type = ?, is_completed = ?, 
                   is_recurring = ?, date = ?
               WHERE id = ?""",
            (transaction.item_id, transaction.value, transaction.type,
             transaction.is_completed, transaction.is_recurring, 
             date_str, transaction.id)
        )
        self.conn.commit()
        return transaction

    def delete(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_by_item_month_year(self, item_id: int, month: int, year: int) -> List[Transaction]:
        cursor = self.conn.cursor()
        # SQLite strftime returns string, so we compare with string formatted month/year
        # %m is 01-12, %Y is YYYY
        month_str = f"{month:02d}"
        year_str = str(year)
        
        cursor.execute("""
            SELECT id, item_id, value, type, is_completed, is_recurring, date 
            FROM transactions 
            WHERE item_id = ? 
            AND strftime('%m', date) = ? 
            AND strftime('%Y', date) = ?
        """, (item_id, month_str, year_str))
        
        return [
            Transaction(
                id=row[0],
                item_id=row[1],
                value=row[2],
                type=row[3],
                is_completed=bool(row[4]),
                is_recurring=bool(row[5]),
                date=Transaction.format_date(row[6])
            )
            for row in cursor.fetchall()
        ]