import dash_bootstrap_components as dbc
import dash_table
from dash import dcc, html


unregistered_table = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Unregistered Sensors"),
            dash_table.DataTable(
                id='unregistered-table',
                columns=[
                    {'name': 'Sensor Name', 'id': 'name'}, 
                    {'name': 'Sensor Type', 'id': 'sensor_type'},
                    {'name': 'ID', 'id': 'id'},],
                data=[],
                row_selectable='single',
            ),
        ]),
        dbc.Col([
            html.H2("Register Sensor"),
            dbc.Input(id='sensor-name', placeholder='Sensor Name', type='text'),
            dcc.Dropdown(id="room-select", options=[]),
            dbc.Button('Register', id='register-button', color='primary'),
            html.Div(id='register-status'),
        ]),
    ]),
])