#Testing for real time display

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

from dbAPI import getLastRow


X = deque(maxlen=10)
X.append(1)
Yaw = deque(maxlen=10)
Yaw.append(1)
Pitch = deque(maxlen=10)
Pitch.append(1)
Roll = deque(maxlen=10)
Roll.append(1)


app = dash.Dash(__name__)

#Defines a graph
app.layout = html.Div([
    html.Div([
        html.H2('Dancer 1',
                style={'float': 'left',
                       }),
        ]),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
        id='graph-update',
        interval=1000,
        n_intervals=0),

    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})

data_dict = {"Yaw":Yaw,
"Pitch": Pitch,
"Roll": Roll
}

@app.callback(
    dash.dependencies.Output('graphs','children'),
     [dash.dependencies.Input('graph-update', 'n_intervals')]
    )
def update_graph(n):
    graphs = []
    data_names = ['Yaw', 'Pitch', 'Roll']
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'
    lastRow = getLastRow("Dancer1")
    X.append(X[-1]+1)
    for data_name in data_names:
        if (data_name == 'Yaw'):
            Yaw.append(lastRow[0])
        elif (data_name == 'Pitch'):
            Pitch.append(lastRow[1])
        else:
            Roll.append(lastRow[2])
        
        data = go.Scatter(
            x=list(X),
            y=list(data_dict[data_name]),
            name='Scatter',
            mode= 'lines+markers'
            )
        graphs.append(html.Div(dcc.Graph(
            id=data_name,
            animate=True,
            figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                        yaxis=dict(range=[0,5]),
                                                        #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                        margin={'l':50,'r':1,'t':45,'b':30},
                                                        title='{}'.format(data_name))}
        )), className=class_choice))
        
    return graphs

#Main function
if __name__ == '__main__':
    app.run_server(debug=True)
    








    
