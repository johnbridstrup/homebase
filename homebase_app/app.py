import os
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


app = dash.Dash(__name__)
SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:8000')

app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
    dcc.Store(id='all-sensors', storage_type='memory'),
    dcc.Store(id='sensor-data', storage_type='memory'),
    html.P("Select sensor: "),
    dcc.Dropdown(id="sensor-select", options=[]),
    dcc.Dropdown(id="sensor-data-select", options=[]),
    html.P("Sensor History: "),
    dcc.Graph(id='sensor-graph'),
])

def get_sensors():
    response = requests.get(f'{SERVER_URL}/sensors/')
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return None
    
def get_sensor_data(id_):
    response = requests.get(f'{SERVER_URL}/sensors/{id_}/data/')
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return None
    
@app.callback(
    Output('all-sensors', 'data'),
    Input('sensor-select', 'id')  # Using an initial input to trigger on load
)
def load_data_on_start(_):
    data = get_sensors()
    return data

@app.callback(
    Output('sensor-select', 'options'),
    Input('all-sensors', 'data')
)
def update_dropdown_options(data):
    if data:
        options = [{'label': item['name'], 'value': item['id']} for item in data]  # Adjust based on your data structure
        return options
    return []

@app.callback(
    [
        Output('sensor-data-select', 'options'),
        Output('sensor-data', 'data'),
    ],
    [Input('sensor-select', 'value')],
)
def sensor_data_options(id_):
    data = get_sensor_data(id_)
    if data is None:
        return [], {}
    df = pd.DataFrame([d["data"] for d in data])
    options = [{'label': item, 'value': item} for item in df.columns]
    df["timestamp"] = pd.to_datetime(pd.Series([d["timestamp"] for d in data]))
    return options, df.to_json()

@app.callback(
    Output('sensor-graph', 'figure'),
    [Input('sensor-data', 'data'), Input('sensor-data-select', 'value'), Input('interval-component', 'n_intervals')],
)
def update_graph(data, value, _):
    if data is None or len(data) == 0:
        return {}
    data = pd.read_json(data)
    fig = px.line(data, x='timestamp', y=value)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)