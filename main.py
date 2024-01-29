# importando as bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
from bs4 import BeautifulSoup

# setando a pagina para ficar no modo pagina inteira
st.set_page_config(
    layout="wide",
    page_title="Portifolio de projetos",
    page_icon=":bar_chart:"
)
# Mudar a pagina pelo side bar
st.sidebar.title('Portfolio')
page = st.sidebar.selectbox(
    'Projetos', ['Apresentação', 'Análise de Ações', 'Dashboard de vendas', 'Ranking de Aeroportos'])

###############################################################################################################################################
# Página de Apresentação
############################################################################################################################################### 

# Condições para mostrar o conteúdo de cada página
if page == 'Apresentação':

    st.subheader("Bem-vindo ao meu Portfólio Python")
    st.text("""
                Bem-vindo à minha página pessoal de portfólio, dedicada aos projetos desenvolvidos com a linguagem Python! 
Meu nome é Cicero Alves e sou entusiasta da análise e ciência de dados. 
Aqui, compartilho minha jornada explorando o vasto mundo da programação Python, traduzindo paixão e dedicação 
em projetos.

Ao navegar pelo menu lateral, você terá a oportunidade de explorar uma variedade de projetos, cada um 
representando um mergulho profundo em desafios únicos. 
Acredito que a programação é mais do que linhas de código; é uma forma de expressão que permite transformar 
ideias em soluções tangíveis.

Meus projetos refletem a diversidade de aplicações da linguagem Python, desde análise de dados até 
implementações mais complexas. 

Sinta-se encorajado a compartilhar seus comentários e sugestões. Estou sempre em busca de aprendizado e 
aprimoramento contínuo. 
Espero que os projetos aqui apresentados despertem seu interesse e ofereçam uma visão do meu comprometimento 
com a excelência na programação Python.

Agradeço por sua visita e espero que desfrute da experiência de explorar meu portfólio. 
Se tiver alguma dúvida ou quiser discutir colaborações, estou à disposição. 
Vamos juntos explorar as possibilidades emocionantes que a linguagem Python nos oferece!

Cicero G. Silva Alves
ciceroalvespro@gmail.com

                """)

###############################################################################################################################################
# Página Análise de Ações
############################################################################################################################################### 

elif page == 'Análise de Ações':

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

    # Filtrando Liquidez
    df_2 = df_2[(df['Liq.2meses'] >= 500000)]

    # Filtrando P/L <=10
    df_2 = df_2[(df['P/L'] > 0) &
                (df['P/L'] <= 10)]
    # filtrando P/VP <= 5
    df_2 = df_2[(df['P/VP'] > 0) &
                (df['P/VP'] <= 5)]

    # Filtrando divida liquida / ebit
    df = df[(df['Dív.Brut/Patrim.'] >= 0) &
            (df['Dív.Brut/Patrim.'] <= 5)]

    # Filtrando empresas com liquidez média de 2 meses acima de  500.000
    df = df[(df['Liq.2meses'] >= 500000)]

    # Filtrando empresas com CAGR lucro acima de 0
    df = df[(df['Cresc.Rec.5a'] > 0)]

    # Filtrando P/L
    df = df[(df['P/L'] > 0)]

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
    # df3= df3.head(10)

    # Criar o dashboard com Streamlit
    st.subheader(':bar_chart: Dashboard de Análise de Ações')
    # st.markdown("#")
    st.markdown("""---""")
    # Criando a Sidebar
    st.sidebar.title('Filtros')
    selected_setor = st.sidebar.selectbox(
        'Selecione o Setor', ['Todos'] + list(setores_df['SETORES'].unique()))

    if selected_setor == 'Todos':
        df3_filtred = df3
    else:
        df3_filtred = df3[df3['SETORES'] == selected_setor]
    st.markdown("1. Modelo")
    st.markdown("""
                Classificação com Filtros de Desempenho Financeiro (DY - ROE - MGL) - Dívida Bruta/Patrimônio entre 0 e 5, Crescimento Recente de 5 anos positivo, Liquidez de 2 meses maior ou igual a 500.000
                """)
    st.write(df3_filtred)

    if selected_setor == 'Todos':
        df2_filtred = df_2
    else:
        df2_filtred = df_2[df_2['SETORES'] == selected_setor]
    st.markdown("2. Modelo ")
    st.markdown("""
                Classificação com Filtros de Precificação ( P/L entre 0 e 10, P/VP menor que 5 )
                """)
    st.write(df2_filtred)

    st.markdown("""#""")
    st.subheader(':bar_chart: Análise dos modelos')
    # st.markdown("#")
    st.markdown("""---""")
    # layout dos graficos
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    # graficos modelo 1
    # Top 10 pagadoras de dividendos (Ativos)
    df3_div = df3_filtred.sort_values(by="Div.Yield", ascending=False)
    df3_div = df3_div.head(10)
    fig_div = px.bar(df3_div, x="Papel", y="Div.Yield",
                     title="1. Modelo: Top 10 Div.Yield")
    col1.plotly_chart(fig_div, use_container_width=True)

    # Top 10 P/VP
    df3_pvp = df3_filtred.sort_values(by="P/VP", ascending=True)
    df3_pvp = df3_pvp.head(10)
    fig_m1pvp = px.bar(df3_pvp, x="Papel", y="P/VP",
                       title="1. Modelo: Top 10 P/VP")
    col3.plotly_chart(fig_m1pvp, use_container_width=True)

    # Top 10 P/VP
    df3_pl = df3_filtred.sort_values(by="P/L", ascending=True)
    df3_pl = df3_pl.head(10)
    fig_m1pl = px.bar(df3_pl, x="Papel", y="P/L",
                      title="1. Modelo: Top 10 P/L")
    col5.plotly_chart(fig_m1pl, use_container_width=True)

    # Graficos modelo 2
    df2_filtred_div = df2_filtred.sort_values(by="Div.Yield", ascending=False)
    df2_filtred_div = df2_filtred_div.head(10)
    fig_m2div = px.bar(df2_filtred_div, x="Papel", y="Div.Yield",
                       title="2. Modelo: Top 10 Div.Yield")
    col2.plotly_chart(fig_m2div, use_container_width=True)

    df2_filtred_pvp = df2_filtred.sort_values(by="P/VP", ascending=True)
    df2_filtred_pvp = df2_filtred_pvp.head(10)
    fig_m2pvp = px.bar(df2_filtred_pvp, x="Papel", y="P/VP",
                       title="2. Modelo: Top 10 P/VP")
    col4.plotly_chart(fig_m2pvp, use_container_width=True)

    df2_filtred_pl = df2_filtred.sort_values(by="P/L", ascending=True)
    df2_filtred_pl = df2_filtred_pl.head(10)
    fig_m2pl = px.bar(df2_filtred_pl, x="Papel", y="P/L",
                      title="2. Modelo: Top 10 P/L")
    col6.plotly_chart(fig_m2pl, use_container_width=True)
    
