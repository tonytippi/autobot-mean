import requests
import pandas as pd

BASE = "https://data-api.binance.vision"
KLINES = "/api/v3/klines"

def get_klines(symbol: str, interval: str, limit: int = 300) -> pd.DataFrame:
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    r = requests.get(BASE + KLINES, params=params, timeout=15)
    r.raise_for_status()
    cols = ["open_time","open","high","low","close","volume","close_time","qav","trades","taker_base","taker_quote","ignore"]
    df = pd.DataFrame(r.json(), columns=cols)
    for c in ["open","high","low","close"]:
        df[c] = df[c].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    return df[["open_time","open","high","low","close","close_time"]]
