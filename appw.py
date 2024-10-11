import streamlit as st
import pandas as pd
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re

# Função para enviar mensagem via WhatsApp
def enviar_whatsapp_link(numero_cliente, mensagem):
    try:
        navegador = webdriver.Chrome()
        navegador.get("https://web.whatsapp.com/")
        st.info("Por favor, escaneie o QR code no WhatsApp Web.")
        
        while len(navegador.find_elements("id", "side")) < 1:
            time.sleep(1)

        texto = urllib.parse.quote(mensagem)
        link = f"https://web.whatsapp.com/send?phone={numero_cliente}&text={texto}"
        navegador.get(link)

        while len(navegador.find_elements("id", "side")) < 1:
            time.sleep(1)

        # Envia a mensagem
        navegador.find_element("xpath", '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]').send_keys(Keys.ENTER)
        st.success(f"Mensagem enviada para o número {numero_cliente}")
    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")
    finally:
        navegador.quit()

# Função para buscar notas fiscais de um cliente
def buscar_notas_cliente(cliente, df):
    todas_notas_cliente = df[df['EMPRESA'].astype(str).str.strip() == str(cliente).strip()]
    notas_abertas = todas_notas_cliente[todas_notas_cliente['SITUAÇÂO'] == 'VENCIDA']
    return todas_notas_cliente, notas_abertas

# Função para gerar mensagem a ser enviada
def gerar_mensagem(notas_cliente):
    mensagem = "Olá, seguem as notas fiscais em aberto:\n\n"
    for index, nota in notas_cliente.iterrows():
        mensagem += f"Nota Fiscal: {nota['NF']}\n"
        mensagem += f"Itens: {nota['Itens']}\n"
        mensagem += f"Quantidade: {nota['Quantidade']}\n"
        mensagem += f"Valor: R${nota['Valor']}\n"
        data_vencimento = nota['VENCIMENTO'].strftime('%d/%m/%Y')  # Formatação da data
        mensagem += f"Data de Vencimento: {data_vencimento}\n\n"
    return mensagem

# Título do aplicativo
st.title("Sistema de Envio de Notas Fiscais via WhatsApp")

# Caminho do arquivo
caminho_arquivo = r'G:/Drives compartilhados/FINANCEIRO (CONTAS A RECEBER)/Controle TLR/Notas Fiscais.xlsx'

# Botão para atualizar os dados
if st.button("Atualizar Dados"):
    df = pd.read_excel(caminho_arquivo)
    st.success("Dados atualizados com sucesso!")
else:
    df = pd.read_excel(caminho_arquivo)

df.columns = df.columns.str.strip()

# Converte a coluna VENCIMENTO para o formato de data e trata a coluna NF como texto
df['VENCIMENTO'] = pd.to_datetime(df['VENCIMENTO'])
df['NF'] = df['NF'].astype(str)

# Formata a coluna VENCIMENTO para o formato desejado
df['VENCIMENTO'] = df['VENCIMENTO'].dt.strftime('%d/%m/%Y')

# Define as colunas desejadas
colunas_desejadas = ['EMPRESA', 'SITUAÇÂO', 'NF', 'VENCIMENTO']

# Remove duplicatas e traz os valores únicos
valores_unicos = df[colunas_desejadas].drop_duplicates()

# Exibe os valores únicos
st.write(valores_unicos.head())

# Seleção do cliente
clientes = df['EMPRESA'].unique().tolist()
cliente = st.selectbox("Selecione o cliente", options=clientes)

if cliente:
    todas_notas_cliente, notas_cliente = buscar_notas_cliente(cliente, df)
    
    if not todas_notas_cliente.empty:
        # Remove duplicatas
        todas_notas_cliente = todas_notas_cliente.drop_duplicates()
        
        st.dataframe(todas_notas_cliente[colunas_desejadas])  # Exibir apenas colunas desejadas
        
        if not notas_cliente.empty:
            mensagem = gerar_mensagem(notas_cliente)
            st.text_area("Mensagem Gerada", mensagem)

            numero_cliente = st.text_input("Digite o número de WhatsApp do cliente (com DDI e DDD)")

            if st.button("Enviar WhatsApp"):
                if numero_cliente and re.match(r'^\+\d{1,3}\d{10}$', numero_cliente):
                    enviar_whatsapp_link(numero_cliente, mensagem)
                else:
                    st.error("Por favor, insira um número de WhatsApp válido.")
        else:
            st.warning("Nenhuma nota fiscal em aberto.")
    else:
        st.warning(f"Nenhuma nota encontrada para o cliente: {cliente}.")
