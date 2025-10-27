import streamlit as st
import pandas as pd
import yfinance as yf
import locale
import plotly.express as px

Caixa = 7000
dolar_df = yf.download('USDBRL=X', period="5d", interval="1d")
dolar = dolar_df['Close']

def cor_valorizacao(valor):
    """
    Retorna a cor 'green' para valores positivos, 'red' para negativos,
    e 'black' para zero.
    """
    cor = 'white'  # Cor padrão
    if valor > 0:
        cor = 'green'
    elif valor < 0:
        cor = 'red'
    return f'color: {cor}'

lista_geral = pd.read_csv("Minha/planilha.csv",sep=";")
print(lista_geral['codigo'])
codigo = list(lista_geral['codigo'])
codigo.remove('CAIXA')
print(codigo)

codigos_b3 = [t for t in codigo if '.SA' in t or '^' in t]
codigos_usd = [t for t in codigo if '.SA' not in t and '^' not in t and 'CAIXA' not in t]

preços_b3 = yf.download(codigos_b3,
                     period="5d",
                     interval="1d")

preços_usd = yf.download(codigos_usd,
                     period="5d",
                     interval="1d")

preços = preços_b3.join(preços_usd).ffill()

lista_planilha = []
codigoo = codigo[:]
codigoo.remove('^BVSP') 
codigoo.remove('^GSPC')
codigoo.remove('^IXIC')
for cc,c in enumerate(codigoo):
    if c == 'JEPI' or c=='BTC-USD' or c=='ETH-USD' or c=='USDT-USD':
        valor = preços['Close'][c][-1]*dolar[-1]
        valor_hoje_em_reais = preços['Close'][c][-1] * dolar[-1]
        valor_ontem_em_reais = preços['Close'][c][-2] * dolar[-2]
        valorizaçao = (valor_hoje_em_reais / valor_ontem_em_reais) - 1
        if c == 'JEPI':
            qnt = (f'{lista_geral['qnt'][cc]:.0f}')
        else:
            qnt = (f'{lista_geral['qnt'][cc]:.4f}')
    else: 
        valor = preços['Close'][c][-1] 
        valorizaçao = valor / preços['Close'][c][-2] - 1
        qnt = (f'{lista_geral['qnt'][cc]:.0f}')
    biblioteca = {'açao':c,'valor':valor,'qnt':qnt,'valorizaçao':valorizaçao}
    lista_planilha.append(biblioteca)
lista_planilha.append({'açao':'Caixa','valor':Caixa,'qnt':'1','valorizaçao':0.00041})

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
carteira = 0
carteira_ontem = 0
for c in lista_planilha: 
    carteira = carteira + c['valor'] * float(c['qnt'])
for cc,c in enumerate(codigoo):
    if c == 'JEPI' or c=='BTC-USD' or c=='ETH-USD' or c=='USDT-USD':
        valor = preços['Close'][c][-2]*float(lista_geral['qnt'][cc])*dolar[-2]
        carteira_ontem = carteira_ontem + valor 
    else:
        valor = preços['Close'][c][-2]*float(lista_geral['qnt'][cc])
        carteira_ontem = carteira_ontem + valor
carteira_real = str(locale.currency(carteira, grouping=True))
valorizaçao = (carteira/carteira_ontem - 1)*100
lucro = str(locale.currency(carteira-carteira_ontem, grouping=True))
ibov = preços['Close']['^BVSP'][-1]
sep = preços['Close']['^GSPC'][-1]
nas = preços['Close']['^IXIC'][-1] 
ibov_val = (ibov/preços['Close']['^BVSP'][-2]-1)*100
sep_val = (sep/preços['Close']['^GSPC'][-2]-1)*100
nas_val = (nas/preços['Close']['^IXIC'][-2]-1)*100

botao2 = []
valor_por_açao = []
for c in lista_planilha:
    valor_total = float(c['qnt'])*c['valor']
    valor_total_real = str(locale.currency(valor_total, grouping=True))
    ticker_total = {'açao':c['açao'],'valor total':valor_total_real,'valorizaçao':c['valorizaçao']}
    botao2.append(ticker_total)
    valor_por_açao.append(valor_total)

ativos = []
total = []
grafico = {'ativos':ativos,'total':total}
for c in lista_planilha:
    valor_total = float(c['qnt'])*c['valor']
    ativos.append(c['açao'])
    total.append(valor_total)

df_grafico = pd.DataFrame(grafico)
fig = px.pie(df_grafico, 
             values='total', 
             names='ativos', 
             title='Gráfico por ativo')

