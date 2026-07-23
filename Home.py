import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout="centered"
)

image= Image.open("logo.png")

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## O Delivery mais rápido da cidade')
st.sidebar.markdown('---')
st.sidebar.markdown('@ViniciusFreitas')

st.header('Curry Company Growth Dashboard 📊')

st.markdown(
    '''
        O Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes
        da Curry Company.

        ### Como utilizar o Dashboard?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de geolocalização.
        - Visão Entregadores:
            - Acompanhamento dos indicadores semanais de crescimento dos entregadores.
        - Visão Restaurante:
            - Indicadores semanais de crescimento dos restaurantes.

        ### Para mais ajuda:
        - Consulte o time de Analytics
    '''
 )
