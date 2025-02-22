import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from nsetools import Nse
import requests
from bs4 import BeautifulSoup

nse = Nse()

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def get_stock_data(symbol, exchange="NSE"):
    """Fetch stock data from NSE or BSE"""
    try:
        # Clean up symbol
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')

        if exchange == "NSE":
            st.info(f"Fetching NSE data for {clean_symbol}...")
            return get_nse_data(clean_symbol)
        else:  # BSE
            st.info(f"Fetching BSE data for {clean_symbol}...")
            return get_bse_data(clean_symbol)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return {
            'valid': False,
            'error': str(e)
        }

def get_nse_data(symbol):
    """Fetch data from NSE"""
    try:
        # Verify symbol validity
        if not nse.is_valid_code(symbol):
            raise Exception(f"Invalid NSE symbol: {symbol}")

        # Get quote from NSE
        quote = nse.get_quote(symbol)
        if not quote:
            raise Exception(f"No data found for symbol: {symbol}")

        # Fetch historical data from Yahoo Finance (NSE)
        yf_symbol = f"{symbol}.NS"
        stock = yf.Ticker(yf_symbol)
        hist = stock.history(period="1y")

        # Format NSE data
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
            'dividendYield': None
        }

        return {
            'info': info,
            'history': hist,
            'valid': True,
            'exchange': 'NSE'
        }
    except Exception as e:
        raise Exception(f"NSE Data Error: {str(e)}")

def get_bse_data(symbol):
    """Fetch data from BSE via Yahoo Finance"""
    try:
        yf_symbol = f"{symbol}.BO"
        stock = yf.Ticker(yf_symbol)
        info = stock.info
        hist = stock.history(period="1y")

        return {
            'info': info,
            'history': hist,
            'valid': True,
            'exchange': 'BSE'
        }
    except Exception as e:
        raise Exception(f"BSE Data Error: {str(e)}")

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
        '52 Week High': f"{info.get('fiftyTwoWeekHigh', 'N/A')}",
        '52 Week Low': f"{info.get('fiftyTwoWeekLow', 'N/A')}",
        'Volume': format_large_number(info.get('volume')),
    }
    return metrics

def prepare_financial_data(info):
    """Prepare financial data for the table"""
    financial_data = {
        'Revenue': format_large_number(info.get('totalRevenue')),
        'Gross Profit': format_large_number(info.get('grossProfits')),
        'Operating Margin': f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') else "N/A",
        'Return on Equity': f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else "N/A",
        'Debt to Equity': f"{info.get('debtToEquity', 'N/A'):.2f}" if info.get('debtToEquity') else "N/A",
        'Current Ratio': f"{info.get('currentRatio', 'N/A'):.2f}" if info.get('currentRatio') else "N/A",
    }
    return pd.DataFrame(list(financial_data.items()), columns=['Metric', 'Value'])