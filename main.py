import streamlit as st
from datetime import datetime
import time
import pandas as pd
import os
import cadastro_clientes        
import cadastro_produtos        
import registro_vendas        
import cadastro_vendedores        
import vendas_realizadas_e_orcamentos
# Configuração da página
st.set_page_config(layout="wide")

# Título da aplicação
st.title("Sistema de Vendas")

# Função para carregar dados de um arquivo CSV, criando-o se não existir
def carregar_csv(nome_arquivo):
    try:
        # Tenta carregar o arquivo CSV com tratamento de encoding e separador
        if "clientes" in nome_arquivo:
            df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        elif "vendedores" in nome_arquivo:
            df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        else:
            df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        
        # Preencher valores NaN com string vazia ou 0
        df = df.fillna('')
        return df
    except FileNotFoundError:
        # Se o arquivo não existir, cria um DataFrame vazio com as colunas corretas
        if "clientes" in nome_arquivo:
            df = pd.DataFrame(columns=["Nome", "Telefone", "Endereço", "Bonus"])
        elif "vendedores" in nome_arquivo:
            df = pd.DataFrame(columns=["Nome", "Código"])
        else:
            df = pd.DataFrame()
        
        # Salva o DataFrame vazio como um novo arquivo CSV
        df.to_csv(nome_arquivo, index=False)
        return df

# Função para salvar dados em um arquivo CSV
def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)    

# Carregar dados dos arquivos CSV
vendedores_df = carregar_csv("vendedores.csv")
clientes_df = carregar_csv("clientes.csv")
produtos_df = carregar_csv("produtos.csv")

# Criando abas para diferentes funcionalidades
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Registro de Vendas", 
    "Cadastro de Clientes", 
    "Cadastro de Produtos", 
    "Cadastro de Vendedores",
    "Vendas e Orcamentos"
])


# Aba de Registro de Vendas
with tab1:
    registro_vendas.app()

# Aba de Cadastro de Clientes
with tab2:
    # Chama a função app() do módulo de cadastro de clientes
    cadastro_clientes.app()

# Aba de Cadastro de Produtos
with tab3:
    cadastro_produtos.app()

# Aba de Cadastro de Vendedores
with tab4:
    cadastro_vendedores.app()

with tab5: 
    vendas_realizadas_e_orcamentos.app()