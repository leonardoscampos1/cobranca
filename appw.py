import streamlit as st
import pandas as pd
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Função para abrir o WhatsApp Web e enviar a mensagem
def enviar_whatsapp_link(numero_cliente, mensagem):
    # Inicializa o WebDriver do Chrome
    navegador = webdriver.Chrome()  # Certifique-se de que o caminho do ChromeDriver está configurado

    # Abre o WhatsApp Web
    navegador.get("https://web.whatsapp.com/")

    # Aguarda o usuário escanear o QR code e logar
    st.info("Por favor, escaneie o QR code no WhatsApp Web.")
    while len(navegador.find_elements("id", "side")) < 1:
        time.sleep(1)

    # Gera o link para enviar a mensagem
    texto = urllib.parse.quote(mensagem)
    link = f"https://web.whatsapp.com/send?phone={numero_cliente}&text={texto}"

    # Navega até o link
    navegador.get(link)

    # Aguarda a página carregar
    while len(navegador.find_elements("id", "side")) < 1:
        time.sleep(1)

    # Envia a mensagem
    navegador.find_element("xpath", '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]').send_keys(Keys.ENTER)
    st.success(f"Mensagem enviada para o número {numero_cliente}")

# Função para buscar as notas fiscais do cliente
def buscar_notas_cliente(codigo_cliente, df):
    todas_notas_cliente = df[df['Código Cliente'].astype(str).str.strip() == str(codigo_cliente).strip()]
    notas_abertas = todas_notas_cliente[todas_notas_cliente['Status'] == 'Aberta']
    return todas_notas_cliente, notas_abertas

# Função para gerar a mensagem para o WhatsApp
def gerar_mensagem(notas_cliente):
    mensagem = "Olá, seguem as notas fiscais em aberto:\n\n"
    for index, nota in notas_cliente.iterrows():
        mensagem += f"Nota Fiscal: {nota['Número NF']}\n"
        mensagem += f"Itens: {nota['Itens']}\n"
        mensagem += f"Quantidade: {nota['Quantidade']}\n"
        mensagem += f"Valor: R${nota['Valor']}\n"
        # Ajustar a data para o formato dd/mm/aaaa
        data_vencimento = nota['Data Vencimento'].strftime('%d/%m/%Y') if isinstance(nota['Data Vencimento'], pd.Timestamp) else nota['Data Vencimento']
        mensagem += f"Data de Vencimento: {data_vencimento}\n\n"
    return mensagem

# Streamlit UI
st.title("Sistema de Envio de Notas Fiscais via WhatsApp")

# Carrega os dados das notas fiscais
df = pd.read_excel('notas_fiscais.xlsx')

# Converter a coluna 'Data Vencimento' para datetime e formatar para dd/mm/aaaa
df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], errors='coerce')

# Formata a data para dd/mm/aaaa ao exibir no DataFrame
df['Data Vencimento'] = df['Data Vencimento'].dt.strftime('%d/%m/%Y')

# Exibe as primeiras linhas do DataFrame para debug
st.write(df.head())  # Debug: Veja se os dados estão corretos

# Entrada para o código do cliente
codigo_cliente = st.text_input("Digite o código do cliente")

if codigo_cliente:
    todas_notas_cliente, notas_cliente = buscar_notas_cliente(codigo_cliente, df)
    
    if not todas_notas_cliente.empty:
        st.dataframe(todas_notas_cliente)
        if not notas_cliente.empty:
            mensagem = gerar_mensagem(notas_cliente)
            st.text_area("Mensagem Gerada", mensagem)

            numero_cliente = st.text_input("Digite o número de WhatsApp do cliente (com DDI e DDD)")

            if st.button("Enviar WhatsApp"):
                if numero_cliente:
                    enviar_whatsapp_link(numero_cliente, mensagem)
                else:
                    st.error("Por favor, insira o número de WhatsApp.")
        else:
            st.warning("Nenhuma nota fiscal em aberto.")
    else:
        st.warning(f"Nenhuma nota encontrada para o cliente com código: {codigo_cliente}.")
