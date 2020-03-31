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
import numpy as np

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
#   <X<
#   <Y<
#   <Z<
#   EMG???
#===============================
Yaw1 = deque(maxlen=10)
Yaw1.append(1)
Pitch1 = deque(maxlen=10)
Pitch1.append(1)
Roll1 = deque(maxlen=10)
Roll1.append(1)
X1 = deque(maxlen=10)
X1.append(1)
Y1 = deque(maxlen=10)
Y1.append(1)
Z1 = deque(maxlen=10)
Z1.append(1)

Yaw2 = deque(maxlen=10)
Yaw2.append(1)
Pitch2 = deque(maxlen=10)
Pitch2.append(1)
Roll2 = deque(maxlen=10)
Roll2.append(1)
X2 = deque(maxlen=10)
X2.append(1)
Y2 = deque(maxlen=10)
Y2.append(1)
Z2 = deque(maxlen=10)
Z2.append(1)

Yaw3 = deque(maxlen=10)
Yaw3.append(1)
Pitch3 = deque(maxlen=10)
Pitch3.append(1)
Roll3 = deque(maxlen=10)
Roll3.append(1)
X3 = deque(maxlen=10)
X3.append(1)
Y3 = deque(maxlen=10)
Y3.append(1)
Z3 = deque(maxlen=10)
Z3.append(1)

MaxAmp = deque(maxlen=10)
MaxAmp.append(1)
MeanAmp = deque(maxlen=10)
MeanAmp.append(1)
RMSAmp = deque(maxlen=10)
RMSAmp.append(1)
MeanFreq = deque(maxlen =10)
MeanFreq.append(1)
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
    html.H6("CG4002 Group 6"),

    dbc.Row([

        dbc.Col([
            html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('Dancer 1')),
            html.Div(style={'font-size':'80%'},id='Dancer1Output'),
            dbc.Row([
                dbc.Col([html.H6('IMU'),
                         
                         html.Div(children=html.Div(id='graphsD1', className = "row")),
                    dcc.Interval(
                        id='graph-update',
                        interval= 1000,
                        n_intervals=0
                        )
                        ]),
                dbc.Col([html.H6('Accelerometer'),
                         html.Div(children=html.Div(id='graphsD2', className = "row"))
                 ])
        ]),

            ]),

        dbc.Col([
            html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('Dancer 2')),
            html.Div(style={'font-size':'80%'},id='Dancer2Output'),
            dbc.Row([
                dbc.Col([html.H6('IMU'),
                         html.Div(children=html.Div(id='graphsD3', className = "row")),
                         ]),
                dbc.Col([html.H6('Accelerometer'),
                         html.Div(children=html.Div(id='graphsD4', className = "row")),
                         ])
                    ]),
            ]),
        ]),

    ##add the EMG to a new row and colum grid with dancer 3
    dbc.Row([
            
            dbc.Col([
                    html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('Dancer 3')),
                    html.Div(style={'font-size':'80%'},id='Dancer3Output'),    
                    dbc.Row([
                        dbc.Col([html.H6('IMU'),
                                 html.Div(children=html.Div(id='graphsD5', className = "row")),
                                 ]),
                        dbc.Col([html.H6('Accelerometer'),
                                 html.Div(children=html.Div(id='graphsD6', className = "row")),
                                 ]),
                        ]),
                ]),
            ##insert EMG here
            dbc.Col([
                html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('EMG')),
                html.Div(style={'font-size':'80%'},id='EMGOutput'),    
                dbc.Row([
                    dbc.Col([html.H6('Time'),
                             html.Div(children=html.Div(id='graphsD7', className = "row")),
                             ]),
                    dbc.Col([html.H6('Frequency'),
                             html.Div(children=html.Div(id='graphsD8', className = "row")),
                             ]),
                    ]),
                ]),
        ]),
    

    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':5000000}

    )


#Data dictionary to associate a string with the revevant dictionary of deques
data_dict = {
"Yaw1":Yaw1,
"Pitch1": Pitch1,
"Roll1": Roll1,
"X1":X1,
"Y1": Y1,
"Z1": Z1,
"Yaw2": Yaw2,
"Pitch2": Pitch2,
"Roll2": Roll2,
"X2":X2,
"Y2": Y2,
"Z2": Z2,
"Yaw3":Yaw3,
"Pitch3": Pitch3,
"Roll3": Roll3,
"X3":X3,
"Y3": Y3,
"Z3": Z3,
"MaxAmp": MaxAmp,
"MeanAmp": MeanAmp,
"RMSAmp": RMSAmp,
"MeanFreq": MeanFreq
##"Yaw4":Yaw4,
##"Pitch4": Pitch4,
##"Roll4": Roll4,
##"X4":X4,
##"Y4": Y4,
##"Z4": Z4,
##"Yaw5": Yaw5,
##"Pitch5": Pitch5,
##"Roll5": Roll5,
##"X5":X5,
##"Y5": Y5,
##"Z5": Z5,
##"Yaw6":Yaw5,
##"Pitch6": Pitch6,
##"Roll6": Roll6,
##"X6":X6,
##"Y6": Y6,
##"Z6": Z6,
}

