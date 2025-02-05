# src/main.py
import os
import sys
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

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

        # Definindo as datas atuais
        data_atual = datetime.now()
        mes_atual = data_atual.month
        ano_atual = data_atual.year

        # Definindo as datas da referência anterior
        data_mes_anterior = data_atual.replace(day=1) - timedelta(days=1)
        mes_data_anterior = data_mes_anterior.strftime("%m")
        ano_data_anterior = data_mes_anterior.strftime("%Y")

        # Tratamento do histórico de transações
        data = pd.DataFrame(data)
        data["Ano"] = data["Ano"].astype(int)
        data["Ref"] = data["Ref"].astype(int)

        # Dataframe com transações recorrentes da referência anterior
        transacoes_recorrentes = data[(data["Ref"] == int(mes_data_anterior)) & (data["Ano"] == int(ano_data_anterior)) & (data["Recorrente"] == "Sim")]
        transacoes_recorrentes = transacoes_recorrentes.drop("Ano", axis=1)

        # Seleciona as transações do ano desejado
        data = data[data["Ano"] == int(selected_transaction_year)] 
        data = data.drop("Ano", axis=1)

        # Se o ano selecionado for o atual, projeta as transações recorrentes para os meses seguintes
        if ano_atual == int(selected_transaction_year):
            # Adiciona as transações recorrentes para os meses seguintes
            for i in range(13 - mes_atual):
                transacoes_recorrentes["Ref"] = i + mes_atual

                # Cria uma chave de identificação única
                transacoes_recorrentes['chave'] = transacoes_recorrentes['Item'] + transacoes_recorrentes['Ref'].astype(str)
                data['chave'] = data['Item'] + data['Ref'].astype(str)

                # Atualiza usando merge
                transacoes_recorrentes = (
                    transacoes_recorrentes.merge(
                        data,
                        on='chave',
                        how='left',
                        suffixes=('', '_novo')
                    )
                )

                # Atualiza as colunas onde há correspondência
                colunas = ['Ref', 'Data', 'Item','Categoria', 'Valor', 'Tipo', 'Status', 'Recorrente']
                for col in colunas:
                    mascara = ~transacoes_recorrentes[f'{col}_novo'].isna()
                    transacoes_recorrentes.loc[mascara, col] = transacoes_recorrentes.loc[mascara, f'{col}_novo']

                # Remove as colunas temporárias
                transacoes_recorrentes = transacoes_recorrentes.drop([col + '_novo' for col in colunas] + ['chave'], axis=1)

                # Concatena os dataframes
                data = pd.concat([data, transacoes_recorrentes], ignore_index=True)

        # Remove duplicatas
        data.drop_duplicates(inplace=True)

        # Trata possíveis erros e garante a conversão correta da coluna Valor para numérico
        data['Valor'] = pd.to_numeric(
            data['Valor'].str.replace('R$', '').str.strip(),
            errors='coerce'
        )

        # Multiplica o valor por -1 se o tipo for Débito
        data['Valor'] = np.where(data['Tipo'] == 'Débito', data['Valor'] * -1, data['Valor'])

        # Pivotando a tabela: linhas itens, colunas mês
        df_exibicao = pd.pivot_table(
            data,
            values="Valor",
            index="Item",
            columns="Ref",
            aggfunc='sum'
        ).reset_index()

        # Ajustando nome dos meses da tabela pivotada
        colunas = df_exibicao.columns
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        novas_colunas = [colunas[0]] + [meses[int(num) - 1] for num in colunas[1:]]
        df_exibicao.columns = novas_colunas

        # Formatação dos valores para exibição
        for num in colunas[1:]:
            df_exibicao[meses[int(num) - 1]] = df_exibicao[meses[int(num) - 1]].apply(lambda x: f"{x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.') if pd.notna(x) else "")
        
        # Adiciona as colunas de categoria aos itens
        df_item = data[["Item", "Categoria", "Tipo"]]
        df_item = df_item.drop_duplicates()
        df_exibicao = df_exibicao.merge(df_item, on="Item", how="left")

        # Classifica o dataframe: Créditos primeiro
        df_exibicao.sort_values(by=["Tipo", "Categoria", "Item"], inplace=True)

        # Reorganiza as colunas
        colunas = df_exibicao.columns.tolist()
        nova_ordem = ['Item', 'Categoria', 'Tipo'] + [col for col in colunas if col not in ['Item', 'Categoria', 'Tipo']]
        df_exibicao = df_exibicao.reindex(columns=nova_ordem)
        df_exibicao.drop(columns=["Tipo"], inplace=True)

        # Exibindo as informações na tabela
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma transação registrada ainda.")

if __name__ == "__main__":
    main()