# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
sites = list(spacex_df['Launch Site'].unique())
sites.append('All')
spacex_df['Booster_Version_abr'] = spacex_df['Booster Version'].map(lambda x: x.split()[1])


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=sites, value='All', 
                                    placeholder='Select a Launch Site here, searchable=True'),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min=0, max=10000, step= 1000, value=[min_payload, max_payload], id='payload-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(site):
    if site == 'All':
        filter = spacex_df['class'] == 1
        graph_df = spacex_df.loc[filter, 'Launch Site'].value_counts().reset_index().sort_values('Launch Site') 
        fig = px.pie(graph_df, values='count', names = 'Launch Site')
        fig.update_layout(title_text='Launch Successes All Sites', title_x=0.5)
    else:
        filter = spacex_df['Launch Site'] == site
        graph_df = spacex_df.loc[filter, 'class'].value_counts().reset_index().sort_values('class')
        legend_vars = graph_df['class'].map({0:  'Failure', 1: 'Success'})
        fig = px.pie(graph_df, values='count', names = legend_vars, color=legend_vars, color_discrete_map = {'Success': 'blue', 'Failure': 'gray'})
        fig.update_layout(title_text=f'Launch Success Rate for Site: {site}', title_x=0.5)
        fig.update_traces(textposition='inside', textinfo='percent+label') 
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_plot(site, payload):
    if site == 'All':
        filter = (spacex_df['Payload Mass (kg)'] > payload[0]) & (spacex_df['Payload Mass (kg)'] < payload[1])
        spacex_df_filtered = spacex_df[filter]
        fig_scatter = px.scatter(spacex_df_filtered , x='Payload Mass (kg)', y = 'class', color='Booster_Version_abr')
        fig_scatter.update_layout(title_text='Launch Status vs. Payload All Sites', title_x=0.5,     
            yaxis = dict(
                tickmode = 'array',
                tickvals = [0, 1],
                ticktext = ['Failure', 'Success']))
        fig_scatter.update_yaxes(range=[-0.5, 1.5])
    else:   
        filter = (spacex_df['Launch Site'] == site) & (spacex_df['Payload Mass (kg)'] > payload[0]) & (spacex_df['Payload Mass (kg)'] < payload[1])
        spacex_df_filtered = spacex_df[filter]
        fig_scatter = px.scatter(spacex_df_filtered, x='Payload Mass (kg)', y = 'class', color='Booster_Version_abr')
        fig_scatter.update_layout(title_text=f'Launch Status vs. Payload for Site = {site}', title_x=0.5,      
            yaxis = dict(
                tickmode = 'array',
                tickvals = [0, 1],
                ticktext = ['Failure', 'Success']))
        fig_scatter.update_xaxes(range=[payload[0], payload[1]])
        fig_scatter.update_yaxes(range=[-0.5, 1.5])
    return fig_scatter


# Run the app
if __name__ == '__main__':
    app.run_server(port = 8060)
