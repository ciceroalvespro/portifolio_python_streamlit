# Importando as bibliotecas
from bs4 import BeautifulSoup
import numpy as np
import requests
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import mplfinance as mpf
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import yfinance as yf
import pandas_datareader.data as web
import sgs

yf.pdr_override()


# Titulo do Dashboard
st.set_page_config(
    layout="wide",
    page_title="Dashboard Financeiro",
    page_icon=":bar_chart:"
)
st.subheader(':bar_chart: Dashboard Financeiro')
st.write('By Cicero Alves')
# st.markdown("#")
st.markdown("""---""")

# GRAFICO
pd.set_option("display.max_columns", 40)
pd.set_option('display.max_rows', 20)

# SIDE BAR
with st.sidebar:

    st.title("Análise Técnica")
    st.sidebar.markdown(("""---"""))
    datain_default = "2024-01-01"
    datain = st.date_input(
        "Início", value=datetime.strptime(datain_default, "%Y-%m-%d"))
    datafim_default = datetime.now().date()
    datafim = st.date_input("Fim", value=datafim_default)
    ticket_default = "PETR4.SA"
    ticket = st.text_input("Ticket", value=ticket_default)


# Parâmetros dos dados
symbol = ticket
start = datain
end = datafim
interval = "1d"

df = web.get_data_yahoo(symbol, start=start, end=end, interval=interval)


with st.expander("Análise Técnica"):
    # Criando gráfico de candlestick
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])

    # Configurações do layout
    fig.update_layout(title=f'Gráfico Diário de {symbol}',
                      xaxis_title='Data',
                      yaxis_title='Preço',
                      xaxis_rangeslider_visible=False)

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig)

# Analise ações

# URL com a tabela de dados
url = "https://www.fundamentus.com.br/resultado.php"

# Obtendo o conteúdo da página em formato de texto
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'close'
}
data = requests.get(url, headers=headers, timeout=5).text
soup = BeautifulSoup(data, "html.parser")

# Procurando a tabela da página
table = soup.find('table')

# Definindo dataframe
df = pd.DataFrame(columns=['Papel', 'Cotação', 'P/L', 'P/VP', 'PSR', 'Div.Yield',
                           'EV/EBIT', 'Mrg. Líq', 'ROE', 'Dív.Brut/Patrim.', 'Cresc.Rec.5a'])

