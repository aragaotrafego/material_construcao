import streamlit as st
import pandas as pd

def app():
    st.title("Vendas Realizadas e Orçamentos")
    
    # Carregar dados de vendas e orçamentos
    try:
        vendas_df = pd.read_csv("vendas.csv", encoding='utf-8', sep=',', on_bad_lines='warn')
        
        if vendas_df.empty:
            print("Não há vendas registradas.")
            return vendas_df  # Retorna um DataFrame vazio ou você pode optar por retornar None
            
    except pd.errors.ParserError as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return None  # Retorna None ou um DataFrame vazio, conforme necessário
    
    # Exibir dados
    st.subheader("Vendas Realizadas")
    st.dataframe(vendas_df)
    
    st.subheader("Orçamentos")
    #st.dataframe(orcamentos_df)

    # Aqui você pode adicionar mais funcionalidades, como filtros ou gráficos
