import streamlit as st
import pandas as pd
import cadastro_clientes
import cadastro_produtos
from envio_msg import SendMessage  
from datetime import datetime, timedelta
from streamlit_searchbox import st_searchbox
import csv
import ast  # Importar o módulo ast
import numpy as np
import json

# Função para carregar dados de um arquivo CSV
def carregar_csv(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=',', on_bad_lines='warn')
        
        if df.empty:
            print("Não há vendas registradas.")
            return df  # Retorna um DataFrame vazio ou você pode optar por retornar None
        
        df = df.fillna('')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Código Venda", "Cliente", "Vendedor", "Canal", 
            "Pagamento", "Produtos", "Total Venda", "Cashback", "Data Compra", "Expira Cashback"
        ])
        df.to_csv(nome_arquivo, index=False)
        return df

# Função para salvar dados em um arquivo CSV
def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

# Função para atualizar data de validade do cashback
def atualizar_validade_cashback(clientes_df, cliente_nome):
    # Encontrar o índice do cliente
    indice_cliente = clientes_df[clientes_df['Nome'] == cliente_nome].index[0]
    
    # Calcular nova data de validade (30 dias a partir da data atual)
    nova_data_validade = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
    
    # Atualizar a data de validade no DataFrame
    clientes_df.loc[indice_cliente, 'Data_Validade_Cashback'] = nova_data_validade
    
    # Salvar as alterações no arquivo CSV
    clientes_df.to_csv("clientes.csv", index=False)
    
    return nova_data_validade

# Função para salvar o orçamento em um arquivo JSON
def salvar_orcamento_json(orcamento, arquivo="orcamentos.json"):
    try:
        with open(arquivo, "r") as f:
            orcamentos = json.load(f)
    except FileNotFoundError:
        orcamentos = []

    orcamentos.append(orcamento)

    with open(arquivo, "w") as f:
        json.dump(orcamentos, f, indent=4)

    st.success(f"Orçamento salvo em {arquivo}")

# Função para carregar orçamentos de um arquivo JSON
def carregar_orcamentos_json(arquivo="orcamentos.json"):
    try:
        with open(arquivo, "r") as f:
            orcamentos = json.load(f)
            return orcamentos
    except FileNotFoundError:
        st.error(f"Arquivo {arquivo} não encontrado.")
        return []

# Função para exibir orçamentos
def exibir_orcamentos(orcamentos):
    for orc in orcamentos:
        st.write(f"Código: {orc['CodigoOrcamento']}")
        st.write(f"Cliente: {orc['Cliente']}")
        st.write(f"Vendedor: {orc['Vendedor']}")
        st.write(f"Canal: {orc['Canal']}")
        st.write(f"Pagamento: {orc['Pagamento']}")
        st.write("Produtos:")
        for produto in orc['Produtos']:
            st.write(f"  - {produto['Nome']}: {produto['Quantidade']} {produto['Unidade']} (R$ {produto['Subtotal']:.2f})")
        st.write(f"Total: R$ {orc['TotalOrcamento']:.2f}")
        st.write(f"Data: {orc['Data']}")
        st.write("-" * 40)

# Função para salvar os orçamentos em um arquivo CSV
def salvar_orcamentos_csv(orcamentos, arquivo="orcamentos.csv"):
    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Escreve o cabeçalho
        writer.writerow(["CodigoOrcamento", "Cliente", "Vendedor", "Canal", "Pagamento", "Produtos", "TotalOrcamento", "Data"])
        # Escreve os dados
        for orc in orcamentos:
            writer.writerow([
                orc["CodigoOrcamento"],
                orc["Cliente"],
                orc["Vendedor"],
                orc["Canal"],
                orc["Pagamento"],
                orc["Produtos"],
                orc["TotalOrcamento"],
                orc["Data"]
            ])
    st.success(f"Arquivo CSV salvo em {arquivo}")

