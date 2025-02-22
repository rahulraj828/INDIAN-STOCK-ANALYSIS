import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from nsetools import Nse
import requests
from bs4 import BeautifulSoup

nse = Nse()

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def get_stock_data(symbol, exchange="US"):
    """Fetch stock data from Yahoo Finance or NSE"""
    try:
        if exchange == "NSE":
            return get_nse_data(symbol)
        else:
            return get_yf_data(symbol)
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def get_yf_data(symbol):
    """Fetch data from Yahoo Finance"""
    stock = yf.Ticker(symbol)
    info = stock.info
    hist = stock.history(period="1y")

    return {
        'info': info,
        'history': hist,
        'valid': True,
        'exchange': 'US'
    }

def get_nse_data(symbol):
    """Fetch data from NSE"""
    try:
        # Get quote from NSE
        quote = nse.get_quote(symbol)

        # Create historical data structure
        today = datetime.now()
        dates = pd.date_range(end=today, periods=30, freq='D')

        # Get historical data from NSE (last 30 days)
        hist_data = pd.DataFrame({
            'Date': dates,
            'Open': [quote['open']] * 30,
            'High': [quote['dayHigh']] * 30,
            'Low': [quote['dayLow']] * 30,
            'Close': [quote['lastPrice']] * 30,
            'Volume': [quote['totalTradedVolume']] * 30
        })
        hist_data.set_index('Date', inplace=True)

        # Format NSE data to match YF structure
        info = {
            'longName': quote['companyName'],
            'currentPrice': quote['lastPrice'],
            'previousClose': quote['previousClose'],
            'regularMarketChangePercent': ((quote['lastPrice'] - quote['previousClose']) / quote['previousClose']) * 100,
            'marketCap': quote['marketCap'],
            'volume': quote['totalTradedVolume'],
            'fiftyTwoWeekHigh': quote['high52'],
            'fiftyTwoWeekLow': quote['low52'],
            'trailingPE': quote.get('pe', None),
            'dividendYield': None  # NSE doesn't provide this directly
        }

        return {
            'info': info,
            'history': hist_data,
            'valid': True,
            'exchange': 'NSE'
        }
    except Exception as e:
        raise Exception(f"Error fetching NSE data: {str(e)}")

def format_large_number(num):
    """Format large numbers with K, M, B suffixes"""
    if num is None:
        return "N/A"

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])

def prepare_metrics_data(info):
    """Prepare metrics data for display"""
    metrics = {
        'Market Cap': format_large_number(info.get('marketCap')),
        'PE Ratio': f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",
        'Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A",
        '52 Week High': f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}" if info.get('exchange') == 'NSE' else f"${info.get('fiftyTwoWeekHigh', 'N/A')}",
        '52 Week Low': f"₹{info.get('fiftyTwoWeekLow', 'N/A')}" if info.get('exchange') == 'NSE' else f"${info.get('fiftyTwoWeekLow', 'N/A')}",
        'Volume': format_large_number(info.get('volume')),
    }
    return metrics

def prepare_financial_data(info):
    """Prepare financial data for the table"""
    currency_symbol = '₹' if info.get('exchange') == 'NSE' else '$'
    financial_data = {
        'Revenue': format_large_number(info.get('totalRevenue')),
        'Gross Profit': format_large_number(info.get('grossProfits')),
        'Operating Margin': f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') else "N/A",
        'Return on Equity': f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else "N/A",
        'Debt to Equity': f"{info.get('debtToEquity', 'N/A'):.2f}" if info.get('debtToEquity') else "N/A",
        'Current Ratio': f"{info.get('currentRatio', 'N/A'):.2f}" if info.get('currentRatio') else "N/A",
    }
    return pd.DataFrame(list(financial_data.items()), columns=['Metric', 'Value'])