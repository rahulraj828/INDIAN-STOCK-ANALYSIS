import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

from utils import get_stock_data, prepare_metrics_data, prepare_financial_data
from dashboard_components import (
    initialize_layout,
    render_price_chart,
    render_market_metrics,
    render_financial_info
)

def format_number(number):
    """Format large numbers with commas"""
    try:
        return "{:,}".format(int(number))
    except (ValueError, TypeError):
        return "N/A"

# Page configuration
st.set_page_config(
    page_title="Indian Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Apply custom styles
from styles import apply_custom_styles
apply_custom_styles()

# Initialize dashboard layout
initialize_layout()

# Header
st.title("📈 Indian Stock Market Analytics")
st.markdown("Get detailed financial information from NSE and BSE markets")

# Add a toggle for dashboard mode
dashboard_mode = st.sidebar.checkbox("Enable Drag & Drop Dashboard", value=False)

# Exchange selection
exchange = st.radio(
    "Select Exchange",
    ["NSE", "BSE"],
    horizontal=True,
    help="Choose NSE or BSE for Indian stocks"
)

# Stock symbol input
symbol_placeholder = "RELIANCE" if exchange == "NSE" else "TATAMOTORS"
symbol = st.text_input(f"Enter Stock Symbol (e.g., {symbol_placeholder})", "").upper()

if symbol:
    try:
        with st.spinner(f'Fetching data for {symbol} from {exchange}...'):
            # Fetch stock data
            data = get_stock_data(symbol, exchange)

            if data['valid']:
                info = data['info']
                history = data['history']

                # Display company name and current price
                st.markdown(f"### {info.get('longName', symbol)}")

                if not dashboard_mode:
                    # Regular mode display
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Current Price",
                            f"₹{info.get('currentPrice', 'N/A')}",
                            f"{info.get('regularMarketChangePercent', 0):.2f}%"
                        )

                    with col2:
                        st.metric(
                            "Previous Close",
                            f"₹{info.get('previousClose', 'N/A')}"
                        )

                    with col3:
                        st.metric(
                            "Today's Volume",
                            format_number(info.get('volume', 'N/A'))
                        )

                # Prepare visualization data
                if not history.empty and all(col in history.columns for col in ['Open', 'High', 'Low', 'Close']):
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
                        yaxis_title="Price (₹)",
                        height=500,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )

                    # Prepare other data
                    metrics = prepare_metrics_data(info)
                    financial_df = prepare_financial_data(info)

                    if dashboard_mode:
                        # Render draggable dashboard
                        render_price_chart(fig)
                        render_market_metrics(metrics)
                        render_financial_info(financial_df)
                    else:
                        # Regular display
                        st.plotly_chart(fig, use_container_width=True)

                        st.subheader("Key Market Metrics")
                        cols = st.columns(3)
                        for i, (metric, value) in enumerate(metrics.items()):
                            with cols[i % 3]:
                                st.markdown(f"""
                                    <div class="metric-card">
                                        <h4>{metric}</h4>
                                        <p style="font-size: 20px;">{value}</p>
                                    </div>
                                """, unsafe_allow_html=True)

                        st.subheader("Financial Information")
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
                    st.warning("Historical data is not available for this stock.")
            else:
                st.error(f"Error fetching data for {symbol}. Please check the symbol and try again.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("👆 Enter a stock symbol above to get started!")