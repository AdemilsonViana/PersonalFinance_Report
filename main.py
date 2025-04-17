#%% ----------------------------------------------
# imports
#streamlit run main.py
import pandas as pd
import streamlit as st

from Functions.APIs.notion import API_Notion
from Functions.Charts.simple_charts import interactive_stacked_bar_chart

#%% ----------------------------------------------
#straemlit config
st.set_page_config(page_title="Workload Report", layout="wide")
st.title('Workload Report')

# Adicionar botão de atualização
if st.button('🔄 Atualizar Dados'):
    st.cache_data.clear()
    st.rerun()

#%% ----------------------------------------------
# Extract data
dataset_id = st.secrets["notion"]["dataset_id"]
token = st.secrets["notion"]["token"]

# adicionanodo o decorador para poder limpar o cache pelo botão
@ st.cache_data
def data_extract():
    return API_Notion(dataset_id, token)

df = data_extract()

#%% ----------------------------------------------
# handle date
df = df[['properties']]
df = pd.json_normalize(df['properties'])
df = df.explode('Gasto.title')
df_title = pd.json_normalize(df['Gasto.title'])
df = pd.concat([df.drop('Gasto.title', axis=1), df_title], axis=1)
df = df[['text.content', 'Valor.number', 'Data.date.start', 'ANO.formula.number', 'Mês da fatura.formula.number', 'Natureza.select.name', 'Tipo gasto 2.select.name']]
    # renomear as colunas
df.rename(columns={'text.content': 'gasto', 'Mês da fatura.formula.number': 'mes_fatura', 'Natureza.select.name': 'natureza', 'ANO.formula.number': 'ano_fatura', 'Data.date.start': 'data', 'Tipo gasto 2.select.name': 'tipo_gasto', 'Valor.number': 'valor'}, inplace=True)
    # alterar os tipos de dados
df['gasto'] = df['gasto'].astype(str)
df['mes_fatura'] = df['mes_fatura'].astype(int)
df['natureza'] = df['natureza'].astype(str)
df['ano_fatura'] = df['ano_fatura'].astype(int)
df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
df['tipo_gasto'] = df['tipo_gasto'].astype(str)
df['valor'] = df['valor'].astype(float)
    # criar a coluna de ano e mês (ano-mes)
df['ano_mes'] = df['ano_fatura'].astype(str) + '-' + df['mes_fatura'].astype(str).str.zfill(2)

#%% ----------------------------------------------
# charts
# tabela auxiliar para gráfico ano_mes por tipo
groupby_gastos_mes = df.groupby(['ano_mes', 'tipo_gasto'])['valor'].sum().reset_index()

#%% ----------------------------------------------
# streamlit
st.sidebar.header('Filters')

# Filtro de ano (multiselect)
anos_disponiveis = ["Todos"] + sorted(df['ano_fatura'].unique().tolist())
anos_selecionados = st.sidebar.multiselect('Selecione o(s) Ano(s)', anos_disponiveis, default="Todos")

# Filtro de mês (multiselect)
meses_disponiveis = ["Todos"] + sorted(df['mes_fatura'].unique().tolist())
meses_selecionados = st.sidebar.multiselect('Selecione o(s) Mês(es)', meses_disponiveis, default="Todos")

# Aplicar os filtros no dataframe groupby_gastos_mes
if "Todos" in anos_selecionados:
    anos_filtrados = groupby_gastos_mes['ano_mes'].str[:4].astype(int).unique()
else:
    anos_filtrados = anos_selecionados

if "Todos" in meses_selecionados:
    meses_filtrados = groupby_gastos_mes['ano_mes'].str[-2:].astype(int).unique()
else:
    meses_filtrados = meses_selecionados

filtered_data = groupby_gastos_mes[
    (groupby_gastos_mes['ano_mes'].str[:4].astype(int).isin(anos_filtrados)) &
    (groupby_gastos_mes['ano_mes'].str[-2:].astype(int).isin(meses_filtrados))
]

# Atualizar o gráfico com os dados filtrados
fig = interactive_stacked_bar_chart(filtered_data, x='ano_mes', y='valor', legend='tipo_gasto')
st.plotly_chart(fig, use_container_width=True)
