import streamlit as st
import pandas as pd
import yfinance as yf
import locale
import plotly.express as px

Caixa = 5900
dolar = yf.download('BRL=X',period="5d",interval="1d")

print(dolar[-1])