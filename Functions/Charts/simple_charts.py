import matplotlib.pyplot as plt
import plotly.express as px

def interactive_stacked_bar_chart(df, x, y, legend):
    """
    Cria um gráfico interativo de barras empilhadas com valores totais exibidos no topo.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados.
        x (str): Nome da coluna para o eixo x.
        y (str): Nome da coluna para o eixo y.
        legend (str): Nome da coluna para a legenda (agrupamento).

    Returns:
        fig: Objeto Plotly Figure.
    """
    # Criar o gráfico de barras empilhadas
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=legend,
        title=f'Gráfico de Barras Empilhadas ({x} por {legend})',
        text=None  # Não exibir valores diretamente nas barras
    )

    # Adicionar o valor total de cada x no topo das barras
    totals = df.groupby(x)[y].sum().reset_index()
    for i, row in totals.iterrows():
        fig.add_annotation(
            x=row[x],
            y=row[y] * 1.08,  # Ajustar o valor para ficar mais acima
            text=f"{row[y]:,.2f}",  # Exibir o total formatado
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # Ajustar layout
    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        legend_title=legend,
        barmode='stack',
        template='plotly_white'
    )

    return fig