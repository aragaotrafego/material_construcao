import streamlit as st
import pandas as pd

# Função para carregar dados de um arquivo CSV
def carregar_csv(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',')
        df = df.fillna('')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Código", "Nome", "Categoria", "Preço", "Estoque"])
        df.to_csv(nome_arquivo, index=False)
        return df

# Função para salvar dados em um arquivo CSV
def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

def app():
    st.header("Cadastro de Produtos")
    
    # Carregar produtos do CSV
    produtos_df = carregar_csv("produtos.csv")
    
    # Colunas para organizar o formulário
    col1, col2 = st.columns(2)
    
    with col1:
        # Campos de entrada para informações do produto
        codigo = st.text_input("Código do Produto", key="codigo_produto")
        nome = st.text_input("Nome do Produto", key="nome_produto")
    
    with col2:
        categoria = st.selectbox("Categoria", 
            ["Construção", "Elétrica", "Hidráulica", "Acabamento"], 
            key="categoria_produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.1, key="preco_produto")
    
    estoque = st.number_input("Quantidade em Estoque", min_value=0, step=1, key="estoque_produto")
    
    # Botão de cadastro
    if st.button("Cadastrar Produto"):
        # Validação dos campos
        if codigo and nome and categoria:
            # Criar novo DataFrame com o produto
            novo_produto = pd.DataFrame({
                "Código": [codigo],
                "Nome": [nome],
                "Categoria": [categoria],
                "Preço": [preco],
                "Estoque": [estoque]
            })
            
            # Adiciona o novo produto ao DataFrame existente
            produtos_df = pd.concat([produtos_df, novo_produto], ignore_index=True)
            
            # Salva o DataFrame atualizado no arquivo CSV
            salvar_csv(produtos_df, "produtos.csv")
            
            # Mensagens de feedback
            st.success("Produto cadastrado com sucesso!")
            st.balloons()  # Efeito visual de comemoração
        else:
            st.error("Preencha todos os campos obrigatórios.")
    
    # Exibição da lista de produtos cadastrados
    st.subheader("Produtos Cadastrados")
    if not produtos_df.empty:
        st.dataframe(produtos_df)
    else:
        st.info("Nenhum produto cadastrado ainda.")

if __name__ == "__main__":
    app()