# src/main.py
import os
import sys
import streamlit as st
import sqlite3
from datetime import datetime

# Adiciona o diretório raiz ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.database.connection import get_connection
from src.repository.item_repository import ItemRepository
from src.repository.transaction_repository import TransactionRepository
from src.models.item import Item
from src.models.transaction import Transaction

# Configuração inicial do Streamlit
st.set_page_config(page_title="Controle Financeiro", layout="wide")

# Conexão com o banco de dados
conn = get_connection()
item_repo = ItemRepository(conn)
transaction_repo = TransactionRepository(conn)

def main():
    st.title("Controle Financeiro")
    
    # Sidebar para formulários
    with st.sidebar:
        st.header("Nova Transação")
        with st.form("transaction_form"):
            items = item_repo.get_all()
            item_options = {f"{item.name} ({item.category})": item.id for item in items}
            
            selected_item = st.selectbox("Item", options=list(item_options.keys()))
            value = st.number_input("Valor", min_value=0.00, step=0.01)
            date = st.date_input("Data", value="today", min_value=None, max_value=None, key=None, help=None, on_change=None, format="DD/MM/YYYY", disabled=False, label_visibility="visible")
            trans_type = st.selectbox("Tipo", options=["Débito", "Crédito"])
            is_completed = st.checkbox("Efetivado")
            is_recurring = st.checkbox("Recorrente")
            submit_trans = st.form_submit_button("Registrar Transação")
            
            if submit_trans and selected_item and value:
                transaction = Transaction(
                    item_id=item_options[selected_item],
                    value=value,
                    type="D" if trans_type == "Débito" else "C",
                    is_completed=is_completed,
                    is_recurring=is_recurring,
                    date=date
                )
                transaction_repo.add(transaction)
                st.success("Transação registrada com sucesso!")
    
        st.header("Cadastro de Item")
        with st.form("item_form"):
            item_name = st.text_input("Nome do Item")
            category = st.text_input("Categoria")
            submit_item = st.form_submit_button("Cadastrar Item")
            
            if submit_item and item_name and category:
                item = Item(name=item_name, category=category)
                item_repo.add(item)
                st.success("Item cadastrado com sucesso!")
        
        
    # Área principal - Matriz de transações
    transactions = transaction_repo.get_all()
    items_dict = {item.id: item for item in item_repo.get_all()}
    def formatar_data(data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y")

    
    if transactions:
        data = []
        for t in transactions:
            item = items_dict.get(t.item_id)
            data.append({
                "Data": formatar_data(t.date),
                "Item": item.name if item else "N/A",
                "Categoria": item.category if item else "N/A",
                "Valor": f"R$ {t.value:.2f}",
                "Tipo": "Débito" if t.type == "D" else "Crédito",
                "Status": "Efetivado" if t.is_completed else "Pendente",
                "Recorrente": "Sim" if t.is_recurring else "Não"
            })
        
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma transação registrada ainda.")

if __name__ == "__main__":
    main()