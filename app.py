from flask import Flask, request
from flask import render_template
import requests 
import pandas as pd
import numpy as np
import datetime
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html, components
import os

if not os.getenv('STOCKS_API_KEY'):
    raise Exception('Stocks API key not found')

def data_for_requested_timeperiod(df, start_date, end_date):
    temp_df = df.drop(['1. open', '4. close', '5. volume'], axis=1)
    temp_df = temp_df[(df.index>= start_date) & (df.index<= end_date)]
    return temp_df

def plotting(df):
    p = figure(plot_width=800, plot_height=400, x_axis_type="datetime")
    p.vbar(x = df.index, width=1, bottom = df['3. low'], top=df['2. high'], color="firebrick")
    script, div = components(p)
    return script, div

app = Flask(__name__)
@app.route('/')
def index_mandana():
    symbol = request.args.get('symbol')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    if not symbol or not start_date or not end_date:
        return render_template('index.html')
    r = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={os.getenv("STOCKS_API_KEY")}')
    all_data = r.json()
    df = pd.DataFrame(all_data['Time Series (Daily)']).transpose()
    df.index = pd.to_datetime(df.index)
    selected_df = data_for_requested_timeperiod(df, start_date, end_date)
    script, div = plotting(selected_df)
    return render_template("index.html", resources=CDN.render(), plot_div = div, plot_script = script) 
if __name__ == "__main__":
    app.run(debug=True)