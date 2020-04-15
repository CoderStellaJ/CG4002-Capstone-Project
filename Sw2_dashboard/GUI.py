#Testing for real time display, developed by Gerald Chua Deng Xiang
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
#   <EMG<
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

#Processing to use bootstrap library
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
        #Dancer 1 graphs
        dbc.Col([
            html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('Dancer 1')),
            html.Div(style={'font-size':'80%'},children = html.H6(id='Dancer1Output')),
            dbc.Row([
                dbc.Col([html.Div(style ={}, children = html.H6('IMU')),
                         html.Div(children=html.Div(id='graphsD1', className = "row")),
                    dcc.Interval(
                        id='graph-update',
                        interval= 1000,
                        n_intervals=0
                        )
                        ]),
                dbc.Col([html.Div(style ={}, children = html.H6('Accelerometer')),
                         html.Div(children=html.Div(id='graphsD2', className = "row"))
                 ])
        ]),

            ]),
        #Dancer 2 graph
        dbc.Col([
            html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('Dancer 2')),
            html.Div(style={'font-size':'80%'},children = html.H6(id='Dancer2Output')),
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
                    html.Div(style={'font-size':'80%'},children = html.H6(id='Dancer3Output')),    
                    dbc.Row([
                        dbc.Col([html.H6('IMU'),
                                 html.Div(children=html.Div(id='graphsD5', className = "row")),
                                 ]),
                        dbc.Col([html.H6('Accelerometer'),
                                 html.Div(children=html.Div(id='graphsD6', className = "row")),
                                 ]),
                        ]),
                ]),
            ##EMG Graphs
            dbc.Col([
                html.Div(style ={'text-align':'center','border': '2px solid black','border-radius':'5px'}, children = html.H5('EMG')),
                html.Div(style={'font-size':'80%'},children = html.H6(id='EMGOutput')),    
                dbc.Row([
                    dbc.Col([html.H6('Amplitude'),
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
}

global front
front = 1
global back
back= 4
global counter
counter = 1

#https://stackoverflow.com/questions/55649356/how-can-i-detect-if-trend-is-increasing-or-decreasing-in-time-series
#Uses a best fit polynomials of 5 recent points to determine if it is a decreasing or increasing function
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

#Determines when frequency is decreasing and time is increasing that the dancer wearing the EMG is fatigued
def EMGAnalytics(MaxAmp,MeanAmp,RMSAmp,MeanFreq):
    #Taking the last 5 datapoints
    try:
        MaxAmpData = (list(MaxAmp))[-5:]
        MaxAmpTrend = determineTrend(MaxAmpData)
        MeanAmpData = (list(MeanAmp))[-5:]
        MeanAmpTrend = determineTrend(MeanAmpData)
        RMSAmpData = (list(RMSAmp))[-5:]
        RMSAmpTrend = determineTrend(RMSAmpData)
        FreqData = (list(MeanFreq))[-5:]
        FreqTrend = determineTrend(FreqData)
        if(FreqTrend == "decreasing" and MaxAmpTrend == "increasing" and MeanAmpTrend == "increasing" and RMSAmpTrend == 'increasing' ): #Time go up Freq go down
            return "Fatigued"#fatigue
        else:
            return "No issues present"#??Ready to dance?
    except:
        return("EMG Analytics processing")

#Determines the EMG box colour
def EMGColour(n, output):
    if(n%2 and output == "Fatigued"):
        return 'springgreen'
    elif (n%2):
        return'springgreen'
    else:
        return 'white'


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
    #Stops updates when the graph is intitally loading, this increasing performance
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
    MLDancer = getLastRow("MLDancer")


    #Append new data to deque
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
    MaxAmp.append(lastRow4[0])
    MeanAmp.append(lastRow4[1])
    RMSAmp.append(lastRow4[2])
    MeanFreq.append(lastRow4[3])

    #Determines the Analytics needed
    output = EMGAnalytics(MaxAmp,MeanFreq)


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

    #Appends graph to EMG time graph
    EMG1.append(dbc.Col(html.Div(dcc.Graph(
                id="EMG1",
                animate=True,
                ##Change the value of 'data' to fig add in MeanAmplitudem RMSAmplitude
                figure={'data': [MaxAmplitude, MeanAmplitude, RMSAmplitude],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                            yaxis=dict(range=[0,5]),#change to 250,250
                                                            margin={'l':30,'r':1,'t':30,'b':30},
                                                            title='{}'.format(''),
                                                            font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                            height = 250,
                                                            width = 360
                                                            )}
            ))))

    MeanFrequency = (go.Scatter(
    x=list(X),
    y=list(data_dict['MeanFreq']),
    name='Mean Frequency',
    mode= 'lines'
    ))
    
    #Appends graph to EMG frquency graph
    EMG2.append(dbc.Col(html.Div(dcc.Graph(
            id="EMG2",
            animate=True,
            ##Change the value of 'data' to fig
            figure={'data': [MeanFrequency],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                        yaxis=dict(range=[0,2]),#change to 1.0 - 2.0
                                                        margin={'l':30,'r':1,'t':30,'b':30},
                                                        title='{}'.format(''),
                                                        font=dict(family='Courier New, monospace', size=12, color='#7f7f7f'),
                                                        height = 250,
                                                        width = 360
                                                        )}
        ))))

    
    #Iterate through all the data to append to the relevant deque that stores Yaw, pitch, roll, x, y , z of beetles
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
                                                            yaxis=dict(range=[-200,200]),#change to 250,250
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
                                                            yaxis=dict(range=[-30000,30000]),# <X<
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
            {'background': EMGColour(n,output)},
            ]



#Main function
if __name__ == '__main__':
    #app.run_server(debug=True)
    main()
