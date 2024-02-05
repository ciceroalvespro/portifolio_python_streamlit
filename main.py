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
df_2 = df[['Papel', 'Type', 'Cotação', 'Div.Yield', 'P/L', 'P/VP', 'Mrg. Líq',
           'ROE', 'Dív.Brut/Patrim.', 'Liq.2meses', 'Cresc.Rec.5a', 'SETORES']]

# Filtros
df_2 = df_2[(df_2["Type"] > 0)]  # Filtrando açoes do tipo Ordinarias
df_2 = df_2[(df_2['Liq.2meses'] >= 100000)]
df_2 = df_2[(df_2['ROE'] > 0)]
df_2 = df_2[(df_2['Mrg. Líq'] >= 0)]
df_2 = df_2[(df_2['Cresc.Rec.5a'] > 0)]
df_2 = df_2[(df_2['P/L'] > 0) & (df_2['P/L'] <= 10)]
df_2 = df_2[(df_2['P/VP'] > 0) & (df_2['P/VP'] <= 5)]

# Rankings
df_2 = df_2.sort_values(by='ROE', ascending=False)
df_2['RK_ROE'] = df_2['ROE'].rank(ascending=True)

df_2 = df_2.sort_values(by='Mrg. Líq', ascending=False)
df_2['RK_MGL'] = df_2['Mrg. Líq'].rank(ascending=True)

df_2 = df_2.sort_values(by='P/L', ascending=True)
df_2['RK_PL'] = df_2['P/L'].rank(ascending=False)

df_2 = df_2.sort_values(by='P/VP', ascending=True)
df_2['RK_PVP'] = df_2['P/VP'].rank(ascending=False)

df_2 = df_2.sort_values(by='Dív.Brut/Patrim.', ascending=True)
df_2['RK_DIV'] = df_2['Dív.Brut/Patrim.'].rank(ascending=False)

# Criar nota final
df_2['NOTA'] = df_2['RK_ROE'] + df_2['RK_MGL'] + \
    df_2['RK_PL'] + df_2['RK_PVP'] + df_2['RK_DIV']

# Criando o Ranking Final
df_2['Ranking'] = df_2['NOTA'].rank(ascending=False)

# Ordenar o RK
df_2 = df_2.sort_values(by='Ranking', ascending=True)

# separando as colunas desejadas
df_2 = df_2[['Ranking', 'Papel', 'Cotação', 'Div.Yield', 'P/L', 'P/VP', 'Mrg. Líq',
             'ROE', 'Dív.Brut/Patrim.', 'SETORES']]

st.sidebar.markdown(("""---"""))
st.sidebar.title("Análise Fundamentalista")
selected_setor = st.sidebar.selectbox(
    'Setor', ['Todos'] + list(setores_df['SETORES'].unique()))

if selected_setor == 'Todos':
    df2_filtred = df_2
else:
    df2_filtred = df_2[df_2['SETORES'] == selected_setor]

with st.expander("Carteira Fundamentalista"):
    st.write(df2_filtred.head(10))

with st.expander("Explicando o modelo"):
    st.markdown("""
                
    O código apresentado realiza uma análise de ações com base em diferentes critérios e cria um ranking final com base nesses critérios.
    
    *Critérios de seleção inicial:*
    
    Primeiramente, são aplicados filtros para selecionar apenas as ações que atendem a 
    determinados requisitos, como tipo de ação, liquidez, retorno sobre patrimônio líquido (ROE),
    margem líquida, crescimento de receita, preço/lucro (P/L) e preço/valor patrimonial (P/VP).
    
    *Criação do ranking:*
    
    Após a aplicação dos filtros, as ações são classificadas e recebem rankings individuais com base 
    nos critérios de ROE, margem líquida, P/L, P/VP e dívida bruta/patrimônio. Em seguida, é calculada 
    uma nota final para cada ação, que é a soma dos rankings individuais. Essa nota final é utilizada 
    para criar um ranking final, onde as ações são classificadas de acordo com sua pontuação total.

    
    Este modelo proporciona uma abordagem sistemática e objetiva para avaliar e classificar empresas com base em métricas financeiras e de desempenho. No entanto, é importante ressaltar que os resultados obtidos pelo modelo devem ser interpretados com cautela e complementados por análises qualitativas e outras fontes de informação. Investimentos em ações e mercados financeiros envolvem riscos e é recomendável que os investidores realizem suas próprias pesquisas e consultem profissionais financeiros antes de tomar decisões de investimento.
    
    *Cicero G. Silva Alves*
    """)


with st.expander("Taxa de juros básica (SELIC - 432)"):
    # Definir a série temporal SELIC e obter os dados
    #data_Inicio = datain.strftime('%d/%m/%Y')
    #data_atual = datafim.strftime('%d/%m/%Y')
    data_atual = datetime.now().strftime('%d/%m/%Y')
    selic = 432
    ts = sgs.time_serie(selic, start='01-01-2010', end=data_atual)

    # Criar DataFrame
    df = pd.DataFrame(ts.items(), columns=['Data', 'Selic'])

    fig = px.area(df, x='Data', y='Selic',
                  title='Taxa SELIC ao longo do tempo')
    st.plotly_chart(fig)

with st.expander("Índice nacional de preços ao consumidor-amplo (IPCA-433)"):
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


