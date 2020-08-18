import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import requests


#GET Nepal Cases Timeline (history)
url = 'https://data.nepalcorona.info/api/v1/covid/timeline'

resp = requests.get(url)

jsonData = resp.json()

timelineDf = pd.DataFrame(jsonData)

#------------------------------------------------------------------------------

#GET Nepal Testing Summary
#Current data on infections in nepal, sourced from MOHP SIT reports

url = 'https://nepalcorona.info/api/v1/data/nepal'

resp = requests.get(url)

jsonData = resp.json()

summaryDf = pd.DataFrame(jsonData)

#------------------------------------------------------------------------------

#GET Nepal Cases By Municipality
#List of infection in Nepal by municipality, district and province. It has geo location, age and gender of the patient

url = 'https://data.nepalcorona.info/api/v1/covid'

resp = requests.get(url)

jsonData = resp.json()

municipalityDf = pd.DataFrame(jsonData)

#------------------------------------------------------------------------------

test = municipalityDf[municipalityDf['currentState'] == 'active']

check = test[['id','reportedOn']].groupby('reportedOn').count()

check = test.groupby('reportedOn').count()

sum(check['id'])

#------------------------------------------------------------------------------

#GET Nepal Cases Summary (count)
#Count of nepali by different facts like agegroup, gender, currentState, province, municipality, district and more

url = 'https://data.nepalcorona.info/api/v1/covid/summary'

resp = requests.get(url)

jsonData = resp.json()

# caseCountDf = pd.DataFrame(jsonData)

#------------------------------------------------------------------------------

#GET World Infection Timeline by Country
#Infection data per day for each countries

url = 'https://data.nepalcorona.info/api/v1/world/history'

resp = requests.get(url)

jsonData = resp.json()

timelineByCountryDf = pd.DataFrame(jsonData)

#------------------------------------------------------------------------------

#GET District list
#fiter using name ?search={name of district}

url = 'https://data.nepalcorona.info/api/v1/districts'

resp = requests.get(url)

jsonData = resp.json()

districtsDf = pd.DataFrame(jsonData)


###############################################################################

###############################################################################

activeByDist = pd.DataFrame()
 
activeByDist = municipalityDf[:]

#------------------------------------------------------------------------------

activeByDist['recoveredOn'] = activeByDist['recoveredOn'].fillna('2100-01-01')

activeByDist['startDate'] = pd.to_datetime(activeByDist['reportedOn'], format='%Y-%m-%d')

activeByDist['endDate'] = pd.to_datetime(activeByDist['recoveredOn'], format='%Y-%m-%d')

#------------------------------------------------------------------------------

distrMap = dict(zip(districtsDf['id'],districtsDf['title_en']))

districtList = list(distrMap.keys())

#------------------------------------------------------------------------------

columnList = ['Date'] + districtList

inputDataDf = pd.DataFrame(columns = columnList)

#------------------------------------------------------------------------------

dateRange = pd.date_range('2020-03-01', periods=170, freq='1D')

inputDataDf['Date'] = dateRange

#------------------------------------------------------------------------------

# Iterate over rows of active cases table and fill in with number of active cases per district

for i, row in inputDataDf.iterrows():
    
    filtered = activeByDist[(activeByDist['startDate'] < row['Date'])&\
                              (activeByDist['endDate']   > row['Date'])]
    
    for distr in districtList:
        
        distrCount = filtered[filtered['district'] == int(distr)]
        
        countVal = len(distrCount)
        
        inputDataDf.at[i, distr] = countVal

#------------------------------------------------------------------------------

inputDataDf = inputDataDf.rename(columns = distrMap)

#------------------------------------------------------------------------------

inputDataDf.index = pd.to_datetime(inputDataDf['Date'])

df = inputDataDf.copy()

del df['Date']

###############################################################################

###############################################################################

# Load data
# demo_data = pd.read_csv('data/stockdata2.csv', index_col=0, parse_dates=True)
# df.index = pd.to_datetime(demo_data['Date'])



# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server


def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list


app.layout = html.Div(
    children=[
            html.Div([
                html.H1("NEPAL COVID-19 INSIGHTS"),
                # html.P("Add Text!")
        ],
            style={'padding': '8px',
                   'backgroundColor': '#DC143C',
                   'color': '#FFFFFF',
                   'padding-top': '30px',
                   # 'padding-left': '445px',
                   'text-align': 'center',
                   'font-size': '10px',
                   }),
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('SEARCH BY DISTRICT',
                                         style={'color': '	#FFFFFF'}),
                                 html.P('Pick one or more districts from the dropdown below.',
                                        style={'color': '#FFFFFF'}),
                                 html.Div(
                                     className='custom-dropdown',
                                     children=[
                                         dcc.Dropdown(id='stockselector', options=get_options(list(df.columns)),
                                                      multi=True, value=['Kathmandu'],
                                                      # style={'backgroundColor': '#FFFFFF',
                                                      #        'color': '#FFFFFF'
                                                      #        },
                                                      ),
                                            ],
                                     # style={'color': '#FFFFFF'}
                                        )
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-white',
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar':False}, animate=True,),

                             ])
                              ])
        ]

)




# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_graph(selected_dropdown_value):
    trace1 = []
    df_sub = df
    for stock in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub.index,
                                 y=df_sub[stock],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#DC143C", '#FF4F00', '#0091D5', '#B3C100', '#C724B1', '#488A99'],
                  template='plotly_white',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'ACTIVE CASES BY DISTRICT',
                         'font': {'color': '#1C4E80'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()],
                         'title' : 'Date',
                         'linecolor' : "#1C4E80",
                         'zeroline': False},
                  yaxis={'title' : 'Confirmed Cases',
                          'linecolor' : "#1C4E80",
                          'zeroline': False},

                  xaxis_showgrid=False,
                  yaxis_showgrid=False,
                  font_color="#1C4E80"
              ),

              }

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)


