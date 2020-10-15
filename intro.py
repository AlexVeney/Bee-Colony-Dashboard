import pandas as pd
import plotly.express as px # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas dataframe)
# *** PostGresql can be used to get the data in here instead ***
df = pd.read_csv("usda_bees.csv")

# Columns of interest: 
# FEATURES - Year, State, ANSI, Affected by, State_Code
# TARGET - Pct of Colonies Impacted
# Ignoring the following columns: Program, Period
df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)
print(df[:5])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    # Title
    html.H1("Bee colonies affected by Varroa mites (USA)", style={'text-align': 'center'}),

    # Dropdown options label(user view) value(value within program (int))
    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(), # Space between div and graph

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# Callbacks use component_ids and component_properties to connect the two+
#   Output and Input
#   2 Outputs: output_container and my_bee_map
#       my_bee_map is the component_id that belongs to Graph
#       output_container is the component_id that belongs to Div
#   1 Input: slct_year
#       slct_year is the component_id that belongs to Dropdown
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)

# Function definition of the callback function
# Number of arguments match the number of inputs 1:1
# The argument corresponds to the component_property
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    # Make copy of dataframe to modify it within the function
    dff = df.copy()
    # Filter dataframe rows with Year that user selected
    dff = dff[dff["Year"] == option_slctd]
    # Filter dataframe rows where bees are affected by mites
    dff = dff[dff["Affected by"] == "Varroa_mites"]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    # # Plotly Graph Objects (GO)
    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Blues',
    #     )]
    # )
    
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)