global front
front = 1
global back
back= 4
global counter
counter = 1

#https://stackoverflow.com/questions/55649356/how-can-i-detect-if-trend-is-increasing-or-decreasing-in-time-series
def determineTrend(data):
    index = [1,2,3,4,5]
    coeffs = np.polyfit(index,list(data), 1)
    slope = coeffs[-2]
    trendVal = float(slope)
    trend = ''
    if(trendVal>0):
        trend = "increasing"
    elif(trendVal<0):
        trend = "decreasing"
    print(float(slope))
    return trend


#Function that updates and animates all the graphs and the different changes in colour and text
@app.callback(
    [dash.dependencies.Output('graphsD1','children'),
     dash.dependencies.Output('graphsD2','children'),
     dash.dependencies.Output('graphsD3','children'),
     dash.dependencies.Output('graphsD4','children'),
     dash.dependencies.Output('graphsD5','children'),
     dash.dependencies.Output('graphsD6','children'),
     dash.dependencies.Output('graphsD7','children'),
     dash.dependencies.Output('graphsD8','children'),
     dash.dependencies.Output('Dancer1Output','children'),
     dash.dependencies.Output('Dancer2Output','children'),
     dash.dependencies.Output('Dancer3Output','children'),
     dash.dependencies.Output('EMGOutput','children'),
     dash.dependencies.Output('Dancer1Output','style'),
     dash.dependencies.Output('Dancer2Output','style'),
     dash.dependencies.Output('Dancer3Output','style'),
     dash.dependencies.Output('EMGOutput','style'),
    ],
    [dash.dependencies.Input('graph-update', 'n_intervals')]
    )
