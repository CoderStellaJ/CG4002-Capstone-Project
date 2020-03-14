#Testing for real time display
#https://community.plot.ly/t/high-cpu-in-the-browser-and-python/17073/6 -> Hacking a method to speed up performance
import dash
from dash import no_update
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

#get last row of data using the function of dbAPI.py
from dbAPI import getLastRow
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Represents the deques that will loaded into the graphs

#The deque that is used for the x-axis
X = deque(maxlen=10)
X.append(1)

#The deques here are used to store the y-axis
# -180<YAW<90
# -90<PITCH<90
# -90<ROW<90
#===============================
Yaw1 = deque(maxlen=10)
Yaw1.append(1)
Pitch1 = deque(maxlen=10)
Pitch1.append(1)
Roll1 = deque(maxlen=10)
Roll1.append(1)

Yaw2 = deque(maxlen=10)
Yaw2.append(1)
Pitch2 = deque(maxlen=10)
Pitch2.append(1)
Roll2 = deque(maxlen=10)
Roll2.append(1)

Yaw3 = deque(maxlen=10)
Yaw3.append(1)
Pitch3 = deque(maxlen=10)
Pitch3.append(1)
Roll3 = deque(maxlen=10)
Roll3.append(1)
#==============================

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Prevents some callback exceptions from slowing down the application
app.config['suppress_callback_exceptions'] = True
def main():
    init_layout(1_000)
    app.run_server(host='127.0.0.1')

