import streamlit as st

from src.cart_view import render_cart
from src.styles import apply_styles

st.set_page_config(page_title="Shopping Cart", page_icon="SC", layout="wide")
apply_styles()
render_cart()
