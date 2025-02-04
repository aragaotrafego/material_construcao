import streamlit as st
import pandas as pd

# Função para carregar dados de um arquivo CSV
def carregar_csv(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        df = df.fillna('')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Nome", "Telefone", "Endereço"])
        df.to_csv(nome_arquivo, index=False)
        return df

# Função para salvar dados em um arquivo CSV
def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

def app():
    st.header("Gerenciamento de Vendedores")
    
    # Carregar vendedores do CSV
    vendedores_df = carregar_csv("vendedores.csv")
    
    # Opções de ação
    acao = st.radio("Selecione uma ação", ["Visualizar Vendedores", "Adicionar Vendedor", "Editar/Excluir Vendedor"])
    
    if acao == "Visualizar Vendedores":
        st.subheader("Vendedores Cadastrados")
        if not vendedores_df.empty:
            st.dataframe(vendedores_df)
        else:
            st.info("Nenhum vendedor cadastrado.")
    
    elif acao == "Adicionar Vendedor":
        st.subheader("Adicionar Novo Vendedor")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telefone")
        
        with col2:
            endereco = st.text_input("Endereço")
           
        
        if st.button("Cadastrar"):
            if nome and telefone and endereco:
                novo_vendedor = pd.DataFrame({
                    "Nome": [nome],
                    "Telefone": [telefone],
                    "Endereço": [endereco],
                    
                })
                
                vendedores_df = pd.concat([vendedores_df, novo_vendedor], ignore_index=True)
                salvar_csv(vendedores_df, "vendedores.csv")
                st.success("Vendedor cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos.")
    
    elif acao == "Editar/Excluir Vendedor":
        st.subheader("Editar ou Excluir Vendedor")
        
        if not vendedores_df.empty:
            # Selecionar vendedor para edição/exclusão
            indice_vendedor = st.selectbox(
                "Selecione o vendedor", 
                range(len(vendedores_df)), 
                format_func=lambda x: vendedores_df.loc[x, "Nome"]
            )
            
            # Mostrar detalhes do vendedor selecionado
            vendedor_selecionado = vendedores_df.loc[indice_vendedor]
            
            col1, col2 = st.columns(2)
            
            with col1:
                novo_nome = st.text_input("Nome", value=vendedor_selecionado["Nome"])
                novo_telefone = st.text_input("Telefone", value=vendedor_selecionado["Telefone"])
            
            with col2:
                novo_endereco = st.text_input("Endereço", value=vendedor_selecionado["Endereço"])
                
            
            col_editar, col_excluir = st.columns(2)
            
            with col_editar:
                if st.button("Atualizar Vendedor"):
                    vendedores_df.loc[indice_vendedor] = [novo_nome, novo_telefone, novo_endereco]
                    salvar_csv(vendedores_df, "vendedores.csv")
                    st.success("Vendedor atualizado com sucesso!")
            
            with col_excluir:
                if st.button("Excluir Vendedor", type="primary"):
                    vendedores_df = vendedores_df.drop(indice_vendedor).reset_index(drop=True)
                    salvar_csv(vendedores_df, "vendedores.csv")
                    st.warning("Vendedor excluído com sucesso!")

if __name__ == "__main__":
    app()