#Creates a layber that will store the components to be rendered
def init_layout(refresh_interval):
        #Defines a graph
    app.layout = html.Div([
    dbc.Row([

        dbc.Col([html.H5('Dancer 1'),
                 html.Div(style={'font-size':'80%', 'background': 'white'},id='Dancer1GT'),
                 html.Div(style={'font-size':'80%'},id='Dancer1Output'),
                 html.Div(children=html.Div(id='graphsD1', className = "row")),
            dcc.Interval(
                id='graph-update',
                interval= 1000,
                n_intervals=0
                )
                ]),

        dbc.Col([html.H5('Dancer 2'),
                 html.Div(style={'font-size':'80%'},id='Dancer2GT'),
                 html.Div(style={'font-size':'80%'},id='Dancer2Output'),
                 html.Div(children=html.Div(id='graphsD2', className = "row"))
                 ]),

        dbc.Col([html.H5('Dancer 3'),
                 html.Div(style={'font-size':'80%'},id='Dancer3GT'),
                 html.Div(style={'font-size':'80%'},id='Dancer3Output'),
                 html.Div(children=html.Div(id='graphsD3', className = "row")),
                 ])
                #style={'float': 'left', 'margin': "5px 10px 10px 5px"}
                    #Figure out a way to make the dancer thing remian

        ]),

    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':5000000}

    )


#Data dictionary to associate a string with the revevant dictionary of deques
data_dict = {
"Yaw1":Yaw1,
"Pitch1": Pitch1,
"Roll1": Roll1,
"Yaw2": Yaw2,
"Pitch2": Pitch2,
"Roll2": Roll2,
"Yaw3":Yaw3,
"Pitch3": Pitch3,
"Roll3": Roll3
}

def ML(lastRow):
    #Pseudo Machine Learning Algorithmn
    if(lastRow[1] == 1.0 and lastRow[2] == 1.0 and lastRow[3] == 1.0):
        returnStr = "shoutout - Position 1,2,3"
    elif(lastRow[1] == 2.0 and lastRow[2] == 3.0 and lastRow[3] == 5.0):
        returnStr = "weightlift - Position 2,3,1"
    elif(lastRow[1] == 3.0 and lastRow[2] == 4.0 and lastRow[3] == 4.0):
        returnStr = "muscle - Position 3,1,2"
    elif(lastRow[1] == 0 and lastRow[2] == 0 and lastRow[3] == 0):
        returnStr = "transition"
    return returnStr

#Function that updates and animates all the graphs and the different changes in colour and text
@app.callback(
    [dash.dependencies.Output('graphsD1','children'),
     dash.dependencies.Output('graphsD2','children'),
     dash.dependencies.Output('graphsD3','children'),
     dash.dependencies.Output('Dancer1Output','children'),
     dash.dependencies.Output('Dancer1GT','children'),
     dash.dependencies.Output('Dancer2Output','children'),
     dash.dependencies.Output('Dancer2GT','children'),
     dash.dependencies.Output('Dancer3Output','children'),
     dash.dependencies.Output('Dancer3GT','children'),
     dash.dependencies.Output('Dancer1Output','style'),
     dash.dependencies.Output('Dancer2Output','style'),
     dash.dependencies.Output('Dancer3Output','style'),
     dash.dependencies.Output('Dancer1GT','style'),
     dash.dependencies.Output('Dancer2GT','style'),
     dash.dependencies.Output('Dancer3GT','style'),
    ],
    [dash.dependencies.Input('graph-update', 'n_intervals')]
    )
def update_graph(n):
    #Stops updates when the graph is intitally loading, this increases performance
    if n is None:
        raise PreventUpdate

    #To be used to display graph for Dancer 1
    graphs = []
    #Dancer 2
    graphs2 = []
    #Dancer 3
    graphs3 = []
    #A list of data names that are needed to update
    data_names = ['Yaw1', 'Pitch1', 'Roll1', 'Yaw2', 'Pitch2', 'Roll2', 'Yaw3', 'Pitch3', 'Roll3']

    #Functions to query the database for the last saved input to PostgreSQL
    lastRow1 = getLastRow("Dancer1")
    lastRow2 = getLastRow("Dancer2")
    lastRow3 = getLastRow("Dancer3")

    #Returns the Machine learning output to be displayed on the dashboard
    returnStr1 = ML(lastRow1)
    returnStr2 = ML(lastRow2)
    returnStr3 = ML(lastRow3)


    #Increase the value of the X-axis by 1 for all graphs
    X.append(X[-1]+1)

    #Iterate through all the data to append to the relevant deque that stores each y-axis value
    for data_name in data_names:
        if (data_name == 'Yaw1'):
            Yaw1.append(lastRow1[1])
        elif (data_name == 'Pitch1'):
            Pitch1.append(lastRow1[2])
        elif (data_name =='Roll1'):
            Roll1.append(lastRow1[3])
        elif (data_name == 'Yaw2'):
            Yaw2.append(lastRow2[1])
        elif (data_name == 'Pitch2'):
            Pitch2.append(lastRow2[2])
        elif (data_name == 'Roll2'):
            Roll2.append(lastRow2[3])
        elif (data_name == 'Yaw3'):
            Yaw3.append(lastRow3[1])
        elif (data_name == 'Pitch3'):
            Pitch3.append(lastRow3[2])
        elif (data_name == 'Roll3'):
            Roll3.append(lastRow3[3])

        #Create the settings of the graph
        data = go.Scatter(
            x=list(X),
            y=list(data_dict[data_name]),
            name='Scatter',
            mode= 'lines'
            )

        #get last digit of the data_name to correspond to the dancer, e.g. Dancer 1/2/3
        dancerNo = data_name[-1]

        #Add the graph to the graphs array for Dancer 1
        if(dancerNo == '1'):
            graphs.append(dbc.Col(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[0,6]),
                                                            #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                            margin={'l':10,'r':1,'t':30,'b':30},
                                                            title='{}'.format(data_name),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 300
                                                            )}
            ))))

        #Add graph to graph2 array for Dancer 2
        elif(dancerNo == '2'):
            graphs2.append(dbc.Col(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[0,6]),
                                                            margin={'l':10,'r':1,'t':30,'b':30},
                                                            title='{}'.format(data_name),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 300
                                                            )}

            ))))
        #Add graph to graph3 array for Dancer 3
        elif(dancerNo == '3'):
            graphs3.append(dbc.Col(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[0,6]),
                                                            margin={'l':10,'r':1,'t':30,'b':30},
                                                            title='{}'.format(data_name),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 300
                                                            )}

            ))))

    

    return [graphs,
            graphs2,
            graphs3,
            "Dance Move Executed: " + returnStr1,
            "Ground Truth: " + lastRow1[0],
            "Dance Move Executed: " + returnStr2,
            "Ground Truth: " + lastRow2[0],
            "Dance Move Executed: " + returnStr3,
            "Ground Truth: " + lastRow3[0],
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'red'} if (n%2) else {'background': 'white'},
            {'background':'red'} if (n%2) else {'background': 'white'},
            {'background':'red'} if (n%2) else {'background': 'white'},
            ]



#Main function
if __name__ == '__main__':
    #app.run_server(debug=True)
    main()
