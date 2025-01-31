# src/database/connection.py
import sqlite3
import os

def get_connection():
    db_path = os.getenv("DATABASE_URL", "data/financial.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Criar tabelas se não existirem
    with open("src/database/schema.sql") as f:
        conn.executescript(f.read())
    
    return conn