# Obtendo todas as linhas da tabela
for row in table.tbody.find_all('tr'):
    # Transformando algumas colunas de string para numeric
    columns = row.find_all('td')
    if columns:
        Papel = columns[0].text.strip(' ')
        Cotacao = pd.to_numeric(columns[1].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        PL = pd.to_numeric(columns[2].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        PVP = pd.to_numeric(columns[3].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        PSR = pd.to_numeric(columns[4].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        DivYield = pd.to_numeric(columns[5].text.strip(' ').replace(
            '%', '').replace('.', '').replace(',', '.'), errors='coerce')
        EVEBIT = pd.to_numeric(columns[10].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        MRGLIQ = pd.to_numeric(columns[13].text.strip(' ').replace(
            '%', '').replace('.', '').replace(',', '.'), errors='coerce')
        ROE = pd.to_numeric(columns[16].text.strip(' ').replace(
            '%', '').replace('.', '').replace(',', '.'), errors='coerce')
        LIQ = pd.to_numeric(columns[17].text.strip(' ').replace(
            '.', '').replace(',', '.'), errors='coerce')
        DívBrutPatrim = pd.to_numeric(columns[19].text.strip(
            ' ').replace('.', '').replace(',', '.'), errors='coerce')
        CrescRec5a = pd.to_numeric(columns[20].text.strip(
            ' ').replace('.', '').replace(',', '.').replace('%', ''), errors='coerce')

        df = pd.concat([df, pd.DataFrame.from_records(
            [{'Papel': Papel,  'Cotação': Cotacao, 'P/L': PL, 'P/VP': PVP, 'PSR': PSR, 'Div.Yield': DivYield, 'EV/EBIT': EVEBIT, 'Mrg. Líq': MRGLIQ, 'ROE': ROE, 'Dív.Brut/Patrim.': DívBrutPatrim, 'Cresc.Rec.5a': CrescRec5a, 'Liq.2meses': LIQ}])], ignore_index=True)

# Opção de imortar em formato .csv
setores_df = pd.read_csv('setores_df.csv', delimiter=';')

df = pd.merge(df, setores_df, on='Papel', how='left')
# Filtrar apenas ações ordinárias (3)
df['Type'] = df['Papel'].apply(lambda x: 1 if '3' in x else 0)

# Criando um novo df para a segunda tabela de P/L e P/VP
df_2 = df[['Papel', 'Cotação', 'Div.Yield', 'P/L', 'P/VP', 'PSR', 'EV/EBIT', 'Mrg. Líq',
           'ROE', 'Dív.Brut/Patrim.', 'SETORES']]

# Filtrando papeis
df_2 = df_2[(df["Type"] > 0)]

# Filtrando P/L <=10
df_2 = df_2[(df['P/L'] > 0) &
            (df['P/L'] <= 10)]
# filtrando P/VP <= 5
df_2 = df_2[(df['P/VP'] > 0) &
            (df['P/VP'] <= 5)]

# Filtrando empresas com liquidez média de 2 meses acima de  100.000
df = df[(df['Liq.2meses'] >= 100000)]

# Ordenar o DY
df2 = df.sort_values(by='Div.Yield', ascending=False)

# Criar ranking DY
df2['RK_DY'] = df2['Div.Yield'].rank(ascending=True)

# Ordenar o ROE
df3 = df2.sort_values(by='ROE', ascending=False)

# Criar ranking do ROE
df3['RK_ROE'] = df3['ROE'].rank(ascending=True)

# Ordenando a Margem Líquida
df3 = df3.sort_values(by='Mrg. Líq', ascending=False)

# Criando ranking da Margem Líquida
df3['RK_MGL'] = df3['Mrg. Líq'].rank(ascending=True)

# Criar nota final
df3['NOTA'] = df3['RK_DY'] + df3['RK_ROE'] + df3['RK_MGL']

# Filtrar ações ordinárias
df3 = df3[(df3['Type'] > 0)]

# Criando o Ranking Final
df3['RK'] = df3['NOTA'].rank(ascending=False)

# Ordenar o RK
df3 = df3.sort_values(by='RK', ascending=True)

# separando as colunas desejadas
df3 = df3[['RK', 'Papel', 'Cotação', 'Div.Yield', 'P/L', 'P/VP', 'PSR', 'EV/EBIT', 'Mrg. Líq',
           'ROE', 'Dív.Brut/Patrim.', 'SETORES']]


st.sidebar.markdown(("""---"""))
st.sidebar.title("Análise Fundamentalista")
selected_setor = st.sidebar.selectbox(
    'Setor', ['Todos'] + list(setores_df['SETORES'].unique()))

if selected_setor == 'Todos':
    df3_filtred = df3
else:
    df3_filtred = df3[df3['SETORES'] == selected_setor]

with st.expander("Análise Fundamentalista"):
    st.write(df3_filtred.head(10))

with st.expander("Explicando o modelo"):
    st.markdown("""
    O modelo de análise desenvolvido tem como objetivo identificar oportunidades de 
    investimento com base em critérios específicos obtidos a partir dos dados divulgados 
    por empresas de capital aberto. Os critérios adotados são os seguintes:
    
    *Critérios de seleção inicial:*

    - O índice P/L (Preço/Lucro) deve ser maior que 0 e menor ou igual a 10.
    - O índice P/VP (Preço/Valor Patrimonial) deve ser maior que 0 e menor ou igual a 5.
    - A liquidez nos últimos 2 meses deve ser maior ou igual a 100.000.
    
    *Criação do ranking:*

    - O Dividend Yield é classificado do maior para o menor, onde a empresa que distribuiu o maior dividendo recebe a maior nota.
    - O ROE (Return on Equity) é classificado do maior para o menor, onde a empresa com o maior ROE recebe a maior nota.
    - A margem líquida é classificada do maior para o menor, onde a empresa com a maior margem recebe a maior nota.
    
    *Cálculo da pontuação e classificação:*

    - As notas de cada critério são somadas para criar um ranking final.
    - A empresa com a maior pontuação recebe a primeira posição no ranking.
    
    Este modelo proporciona uma abordagem sistemática e objetiva para avaliar e classificar empresas com base em métricas financeiras e de desempenho. No entanto, é importante ressaltar que os resultados obtidos pelo modelo devem ser interpretados com cautela e complementados por análises qualitativas e outras fontes de informação. Investimentos em ações e mercados financeiros envolvem riscos e é recomendável que os investidores realizem suas próprias pesquisas e consultem profissionais financeiros antes de tomar decisões de investimento.
    
    *Cicero G. Silva Alves*
    """)


with st.expander("Gráficos Fundamentalista"):
    # graficos modelo 1

    # Top 10 P/VP
    # filtrando P/VP <= 5
    df3_filtred = df3_filtred[(df3_filtred['P/VP'] > 0) &
                              (df['P/VP'] <= 5)]
    df3_pvp = df3_filtred.sort_values(by="P/VP", ascending=True)
    df3_pvp = df3_pvp.head(10)
    fig_m1pvp = px.bar(df3_pvp, x="Papel", y="P/VP",
                       title="Top 10 P/VP")
    st.plotly_chart(fig_m1pvp, use_container_width=True)

    # Top 10 P/L

    df3_filtred = df3_filtred[(df3_filtred['P/L'] > 0) &
                              (df['P/VP'] <= 10)]
    df4_pl = df3_filtred.sort_values(by="P/L", ascending=True)
    df4_pl = df4_pl.head(10)
    fig_pl = px.bar(df4_pl, x="Papel", y="P/L",
                    title="Top 10 P/L")
    st.plotly_chart(fig_pl, use_container_width=True)

with st.expander("Taxa Selic"):
    # Definir a série temporal SELIC e obter os dados
    data_atual = datetime.now().strftime('%d/%m/%Y')
    selic = 432
    ts = sgs.time_serie(selic, start='01/01/2010', end=data_atual)

    # Criar DataFrame
    df = pd.DataFrame(ts.items(), columns=['Data', 'Selic'])

    fig = px.area(df, x='Data', y='Selic',
                  title='Taxa SELIC ao longo do tempo')
    st.plotly_chart(fig)

with st.expander("IPCA - Inflação"):
    # Definir a série temporal SELIC e obter os dados
    data_atual = datetime.now().strftime('%d/%m/%Y')
    IPCA = 433
    ts = sgs.time_serie(IPCA, start='01/01/2020', end=data_atual)

    # Criar DataFrame
    df = pd.DataFrame(ts.items(), columns=['Data', 'IPCA'])

    fig = px.bar(df, x='Data', y='IPCA',
                  title='Inflação ao longo do tempo')
    st.plotly_chart(fig)


with st.expander("Disclaimer"):
    st.markdown("""
                *O conteúdo deste site tem fins educacionais e informativos apenas e não deve ser interpretado como conselho financeiro, de investimento ou de negociação*.""")
#