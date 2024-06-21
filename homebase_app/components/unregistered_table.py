import dash_bootstrap_components as dbc
import dash_table
from dash import html


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
        ],width={'size':1,'offset':0,'order':'1'}),
        dbc.Col([
            html.H2("Register Sensor"),
            dbc.Input(id='sensor-name', placeholder='Sensor Name', type='text'),
            dbc.Button('Register', id='register-button', color='primary'),
            html.Div(id='register-status'),
        ],width={'size':1,'offset':0,'order':'1'}),
    ]),
])