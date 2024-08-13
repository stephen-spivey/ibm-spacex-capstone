import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown list for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),
    
    html.Br(),
    
    # Pie chart to show the total successful launches count
    dcc.Graph(id='success-pie-chart'),
    
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    
    html.Br(),
    
    # Scatter chart to show correlation between payload and launch success
    dcc.Graph(id='success-payload-scatter-chart'),
    
    html.Br()
])

# Callback to update pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    
    outcome_counts = filtered_df['class'].value_counts().reset_index()
    outcome_counts.columns = ['Outcome', 'Count']
    
    fig = px.pie(
        outcome_counts,
        names='Outcome',
        values='Count',
        title=f'Launch Outcomes for {entered_site}' if entered_site != 'ALL' else 'Launch Outcomes for All Sites'
    )
    
    return fig

# Callback to update scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df
    if selected_site != 'ALL':
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload Mass vs. Class for {selected_site}' if selected_site != 'ALL' else 'Payload Mass vs. Class for All Sites',
        labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Success (1) / Failure (0)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)