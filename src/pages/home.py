import streamlit as st
from src.database.connection import get_connection
from src.repository.item_repository import ItemRepository
from src.repository.transaction_repository import TransactionRepository
from src.models.item import Item
from src.models.transaction import Transaction

# Conexão com o banco de dados
conn = get_connection()
item_repo = ItemRepository(conn)
transaction_repo = TransactionRepository(conn)


col1, col2 = st.columns(2)

with col1:
    st.subheader("Nova Transação")
    with st.form("transaction_form"):
        items = item_repo.get_all()
        item_options = {f"{item.name} ({item.category})": item.id for item in items}

        selected_item = st.selectbox("Item", options=list(item_options.keys()))
        value = st.number_input("Valor", min_value=0.00, step=0.01)
        date = st.date_input("Data", format="DD/MM/YYYY")
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

with col2:
    st.subheader("Cadastro de Item")
    with st.form("item_form"):
        item_name = st.text_input("Nome do Item")
        category = st.text_input("Categoria")
        submit_item = st.form_submit_button("Cadastrar Item")

        if submit_item and item_name and category:
            item = Item(name=item_name, category=category)
            item_repo.add(item)
            st.success("Item cadastrado com sucesso!")