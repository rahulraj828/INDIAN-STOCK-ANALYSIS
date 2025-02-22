import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from nsetools import Nse
import requests
from bs4 import BeautifulSoup
import trafilatura
import json

nse = Nse()

def get_nse_quote(symbol):
    """Get real-time NSE quote data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # First try NSE India website
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass

    try:
        # Fallback to nsetools
        quote = nse.get_quote(symbol)
        if quote:
            return quote
    except:
        pass

    # Final fallback to Yahoo Finance
    try:
        stock = yf.Ticker(f"{symbol}.NS")
        info = stock.info
        if info:
            return {
                'lastPrice': info.get('currentPrice'),
                'open': info.get('open'),
                'dayHigh': info.get('dayHigh'),
                'dayLow': info.get('dayLow'),
                'previousClose': info.get('previousClose'),
                'totalTradedVolume': info.get('volume'),
                'marketCap': info.get('marketCap'),
                'high52': info.get('fiftyTwoWeekHigh'),
                'low52': info.get('fiftyTwoWeekLow'),
                'companyName': info.get('longName'),
                'pe': info.get('trailingPE')
            }
    except:
        pass

    raise Exception(f"Unable to fetch data for {symbol}")

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
        # Get quote data
        quote = get_nse_quote(symbol)
        if not quote:
            raise Exception(f"No data found for symbol: {symbol}")

        # Fetch historical data from Yahoo Finance
        yf_symbol = f"{symbol}.NS"
        stock = yf.Ticker(yf_symbol)
        hist = stock.history(period="1y")

        # Format data
        info = {
            'longName': quote.get('companyName', symbol),
            'currentPrice': quote.get('lastPrice'),
            'previousClose': quote.get('previousClose'),
            'regularMarketChangePercent': ((quote.get('lastPrice', 0) - quote.get('previousClose', 0)) / quote.get('previousClose', 1)) * 100,
            'marketCap': quote.get('marketCap'),
            'volume': quote.get('totalTradedVolume'),
            'fiftyTwoWeekHigh': quote.get('high52'),
            'fiftyTwoWeekLow': quote.get('low52'),
            'trailingPE': quote.get('pe'),
            'dividendYield': None,
            'exchange': 'NSE'
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
    """Fetch data from BSE"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Try Yahoo Finance first
        yf_symbol = f"{symbol}.BO"
        stock = yf.Ticker(yf_symbol)
        info = stock.info
        hist = stock.history(period="1y")

        if not info:
            raise Exception("No data found")

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
        '52 Week High': f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}",
        '52 Week Low': f"₹{info.get('fiftyTwoWeekLow', 'N/A')}",
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