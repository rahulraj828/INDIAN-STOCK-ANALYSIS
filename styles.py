import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .stock-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .error-message {
            color: #dc3545;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8d7da;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
