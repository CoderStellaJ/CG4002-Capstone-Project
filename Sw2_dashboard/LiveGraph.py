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

from random import seed
from random import randint
# seed random number generator
seed(1)

X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(1)
sensorValues = [2,3]

def addSensorValues():
    for x in range(30):
        sensorValues.append(x)


app = dash.Dash(__name__)

#Defines a graph
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals = 0
        )
    ]
)

#generate dummyData whenever there is a sensor showed
def dummyData():
    i = 0
    for _ in range(10):
        i = randint(0, 30)
    return sensorValues[i]


@app.callback(Output('live-graph', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    
    X.append(X[-1]+1)
    #Y.append(Y[-1]+Y[-1]*random.uniform(-0.1,0.1))
    #Y.append(dummyData())
    Y.append(getLastRow("testTable"))
    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )#selects the range of values
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[0,max(Y)]),)}







#Main function
if __name__ == '__main__':
    addSensorValues()
    #print(sensorValues)
    app.run_server(debug=True)
    
