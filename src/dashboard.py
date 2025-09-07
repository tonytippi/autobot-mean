import os, time
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Mean‑RSI Signals", layout="wide")
st.title("📈 Mean‑RSI Signal Dashboard")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/signals.db")
engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=15)
def load_signals():
    try:
        df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 500", engine)
        # convert to pandas datetime (ensure timezone aware strings are parsed)
        for c in ["bar_open_time","bar_close_time","created_at"]:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c])
        return df
    except Exception as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()

df = load_signals()
if df.empty:
    st.info("No signals yet. Wait for the bot to emit signals.")
    st.stop()

# Filters
cols = st.columns(4)
symbols = sorted(df["symbol"].unique().tolist())
intervals = sorted(df["interval"].unique().tolist())
sym = cols[0].selectbox("Symbol", options=["All"]+symbols, index=0)
tf  = cols[1].selectbox("Timeframe", options=["All"]+intervals, index=0)
n   = cols[2].slider("Rows", min_value=20, max_value=500, value=200, step=10)
autorefresh = cols[3].checkbox("Auto refresh (15s)")

f = df.copy()
if sym != "All": f = f[f["symbol"]==sym]
if tf != "All": f = f[f["interval"]==tf]
f = f.head(n)

st.subheader("Latest Signals")
st.dataframe(f[["id","symbol","interval","side","close","rsi","sma20","thr","atr14","suggested_tp","suggested_sl","bar_close_time","created_at"]])

# Quick chart: close vs sma20 of the most recent symbol/timeframe
if not f.empty:
    last_row = f.iloc[0]
    st.subheader(f"Last signal detail — {last_row['symbol']} {last_row['interval']}")
    st.json({
        "close": float(last_row["close"]),
        "rsi": float(last_row["rsi"]),
        "sma20": float(last_row["sma20"]),
        "thr": float(last_row["thr"]),
        "atr14": float(last_row["atr14"]),
        "tp": float(last_row["suggested_tp"]),
        "sl": float(last_row["suggested_sl"]),
        "bar_close_time": str(last_row["bar_close_time"]),
    })

if autorefresh:
    st.experimental_rerun()
