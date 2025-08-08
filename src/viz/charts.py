import plotly.express as px
import pandas as pd

def line_trend(df: pd.DataFrame, x="date", y="registrations", color=None, title="Trend"):
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Date=%{x|%Y-%m-%d}"
                      "<br>Registrations=%{y:,}<extra></extra>"
        if color else
        "Date=%{x|%Y-%m-%d}<br>Registrations=%{y:,}<extra></extra>"
    )
    fig.update_layout(legend_title_text="")
    return fig

def bar_growth(df: pd.DataFrame, x, y="yoy_pct", color=None, title="Growth %"):
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>")
    fig.update_layout(legend_title_text="")
    return fig