###############################################################################################################################################
# PAGINA RANKING AEROPORTOS BRASILEIROS - ANAC 
###############################################################################################################################################

elif page == 'Ranking de Aeroportos':
    
    # Título da página
    st.subheader(":bar_chart: Ranking de Aeroportos Brasileiros")
    st.markdown("*Fonte: Dados estatísticos publicados pela ANAC - Agência Nacional de Aviação Civil*")

    # st.markdown("#")
    st.markdown("""---""")
    
    base_url = "https://raw.githubusercontent.com/ciceroalvespro/portifolio_python_streamlit/master/Dados%20publicos%20anac/dados_publicos_anac_{}.csv"

    # Lista para armazenar os DataFrames de cada ano
    dfs = []

    # Iterar sobre os anos de 2013 a 2023
    for year in range(2013, 2024):
        url = base_url.format(year)
        df = pd.read_csv(url, sep=";")
        dfs.append(df)

    # Concatenar todos os DataFrames em um único DataFrame
    df = pd.concat(dfs, ignore_index=True)

    # df origem (decolagem)
    pd.options.mode.copy_on_write = True
    # filtrar o pais de origen (Brasil)
    df_origem = df[df["AEROPORTO DE ORIGEM (PAÍS)"] =="BRASIL"]
    # criar uma coluna com AEROPORTO DE ORIGEM (SIGLA) - AERODROMO
    df_origem["AERODROMO"] = df_origem["AEROPORTO DE ORIGEM (SIGLA)"]
    # criar uma coluna com o tipo de movimento
    df_origem["MOVIMENTO TIPO"] = "DECOLAGEM"
    #criar coluna calculada para pax
    df_origem["PASSAGEIROS"] = df_origem["PASSAGEIROS PAGOS"] + df_origem["PASSAGEIROS GRÁTIS"]
    # separa as colunas ANO - MES - EMPRESA (SIGLA) - AERODROMO - PASSAGEIROS PAGOS - CARGA PAGA (KG) - DECOLAGENS
    df_origem = df_origem[["ANO", "MÊS","MOVIMENTO TIPO", "AERODROMO","EMPRESA (SIGLA)", "PASSAGEIROS","CARGA PAGA (KG)","DECOLAGENS","CORREIO (KG)"]]

    # df destino (pouso)
    pd.options.mode.copy_on_write = True
    # filtrar o pais de destino (Brasil)
    df_destino = df[df["AEROPORTO DE DESTINO (PAÍS)"] =="BRASIL"]
    # criar uma coluna com AEROPORTO DE DESTINO (SIGLA) - AERODROMO
    df_destino["AERODROMO"] = df_destino["AEROPORTO DE DESTINO (SIGLA)"]
    # criar uma coluna com o tipo de movimento
    df_destino["MOVIMENTO TIPO"] = "POUSO"
    #criar coluna calculada para pax
    df_destino["PASSAGEIROS"] = df_destino["PASSAGEIROS PAGOS"] + df_destino["PASSAGEIROS GRÁTIS"]
    # separa as colunas ANO - MES - EMPRESA (SIGLA) - AERODROMO - PASSAGEIROS PAGOS - CARGA PAGA (KG) - DECOLAGENS
    df_destino = df_destino[["ANO", "MÊS","MOVIMENTO TIPO", "AERODROMO","EMPRESA (SIGLA)", "PASSAGEIROS","CARGA PAGA (KG)","DECOLAGENS","CORREIO (KG)"]]

    # crando um data frame unico
    df_anac = pd.concat([df_origem, df_destino], ignore_index=True)
    
    # filtros
    st.sidebar.title("Filtros")
    filtro_graficos = st.sidebar.selectbox('Gráficos', ['Passageiros', 'Movimentos', 'Carga Aérea','Evolução'])
        
    
    if filtro_graficos == "Passageiros":
        filtro_ano = st.sidebar.selectbox("Ano", df_anac["ANO"].unique())
        
        # PAX
        # preparando o grafico
        df_anac_group_pax = df_anac[df_anac["ANO"] == filtro_ano]
        df_anac_group_pax = df_anac_group_pax.groupby("AERODROMO")["PASSAGEIROS"].sum().reset_index()
        df_anac_group_pax = df_anac_group_pax.sort_values("PASSAGEIROS", ascending=False)
        df_anac_group_pax = df_anac_group_pax.head(10)
        # criando o grafico pax
        fig_pax = px.bar(df_anac_group_pax, x="AERODROMO", y="PASSAGEIROS", title="Ranking de aeródromos por passageiro - Top 10")
        fig_pax.update_traces(texttemplate='%{value}', textposition='outside')
        #col1.plotly_chart(fig_pax, use_container_width=True)
        fig_pax

    elif filtro_graficos == "Movimentos":
        filtro_ano = st.sidebar.selectbox("Ano", df_anac["ANO"].unique())
        # MOVIMENTOS
        # preparando o grafico
        df_anac_group_atm = df_anac.groupby("AERODROMO")["DECOLAGENS"].sum().reset_index()
        df_anac_group_atm = df_anac_group_atm.sort_values("DECOLAGENS", ascending=False)
        df_anac_group_atm = df_anac_group_atm.head(10)
        # criando o grafico pax
        fig_atm = px.bar(df_anac_group_atm, x="AERODROMO", y="DECOLAGENS", title="Ranking de aeródromos por movimentos - Top 10")
        fig_atm.update_traces(texttemplate='%{value}', textposition='outside')
        #col2.plotly_chart(fig_atm, use_container_width=True)
        fig_atm
        
    elif filtro_graficos == "Carga Aérea":
        filtro_ano = st.sidebar.selectbox("Ano", df_anac["ANO"].unique())
       
        # CARGO
        # preparando o grafico
        # layout dos graficos
        
        col1, col2 = st.columns(2)
               
        df_anac_group_cargo = df_anac.groupby("AERODROMO")["CARGA PAGA (KG)"].sum().reset_index()
        df_anac_group_cargo = df_anac_group_cargo.sort_values("CARGA PAGA (KG)", ascending=False)
        df_anac_group_cargo = df_anac_group_cargo.head(10)
        # criando o grafico pax
        fig_cargo = px.bar(df_anac_group_cargo, x="AERODROMO", y="CARGA PAGA (KG)", title="Ranking de aeródromos por carga aérea - Top 10")
        fig_cargo.update_traces(texttemplate='%{value}', textposition='outside')
        col1.plotly_chart(fig_cargo, use_container_width=True)
        
        
        # CORREIO
        # preparando o grafico
        df_anac_group_correio = df_anac.groupby("AERODROMO")["CORREIO (KG)"].sum().reset_index()
        df_anac_group_correio = df_anac_group_correio.sort_values("CORREIO (KG)", ascending=False)
        df_anac_group_correio = df_anac_group_correio.head(10)
        # criando o grafico pax
        fig_correio = px.bar(df_anac_group_correio, x="AERODROMO", y="CORREIO (KG)", title="Ranking de aeródromos por correio aéreo - Top 10")
        fig_correio.update_traces(texttemplate='%{value}', textposition='outside')
        col2.plotly_chart(fig_correio, use_container_width=True)
        
    else:
        col1, col2 = st.columns(2)
        
        st.write("Evolução PAX")
        filtro_ano = st.sidebar.selectbox("Ano", df_anac["ANO"].unique())
        filtro_aeroportos = st.sidebar.selectbox("Aeroportos", df_anac["AERODROMO"].unique())
        df_anac_evo_pax = df_anac[df_anac["AERODROMO"] == filtro_aeroportos]
        df_anac_evo_pax = df_anac_evo_pax.groupby("MÊS")["PASSAGEIROS"].sum().reset_index()

        df_anac_evo_pax_y = df_anac[df_anac["AERODROMO"] == filtro_aeroportos]
        df_anac_evo_pax_y = df_anac_evo_pax_y.groupby("ANO")["PASSAGEIROS"].sum().reset_index()
           
        fig_evo_pax = px.bar(df_anac_evo_pax, x="MÊS", y="PASSAGEIROS", title="Evolução mensal na movimentação de passageiros")


        fig_ev_ano = px.bar(df_anac_evo_pax_y, x="ANO", y="PASSAGEIROS", title="Evolução anual na movimentação de passageiros")
        
        col1.plotly_chart(fig_evo_pax, use_container_width=True)
        
      

     
     

    
    
    st.markdown("#")
    st.markdown("""---""")
    st.markdown("*Dados atualizados até 31 de dezembro de 2023*")
