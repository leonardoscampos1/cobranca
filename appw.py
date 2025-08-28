import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Cobrança de Clientes", page_icon="💬")
st.title("💬 Sistema de Cobrança via WhatsApp")

uploaded_file = st.file_uploader("📤 Envie o arquivo Excel ou CSV", type=["xlsx", "csv"])

if uploaded_file:
    # Ler arquivo
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, dtype=str)
    else:
        df = pd.read_csv(uploaded_file, dtype=str, sep=';')

    # Formatar colunas
    df['EMISSÃO'] = pd.to_datetime(df['EMISSÃO'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['VENCIMENTO'] = pd.to_datetime(df['VENCIMENTO'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['VALOR'] = df['VALOR'].str.replace(',', '.').astype(float)
    df['VALOR'] = df['VALOR'].map(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    st.success("✅ Arquivo carregado com sucesso!")
    st.dataframe(df.head())

    # Agrupar por cliente
    clientes = df.groupby('CÓD.')
    for cod, dados_cliente in clientes:
        nome_cliente = dados_cliente['CLIENTE'].iloc[0]
        telefone = dados_cliente['TELEFONE'].iloc[0]

        # Montar mensagem
        texto = f"Olá {nome_cliente}, segue o resumo das suas notas fiscais pendentes:\n\n"
        for _, row in dados_cliente.iterrows():
            texto += (
                f"NF: {row['NF']}\n"
                f"Emissão: {row['EMISSÃO']}\n"
                f"Vencimento: {row['VENCIMENTO']}\n"
                f"Valor: {row['VALOR']}\n"
                f"Observação: {row['OBS']}\n\n"
            )
        texto += f"Atenciosamente,\n{dados_cliente['VENDEDOR'].iloc[0]}"

        # Criar link WhatsApp
        link = f"https://web.whatsapp.com/send?phone=55{telefone}&text={urllib.parse.quote(texto)}"
        st.markdown(f"[📤 Enviar mensagem para {nome_cliente} ({telefone})]({link})", unsafe_allow_html=True)
