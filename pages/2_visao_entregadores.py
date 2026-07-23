#Importações
import pandas as pd
import streamlit as st

from haversine import haversine
import folium
import plotly.express as px
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

#---------------------------
#Funções
#---------------------------

def clean_code( df1 ):
    '''
    Esta função faz a limpeza do dataframe original

    Limpezas:
    1. Corta espaços em branco indesejáveis nas colunas
    2. Remoção de NaN
    3. Converte tipo das colunas
    4. Formata coluna de data
    5. Remove texto da coluna time taken

    Input: Dataframe
    Output: Dataframe
    '''
    
    #Remove espaços em branco
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ', '', regex=False)
    df1['Weatherconditions'] = df1['Weatherconditions'].str.replace('conditions ', '', regex=False)
    
    #Remove NaN
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].replace('NaN ', pd.NA)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].replace('NaN ', pd.NA)
    df1['Time_Orderd'] = df1['Time_Orderd'].replace('NaN ', pd.NA)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].replace('NaN ', pd.NA)
    df1['City'] = df1['City'].replace('NaN', pd.NA)
    
    df1 = df1.dropna(subset=['Delivery_person_Age', 'Delivery_person_Ratings', 'Time_Orderd', 'multiple_deliveries', 'City']).copy()
    
    #Transformação da coluna data para formato datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    #Convertendo tipos das colunas de ratings e time_taken
    df1.loc[:, 'Delivery_person_Ratings'] = df1.loc[:, 'Delivery_person_Ratings'].astype(float)
    df1.loc[:,'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].astype(int)

    return df1


def delivery_person_rating(df1):
    '''
        Esta função calcula as avaliações médias por entregador.

        Input: Dataframe
        OutPut: Dataframe
    '''
    df_rating_by_delivery_person = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                .groupby(['Delivery_person_ID'])
                                .mean()
                                .reset_index() )

    df_rating_by_delivery_person
    return df_rating_by_delivery_person


def avg_std_rating_metrics(df1, col):
    '''
        Esta função calcula as avaliações médias e desvio padrão por densidade de trânsito.

        Input: Dataframe
        OutPut: Dataframe
    '''
    df_mean_std = (df1.loc[: , ['Delivery_person_Ratings', col]]
                                .groupby([col])
                                .agg({'Delivery_person_Ratings': ['mean', 'std']})
                                .reset_index()) 

    df_mean_std.columns  = [col, 'Rating_mean', 'Rating_std']
    df_mean_std
    
    return df_mean_std

def top_delivery_workers(df1, asc):
    '''
        Esta função calcula os top 10 entregadores mais rápidos e mais lentos.

        Input: Dataframe
        OutPut: Dataframe
    '''
                
    metropolitian = df1['City'] == 'Metropolitian'
    semi_urban = df1['City'] == 'Semi-Urban'
    urban = df1['City'] == 'Urban'
    
    df_metropolitian = (df1.loc[metropolitian, ['Delivery_person_ID', 'City','Time_taken(min)']]
                                            .groupby(['Delivery_person_ID', 'City'])
                                            .agg({'Time_taken(min)': 'mean'})
                                            .sort_values(by='Time_taken(min)', ascending=asc)
                                            .reset_index().head(10))
    
    df_semi_urban = (df1.loc[semi_urban, ['Delivery_person_ID', 'City','Time_taken(min)']]
                                        .groupby(['Delivery_person_ID', 'City'])
                                        .agg({'Time_taken(min)': 'mean'})
                                        .sort_values(by='Time_taken(min)', ascending=asc)
                                        .reset_index().head(10))
    
    df_urban = (df1.loc[urban, ['Delivery_person_ID', 'City','Time_taken(min)']]
                                    .groupby(['Delivery_person_ID', 'City'])
                                    .agg({'Time_taken(min)': 'mean'})
                                    .sort_values(by='Time_taken(min)', ascending=asc)
                                    .reset_index().head(10))
    
    df_top_delivery_workers = pd.concat([df_metropolitian, df_semi_urban, df_urban])
    df_top_delivery_workers
    return df_top_delivery_workers

#Extração do dado
df = pd.read_csv("../dataset/train.csv")

#Limpando o dataset
df1 = clean_code(df)

# ===============================
# Layout Streamlit
# ===============================

#------------------
#Sidebar
#------------------

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## O Delivery mais rápido da cidade')
st.sidebar.markdown('---')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(label='Até qual data?', min_value=datetime(2022, 2, 11), max_value=datetime(2022,4,6), value=datetime(2022,4,6), format='DD-MM-YYYY')

st.sidebar.markdown('---')

traffic_density_options = st.sidebar.multiselect(label='Quais as condições de trânsito?', options=['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])

wheater_options = st.sidebar.multiselect(label='Quais as condições climáticas?', options=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny','Windy'], default=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny','Windy'])


st.sidebar.markdown('---')

st.sidebar.markdown('## Desenvolvido por Comunidade DS')

#Filtro de Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_density_options)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro Clima
linhas_selecionadas = df1['Weatherconditions'].isin(wheater_options)
df1 = df1.loc[linhas_selecionadas, :]

#Main Page

st.set_page_config(page_icon='🚚',layout='wide')

st.header('Marketplace - Visão Entregadores 🚚')

tab1, tab2 = st.tabs(['Visão Gerencial', '-'])

with tab1:

    st.space('small')
    
    with st.container():

        st.subheader('Métricas Gerais')

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label='Menor idade',value =f"{df1.loc[:, 'Delivery_person_Age'].min()} anos")

        with col2:
            st.metric(label='Maior idade',value =f"{df1.loc[:, 'Delivery_person_Age'].max()} anos")

        with col3:
            st.metric(label='Melhor condição de veículo',value =df1.loc[:, 'Vehicle_condition'].max())
            
        with col4:
            st.metric(label='Pior condição de veículo',value =df1.loc[:, 'Vehicle_condition'].min())
           

    with st.container():
        
        col1, col2 = st.columns(2)

        with col1:
            
            st.markdown('##### Avaliação média por entregador')
            delivery_person_rating(df1)
            

        with col2:
            st.markdown('##### Avaliação média e desvio padrão por densidade de tráfego')
            avg_std_rating_metrics(df1, col='Road_traffic_density')
            
            
#           -----------------------------line break ---------------------------------------
            st.markdown('##### Avaliação média e desvio padrão por condição climática')
            avg_std_rating_metrics(df1, col='Weatherconditions')
         

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top 10 entregadores mais rápidos por cidade')
            top_delivery_workers(df1, asc=True)
            

        with col2:
            st.markdown('##### Top 10 entregadores mais lentos por cidade')
            top_delivery_workers(df1, asc=False)            
            
