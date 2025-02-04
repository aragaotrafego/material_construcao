import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Função para carregar dados de um arquivo CSV
def carregar_csv(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        df = df.fillna('')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Nome", "Telefone", "Endereço", "Bonus", "Data_Validade_Cashback"])
        df.to_csv(nome_arquivo, index=False)
        return df

# Função para salvar dados em um arquivo CSV
def salvar_csv(df, nome_arquivo):
    # Remover espaços nos nomes das colunas e manter apenas uma coluna de data de validade
    df.columns = [col.strip() for col in df.columns]
    if 'Data_Validade_Cashback' in df.columns and df.columns.tolist().count('Data_Validade_Cashback') > 1:
        df = df.loc[:, ~df.columns.duplicated()]
    
    df.to_csv(nome_arquivo, index=False)

def app():
    st.header("Gerenciamento de Clientes")
    
    # Carregar clientes do CSV
    clientes_df = carregar_csv("clientes.csv")
    
    # Opções de ação
    acao = st.radio("Selecione uma ação", ["Visualizar Clientes", "Adicionar Cliente", "Editar/Excluir Cliente"])
    
    if acao == "Visualizar Clientes":
        st.subheader("Clientes Cadastrados")
        if not clientes_df.empty:
            st.dataframe(clientes_df)
        else:
            st.info("Nenhum cliente cadastrado.")
    
    elif acao == "Adicionar Cliente":
        st.subheader("Adicionar Novo Cliente")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telefone", value="55 ", placeholder="Formato: 55 21999999999")
            if not telefone.startswith("55 ") and telefone:  # Verifica se o telefone começa com 55 e não está vazio
                telefone = "55 " + telefone  # Adiciona 55 se não estiver presente
        
        with col2:
            endereco = st.text_input("Endereço")
                    
        if st.button("Cadastrar"):
            if nome and telefone and endereco:
                # Definir data atual e bônus inicial
                data_atual = datetime.now().strftime('%d/%m/%Y')
                
                novo_cliente = pd.DataFrame({
                    "Nome": [nome],
                    "Telefone": [telefone],
                    "Endereço": [endereco],
                    "Bonus": [0.0],  # Bônus inicial zero
                    "Data_Validade_Cashback": [data_atual]  # Data atual como validade inicial
                })
                
                clientes_df = pd.concat([clientes_df, novo_cliente], ignore_index=True)
                salvar_csv(clientes_df, "clientes.csv")
                st.success("Cliente cadastrado com sucesso!")
                st.write("Detalhes do novo cliente:")
                st.write(novo_cliente)
                st.write(f"Total de clientes: {len(clientes_df)}")
            else:
                st.error("Preencha todos os campos.")
    
    elif acao == "Editar/Excluir Cliente":
        st.subheader("Editar ou Excluir Cliente")
        
        if not clientes_df.empty:
            # Selecionar cliente para edição/exclusão
            indice_cliente = st.selectbox(
                "Selecione o cliente", 
                range(len(clientes_df)), 
                format_func=lambda x: clientes_df.loc[x, "Nome"]
            )
            
            # Mostrar detalhes do cliente selecionado
            cliente_selecionado = clientes_df.loc[indice_cliente]
            
            col1, col2 = st.columns(2)
            
            with col1:
                novo_nome = st.text_input("Nome", value=cliente_selecionado["Nome"])
                novo_telefone = st.text_input("Telefone", value=cliente_selecionado["Telefone"])
            
            with col2:
                novo_endereco = st.text_input("Endereço", value=cliente_selecionado["Endereço"])
                novo_bonus = st.number_input(
                    "Bonus", 
                    value=float(cliente_selecionado["Bonus"]) if pd.notna(cliente_selecionado["Bonus"]) else 0.0, 
                    min_value=0.0
                )
                data_atual = datetime.now().strftime('%d/%m/%Y')
                novo_data_validade_cashback = st.date_input("Data Validade Cashback", value=datetime.strptime(data_atual, '%d/%m/%Y'))
                novo_data_validade_cashback = novo_data_validade_cashback.strftime('%d/%m/%Y')
                            
            col_editar, col_excluir = st.columns(2)
            
            with col_editar:
                if st.button("Atualizar Cliente"):
                    clientes_df.loc[indice_cliente] = [novo_nome, novo_telefone, novo_endereco, novo_bonus, novo_data_validade_cashback]
                    salvar_csv(clientes_df, "clientes.csv")
                    st.success("Cliente atualizado com sucesso!")
            
            with col_excluir:
                if st.button("Excluir Cliente"):
                    clientes_df = clientes_df.drop(indice_cliente)
                    salvar_csv(clientes_df, "clientes.csv")
                    st.success("Cliente excluído com sucesso!")
                    st.experimental_rerun()

if __name__ == "__main__":
    app()