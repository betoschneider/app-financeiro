# src/pages/home.py
import streamlit as st
from datetime import datetime
from src.database.connection import get_connection
from src.repository.item_repository import ItemRepository
from src.repository.transaction_repository import TransactionRepository
from src.models.item import Item
from src.models.transaction import Transaction

# Conexão com o banco de dados
conn = get_connection()
item_repo = ItemRepository(conn)
transaction_repo = TransactionRepository(conn)

# Título principal
st.title("Controle Financeiro - Manutenção")

# Primeira linha: Formulários lado a lado
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

# Segunda linha: Formulários de alteração/exclusão
col3, col4 = st.columns(2)

with col3:
    st.subheader("Alterar/Excluir Transação")
    
    # Lista de transações para seleção
    transactions = transaction_repo.get_all()
    items_dict = {item.id: item for item in item_repo.get_all()}
    
    if transactions:
        # Criar opções para o selectbox
        transaction_options = {
            f"{datetime.strftime(t.date, '%d/%m/%Y')} - {items_dict.get(t.item_id).name if items_dict.get(t.item_id) else 'N/A'} - R$ {t.value:.2f}": t 
            for t in transactions
        }
        
        selected_transaction_key = st.selectbox(
            "Selecione a Transação",
            options=list(transaction_options.keys())
        )
        
        if selected_transaction_key:
            selected_transaction = transaction_options[selected_transaction_key]
            
            with st.form("edit_transaction_form"):
                # Campos do formulário preenchidos com os valores atuais
                items = item_repo.get_all()
                item_options = {f"{item.name} ({item.category})": item.id for item in items}
                current_item = f"{items_dict[selected_transaction.item_id].name} ({items_dict[selected_transaction.item_id].category})"
                
                edit_item = st.selectbox("Item", options=list(item_options.keys()), index=list(item_options.keys()).index(current_item))
                edit_value = st.number_input("Valor", min_value=0.00, step=0.01, value=float(selected_transaction.value))
                edit_date = st.date_input("Data", value=selected_transaction.date, format="DD/MM/YYYY")
                edit_type = st.selectbox("Tipo", options=["Débito", "Crédito"], 
                                       index=0 if selected_transaction.type == "D" else 1)
                edit_completed = st.checkbox("Efetivado", value=selected_transaction.is_completed)
                edit_recurring = st.checkbox("Recorrente", value=selected_transaction.is_recurring)
                
                col_buttons = st.columns([1, 1])
                with col_buttons[0]:
                    update_button = st.form_submit_button("Atualizar", type="primary")
                with col_buttons[1]:
                    delete_button = st.form_submit_button("Excluir", type="secondary")
                
                if update_button:
                    selected_transaction.item_id = item_options[edit_item]
                    selected_transaction.value = edit_value
                    selected_transaction.date = datetime.combine(edit_date, datetime.min.time())
                    selected_transaction.type = "D" if edit_type == "Débito" else "C"
                    selected_transaction.is_completed = edit_completed
                    selected_transaction.is_recurring = edit_recurring
                    
                    transaction_repo.update(selected_transaction)
                    st.success("Transação atualizada com sucesso!")
                    st.rerun()
                
                elif delete_button:
                    transaction_repo.delete(selected_transaction.id)
                    st.success("Transação excluída com sucesso!")
                    st.rerun()

with col4:
    st.subheader("Alterar/Excluir Item")
    
    items = item_repo.get_all()
    if items:
        # Criar opções para o selectbox
        item_options = {f"{item.name} ({item.category})": item for item in items}
        selected_item_key = st.selectbox(
            "Selecione o Item",
            options=list(item_options.keys())
        )
        
        if selected_item_key:
            selected_item = item_options[selected_item_key]
            
            with st.form("edit_item_form"):
                # Campos do formulário preenchidos com os valores atuais
                edit_name = st.text_input("Nome do Item", value=selected_item.name)
                edit_category = st.text_input("Categoria", value=selected_item.category)
                
                col_buttons = st.columns([1, 1])
                with col_buttons[0]:
                    update_item_button = st.form_submit_button("Atualizar", type="primary")
                with col_buttons[1]:
                    delete_item_button = st.form_submit_button("Excluir", type="secondary")
                
                if update_item_button:
                    selected_item.name = edit_name
                    selected_item.category = edit_category
                    
                    item_repo.update(selected_item)
                    st.success("Item atualizado com sucesso!")
                    st.rerun()
                
                elif delete_item_button:
                    # Verificar se existem transações vinculadas
                    transactions = transaction_repo.get_all()
                    has_transactions = any(t.item_id == selected_item.id for t in transactions)
                    
                    if has_transactions:
                        st.error("Não é possível excluir o item pois existem transações vinculadas.")
                    else:
                        item_repo.delete(selected_item.id)
                        st.success("Item excluído com sucesso!")
                        st.rerun()
    else:
        st.info("Nenhum item disponível para edição.")