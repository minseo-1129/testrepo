import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

spacex_df = pd.read_csv('spacex_launch_dash.csv')

launch_sites = spacex_df['Launch Site'].unique()

dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, 2000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    dcc.Graph(id='success-payload-scatter-chart')
])

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']
        fig = px.pie(success_counts, values='Success Count', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        class_counts['class'] = class_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(class_counts, values='count', names='class',
                     title=f'Success vs Failure for site {selected_site}')
    return fig

# Scatter plot 콜백
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(df_filtered, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs Outcome for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]
        fig = px.scatter(df_filtered, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs Outcome for site {selected_site}',
                         labels={'class': 'Launch Outcome'})

    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8051)