from dataclasses import dataclass
import pandas as pd
from indicators import rsi_wilder, atr, sma, stdev

@dataclass
class MeanRSIParams:
    k: float = 1.0
    rsi_min: float = 30.0
    sl_atr_mult: float = 1.5

def last_closed_index(kl: pd.DataFrame, now_ts) -> int:
    last_close_time = kl["close_time"].iloc[-1]
    return -2 if now_ts < last_close_time else -1

def generate_signal(kl: pd.DataFrame, params: MeanRSIParams, now_ts) -> dict | None:
    if len(kl) < 60:
        return None
    idx = last_closed_index(kl, now_ts)
    c = kl["close"].copy()
    h = kl["high"].copy()
    l = kl["low"].copy()
    sma20 = sma(c, 20)
    sd20 = stdev(c, 20)
    rsi14 = rsi_wilder(c, 14)
    atr14 = atr(h, l, c, 14)
    thr = sma20 - params.k * sd20
    close = c.iloc[idx]
    rsi_val = rsi14.iloc[idx]
    thr_val = thr.iloc[idx]
    sma_val = sma20.iloc[idx]
    atr_val = atr14.iloc[idx]
    if pd.isna(thr_val) or pd.isna(rsi_val) or pd.isna(sma_val) or pd.isna(atr_val):
        return None
    if (close < thr_val) and (rsi_val > params.rsi_min):
        sl = close - params.sl_atr_mult * atr_val
        return {
            "side": "BUY",
            "close": float(close),
            "rsi": float(rsi_val),
            "sma20": float(sma_val),
            "thr": float(thr_val),
            "atr14": float(atr_val),
            "suggested_tp": float(sma_val),
            "suggested_sl": float(sl),
            "signal_bar_open_time": kl["open_time"].iloc[idx].isoformat(),
            "signal_bar_close_time": kl["close_time"].iloc[idx].isoformat(),
            "entry_note": "Entry at next bar open (signal on closed candle)"
        }
    return None
