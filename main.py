# Test Project To Learn About StreamLit
# Time and Date Module Imports
import time
from datetime import date
# Data Wrangling Module Imports
import csv
import pandas as pd
# os Imports
import os
# Streamlit module import
import streamlit as st
# API Module Imports
import requests
from io import StringIO
from stocksymbol import StockSymbol
# Plotly Module Imports
import plotly.express as px

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', None)

# Streamlit Code
st.markdown('''         ## 💵 Stock Market Data & Analysis📈''')
st.sidebar.header('Enter The Following Details')
dt1 = st.sidebar.date_input('Start Date')
dt2 = st.sidebar.date_input('End Date')
unix_time1 = time.mktime(dt1.timetuple())
unix_time1 = int(unix_time1)
unix_time2 = time.mktime(dt2.timetuple())
unix_time2 = int(unix_time2)

ss = StockSymbol(st.secrets['api_key'])
symbol_list_us = ss.get_symbol_list(market='US')

symbol_list_steamlit = []
for i in range(len(symbol_list_us)):
    symbol_list_steamlit.append(symbol_list_us[i]['symbol'])

stock_symbol = st.sidebar.selectbox('Select The Stock Symbol', symbol_list_steamlit)

def api_call(user_agent, unix_time1, unix_time2, stock_symbol):
    dt = date.today()
    dt = time.mktime(dt.timetuple())
    dt = int(dt)

    if unix_time1 == unix_time2:
        url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols='
        headers = {'user-agent': user_agent}
        response = requests.get(url + stock_symbol, headers=headers)
        web_data = response.json()
        pd_stock_interim = pd.json_normalize(web_data['quoteResponse']['result'])
        pd_stock_output = pd_stock_interim.filter(items=['longName','regularMarketOpen','regularMarketPrice',
                                                         'regularMarketDayHigh','regularMarketDayRange','regularMarketDayLow',
                                                         'fiftyTwoWeekHigh','fiftyTwoWeekLow','regularMarketVolume',
                                                         'trailingPE','averageDailyVolume3Month'])
        pd_stock_output = pd_stock_output.rename(columns={'longName':'Stock_Name','regularMarketOpen':'Open',
                                                          'regularMarketPrice':'Market_Price','regularMarketDayHigh':'Market_High',
                                                          'regularMarketDayRange':'Market_Day_Range',
                                                          'regularMarketDayLow':'Market_Low',
                                                          'fiftyTwoWeekHigh':'52W H','fiftyTwoWeekLow': '52W L',
                                                          'regularMarketVolume':'Vol',
                                                          'trailingPE':'PE','averageDailyVolume3Month':'Avg Vol'})
        col1, col2, col3 = st.columns(3)
        col1.metric('Open', pd_stock_output['Open'])
        col3.metric('Market Price', pd_stock_output['Market_Price'])
        col1, col2, col3 = st.columns(3)
        col1.metric('Market High', pd_stock_output['Market_High'])
        col2.metric('Market Low', pd_stock_output['Market_Low'])
        col3.metric('52W H', pd_stock_output['52W H'])
        col1, col2, col3 = st.columns(3)
        col1.metric('52W L', pd_stock_output['52W L'])
        col2.metric('Vol', pd_stock_output['Vol'])
        col3.metric('Avg Vol', pd_stock_output['Avg Vol'])
        st.metric('Market Day Range', (str(pd_stock_output['Market_Day_Range'])[5:]).
                  rstrip('Name: Market_Day_Range, dtype: object'))
    else:
        url = 'https://query1.finance.yahoo.com/v7/finance/download/'
        headers = {'user-agent': user_agent}
        params = {'period1': unix_time1,
                  'period2': unix_time2,
                  'interval': '1d',
                  'events': 'history'}

        response = requests.get(url + stock_symbol, headers=headers, params = params)
        web_data = StringIO(response.text)
        pd_stock_interim = csv.reader(web_data)
        pd_stock_inter = pd.DataFrame(pd_stock_interim)
        new_header = pd_stock_inter.iloc[0]
        pd_stock_inter.columns = new_header
        st.dataframe(pd_stock_inter[1:])
        pd_stock_inter = pd_stock_inter.drop([0])

        pd_stock_inter['Close'] = pd_stock_inter['Close'].astype(str).astype(float)
        return pd_stock_inter

def plot_graph(pd_stock_inter, unix_time1, unix_time2):
    dt = date.today()
    dt = time.mktime(dt.timetuple())
    dt = int(dt)
    if unix_time1 == unix_time2:
        pass
    else:
        fig = px.line(data_frame=pd_stock_inter, x='Date', y='Close',
                      labels={'Date':'Stock By Date', 'Close':'Stock Value'})
        st.markdown('''#### Data Trend By Date''')
        st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button('Submit'):
    pd_stock_inter = api_call(st.secrets['user_agent'], unix_time1, unix_time2, stock_symbol)
    plot_graph(pd_stock_inter, unix_time1, unix_time2)
