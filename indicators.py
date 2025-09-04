import pandas as pd

def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    roll_dn = down.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = roll_up / roll_dn
    rsi = 100 - (100/(1+rs))
    return rsi

def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    h_l = high - low
    h_pc = (high - close.shift()).abs()
    l_pc = (low - close.shift()).abs()
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()

def sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(length, min_periods=length).mean()

def stdev(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(length, min_periods=length).std()
