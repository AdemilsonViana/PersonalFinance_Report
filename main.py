#%% ----------------------------------------------
# imports
#streamlit run main.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from Functions.APIs.notion import API_Notion

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
    # criar a coluna de ano e mês
df['ano_mes'] = df['data'].dt.to_period('M')

#%% ----------------------------------------------
# charts
# gráfico de barras empilhadas tipo_gasto por ano_mes
groupby_gastos_mes = df.groupby(['ano_mes', 'tipo_gasto'], as_index=False)['valor'].sum()

pivot_gastos_mes = groupby_gastos_mes.pivot(index='ano_mes', columns='tipo_gasto', values='valor').fillna(0)

pivot_gastos_mes.index = pivot_gastos_mes.index.astype(str)
#%% ----------------------------------------------
# streamlit
st.dataframe(df, hide_index=True)

#grafico de barras empilhadas tipo_gasto por ano_mes
st.subheader('Gastos por Tipo de Gasto')
st.bar_chart(pivot_gastos_mes, use_container_width=True)
