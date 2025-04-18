from flask import Flask, request, jsonify
import pandas as pd
import os

# importa a função API_Notion que você já usa
from Functions.APIs.notion import API_Notion

app = Flask(__name__)

# Defina suas credenciais manualmente por enquanto
NOTION_DATASET_ID = os.environ['NOTION_DATASET_ID']
NOTION_TOKEN = os.environ['NOTION_TOKEN']


def extrair_tratar_dados(dataset_id, token, ano_mes=None, ano_fatura=None):
    df = API_Notion(dataset_id, token)

    # Normalização e tratamento
    df = df[['properties']]
    df = pd.json_normalize(df['properties'])
    df = df.explode('Gasto.title')
    df_title = pd.json_normalize(df['Gasto.title'])
    df = pd.concat([df.drop('Gasto.title', axis=1), df_title], axis=1)
    df = df[['text.content', 'Valor.number', 'Data.date.start', 'ANO.formula.number',
             'Mês da fatura.formula.number', 'Natureza.select.name', 'Tipo gasto 2.select.name']]
    df.rename(columns={
        'text.content': 'gasto',
        'Mês da fatura.formula.number': 'mes_fatura',
        'Natureza.select.name': 'natureza',
        'ANO.formula.number': 'ano_fatura',
        'Data.date.start': 'data',
        'Tipo gasto 2.select.name': 'tipo_gasto',
        'Valor.number': 'valor'
    }, inplace=True)

    df['gasto'] = df['gasto'].astype(str)
    df['mes_fatura'] = df['mes_fatura'].astype(int)
    df['natureza'] = df['natureza'].astype(str)
    df['ano_fatura'] = df['ano_fatura'].astype(int)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['tipo_gasto'] = df['tipo_gasto'].astype(str)
    df['valor'] = df['valor'].astype(float)
    df['ano_mes'] = df['ano_fatura'].astype(str) + '-' + df['mes_fatura'].astype(str).str.zfill(2)

    # Aplicar os filtros opcionais
    if ano_mes:
        df = df[df['ano_mes'] == ano_mes]
    if ano_fatura:
        df = df[df['ano_fatura'] == int(ano_fatura)]

    return df

@app.route('/gastos', methods=['POST'])
def gastos():
    body = request.get_json()
    ano_mes = body.get('ano_mes')
    ano_fatura = body.get('ano_fatura')

    try:
        df = extrair_tratar_dados(NOTION_DATASET_ID, NOTION_TOKEN, ano_mes, ano_fatura)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(df.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) # Para produção
    # app.run(debug=True) # Para desenvolvimento

