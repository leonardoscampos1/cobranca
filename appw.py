import streamlit as st
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidSessionIdException
import time

st.set_page_config(page_title="Cobrança de Clientes", page_icon="💬", layout="centered")
st.title("💬 Sistema de Cobrança via WhatsApp (Automático)")

uploaded_file = st.file_uploader("📤 Envie o arquivo Excel ou CSV com os dados", type=["xlsx", "csv"])

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

    if st.button("📤 Enviar mensagens pelo WhatsApp"):
        st.info("🔹 Abrindo o navegador... Escaneie o QR Code no WhatsApp Web se necessário.")
        try:
            # Inicializar Selenium
            driver = webdriver.Chrome()  # Ajuste caso use outro driver
            driver.get("https://web.whatsapp.com/")
            # Espera até que o painel lateral do WhatsApp Web apareça (elemento com ID "side")
            while len(driver.find_elements(By.ID, "side")) < 1:
                st.info("🔹 Aguardando carregamento do WhatsApp Web (escaneie o QR Code se necessário)...")
                time.sleep(1)

            st.success("✅ WhatsApp Web carregado. Aguardando estabilização...")
            time.sleep(3)  # tempo extra para garantir que tudo carregou
        except InvalidSessionIdException as e:
            st.error("⚠️ Ocorreu um erro na sessão do navegador!") 

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
                    f"Valor: {row['VALOR']:.2f}".replace('.', ',') + "\n"
                    f"Observação: {row['OBS']}\n\n"
                )
            texto += f"Atenciosamente,\n{dados_cliente['VENDEDOR'].iloc[0]}"

            # Abrir WhatsApp para o telefone
            url = f"https://web.whatsapp.com/send?phone=55{telefone}&text={urllib.parse.quote(texto)}"
            driver.get(url)
            time.sleep(10)  # esperar carregar a conversa

            # Enviar mensagem pressionando Enter
            try:
                campo_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                campo_texto.send_keys(Keys.ENTER)
                st.success(f"✅ Mensagem enviada para {nome_cliente} ({telefone})")
            except:
                st.error(f"❌ Não foi possível enviar para {nome_cliente} ({telefone})")
            
            time.sleep(5)  # esperar antes de enviar para o próximo cliente

        st.success("🎉 Todas as mensagens foram enviadas!")
