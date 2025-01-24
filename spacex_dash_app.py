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

# Extract Launch site names
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site']]

# Start with the default "All Sites" option
options = [{'label': 'All Sites', 'value': 'ALL'}]

# Add each launch site to the options
for _, row in launch_sites_df.iterrows():
    options.append({'label': row['Launch Site'], 'value': row['Launch Site']})


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                  dcc.Dropdown(id='site-dropdown',
                options=options,
                value='ALL',
                placeholder="Select a Launch Site here",
                searchable=True
                ),
                                html.Br(),
    # Range Slider for payload selection
    html.Div([
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: f'{i} kg' for i in range(0, 11000, 2500)},
            value=[min_payload, max_payload]
        )
    ]),
    html.Br(),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
            fig = px.pie(spacex_df, values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site')
            return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Group data by class for the selected site
        success_count = filtered_df['class'].value_counts().reset_index()
        success_count.columns = ['class', 'count']

        fig = px.pie(
            success_count,
            values='count',
            names='class',
            title=f'Total Success Launches for Site {entered_site}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter the dataframe based on the payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if entered_site == 'ALL':
        # If 'ALL' sites are selected, plot data for all launch sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Launch Outcome'},
        )
    else:
        # Filter dataframe for the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for Site {entered_site}',
            labels={'class': 'Launch Outcome'},
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