def app():
    # Inicializar produtos_selecionados se não existir
    if 'produtos_selecionados' not in st.session_state:
        st.session_state.produtos_selecionados = []

    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Selecione uma aba:", ("Registro de Vendas", "Orçamentos Abertos"))

    if page == "Registro de Vendas":
        st.header("Registro de Vendas")
        
        # Carregar dados necessários
        clientes_df = cadastro_clientes.carregar_csv("clientes.csv")
        vendedores_df = cadastro_clientes.carregar_csv("vendedores.csv")
        produtos_df = cadastro_produtos.carregar_csv("produtos.csv")
        vendas_df = carregar_csv("vendas.csv")
        
        # Função de busca genérica
        def search_lista(lista, searchterm: str):
            if not searchterm:
                return []
            return [item for item in lista if searchterm.lower() in item.lower()]

        # Seleção de Cliente
        if not clientes_df.empty:
            # Adicionar coluna de data de validade do cashback se não existir
            if 'Data_Validade_Cashback' not in clientes_df.columns:
                # Calcular data de validade 30 dias a partir de hoje
                clientes_df['Data_Validade_Cashback'] = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
            
            # Função de busca para clientes
            def search_clientes(searchterm: str):
                if not searchterm:
                    return []
                return [p for p in clientes_df["Nome"].tolist() if searchterm.lower() in p.lower()]
            
            # Seleção de cliente com searchbox
            cliente = st_searchbox(
                search_function=search_clientes,
                placeholder="Digite o nome do cliente",
                label="Cliente",
                key="cliente_searchbox"
            )
            
            # Obter o telefone quando um cliente é selecionado
            if cliente and cliente in clientes_df["Nome"].tolist():
                cliente_info = clientes_df[clientes_df["Nome"] == cliente]
                celular = cliente_info["Telefone"].values[0]
                bonus = cliente_info["Bonus"].values[0]
                
                # Tratamento para data de validade
                try:
                    data_validade = cliente_info["Data_Validade_Cashback"].values[0]
                except KeyError:
                    # Se a coluna não existir, use a data atual + 30 dias
                    data_validade = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
                
                # Formatar o número para o padrão do WhatsApp (remover caracteres especiais e adicionar código do país)
                celular = ''.join(filter(str.isdigit, str(celular)))
                if not celular.startswith('55'):
                    celular = '55' + celular
                
                # Calcular dias restantes
                data_validade_dt = datetime.strptime(data_validade, '%d/%m/%Y')
                dias_restantes = (data_validade_dt - datetime.now()).days
                
                # Mostrar informações de cashback
                st.markdown("""
    **Informações de Cashback:** 
    - **Disponível:** R$ {:.2f} 💰
    - **Data de Validade:** {} 📅
    - **Dias Restantes:** {} dias ⏳
                """.format(bonus, data_validade, dias_restantes))
        else:
            cliente = st.selectbox("Cliente", ["Nenhum cliente cadastrado"])
        
        # Seleção de Vendedor
        if not vendedores_df.empty and vendedores_df is not None:
            # Função de busca para vendedores
            def search_vendedores(searchterm: str):
                if not searchterm:
                    return []
                # Use the first column for searching, and handle potential empty DataFrame
                try:
                    return [p for p in vendedores_df.iloc[:, 0].tolist() if searchterm.lower() in str(p).lower()]
                except IndexError:
                    return []
            
            # Seleção de vendedor com searchbox
            vendedor = st_searchbox(
                search_function=search_vendedores,
                placeholder="Digite o nome do vendedor",
                label="Vendedor",
                key="vendedor_searchbox"
            )
        else:
            vendedor = st.selectbox("Vendedor", ["Nenhum vendedor cadastrado"])
        
        
        # Seleção de Produtos
        st.subheader("Selecione o Produto")
        
        # Preparar lista de produtos com informações
        lista_produtos = produtos_df["Nome"].tolist()
        
        
        # Colunas para layout de seleção de produtos
        col_select, col_lista = st.columns([3, 2])
        
        with col_select:
            # Função de busca para o searchbox
            def search_produtos(searchterm: str):
                if not searchterm:
                    return []
                return [p for p in lista_produtos if searchterm.lower() in p.lower()]
            
            # Seleção de produto com searchbox
            produto = st_searchbox(
                search_function=search_produtos,
                placeholder="Digite o nome do produto",
                label="Produto",
                key="produto_searchbox"
            )
            
            # Mostrar informações do produto
            if produto and produto in lista_produtos:
                # Encontrar informações do produto
                produto_info = produtos_df[produtos_df["Nome"] == produto]
                
                # Colunas para mostrar informações
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Preço:** R$ {produto_info['Preço'].values[0]:.2f}")
                    st.write(f"**Estoque:** {produto_info['Estoque'].values[0]} unid.")
                
                with col2:
                    # Quantidade do produto
                    quantidade = st.number_input(
                        f"Quantidade ({produto_info['Unidade'].values[0]})", 
                        min_value=0.0, 
                        max_value=float(produto_info['Estoque'].values[0]), 
                        value=0.0,
                        step=0.1 if produto_info['Unidade'].values[0] in ['M', 'M³'] else 1.0,
                        help=f"Máximo disponível: {produto_info['Estoque'].values[0]} {produto_info['Unidade'].values[0]}"
                    )
                
                # Calcular subtotal
                if quantidade > 0:
                    preco_produto = produto_info['Preço'].values[0]
                    subtotal = quantidade * preco_produto
                    st.write(f"**Subtotal:** R$ {subtotal:.2f}")
            else:
                quantidade = 0
                subtotal = 0
            
            # Botão para adicionar produto
            if st.button("Adicionar Produto"):
                if not produto:  # Verifica se o campo produto está vazio
                    st.error("Por favor, selecione um produto.")
                elif quantidade <= 0:  # Verifica se a quantidade é válida
                    st.error("A quantidade deve ser maior que zero.")
                elif produto and produto in lista_produtos:
                    # Encontrar unidade do produto
                    try:
                        unidade = produtos_df[produtos_df["Nome"] == produto]["Unidade"].values[0]
                    except IndexError:
                        unidade = 'UN'  # Valor padrão se não encontrar
                    
                    # Adicionar produto à lista de selecionados
                    st.session_state.produtos_selecionados.append({
                        "produto": produto,
                        "quantidade": quantidade,
                        "unidade": unidade,
                        "subtotal": quantidade * produtos_df[produtos_df["Nome"] == produto]["Preço"].values[0]
                    })
                    
                    # Atualizar o estoque do produto
                    produtos_df.loc[produtos_df["Nome"] == produto, "Estoque"] -= quantidade  # Diminui a quantidade do estoque

                    # Salvar as alterações no arquivo CSV
                    produtos_df.to_csv("produtos.csv", index=False)  # Salva o DataFrame atualizado
                    
                    st.success(f"{quantidade} {unidade} de {produto} adicionado!")
        
        with col_lista:
            # Mostrar produtos selecionados
            if hasattr(st.session_state, 'produtos_selecionados') and st.session_state.produtos_selecionados:
                st.subheader("Produtos Selecionados")
                total_venda = 0
                
                # Inicializar estado de edição se não existir
                if 'produto_editando' not in st.session_state:
                    st.session_state.produto_editando = None
                
                produtos_para_remover = []
                
                for i, item in enumerate(st.session_state.produtos_selecionados):
                    # Adicionar tratamento para unidade
                    unidade = item.get('unidade', 'UN')
                    
                    # Colunas para layout
                    col1, col2, col3 = st.columns([4, 4, 2])
                    
                    with col1:
                        # Se não estiver editando, mostrar informações normalmente
                        if st.session_state.produto_editando != i:
                            st.write(f"{item['quantidade']} {unidade} x {item['produto']} - R$ {item['subtotal']:.2f}")
                            total_venda += item['subtotal']
                        else:
                            # Modo de edição
                            novo_produto = st.selectbox(
                                "Selecione o Produto", 
                                ["Selecione um produto"] + list(produtos_df["Nome"]),
                                index=list(produtos_df["Nome"]).index(item["produto"]) + 1 if item["produto"] in list(produtos_df["Nome"]) else 0,
                                key=f"editar_produto_{i}"
                            )
                            
                            nova_quantidade = st.number_input(
                                f"Quantidade ({unidade})", 
                                min_value=0.0, 
                                max_value=float(produtos_df[produtos_df["Nome"] == novo_produto]["Estoque"].values[0]) if novo_produto != "Selecione um produto" else 100.0, 
                                value=float(item["quantidade"]),
                                key=f"editar_quantidade_{i}"
                            )
                    
                    with col2:
                        # Botão de editar
                        if st.session_state.produto_editando != i:
                            if st.button(f"✏️", key=f"btn_editar_{i}"):
                                st.session_state.produto_editando = i
                        else:
                            # Botão de salvar edição
                            if st.button("💾", key=f"btn_salvar_{i}"):
                                # Calcular novo subtotal
                                if novo_produto != "Selecione um produto" and nova_quantidade > 0:
                                    novo_preco = produtos_df[produtos_df["Nome"] == novo_produto]["Preço"].values[0]
                                    novo_subtotal = nova_quantidade * novo_preco
                                    nova_unidade = produtos_df[produtos_df["Nome"] == novo_produto]["Unidade"].values[0]
                                    
                                    # Atualizar produto na lista
                                    st.session_state.produtos_selecionados[i] = {
                                        "produto": novo_produto,
                                        "quantidade": nova_quantidade,
                                        "unidade": nova_unidade,
                                        "subtotal": novo_subtotal
                                    }
                                    
                                    # Mensagem de sucesso
                                    st.success(f"Produto atualizado: {nova_quantidade} {nova_unidade} de {novo_produto}")
                                
                                # Sair do modo de edição
                                st.session_state.produto_editando = None
                    
                    with col3:
                        # Botão de excluir
                        if st.session_state.produto_editando != i:
                            if st.button(f"🗑️", key=f"btn_excluir_{i}"):
                                produtos_para_remover.append(i)
                                st.success("Produto removido!")
                
                # Remover produtos marcados para exclusão
                for index in sorted(produtos_para_remover, reverse=True):
                    del st.session_state.produtos_selecionados[index]
                
                st.write(f"**Total da Venda: R$ {total_venda:.2f}**")
                
                # Calcular total da venda
                total_venda = sum(item['subtotal'] for item in st.session_state.produtos_selecionados)
                
                # Verificar regra de cashback se um cliente foi selecionado
                if cliente and cliente != "Selecione o cliente":
                    cliente_info = clientes_df[clientes_df["Nome"] == cliente]
                    bonus = cliente_info["Bonus"].values[0]
                    
                    # Definir valor mínimo como o dobro do cashback
                    valor_minimo_cashback = bonus * 2
                    
                    with st.container():
                        st.markdown("### Informações de Cashback")
                        
                        if total_venda >= valor_minimo_cashback:
                            valor_apos_cashback = total_venda - bonus
                            st.write(f"Cashback Disponível: R$ {bonus:.2f}")
                            st.write(f"Valor Mínimo para Uso: R$ {valor_minimo_cashback:.2f}")
                            st.write(f"Valor Após Cashback: R$ {valor_apos_cashback:.2f} ✅")
                        else:
                            valor_faltante = valor_minimo_cashback - total_venda
                            st.write(f"Cashback Disponível: R$ {bonus:.2f} 💰") 
                            st.write(f"Valor Mínimo para Uso: R$ {valor_minimo_cashback:.2f} 💱")
                            st.write(f"Valor Faltante: R$ {valor_faltante:.2f} ❌")
        
        

        sender = SendMessage()

    elif page == "Orçamentos Abertos":
        st.header("Orçamentos Abertos")
        
        # Carregar e exibir orçamentos
        try:
            orcamentos_df = pd.read_csv("orcamentos.csv", encoding='utf-8', sep=',', on_bad_lines='warn')
            if orcamentos_df.empty:
                st.write("Não há orçamentos abertos.")
            else:
                for index, row in orcamentos_df.iterrows():
                    st.write(f"Código: {row['CodigoOrcamento']}")
                    st.write(f"Cliente: {row['Cliente']}")
                    st.write(f"Vendedor: {row['Vendedor']}")
                    st.write(f"Canal: {row['Canal']}")
                    st.write(f"Pagamento: {row['Pagamento']}")
                    st.write("Produtos:")
                    # st.write(f"String de Produtos: {row['Produtos']}")
                    try:
                        produtos = ast.literal_eval(row['Produtos'])  # Usando ast.literal_eval para converter a string de volta para lista
                    except (ValueError, SyntaxError) as e:
                        st.error(f"Erro ao converter produtos: {e}")
                        continue  # Pular para o próximo orçamento se houver erro
                    for produto in produtos:
                        st.write(f"  - {produto['Nome']}: {produto['Quantidade']} {produto['Unidade']} (R$ {produto['Subtotal']:.2f})")
                    st.write(f"Total: R$ {row['TotalOrcamento']:.2f}")
                    st.write(f"Data: {row['Data']}")
                    st.write("-" * 40)
        except FileNotFoundError:
            st.write("O arquivo de orçamentos não foi encontrado.")
        except pd.errors.ParserError as e:
            st.write(f"Erro ao ler o arquivo de orçamentos: {e}")

    # Seleção de Canal
    canais = ["Loja ", "WhatsApp", "Telefone"]
    canal = st.selectbox("Canal", canais)
    
    # Seleção de Pagamento
    formas_pagamento = ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito", "Boleto", "Transferência Bancária"]
    pagamento = st.selectbox("Pagamento", formas_pagamento)
    
    # Botão para criar orçamento e finalizar venda
    col_orcamento, col_finalizar = st.columns(2)  # Criar colunas para os botões
    with col_orcamento:
        if st.button("Criar Orçamento"):
            campos_faltando = []  # Lista para armazenar campos faltando

            if not cliente:  # Verifica se o campo cliente está vazio
                campos_faltando.append("Cliente")
            if not vendedor:  # Verifica se o campo vendedor está vazio
                campos_faltando.append("Vendedor")
            if not st.session_state.produtos_selecionados:  # Verifica se não há produtos selecionados
                campos_faltando.append("Produtos")

            if campos_faltando:  # Se houver campos faltando
                st.error(f"Por favor, preencha os seguintes campos: {', '.join(campos_faltando)}")  # Mensagem de erro
            else:
                # Gerar um código de orçamento
                codigo_orcamento = f"ORC-{int(datetime.now().timestamp())}"  # Exemplo de código baseado em timestamp
                
                # Coletar dados do orçamento
                produtos = [
                    {
                        "Nome": item["produto"],
                        "Quantidade": item["quantidade"],
                        "Unidade": item["unidade"],
                        "Subtotal": float(item["subtotal"]) if isinstance(item["subtotal"], (int, float)) else float(item["subtotal"].item())  # Converter para float
                    } for item in st.session_state.produtos_selecionados
                ]
                
                # Converter a lista de produtos para uma string formatada
                produtos_str = str(produtos).replace("'", "\"")  # Trocar aspas simples por aspas duplas
                produtos_str = produtos_str.replace('"', "'")  # Trocar aspas duplas por aspas simples
                
                dados_orcamento = {
                    "CodigoOrcamento": codigo_orcamento,
                    "Cliente": cliente,
                    "Vendedor": vendedor,
                    "Canal": canal,
                    "Pagamento": pagamento,
                    "Produtos": produtos_str,  # Usar a string formatada
                    "TotalOrcamento": total_venda,
                    "Data": datetime.now().strftime('%Y-%m-%d')  # Data atual formatada
                }
                
                # Salvar o orçamento no arquivo CSV
                with open("orcamentos.csv", "a", newline='') as f:  # Abre o arquivo CSV em modo de anexação
                    writer = csv.writer(f)
                    writer.writerow([dados_orcamento['CodigoOrcamento'], dados_orcamento['Cliente'], dados_orcamento['Vendedor'], dados_orcamento['Canal'], dados_orcamento['Pagamento'], dados_orcamento['Produtos'], dados_orcamento['TotalOrcamento'], dados_orcamento['Data']])

                # Exibir o orçamento formatado
                st.write(f"**Código:** {dados_orcamento['CodigoOrcamento']}")
                st.write(f"**Cliente:** {dados_orcamento['Cliente']}")
                st.write(f"**Vendedor:** {dados_orcamento['Vendedor']}")
                st.write(f"**Canal:** {dados_orcamento['Canal']}")
                st.write(f"**Pagamento:** {dados_orcamento['Pagamento']}")
                st.write("**Produtos:**")
                for produto in produtos:
                    st.write(f"  - {produto['Nome']}: {produto['Quantidade']} {produto['Unidade']} (R$ {produto['Subtotal']:.2f})")
                st.write(f"**Total:** R$ {dados_orcamento['TotalOrcamento']:.2f}")
                st.write(f"**Data:** {dados_orcamento['Data']}")
                st.write("----------------------------------------")

    with col_finalizar:
        if st.button("Finalizar Venda"):
            campos_faltando = []  # Lista para armazenar campos faltando

            if not cliente:  # Verifica se o campo cliente está vazio
                campos_faltando.append("Cliente")
            if not vendedor:  # Verifica se o campo vendedor está vazio
                campos_faltando.append("Vendedor")
            if not st.session_state.produtos_selecionados:  # Verifica se não há produtos selecionados
                campos_faltando.append("Produtos")

            if campos_faltando:  # Se houver campos faltando
                st.error(f"Por favor, preencha os seguintes campos: {', '.join(campos_faltando)}")  # Mensagem de erro
            else:
                # Mensagens de depuração para verificar quais campos estão vazios
                if not cliente:
                    st.warning("O campo Cliente está vazio.")
                if not vendedor:
                    st.warning("O campo Vendedor está vazio.")
                if not st.session_state.produtos_selecionados:
                    st.warning("Nenhum produto foi selecionado.")
                    
                st.error("Por favor, preencha todos os campos necessários.")

if __name__ == "__main__":
    app()