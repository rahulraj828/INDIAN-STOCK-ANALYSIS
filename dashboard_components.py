import streamlit as st
from streamlit_elements import elements, dashboard, mui, html
from contextlib import contextmanager
import json

# Default layout configuration
DEFAULT_LAYOUT = [
    # Saving layout as a list of dictionaries for easy modification
    {
        "key": "price_chart",
        "x": 0, "y": 0,
        "width": 12, "height": 3,
        "title": "Stock Price Chart"
    },
    {
        "key": "market_metrics",
        "x": 0, "y": 3,
        "width": 6, "height": 2,
        "title": "Market Metrics"
    },
    {
        "key": "financial_info",
        "x": 6, "y": 3,
        "width": 6, "height": 2,
        "title": "Financial Information"
    }
]

def initialize_layout():
    """Initialize dashboard layout in session state"""
    if "dashboard_layout" not in st.session_state:
        st.session_state.dashboard_layout = DEFAULT_LAYOUT

def save_layout(layout):
    """Save current layout to session state"""
    st.session_state.dashboard_layout = layout

def load_layout():
    """Load layout from session state"""
    return st.session_state.dashboard_layout

@contextmanager
def drag_container():
    """Create a draggable container context"""
    with elements("dashboard"):
        with dashboard.Grid(load_layout(), onChange=save_layout):
            yield

def create_card(title, content):
    """Create a draggable card with title and content"""
    return mui.Card(
        children=[
            mui.CardHeader(title=title),
            mui.CardContent(children=content)
        ],
        sx={
            "height": "100%",
            "display": "flex",
            "flexDirection": "column"
        }
    )

def render_price_chart(fig):
    """Render price chart widget"""
    with drag_container():
        with dashboard.Item("price_chart"):
            create_card(
                "Stock Price Chart",
                html.Div(fig)
            )

def render_market_metrics(metrics):
    """Render market metrics widget"""
    with drag_container():
        with dashboard.Item("market_metrics"):
            create_card(
                "Market Metrics",
                mui.Grid(
                    children=[
                        mui.Typography(f"{k}: {v}") 
                        for k, v in metrics.items()
                    ],
                    spacing=2,
                    container=True
                )
            )

def render_financial_info(financial_df):
    """Render financial information widget"""
    with drag_container():
        with dashboard.Item("financial_info"):
            create_card(
                "Financial Information",
                mui.TableContainer(
                    children=[
                        mui.Table(
                            children=[
                                mui.TableHead(
                                    children=[
                                        mui.TableRow(
                                            children=[
                                                mui.TableCell(col) 
                                                for col in financial_df.columns
                                            ]
                                        )
                                    ]
                                ),
                                mui.TableBody(
                                    children=[
                                        mui.TableRow(
                                            children=[
                                                mui.TableCell(cell) 
                                                for cell in row
                                            ]
                                        ) for row in financial_df.values
                                    ]
                                )
                            ]
                        )
                    ]
                )
            )