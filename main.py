import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

from utils import get_stock_data, prepare_metrics_data, prepare_financial_data
from styles import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Apply custom styles
apply_custom_styles()

# Header
st.title("📈 Stock Analytics Dashboard")
st.markdown("Enter a stock symbol to view detailed financial information and analytics.")

# Stock symbol input
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL)", "").upper()

if symbol:
    # Fetch stock data
    data = get_stock_data(symbol)
    
    if data['valid']:
        info = data['info']
        history = data['history']
        
        # Display company name and current price
        st.markdown(f"### {info.get('longName', symbol)}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Current Price",
                f"${info.get('currentPrice', 'N/A')}",
                f"{info.get('regularMarketChangePercent', 0):.2f}%"
            )
        
        with col2:
            st.metric(
                "Previous Close",
                f"${info.get('previousClose', 'N/A')}"
            )
        
        # Stock price chart
        st.subheader("Stock Price History")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=history.index,
            open=history['Open'],
            high=history['High'],
            low=history['Low'],
            close=history['Close'],
            name='Price'
        ))
        
        fig.update_layout(
            template='plotly_white',
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        st.subheader("Key Metrics")
        metrics = prepare_metrics_data(info)
        cols = st.columns(3)
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="metric-card">
                        <h4>{metric}</h4>
                        <p style="font-size: 20px;">{value}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Financial data table
        st.subheader("Financial Information")
        financial_df = prepare_financial_data(info)
        st.table(financial_df)
        
        # Download button for CSV
        csv = financial_df.to_csv(index=False)
        st.download_button(
            label="Download Financial Data (CSV)",
            data=csv,
            file_name=f"{symbol}_financial_data.csv",
            mime="text/csv"
        )
        
    else:
        st.error(f"Error fetching data for {symbol}. Please check the symbol and try again.")
else:
    st.info("👆 Enter a stock symbol above to get started!")
