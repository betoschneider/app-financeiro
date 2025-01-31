# src/main.py
import os
import sys
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

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
    
    if transactions:
        # Criar opções para o selectbox
        transaction_year = {
            f"{datetime.strftime(t.date, '%Y')} ": t 
            for t in transactions
        }
        
        selected_transaction_year = st.selectbox(
            "Selecione ano",
            options=list(transaction_year.keys())
        )
        
        data = []
        for t in transactions:
            item = items_dict.get(t.item_id)
            data.append({
                "Ano": t.date.strftime("%Y"),
                "Ref": t.date.strftime("%m"),
                "Data": t.date.strftime("%d/%m/%Y"),
                "Item": item.name if item else "N/A",
                "Categoria": item.category if item else "N/A",
                "Valor": f"R$ {t.value:.2f}",
                "Tipo": "Débito" if t.type == "D" else "Crédito",
                "Status": "Efetivado" if t.is_completed else "Pendente",
                "Recorrente": "Sim" if t.is_recurring else "Não"
            })

        # Tratamento do histórico de transações
        data = pd.DataFrame(data)
        data["Ano"] = data["Ano"].astype(int)
        data["Ref"] = data["Ref"].astype(int)
        # Seleciona o ano desejado
        data = data[data["Ano"] == int(selected_transaction_year)] 
        data = data.drop("Ano", axis=1)
        # Busca o último mês com transação
        max_mes = data["Ref"].max()
        # DF temporário com as transações recorrentes do último mês
        transacoes_recorrentes = data[(data["Ref"] == max_mes) & (data["Recorrente"] == "Sim")]
        # Adiciona as transações recorrentes para os meses seguintes
        for i in range(12 - max_mes):
            transacoes_recorrentes["Ref"] = i + max_mes + 1
            data = pd.concat([data, transacoes_recorrentes], ignore_index=True)
        # Pivotando a tabela: linhas itens, colunas mês
        data = pd.pivot_table(
            data,
            values="Valor",
            index="Item",
            columns="Ref",
            aggfunc='sum'
        ).reset_index()
        # Ajustando nome dos meses
        colunas = data.columns
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        novas_colunas = [colunas[0]] + [meses[int(num) - 1] for num in colunas[1:]]
        data.columns = novas_colunas

        # Exibindo as informações na tabela
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma transação registrada ainda.")

if __name__ == "__main__":
    main()