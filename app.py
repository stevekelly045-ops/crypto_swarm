import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Crypto Swarm Dashboard", page_icon="🐝", layout="wide")

st.title("🐝 Autonomous Crypto Swarm Dashboard")
st.markdown("Monitor your multi-agent trading swarm's real-time decisions, signals, and simulated performance.")

# Sidebar Controls
st.sidebar.header("Swarm Controls")
st.sidebar.info("Status: Active / Monitoring BTC, ETH, SOL")

# Load Trade History CSV
history_file = "trade_history.csv"

if os.path.exists(history_file):
    df = pd.read_csv(history_file)
    
    # Metrics Row
    total_signals = len(df)
    buy_signals = len(df[df['signal'] == 'BUY'])
    sell_signals = len(df[df['signal'] == 'SELL'])
    hold_signals = len(df[df['signal'] == 'HOLD'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Evaluations", total_signals)
    col2.metric("🟢 Buy Signals", buy_signals)
    col3.metric("🔴 Sell Signals", sell_signals)
    col4.metric("⚪ Hold Signals", hold_signals)
    
    st.divider()
    
    # Data Table View
    st.subheader("📋 Live Swarm Decision Log")
    st.dataframe(df.tail(20).sort_values(by="timestamp", ascending=False), width='stretch')
    
    # Simple Chart of Prices over time
    if not df.empty:
        st.subheader("📈 Asset Price Tracking")
        selected_coin = st.selectbox("Select Coin to View:", df['symbol'].unique())
        coin_data = df[df['symbol'] == selected_coin]
        if not coin_data.empty:
            st.line_chart(coin_data.set_index('timestamp')['price'])
else:
    st.warning("⚠️ No `trade_history.csv` file found yet! Run your `crypto_swarm.py` script first to generate trade logs.")