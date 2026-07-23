##Libraries
import pandas as pd
import streamlit as st
import numpy as np

from haversine import haversine
import folium
import plotly.express as px
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go

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

def unique_deliveryWorkers(df1):
    '''
        Está função calcula a quantidade de entregadores únicos na base.

        Input: Dataframe
        Output: class string
    '''
    delivery_workers_num = len(df1['Delivery_person_ID'].unique())
    return delivery_workers_num
    

def average_restaurants_distance(df1):
    '''
        Esta função retorna a distância média dos restaurantes dos locais de entrega.

        Input: Dataframe
        Output: class string
    '''
    cols_loc = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']

    df1['delivery_distance'] = (df1.loc[:, cols_loc].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis= 1))

    avg_restaurants_distance = f'{np.round(df1['delivery_distance'].mean(), 2)} km'
    return avg_restaurants_distance

def festival_timeDelivery(df1, hasFestival, col):
    '''
        Esta função calcula o tempo de entrega médio e o desvio padrão com base na época de Festival.
        Parâmetros:
            df1 -> Dataframe de entrada para realizar os cálculos necessários
            hasFestival -> Se hasFestival = 1, então o cálculo é feito fora da época de Festival, se
                           hasFestival = 2, o cálculo é feito na época de Festival.
            col -> define a coluna da métrica a ser calcula, Avg_Time_Taken ou Std_Time_Taken.

        Input: Dataframe, number, string.
        Output: class string.
    '''
    
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                    .groupby(['Festival'])
                    .agg({'Time_taken(min)': ['mean', 'std']})
                    .reset_index())
    df_aux.columns = ['Festival', 'Avg_Time_Taken', 'Std_Time_Taken']
    metrics_timeTaken = f'{np.round(df_aux.loc[hasFestival, col], 1)} min'
    
    return metrics_timeTaken

def average_distance_city(df1):
    '''
        Esta função retorna um gráfico de barras que calcula a distância média das entregas por cidade.

        Input: Dataframe
        Output: Streamlit chart function
    '''
    
    df_distance_bycity = df1.loc[:, ['delivery_distance', 'City']].groupby(['City']).mean().reset_index()

    bar_chart = st.plotly_chart(px.bar(df_distance_bycity, x='City', y='delivery_distance', text_auto=True, labels={
        'City':'Cidade',
        'delivery_distance': 'Distância média (km)'
    }))
    
    return bar_chart

def avg_std_time_city(df1):
    '''
        Esta função retorna um gráfico de barras que calcula o tempo médio e desvio padrão das entregas por cidade.

        Input: Dataframe
        Output: Streamlit chart function
    '''
    df_aux = (df1.loc[: , ['Time_taken(min)', 'City']]
                    .groupby(['City'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['Avg_TimeTaken_ByCity', 'Std_TimeTaken_ByCity']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    error_bar_chart = st.plotly_chart(fig.add_trace(go.Bar(name='Details', x=df_aux['City'], y=df_aux['Avg_TimeTaken_ByCity'], error_y=dict(type='data', array=df_aux['Std_TimeTaken_ByCity']))).update_layout(xaxis_title='Cidade', yaxis_title='Tempo médio de entrega (min)'))
    return error_bar_chart

def avg_std_timeDelivery_typeOrder(df1):
    '''
        Esta função retorna um gráfico de barras agrupadas que calcula o tempo médio e desvio padrão das entregas por tipo de pedido e por cidade.

        Input: Dataframe
        Output: plotly_graph_object function
    '''
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
    
    df_aux.columns = ['time_taken_mean', 'time_taken_std']
    
    df_aux = df_aux.reset_index()
    
    fig = px.bar(
        df_aux,
        x="City",
        y="time_taken_mean",
        color="Type_of_order",
        barmode="group",
        error_y="time_taken_std",
        labels={
            "City": "Cidade",
            "time_taken_mean": "Tempo médio de entrega (min)",
            "Type_of_order": "Tipo de pedido",
            "time_taken_std": "Desvio-padrão"
        }
    )
    
    fig.update_layout(template="plotly_white")
    
    return fig

def avg_std_timeDelivery_CityAndTraffic(df1):
    '''
        Esta função retorna um gráfico de barras agrupadas que calcula o tempo médio e desvio padrão das entregas por cidade e por densidade de trânsito.

        Input: Dataframe
        Output: plotly_graph_object function
    '''
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['time_taken_avg', 'time_taken_std']
    
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='time_taken_avg', color='time_taken_std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['time_taken_std']))
    fig.update_layout(
coloraxis_colorbar_title="Desvio-padrão do tempo<br>de entrega (minutos)"
)
    
    return fig

#Import dataset
df = pd.read_csv("../dataset/train.csv")

df1 = clean_code(df)

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

#--------------------
# Main Page
#--------------------
st.set_page_config(page_icon="🍴",layout="wide")

st.header('Marketplace - Visão Restaurantes 🍴')

tab1, tab2 = st.tabs(['Visão Gerencial', '-'])

with tab1:
    with st.container():

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            #Nº entregadores únicos
            delivery_workers_num = unique_deliveryWorkers(df1)
            st.metric(label='Nº Entregadores',value=delivery_workers_num)
            
        with col2:
            #Distância Média dos Restaurantes
            avg_restaurants_distance = average_restaurants_distance(df1)
            st.metric(label='Dist. Média Restaurantes',value=avg_restaurants_distance)

        with col3:
            #Tempo de entrega dos pedidos com Festival
            metrics_timeTaken = festival_timeDelivery(df1, hasFestival=2, col='Avg_Time_Taken')
            st.metric(label='Tempo Entrega Festival', value= metrics_timeTaken)
            
        with col4:
            #Tempo de entrega dos pedidos sem Festival
            metrics_timeTaken = festival_timeDelivery(df1, hasFestival=1, col='Avg_Time_Taken')
            st.metric(label='Tempo Entrega Sem Festival', value= metrics_timeTaken)
        with col5:
            #Desvio Padrão do tempo de entrega com Festival 
            metrics_timeTaken = festival_timeDelivery(df1, hasFestival=2, col='Std_Time_Taken')
            st.metric(label='Desvio Padrão Festival', value= metrics_timeTaken)
        with col6:
            #Desvio Padrão do tempo de entrega sem Festival
            metrics_timeTaken = festival_timeDelivery(df1, hasFestival=1, col='Std_Time_Taken')
            st.metric(label='Desvio Padrão Sem Festival', value= metrics_timeTaken)


    with st.container():
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Distância Média de Entrega por Cidade')
            average_distance_city(df1)
                
        with col2:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade ')
            avg_std_time_city(df1)

    with st.container():
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
            fig = avg_std_timeDelivery_typeOrder(df1)    
            st.plotly_chart(fig)
            
        with col2:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego')
            fig = avg_std_timeDelivery_CityAndTraffic(df1)
            st.plotly_chart(fig)








