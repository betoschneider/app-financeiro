# src/repository/item_repository.py
import os
import sys
from typing import List

# Adiciona o diretório raiz ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from src.repository.base_repository import BaseRepository
from src.models.item import Item

class ItemRepository(BaseRepository[Item]):
    def add(self, item: Item) -> Item:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, category) VALUES (?, ?)",
            (item.name, item.category)
        )
        self.conn.commit()
        item.id = cursor.lastrowid
        return item
    
    def get_all(self) -> List[Item]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, category FROM items")
        return [Item(*row) for row in cursor.fetchall()]
    
    def get_by_id(self, id: int) -> Item:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, category FROM items WHERE id = ?", (id,))
        row = cursor.fetchone()
        return Item(*row) if row else None
    
    def update(self, item: Item) -> Item:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE items SET name = ?, category = ? WHERE id = ?",
            (item.name, item.category, item.id)
        )
        self.conn.commit()
        return item
    
    def delete(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0