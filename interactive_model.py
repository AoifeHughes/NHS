import plotly.graph_objects as go
from scipy.integrate import odeint
import numpy as np
from dash import Dash, dcc, html, Input, Output

# Modified model function with fixed ward limit
def ward_model(y, t, C, alpha, gamma, S, Illness_Prob, Population):
    P, W = y
    new_illnesses = Illness_Prob * Population  # New patients needing hospitalization

    # Calculate ward pressure and adjust recovery rate
    ward_pressure = max(0, P / C - 1)
    adjusted_gamma = max(0.01, gamma * (1 - ward_pressure) * S)

    # Calculate admitted patients based on ward capacity
    if P < C:
        admitted_patients = min(W, alpha * W, C - P)
    else:
        admitted_patients = 0

    # Calculate the change in current and waiting patients
    dPdt = admitted_patients - adjusted_gamma * P
    dWdt = new_illnesses - admitted_patients  # Always considering new illnesses

    return dPdt, dWdt


# Function to create the figure with given values
def create_figure(C, alpha, gamma, S, Illness_Prob, Population, P0, W0, days):
    t = np.linspace(0, days, days)
    y0 = P0, W0
    ret = odeint(ward_model, y0, t, args=(C, alpha, gamma, S, Illness_Prob, Population))
    P, W = ret.T

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=P, mode='lines', name='Current Patients'))
    fig.add_trace(go.Scatter(x=t, y=W, mode='lines', name='Waiting Patients'))

    fig.update_layout(title='Hospital Ward Strain Model',
                      xaxis_title='Time (days)',
                      yaxis_title='Number of Patients')
    return fig

# Create the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='ward-model-graph'),
    html.Div([
        html.Label('Ward Capacity (C):'),
        dcc.Slider(50, 200, 10, value=100, id='C-slider'),
        html.Label('Admission Rate (Alpha):'),
        dcc.Slider(0.1, 1.0, 0.1, value=0.1, id='alpha-slider'),
        html.Label('Discharge Rate (Gamma):'),
        dcc.Slider(0.1, 1.0, 0.1, value=0.1, id='gamma-slider'),
        html.Label('Staff Availability (S):'),
        dcc.Slider(0.1, 2, 0.1, value=1, id='S-slider'),
        html.Label('Illness Probability:'),
        dcc.Slider(0.001, 0.01, 0.001, value=0.005, id='Illness_Prob-slider'),
        html.Label('Total Population:'),
        dcc.Slider(1000, 10000, 1000, value=5000, id='Population-slider'),
        html.Label('Initial Current Patients (P0):'),
        dcc.Slider(0, 100, 5, value=50, id='P0-slider'),
        html.Label('Initial Waiting Patients (W0):'),
        dcc.Slider(0, 50, 5, value=25, id='W0-slider'),
        html.Label('Simulation Duration (Days):'),
        dcc.Slider(30, 100, 10, value=50, id='days-slider')
    ], style={'width': '80%', 'margin': '0 auto'})
])

# Callback to update the graph
@app.callback(
    Output('ward-model-graph', 'figure'),
    [Input('C-slider', 'value'),
     Input('alpha-slider', 'value'),
     Input('gamma-slider', 'value'),
     Input('S-slider', 'value'),
     Input('Illness_Prob-slider', 'value'),
     Input('Population-slider', 'value'),
     Input('P0-slider', 'value'),
     Input('W0-slider', 'value'),
     Input('days-slider', 'value')]
)
def update_graph(C, alpha, gamma, S, Illness_Prob, Population, P0, W0, days):
    return create_figure(C, alpha, gamma, S, Illness_Prob, Population, P0, W0, days)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