def update_graph(n):
    #Stops updates when the graph is intitally loading, this increases performance
    if n is None:
        raise PreventUpdate

    #To be used to display graph for graphs 1,2 are for dancer 1, graphs 3 & 4 are for dancer 2, graphs 5 & 6 are for dancer 3
    YPR1 = []
    XYZ1 = []
    YPR2 = []
    XYZ2 = []
    YPR3 = []
    XYZ3 = []
    EMG1 = []
    EMG2 = []
    #A list of data names that are needed to update
    data_names = ['Beetle1', 'Beetle2', 'Beetle3']

    #Functions to query the database for the last saved input to PostgreSQL
    lastRow1 = getLastRow("Beetle1")
    lastRow2 = getLastRow("Beetle2")
    lastRow3 = getLastRow("Beetle3")
    lastRow4 = getLastRow("EMG")
    MLDancer1 = getLastRow("MLDancer1")


    #Append new data
    Yaw1.append(lastRow1[0])
    Pitch1.append(lastRow1[1])
    Roll1.append(lastRow1[2])
    X1.append(lastRow1[3])
    Y1.append(lastRow1[4])
    Z1.append(lastRow1[5])
    Yaw2.append(lastRow2[0])
    Pitch2.append(lastRow2[1])
    Roll2.append(lastRow2[2])
    X2.append(lastRow2[3])
    Y2.append(lastRow2[4])
    Z2.append(lastRow2[5])
    Yaw3.append(lastRow3[0])
    Pitch3.append(lastRow3[1])
    Roll3.append(lastRow3[2])
    X3.append(lastRow3[3])
    Y3.append(lastRow3[4])
    Z3.append(lastRow3[5])
    #MaxAmp.append(lastRow4[0])
     #+(randint(-1, 1))
    #===================================Test
    global front
    global back
    global counter
    if(front == 5 or front == 0):
        counter *=-1
    front +=counter
    back +=counter*-1
    MaxAmp.append(front)
    MeanFreq.append(back)
    output = ''
    try:
        AmpData = (list(MaxAmp))[-5:]
        AmpTrend = determineTrend(AmpData)
        FreqData = (list(MeanFreq))[-5:]
        FreqTrend = determineTrend(FreqData)
        if(FreqTrend == "decreasing" and AmpTrend == "increasing"):
            output = "Fatigued"
        else:
            output = "Ready to Dance"
    except:
        print("EMG output not ready")
    
    #==========================================
    
    MeanAmp.append(lastRow4[1])
    RMSAmp.append(lastRow4[2])
    #MeanFreq.append(lastRow4[3])


    #Increase the value of the X-axis by 1 for all graphs
    X.append(X[-1]+1)
    
    MaxAmplitude = (go.Scatter(
        x=list(X),
        y=list(data_dict['MaxAmp']),
        name='Max Amplitude',
        mode= 'lines'
        ))
    MeanAmplitude = (go.Scatter(
        x=list(X),
        y=list(data_dict['MeanAmp']),
        name='Mean Amplitude',
        mode= 'lines'
        ))
    RMSAmplitude = (go.Scatter(
        x=list(X),
        y=list(data_dict['RMSAmp']),
        name='RMS Amplitude',
        mode= 'lines'
        ))
    MeanFrequency = (go.Scatter(
        x=list(X),
        y=list(data_dict['MeanFreq']),
        name='Mean Frequency',
        mode= 'lines'
        ))
    EMG1.append(dbc.Col(html.Div(dcc.Graph(
                id="EMG1",
                animate=True,
                ##Change the value of 'data' to fig add in MeanAmplitudem RMSAmplitude
                figure={'data': [MaxAmplitude],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[0,5]),#change to 250,250
                                                            #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                            #yaxis = dict(range = [min(),max()])
                                                            margin={'l':30,'r':1,'t':30,'b':30},
                                                            title='{}'.format(''),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 360
                                                            )}
            ))))
    EMG2.append(dbc.Col(html.Div(dcc.Graph(
            id="EMG2",
            animate=True,
            ##Change the value of 'data' to fig
            figure={'data': [MeanFrequency],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                        yaxis=dict(range=[0,5]),#change to 1.0 - 2.0
                                                        #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                        #yaxis = dict(range = [min(),max()])
                                                        margin={'l':30,'r':1,'t':30,'b':30},
                                                        title='{}'.format(''),
                                                        font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                        height = 250,
                                                        width = 360
                                                        )}
        ))))

    
    #Iterate through all the data to append to the relevant deque that stores each y-axis value
    for data_name in data_names:
        dancerNo =  data_name[-1]
        YAW = (go.Scatter(
        x=list(X),
        y=list(data_dict['Yaw' + dancerNo]),
        name='Yaw',
        mode= 'lines'
        ))
        PITCH = (go.Scatter(
        x=list(X),
        y=list(data_dict['Pitch' + dancerNo]),
        name='Pitch',
        mode= 'lines'
        ))
        ROLL = (go.Scatter(
        x=list(X),
        y=list(data_dict['Roll'+dancerNo]),
        name='Roll',
        mode= 'lines'
        ))
        XAxis = (go.Scatter(
        x=list(X),
        y=list(data_dict['X'+dancerNo]),
        name='X-Axis',
        mode= 'lines'
        ))
        YAxis = (go.Scatter(
        x=list(X),
        y=list(data_dict['Y'+dancerNo]),
        name='Y-Axis',
        mode= 'lines'
        ))
        ZAxis = (go.Scatter(
        x=list(X),
        y=list(data_dict['Z'+dancerNo]),
        name='Z-Axis',
        mode= 'lines'
        ))
        
        

        YPR = eval("YPR" + dancerNo)
        XYZ = eval("XYZ" + dancerNo)

        YPR.append(dbc.Col(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                ##Change the value of 'data' to fig
                figure={'data': [YAW,PITCH,ROLL],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[-5000,5000]),#change to 250,250
                                                            #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                            #yaxis = dict(range = [min(),max()])
                                                            margin={'l':30,'r':1,'t':30,'b':30},
                                                            title='{}'.format(''),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 360
                                                            )}
            ))))
        XYZ.append(dbc.Col(html.Div(dcc.Graph(
                id=data_name,
                animate=True,
                ##Change the value of 'data' to fig
                figure={'data': [XAxis,YAxis,ZAxis],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[-50000,50000]),# <X<
                                                            #yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),
                                                            #yaxis = dict(range = [min(),max()])
                                                            margin={'l':30,'r':1,'t':30,'b':30},
                                                            title='{}'.format(''),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 360
                                                            )}
            ))))

    

    return [YPR1,
            XYZ1,
            YPR2,
            XYZ2,
            YPR3,
            XYZ3,
            EMG1,
            EMG2,
            "Dance Move Executed: " + MLDancer1[0],
            "Dance Move Executed: " + MLDancer1[0],
            "Dance Move Executed: " + MLDancer1[0],
            output,
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'springgreen'} if (n%2) else {'background': 'white'},
            {'background':'red'} if (n%2 and output == 'Fatigued') else {'background': 'white'},
            ]



#Main function
if __name__ == '__main__':
    #app.run_server(debug=True)
    main()
