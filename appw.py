import streamlit as st
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Configurações do Streamlit
st.set_page_config(page_title="Cobrança de Clientes", page_icon="💬")
st.title("💬 Sistema de Cobrança via WhatsApp (Automático)")

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

    if st.button("📤 Enviar mensagens pelo WhatsApp"):
        st.info("🔹 Abrindo o navegador... Escaneie o QR Code no WhatsApp Web se necessário.")

        try:
            # Configuração do Selenium
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")

            # Ajuste o caminho do chromedriver no seu PC
            service = Service(r"C:\caminho\para\chromedriver.exe")

            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get("https://web.whatsapp.com/")

            # Aguardar login
            while len(driver.find_elements(By.ID, "side")) < 1:
                st.warning("Escaneie o QR Code no WhatsApp Web...")
                time.sleep(2)

            st.success("✅ WhatsApp Web carregado com sucesso!")

            # Agrupar mensagens por cliente
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

                # Abrir a conversa
                url = f"https://web.whatsapp.com/send?phone=55{telefone}&text={urllib.parse.quote(texto)}"
                driver.get(url)
                time.sleep(8)

                # Enviar mensagem automaticamente
                try:
                    campo_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    campo_texto.send_keys(Keys.ENTER)
                    st.success(f"✅ Mensagem enviada para {nome_cliente} ({telefone})")
                except:
                    st.error(f"❌ Falha ao enviar para {nome_cliente} ({telefone})")

                time.sleep(5)

            st.success("🎉 Todas as mensagens foram enviadas!")

        except Exception as e:
            st.error(f"⚠️ Erro ao iniciar o Selenium: {str(e)}")
