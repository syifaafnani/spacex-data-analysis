# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                  dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                ],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                                ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                    2500: '2500',
                                                    5000: '5000',
                                                    7500: '7500',
                                                    10000: '10000'},
                                                value=[min_payload, max_payload]),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
                    names='Launch Site', 
                    title='Total Success Launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        selected_df = spacex_df.loc[(spacex_df['Launch Site'] == entered_site)]
        selected_df = selected_df.groupby(['Launch Site','class']).size().reset_index(name='class_count')
        fig = px.pie(selected_df, values='class_count', 
                    names='class', 
                    title='Total Success Launches for Site %s' % entered_site)
        return fig

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")]
            )
def get_scatter_chart(site, payload):
    if site and payload:
        selected_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0], payload[1])]
        if site == 'ALL':
            fig = px.scatter(selected_df, x='Payload Mass (kg)', 
                        y='class', color='Booster Version Category',
                        title='Correlation between Payload and Success for all Sites')
            return fig
        else:
            # return the outcomes piechart for a selected site
            selected_df = selected_df.loc[(selected_df['Launch Site'] == site)]
            fig = px.scatter(selected_df, x='Payload Mass (kg)', 
                        y='class', color='Booster Version Category',
                        title='Correlation between Payload and Success for Site %s' % site)
            return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
