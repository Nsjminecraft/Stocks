from flask import Flask, render_template, request
import requests
import finnhub
from yahoo_fin import stock_info
from datetime import datetime

app = Flask(__name__)

# Replace with your actual API keys and API URLs
ALPHA_VANTAGE_API_KEY = 'YOUR_KEY_HERE'
ALPHA_VANTAGE_API_URL = 'https://www.alphavantage.co/query'
FINNHUB_API_KEY = 'cqt50c1r01qvdch2pfpgcqt50c1r01qvdch2pfq0'
FINNHUB_CLIENT = finnhub.Client(api_key=FINNHUB_API_KEY)

def get_alpha_vantage_stock(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '5min',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(ALPHA_VANTAGE_API_URL, params=params)
    data = response.json()
    time_series = data.get('Time Series (5min)', {})
    if not time_series:
        return {'symbol': symbol, 'price': 'N/A', 'time': 'N/A', 'source': 'Alpha Vantage'}
    latest_time = sorted(time_series.keys())[0]
    latest_data = time_series[latest_time]
    return {
        'symbol': symbol,
        'price': latest_data['4. close'],
        'time': latest_time,
        'source': 'Alpha Vantage'
    }

def get_yahoo_finance_stock(symbol):
    try:
        price = stock_info.get_live_price(symbol)
        return {
            'symbol': symbol,
            'price': price,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Static timestamp
            'source': 'Yahoo Finance'
        }
    except Exception as e:
        print(f"Error fetching Yahoo Finance data: {e}")
        return {
            'symbol': symbol,
            'price': 'N/A',
            'time': 'N/A',
            'source': 'Yahoo Finance'
        }

def get_finnhub_stock(symbol):
    try:
        quote = FINNHUB_CLIENT.quote(symbol)
        return {
            'symbol': symbol,
            'price': quote['c'],  # Current price
            #'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Static timestamp
            'time' : quote['t'],
            'source': 'Finnhub'
        }
    except Exception as e:
        print(f"Error fetching Finnhub data: {e}")
        return {
            'symbol': symbol,
            'price': 'N/A',
            'time': 'N/A',
            'source': 'Finnhub'
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    symbol = request.form.get('symbol', '') or request.form.get('predefined-symbols', '') or request.form.get('symbol-name', '')
    stocks = [
        get_alpha_vantage_stock(symbol),
        get_yahoo_finance_stock(symbol),
        get_finnhub_stock(symbol)
    ]
    return render_template('index.html', stocks=stocks, selected_symbol=symbol, symbol_name=symbol)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
