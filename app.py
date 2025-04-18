from flask import Flask, request, jsonify
import pandas as pd
import os

# importa a função API_Notion que você já usa
from Functions.APIs.notion import API_Notion

app = Flask(__name__)

# Defina suas credenciais manualmente por enquanto
NOTION_DATASET_ID = os.environ.get('NOTION_DATASET_ID', '281707d290f94fc8a4181001c19764e2')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN', 'secret_wYb1plG31lhuYkJGaRLlCazU4H8GTpVcFON05ehaNjN')


def extrair_tratar_dados(dataset_id, token, data_inicio=None, data_fim=None, data=None, ano_mes=None):
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
    if data_inicio:
        df = df[df['data'] >= pd.to_datetime(data_inicio)]
    if data_fim:
        df = df[df['data'] <= pd.to_datetime(data_fim)]
    if data:
        df = df[df['data'] == pd.to_datetime(data)]
    if ano_mes:
        df = df[df['ano_mes'] == ano_mes]

    return df

@app.route('/gastos', methods=['POST'])
def gastos():
    body = request.get_json()
    data_inicio = body.get('data_inicio')
    data_fim = body.get('data_fim')
    data = body.get('data')
    ano_mes = body.get('ano_mes')

    try:
        df = extrair_tratar_dados(NOTION_DATASET_ID, NOTION_TOKEN, data_inicio, data_fim, data, ano_mes)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(df.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
