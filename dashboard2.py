# Setup the Jupyter version of Dash
from jupyter_dash import JupyterDash

# Configure the necessary Python module imports
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output


# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#### FIX ME #####
# change animal_shelter and AnimalShelter to match your CRUD Python module file name and class name
from crud import CRUD


###########################
# Data Manipulation / Model
###########################
# FIX ME update with your username and password and CRUD Python module name. NOTE: You will
# likely need more variables for your constructor to handle the hostname and port of the MongoDB
# server, and the database and collection names

username = "aacuser"
password = "password"
host = "nv-desktop-services.apporto.com"
port = 32021
db = "AAC"
col = "animals"
shelter = CRUD(username, password, host, port, db, col)


# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(shelter.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invalid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will return a new dataframe that does not contain the dropped column(s)
df.drop(columns=['_id'], inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)

logo_path = "logo.png"

#########################
# Dashboard Layout / View
#########################
app = JupyterDash('SimpleExample')

app.layout = html.Div([
    html.Div(id='hidden-div', style={'display': 'none'}),
    html.Center(html.A(href="https://www.snhu.edu", children=[html.Img(src=app.get_asset_url(logo_path))])),
    html.H4("Jake Brunton"),
    html.Div(className='buttonRow', 
             style={'display': 'flex'},
             children=[
                 html.Button(id='submit-button-one', n_clicks=0, children='Cats'),
                 html.Button(id='submit-button-two', n_clicks=0, children='Dogs'),
                 dcc.Dropdown(['Disaster Rescue', 'Water Rescue', 'Wilderness/Mountain Rescue', 'Default'], 
                              'Default', id='type-dropdown')
             ]),
    dash_table.DataTable(id='datatable-id',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": True}
                                  for i in df.columns],
                         data=df.to_dict('records'),
                         editable=False,
                         filter_action="native",
                         sort_action="native",
                         sort_mode="multi",
                         column_selectable=False,
                         row_selectable="single",
                         row_deletable=False,
                         selected_columns=[],
                         selected_rows=[0],
                         page_action="native",
                         page_current=0,
                         page_size=10
                        ),
    html.Br(),
    html.Div([
        html.Hr(),
        dcc.Graph(id='pie-chart'),
        html.Hr(),
    ]),
    html.Div(className='col s12 m6', id='map-id')
])

#############################################
# Interaction Between Components / Controller
#############################################
# This callback will highlight a row on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]

# Callback for filtering the data in the table based on dropdown selection
@app.callback(
    Output('datatable-id', 'data'),
    [Input('type-dropdown', 'value')]
)
def update_table(typeSelect):
    query = {}
    if typeSelect == "Disaster Rescue":
        query = {"animal_type": "Dog", "breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]}}
    elif typeSelect == "Water Rescue":
        query = {"animal_type": "Dog", "breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]}}
    elif typeSelect == "Wilderness/Mountain Rescue":
        query = {"animal_type": "Dog", "breed": {"$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"]}}
    elif typeSelect == "Default":
        query = {}  # No filter applied, show all data
    
    df_filtered = pd.DataFrame.from_records(shelter.read(query))
    df_filtered.drop(columns=['_id'], inplace=True)
    
    return df_filtered.to_dict('records')

# Callback for updating the pie chart based on the current data displayed in the datatable
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('datatable-id', 'derived_virtual_data')]
)
def update_pie_chart(virtual_data):
    # Convert the virtual data back to a DataFrame
    if virtual_data is None or len(virtual_data) == 0:
        fig = px.pie(names=['No Data'], values=[1], title='No Data Available')
        fig.update_traces(marker=dict(colors=['#FFFFFF']))
    else:
        df_filtered = pd.DataFrame.from_dict(virtual_data)
        
        # Create Pie Chart based on the filtered data shown in the table
        fig = px.pie(df_filtered, names='breed', title='Breed Distribution')

    return fig

# This callback will update the geo-location chart for the selected data entry
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):
    dff = pd.DataFrame.from_dict(viewData)
    if index is None:
        row = 0
    else:
        row = index[0]
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'},
               center=[30.75, -97.48], zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            dl.Marker(position=[dff.iloc[row, 13], dff.iloc[row, 14]],
                      children=[
                          dl.Tooltip(dff.iloc[row, 4]),
                          dl.Popup([
                              html.H1("Animal Name"),
                              html.P(dff.iloc[row, 9])
                          ])
                      ])
        ])
    ]

app.run_server(debug=True)
