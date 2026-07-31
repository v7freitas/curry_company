# Curry Company Growth Dashboard

Dashboard interativo para acompanhar métricas operacionais da **Curry Company**, um marketplace de delivery. A aplicação transforma os dados de pedidos em indicadores e visualizações para apoiar a análise do negócio.

## Acesse o app

O dashboard já está publicado no Streamlit:

**[Abrir o Curry Company Growth Dashboard](https://currycompany-n7vpucrfjmqmlfe2nr3nwf.streamlit.app/)**

## Funcionalidades

- **Visão Empresa:** pedidos por dia, densidade de tráfego, pedidos por cidade, indicadores semanais e mapa das entregas.
- **Visão Entregadores:** métricas de perfil, avaliações e desempenho dos entregadores.
- **Visão Restaurantes:** distância média das entregas, tempos de entrega e análises por cidade, pedido e tráfego.
- Filtros por data, condições de tráfego e clima.

## Tecnologias

- Python 3.12
- Streamlit
- Pandas e NumPy
- Plotly
- Folium e Streamlit-Folium

## Como executar localmente

1. Clone este repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual (recomendado).
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Inicie a aplicação:

   ```bash
   streamlit run Home.py
   ```

5. Abra o endereço indicado pelo Streamlit no navegador.

## Estrutura do projeto

```text
.
├── Home.py                 # Página inicial da aplicação
├── pages/                  # Páginas e visões do dashboard
├── dataset/train.csv       # Base de dados utilizada nas análises
├── logo.png                # Logo da Curry Company
└── requirements.txt        # Dependências do projeto
```
