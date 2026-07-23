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

def orders_by_day(df1):
    '''
    Essa função tem como objetivo fazer definir uma dataframe que faz uma contagem dos pedidos agrupados
    pela data e inserir os dados do dataframe em um gráfico.

    Input: dataframe
    Output: bar chart
    '''
    #Fazer uma contagem das colunas ID agrupadas por Order_Date
    df_auxiliar = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    #Desenhar gráfico de barras
    fig = px.bar(df_auxiliar, x = 'Order_Date', y = 'ID', labels={'Order_Date':'Data', 'ID':'Pedidos'})
    
    return fig

def orders_by_traffic(df1):
    '''
    Essa função tem como objetivo definir uma dataframe que faz uma contagem dos pedidos agrupados
    pela densidade de trânsito e inserir os dados do dataframe em um gráfico.

    Input: dataframe
    Output: pie chart
    '''
    # Contar o número de entregas (ID) agrupado pelo Road_traffic_density
    df_auxiliar = df1.loc[:, ['ID' ,'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    #Calcular o percentual de pedidos
    df_auxiliar['orders_perc'] = df_auxiliar['ID'] / df_auxiliar['ID'].sum()
    #Desenhar o gráfico de pizza
    fig = px.pie(df_auxiliar, names= 'Road_traffic_density', values= 'ID')
    
    return fig

def orders_by_city_by_traffic(df1):
    '''
    Essa função tem como objetivo definir uma dataframe que faz uma contagem dos pedidos agrupados
    por cidade e pela densidade de trânsito e inserir os dados do dataframe em um gráfico.

    Input: dataframe
    Output: scatter chart
    '''
    ##Quantidade de pedidos por cidade e por tipo de trafego
    qtd_pedidos_cidade_trafego = df1.loc[:,['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index() 
    
    fig = px.scatter(qtd_pedidos_cidade_trafego, x = 'City', y = 'Road_traffic_density', size='ID', color='City', labels={'City':'Cidade', 'Road_traffic_density': 'Densidade de Trânsito'} )
    fig.update_layout(
        legend=dict(
            orientation="h",      # "h" = horizontal, "v" = vertical
            yanchor="bottom",
            y=1,                # posição vertical (1.02 = logo acima do gráfico)
            xanchor="center",
            x=0.2                   # posição horizontal
        )
    )

    return fig

def orders_by_week(df1):
    '''
    Essa função tem como objetivo definir uma dataframe que faz uma contagem dos pedidos agrupados
    por semana e inserir os dados do dataframe em um gráfico.

    Input: dataframe
    Output: line chart
    '''
    
    fig = px.line(qtd_pedidos_semana, x = 'week_of_year', y = 'ID', labels={
        'ID':'Pedidos', 'week_of_year':'Semana do ano'
    })
    return fig

def orders_by_deliveryPerson_by_week(df1): 
    '''
    Essa função tem como objetivo definir uma dataframe que faz uma contagem dos pedidos por
    entregador agrupados por semana e inserir os dados do dataframe em um gráfico.

    Input: dataframe
    Output: line chart
    '''
    
    qtd_entregadores_by_week = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique()
    
    df_aux_ = pd.merge(qtd_entregadores_by_week, qtd_pedidos_semana, how='inner',  on='week_of_year')
    df_aux_['orders_by_delivery_person'] = df_aux_['ID'] / df_aux_['Delivery_person_ID']
    
    fig = px.line(df_aux_, x = 'week_of_year', y = 'orders_by_delivery_person', labels={
        'orders_by_delivery_person':'Pedidos por entregador', 'week_of_year':'Semana do ano'
    })
    return fig

def orders_located_by_city_by_traffic(df1):

    '''
    Essa função tem como objetivo definir uma dataframe que identifica a localização central das entregas dos
    pedidos agrupados por cidade e densidade de trânsito e plotar em um mapa para visualização dos pontos.

    Input: dataframe
    Output: map
    '''
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    map = folium.Map(
        location=[df_aux['Delivery_location_latitude'].mean(),
                  df_aux['Delivery_location_longitude'].mean()
                  ],
        zoom_start=11
    )
    
    for index, location_info in df_aux.iterrows():
      folium.Marker([ location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude'] ],
                    popup=location_info[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    ).add_to(map)
    
    folium_static(map, width=1024, height=600)
    return None

#Extração do dado
df = pd.read_csv("../dataset/train.csv")

#Limpando os dados
df1 = clean_code( df )

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

st.sidebar.markdown('---')

st.sidebar.markdown('## Desenvolvido por Comunidade DS')

#-----------------
#Main page
#-----------------
st.set_page_config(page_icon="📈",layout="wide")
st.header('Marketplace - Visão Empresa 📈')

#Filtro de Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_density_options)
df1 = df1.loc[linhas_selecionadas, :]

#-----------------
# Layout Gráficos
#-----------------

tab1, tab2, tab3 =  st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])

with tab1:
    with st.container():

        st.markdown('### Pedidos por Dia')
        fig = orders_by_day(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('### % de Pedidos por Densidade de Trânsito')
            fig = orders_by_traffic(df1)   
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown('### Pedidos por Cidade por Tipo de Tráfego')
            fig = orders_by_city_by_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
                    
with tab2:

    with st.container():

        st.markdown('### Pedidos por Semana')
        
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        qtd_pedidos_semana = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
        
        fig = orders_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():

        st.markdown('### Pedidos por Entregador por Semana')
        fig = orders_by_deliveryPerson_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown('# Mapas')

    with st.container():

        st.markdown('### Localização central das entregas por Cidade por Tipo de Tráfego')
        orders_located_by_city_by_traffic(df1)
        
        





