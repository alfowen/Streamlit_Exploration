# Test Project To Learn About StreamLit
# Time and Date Module Imports
import time
from datetime import date
# Data Wrangling Module Imports
import csv
import pandas as pd
# os Imports
import os
from dotenv import load_dotenv, find_dotenv
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

# Environment Parameters
load_dotenv(find_dotenv())
api_key = os.environ.get('API_KEY')
user_agent = os.environ.get('USER_AGENT')

# Streamlit Code
st.markdown('''         ## 💵 Stock Market Data & Analysis📈''')
st.sidebar.header('Enter The Following Details')
dt1 = st.sidebar.date_input('Start Date')
dt2 = st.sidebar.date_input('End Date')
unix_time1 = time.mktime(dt1.timetuple())
unix_time1 = int(unix_time1)
unix_time2 = time.mktime(dt2.timetuple())
unix_time2 = int(unix_time2)

ss = StockSymbol(api_key)
symbol_list_us = ss.get_symbol_list(market='US')

symbol_list_steamlit = []
for i in range(len(symbol_list_us)):
    symbol_list_steamlit.append(symbol_list_us[i]['symbol'])

stock_symbol = st.sidebar.selectbox('Select The Stock Symbol', symbol_list_steamlit)

def api_call(user_agent, unix_time1, unix_time2, stock_symbol):
    dt = date.today()
    dt = time.mktime(dt.timetuple())
    dt = int(dt)

    if unix_time1 == unix_time2 and unix_time1 == dt:
        url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols='
        headers = {'user-agent': user_agent}
        response = requests.get(url + stock_symbol, headers=headers)
        web_data = response.json()
        pd_stock_interim = pd.json_normalize(web_data['quoteResponse']['result'])
        st.table(pd_stock_interim)
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
    if unix_time1 == unix_time2 and unix_time1 == dt:
        pass
    else:
        fig = px.line(data_frame=pd_stock_inter, x='Date', y='Close',
                      labels={'Date':'Stock By Date', 'Close':'Stock Value'})
        st.markdown('''#### Data Trend By Date''')
        st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button('Submit'):
    pd_stock_inter = api_call(user_agent, unix_time1, unix_time2, stock_symbol)
    plot_graph(pd_stock_inter, unix_time1, unix_time2)
