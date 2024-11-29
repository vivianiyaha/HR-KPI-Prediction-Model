import streamlit as st
import pandas as pd
import numpy as np
from pybitget import Client
import time
import ta

# Initialize Bitget Client
api_key = st.secrets["api-key"]
api_secret = st.secrets["secret-key"]
api_passphrase = st.secrets["api-passphrase"]
client = Client(api_key, api_secret, passphrase=api_passphrase)

# Streamlit UI
st.title("Crypto Scalping Bot - Bitget Futures")
st.write("Trading Bot with 1-Minute EMA/RSI Strategy for Multiple Pairs")

# Bot control buttons
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

def start_bot():
    st.session_state.bot_running = True
    st.write("Bot started!")

def stop_bot():
    st.session_state.bot_running = False
    st.write("Bot stopped!")

st.button("Start Bot", on_click=start_bot)
st.button("Stop Bot", on_click=stop_bot)

# Strategy parameters
EMA_SHORT = 50
EMA_LONG = 200
RSI_PERIOD = 14
TAKE_PROFIT = 0.01  # 1%
STOP_LOSS = 0.005   # 0.5%
LEVERAGE = 5
TRADE_AMOUNT = 0.001  # Adjust based on your risk management

# Pairs to trade
PAIRS = ['XRPUSDT_UMCBL', 'ZRCUSDT_UMCBL', 'XUSDT_UMCBL', 'SHIBUSDT_UMCBL', 'MEMEFIUSDT_UMCBL']

# Trading functions
def get_historical_data(symbol):
    # Fetch historical data (1-min candles)
    response = client.mix_get_kline(symbol=symbol, granularity='60', limit=200)
    df = pd.DataFrame(response['data'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def calculate_indicators(df):
    df['ema_short'] = ta.trend.ema_indicator(df['close'], window=EMA_SHORT)
    df['ema_long'] = ta.trend.ema_indicator(df['close'], window=EMA_LONG)
    df['rsi'] = ta.momentum.rsi(df['close'], window=RSI_PERIOD)
    return df

def place_order(symbol, side):
    client.mix_set_leverage(symbol=symbol, leverage=LEVERAGE)
    order = client.mix_place_order(symbol=symbol, side=side, orderType="market", size=TRADE_AMOUNT)
    return order

def manage_trade(symbol):
    df = get_historical_data(symbol)
    df = calculate_indicators(df)
    last_row = df.iloc[-1]

    if st.session_state.bot_running:
        # Long condition
        if last_row['ema_short'] > last_row['ema_long'] and 30 < last_row['rsi'] < 70:
            st.write(f"Placing LONG trade for {symbol}...")
            place_order(symbol, "open_long")

        # Short condition
        elif last_row['ema_short'] < last_row['ema_long'] and 30 < last_row['rsi'] < 70:
            st.write(f"Placing SHORT trade for {symbol}...")
            place_order(symbol, "open_short")

        time.sleep(1)  # 1-second delay between checks to avoid rate limits

# Run the bot continuously when started
while st.session_state.bot_running:
    for pair in PAIRS:
        manage_trade(pair)
    time.sleep(60)  # Run every minute