tipos_de_ativos = ['Baixo Crescimento', 'Médio Crescimento', 'Alto Crescimento', 'Ciclicas', 'FI', 'Criptomoedas']
tipos_de_ativos_nn_visual = ['baixo','medio','alto','ciclica','fi','criptomoeda']
lista_segmento = {'baixo':[],'medio':[],'alto':[],'ciclica':[],'fi':[],'criptomoeda':[]}
ativo = list(lista_geral['ativo'])
for cc,c in lista_geral.iterrows():
    categoria = c['ativo']
    codigo_ativo = c['codigo']
    if categoria in lista_segmento:
        lista_segmento[categoria].append(codigo_ativo)

valor_por_segmento = []
valorizaçao_por_segmento = []
for cc,c in enumerate(lista_segmento):
    por_ativo = lista_segmento[c]
    soma = 0
    for b in por_ativo:
        pos_qnt = 0
        for aa,a in enumerate(lista_geral['codigo']):
            if a == b:
                pos_qnt = aa
        soma = float(soma + valor_por_açao[pos_qnt])
    valor_por_segmento.append(soma)

ideal = ['30%','17%','10%','15%','15%','3%']
tabela_2 = []
for c in range(len(tipos_de_ativos)):
    biblioteca = {'Ativos':tipos_de_ativos[c],'Valor Total':valor_por_segmento[c],'Qnt. %':f'{valor_por_segmento[c]/carteira:.2%}','ideal':ideal[c]}
    tabela_2.append(biblioteca)
tabela_2.append({'Ativos':'Caixa','Valor Total':Caixa,'Qnt. %':f'{Caixa/carteira:.2%}','ideal':'10%'})

valorizar = 0
for cc,c in enumerate(botao2):
    valorizar = valorizar + c['valorizaçao']*(valor_por_açao[cc]/carteira)

dado1 = []
dado2 = []
for c in tabela_2:
    dado1.append(c['Ativos'])
    dado2.append(c['Valor Total'])
grafico2 = {'Ativos':dado1,'Total':dado2}
df_grafico2 = pd.DataFrame(grafico2)
fig2 = px.pie(df_grafico2, 
             values='Total', 
             names='Ativos',
             title='Por Segmento')

col1, col2 = st.columns([2,1])
with col1:
    st.write(f'# Carteira: {carteira_real}')
with col2:
    st.write('###### ㅤ')
    if valorizaçao>0:
        st.write(f'##### :green[+{valorizar:.3%}]') 
    elif valorizaçao == 0:
        st.write(f'##### {valorizar:.3%}') 
    else:
        st.write(f'##### :red[{valorizar:.3%}]') 
    st.write('###### ㅤ')




col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.metric(
    label="IBOVESPA", 
    value= str(locale.currency(ibov, grouping=True)),
    delta= f'{ibov_val:.3f}%',
    delta_color="normal")
with col2:
    st.metric(
    label="NASDAQ", 
    value= f'$ {nas:.2f}',
    delta= f'{nas_val:.3f}%',
    delta_color="normal")
with col3:
    st.metric(
    label="S&P500", 
    value= f'$ {sep:.2f}',
    delta= f'{sep_val:.3f}%',
    delta_color="normal")

st.divider()

col1, col2 = st.columns([10,11])
with col1:
    tab_unidade, tab_total = st.tabs(["Unidade", "Total"])
    with tab_unidade: 
        df = pd.DataFrame(lista_planilha)
        df_estilizado = df.style.format({
        'valor': lambda x: locale.currency(x, grouping=True),'valorizaçao': '{:.3%}'.format}).applymap(cor_valorizacao,subset=['valorizaçao'])
        st.dataframe(df_estilizado, hide_index=True)
    with tab_total:
        df = pd.DataFrame(botao2)
        df_estilizado = df.style.format({
        'valor': lambda x: locale.currency(x, grouping=True),'valorizaçao': '{:.3%}'.format}).applymap(cor_valorizacao,subset=['valorizaçao'])
        st.dataframe(df_estilizado, hide_index=True)

with col2:
    st.plotly_chart(fig)

st.divider()

col1, col2 = st.columns([10,11],vertical_alignment="top")
with col1:
    df = pd.DataFrame(tabela_2)
    df_estilizado = df.style.format({
    'Valor Total': lambda x: locale.currency(x, grouping=True)})
    st.dataframe(df_estilizado, hide_index=True)

with col2:
    st.plotly_chart(fig2)

st.sidebar.header('Classe de Ativo')

for c in range(0,6):
    with st.sidebar.expander(tipos_de_ativos[c]):
        for b in lista_segmento[tipos_de_ativos_nn_visual[c]]:
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(b)
            with col2:
                for aa,a in enumerate(botao2): 
                    if a['açao'] == b:
                        st.write(f'{valor_por_açao[aa]/carteira:.2%}')

with st.sidebar.expander('Caixa'):
    col1, col2 = st.columns([2,1])
    with col1:
        st.write("Caixa")
    with col2:

        st.write(f'{Caixa/carteira:.2%}') 

