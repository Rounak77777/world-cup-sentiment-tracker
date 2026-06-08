import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3

#initializing the Dash app
app = dash.Dash(__name__)

#UI Layout
app.layout = html.Div(style={'backgroundColor': '#111111', 'color': '#7FDBFF', 'fontFamily': 'sans-serif'}, children=[
    html.H1("World Cup 2026 Live Sentiment Tracker", style={'textAlign': 'center', 'padding': '20px'}),
    
    #graph comment 
    dcc.Graph(id='live-graph', animate=False),
    
    #auto refresher (fires every 10 seconds)
    dcc.Interval(
        id='graph-update',
        interval=10 * 1000, 
        n_intervals=0
    )
])

#this function runs every time the dcc.Interval ticks
@app.callback(Output('live-graph', 'figure'), 
              [Input('graph-update', 'n_intervals')])
def update_graph(n):
    try:
        #reading the latest data from SQLite
        conn = sqlite3.connect('sentiment_data.db', check_same_thread=False)
        
        #pulling last 90 rows (which equals the last 15 minutes of data at 10s intervals)
        query = "SELECT * FROM timeline ORDER BY timestamp DESC LIMIT 90"
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception:
        # If the database file or table doesn't exist yet, assign an empty DataFrame
        df = pd.DataFrame()
    
    # Setup dual axis figure baseline
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Graceful error handling: If database is empty, show a loading placeholder instead of crashing
    if df.empty:
        fig.update_layout(
            template="plotly_dark",
            annotations=[{
                "text": "Waiting for live World Cup data pipeline to start...",
                "xref": "paper", "yref": "paper",
                "showarrow": False,
                "font": {"size": 20, "color": "gray"}
            }]
        )
        fig.update_yaxes(title_text="Volume (Posts/10s)", secondary_y=False, showgrid=False)
        fig.update_yaxes(title_text="Sentiment", range=[-1.1, 1.1], secondary_y=True, showgrid=False)
        return fig

    #SQLite returns descending so we get newest first, but Plotly needs ascending to draw left to right
    df = df.sort_values('timestamp')

    #adding post volume (bar chart in background)
    fig.add_trace(
        go.Bar(
            x=df['timestamp'], 
            y=df['post_volume'], 
            name="Tweet Volume", 
            opacity=0.3, 
            marker_color='gray'
        ),
        secondary_y=False,
    )

    #adding sentiment score (line chart in foreground)
    #using a 3-window rolling average to smooth out jaggedness of the line
    smoothed_sentiment = df['avg_sentiment'].rolling(window=3, min_periods=1).mean()
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=smoothed_sentiment, 
            name="Avg Sentiment (-1 to 1)", 
            mode='lines+markers', 
            line=dict(color='#00ffcc', width=3)
        ),
        secondary_y=True,
    )

    #UI formatting
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    #locking sentiment axis from -1 to +1 so baseline never shifts
    fig.update_yaxes(title_text="Volume (Posts/10s)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Sentiment", range=[-1.1, 1.1], secondary_y=True, showgrid=True, gridcolor='#333333')

    return fig

if __name__ == '__main__':
    #running server on port 8050
    app.run(host='0.0.0.0', debug=True, port=8050)