import streamlit as st
import pandas as pd
import datetime

# Função para atualizar a situação das notas com base na data de vencimento
def atualizar_situacao(df):
    hoje = datetime.datetime.now()
    df['SITUAÇÂO'] = df['VENCIMENTO'].apply(
        lambda x: 'VENCIDA' if x < hoje else 
        ('VENCE EM 7 DIAS' if (x - hoje).days <= 7 else 'NO PRAZO')
    )
    return df

# Carrega os dados das notas fiscais
df = pd.read_excel(r'G:/Drives compartilhados/FINANCEIRO (CONTAS A RECEBER)/Controle TLR/Notas Fiscais.xlsx')
df.columns = df.columns.str.strip()  # Remove espaços em branco nos nomes das colunas

# Converte a coluna VENCIMENTO para o formato de data
df['VENCIMENTO'] = pd.to_datetime(df['VENCIMENTO'])
df['NF'] = df['NF'].astype(str)

# Atualiza a situação das notas
df = atualizar_situacao(df)

# Remove duplicatas para filtros
clientes = df['EMPRESA'].drop_duplicates().tolist()
filiais = df['FILIAL'].drop_duplicates().tolist()  # Supondo que há uma coluna FILIAL
situacoes = df['SITUAÇÂO'].drop_duplicates().tolist()

# Seleciona cliente, filial e situação
cliente_selecionado = st.selectbox("Selecione o cliente", options=clientes)
filial_selecionada = st.selectbox("Selecione a filial", options=filiais)
situacao_selecionada = st.selectbox("Selecione a situação", options=situacoes)

# Filtra as notas com base nos selecionados
notas_cliente = df[
    (df['EMPRESA'] == cliente_selecionado) & 
    (df['FILIAL'] == filial_selecionada) & 
    (df['SITUAÇÂO'] == situacao_selecionada)
]

# Exibe as notas filtradas
if not notas_cliente.empty:
    st.subheader("Notas Filtradas:")
    
    # Remove duplicatas ao exibir checkboxes
    notas_cliente = notas_cliente.drop_duplicates(subset=['NF'])  # Mude o campo se necessário
    notas_selecionadas = []
    
    for index, nota in notas_cliente.iterrows():
        checkbox_key = f"nota_{index}"  # Chave única
        if st.checkbox(f"Nota Fiscal: {nota['NF']} - Preço Final: R${nota['PRECO_FINAL']} - Venc.: {nota['VENCIMENTO'].strftime('%d/%m/%Y')}", key=checkbox_key):
            notas_selecionadas.append(nota)

    # Detalhes das notas selecionadas
    if notas_selecionadas:
        st.subheader("Detalhes das Notas Selecionadas:")
        for nota in notas_selecionadas:
            st.write(f"**Nota:** {nota['NF']}")
            st.write(f"**Itens:** {nota['Itens']}")
            st.write(f"**Quantidade:** {nota['Quantidade']}")
            st.write(f"**Preço Final:** R${nota['PRECO_FINAL']}")
else:
    st.warning("Nenhuma nota encontrada para os filtros selecionados.")
