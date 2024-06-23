import os
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from components.unregistered_table import unregistered_table


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
    unregistered_table,
    dbc.Button('Create Room', id='create-room-button', color='primary'),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Create Room")),
            dbc.ModalBody(
                dbc.Form([
                    dbc.Input(id="room-name", placeholder="Enter Room Name"),
                ])
            ),
            dbc.ModalFooter(
                dbc.Button("Submit", id="submit-form-button", className="ml-auto", n_clicks=0)
            ),
        ],
        id="form-modal",
        is_open=False,
    ),
    html.Div(id="create-room-info")
])

def get_sensors():
    sen_response = requests.get(f'{SERVER_URL}/sensors/')
    roo_response = requests.get(f'{SERVER_URL}/rooms/')
    if sen_response.status_code == 200 and roo_response.status_code == 200:
        return sen_response.json()["results"], roo_response.json()["results"]
    else:
        sen_response.raise_for_status()
        roo_response.raise_for_status()
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
    [
        Output('sensor-select', 'options'),
        Output('unregistered-table', 'data'),
        Output('room-select', 'options')
    ],
    Input('all-sensors', 'data')
)
def update_dropdown_options(data):
    data, rooms = data
    if data:
        options = [{'label': item['name'], 'value': item['id']} for item in data if item["status"] != "Unregistered"]
        room_opts = [{'label': item['name'], 'value': item['id']} for item in rooms]
        unreg_sensors = [
            {
                "name": item['name'], 
                "sensor_type": item['sensor_type'],
                "id": item['id'],
            } for item in data if item["status"] == "Unregistered"]
        return options, unreg_sensors, room_opts
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

@app.callback(
    Output('register-status', 'children'),
    [Input('register-button', 'n_clicks')],
    [State('sensor-name', 'value'), State('unregistered-table', 'selected_cells'), State("room-select", "value")],
)
def register_sensor(n_clicks, name, selected_cells, room=None):
    if n_clicks == 0:
        return ""
    if name:
        id_ = selected_cells[0]["row_id"]
        response = requests.post(f'{SERVER_URL}/sensors/{id_}/register/', json={"name": name, "room": room})
        if response.status_code == 200:
            return "Sensor registered successfully"
        else:
            return "Failed to register sensor"
    else:
        return "Please enter a sensor name"


# Create Room Modal
@app.callback(
    Output("form-modal", "is_open"),
    [Input("create-room-button", "n_clicks"), Input("submit-form-button", "n_clicks")],
    [State("form-modal", "is_open")],
)
def toggle_modal(open_clicks, submit_clicks, is_open):
    if open_clicks or submit_clicks:
        return not is_open
    return is_open

# Define the callback to handle form submission
@app.callback(
    Output("create-room-info", "children"),
    [Input("submit-form-button", "n_clicks")],
    [State("room-name", "value")]
)
def handle_form_submission(n_clicks, name):
    if n_clicks > 0:
        response = requests.post(f'{SERVER_URL}/rooms/', data={"name": name})
        if response.status_code == 201:
            return f"Room {name} created successfully"
        response.raise_for_status()
    return ""


if __name__ == '__main__':
    app.run_server(debug=True)