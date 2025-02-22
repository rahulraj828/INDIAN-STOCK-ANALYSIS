# Indian Stock Market Analytics Dashboard

A comprehensive Streamlit-based stock data visualization tool focused on Indian stock markets (NSE and BSE), providing real-time data fetching and interactive analysis capabilities.

## Features

- Real-time stock data from NSE and BSE
- Interactive candlestick charts
- Key market metrics visualization
- Financial information display
- Drag-and-drop customizable dashboard
- CSV data export functionality

## Dependencies

The project requires the following Python packages:
- streamlit
- pandas
- yfinance
- plotly
- nsetools
- streamlit-elements
- beautifulsoup4
- requests
- trafilatura

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repository-url>
cd indian-stock-analytics
```

2. Install the required packages:
```bash
pip install streamlit pandas yfinance plotly nsetools streamlit-elements beautifulsoup4 requests trafilatura
```

3. Create a `.streamlit` folder and add `config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#262730"
font = "sans serif"
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run main.py
```

2. Access the dashboard in your web browser at `http://localhost:5000`

3. Enter a stock symbol (e.g., RELIANCE for NSE or TATAMOTORS for BSE)

4. Toggle between NSE and BSE exchanges

5. Enable the drag-and-drop dashboard mode using the sidebar checkbox

## Project Structure

- `main.py`: Main application file
- `utils.py`: Utility functions for data fetching and processing
- `styles.py`: Custom CSS styles
- `dashboard_components.py`: Drag-and-drop dashboard components

## GitHub Deployment Steps

1. Initialize Git repository (if not already done):
```bash
git init
```

2. Add your files:
```bash
git add .
```

3. Commit your changes:
```bash
git commit -m "Initial commit"
```

4. Create a new repository on GitHub

5. Link and push to your GitHub repository:
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## Note
This project is designed to work with Indian stock market data. Make sure you have proper internet connectivity to fetch real-time stock information.