###############################################################################################################################################
# PAGINA Dashboard de vendas 
###############################################################################################################################################    
else:
    # Título alinhado ao centro
    st.subheader(":bar_chart: Dashboad de vendas")
    # st.markdown("#")
    st.markdown("""---""")
    # st.markdown("<h1 style='text-align: center;'>Sales Dashboard</h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>by Cicero Alves</h3>", unsafe_allow_html=True)
    # lendo a base de dados em csv # delimiter ou sep
    df = pd.read_csv("supermarket_sales.csv", sep=";", decimal=",")
    # convertendo a coluna de data de str para datatime
    df["Date"] = pd.to_datetime(df["Date"])
    # ordenando a tabela pela coluna data
    df = df.sort_values("Date")
    # criando uma coluna Month para visualizar mes a mes no formato ex. 2023-1
    df["Month"] = df["Date"].apply(lambda x: str(x.year) + "-" + str(x.month))
    # criando a side bar do dash e uma select box com os dados da coluna month crianda
    st.sidebar.title("Filtros")
    month = st.sidebar.selectbox("Mês", df["Month"].unique())
    # criando um df filtrado pelo mes selecionando no selectbox
    df_filtered = df[df["Month"] == month]
    # definindo os containers onde os graficos ficaram no dash
    col1, col2,  = st.columns(2)
    col3, col4, = st.columns(2)
    col5, col6, = st.columns(2)
    # criando um grafico de barras com o total por dia destacando as cidades
    fig_date = px.bar(df_filtered, x="Date", y="Total",
                      color="City", title="Faturamento por dia")
    # plotando o grafico no container criado
    col1.plotly_chart(fig_date, use_container_width=True)
    # criando um grafico de barras contando os produtos vendidos por dia destacando a cidade e na horizontal
    fig_prod = px.bar(df_filtered, x="Date", y="Product line",
                      color="City", title="Faturamento por produto", orientation="h")
    # plotando o grafico no container criado
    col2.plotly_chart(fig_prod, use_container_width=True)
    # criando um df com a tabela fitrada agrupando por cidade e mostrando o total
    city_total = df_filtered.groupby("City")[["Total"]].sum().reset_index()
    # criando um grafico de barras com o df criado com o faturamento por filial
    fig_city = px.bar(city_total, x="City", y="Total",
                      title="Faturamento por filial")
    # plotando o grafico no container col3
    col3.plotly_chart(fig_city, use_container_width=True)
    # criando um grafico de pizza com o total de faturamento por meio depagamento
    fig_pay = px.pie(df_filtered, values="Total", names="Payment",
                     title="Faturamento por meio de pagamento")
    # plotando o grafico no container col4
    col4.plotly_chart(fig_pay, use_container_width=True)
    # criando um df com a media do rating de avaliação
    df_rating = df_filtered.groupby("City")[["Rating"]].mean().reset_index()
    # criando um grafico de barras com a media de avaliação por cidade
    fig_rating = px.bar(df_rating, x="City", y="Rating",
                        title="Avaliação por filial")
    # plotando o grafico no container col5
    col5.plotly_chart(fig_rating, use_container_width=True)
    # criando um grafico de barras com a media de avaliação por linha de produto
    df_rating_prod = df_filtered.groupby(
        "Product line")[["Rating"]].mean().reset_index()
    fig_rating_prod = px.bar(
        df_rating_prod, x="Product line", y="Rating", title="Avaliação por produto")
    col6.plotly_chart(fig_rating_prod, use_container_width=True)
