import numpy as np
import pandas as pd

def calculate_indicators(df):
    df = df.copy()
    close = pd.to_numeric(df[" close"], errors="coerce") if " close" in df else pd.to_numeric(df["close"], errors="coerce")
    volume_col = " volume" if " volume" in df else "volume"
    high_col = " high" if " high" in df else "high"
    low_col = " low" if " low" in df else "low"
    volume = pd.to_numeric(df[volume_col], errors="coerce")
    high = pd.to_numeric(df[high_col], errors="coerce")
    low = pd.to_numeric(df[low_col], errors="coerce")
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    ema12, ema26 = close.ewm(span=12, adjust=False).mean(), close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    typical = (high + low + close) / 3
    money_flow = typical * volume
    pos = money_flow.where(typical.diff() > 0, 0).rolling(14).sum()
    neg = money_flow.where(typical.diff() < 0, 0).rolling(14).sum()
    mfi = 100 - 100 / (1 + pos / neg.replace(0, np.nan))
    out = {
        "close": float(close.iloc[-1]), "rsi": float(rsi.iloc[-1]),
        "macd_hist": float((macd-signal).iloc[-1]),
        "ema20": float(close.ewm(span=20, adjust=False).mean().iloc[-1]),
        "ema50": float(close.ewm(span=50, adjust=False).mean().iloc[-1]),
        "sma200": float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else np.nan,
        "volume_ratio": float(volume.iloc[-1] / volume.tail(20).mean()),
        "mfi": float(mfi.iloc[-1]) if pd.notna(mfi.iloc[-1]) else 50.0,
        "return5": float(close.pct_change(5).iloc[-1] * 100),
        "return20": float(close.pct_change(20).iloc[-1] * 100),
    }
    return out
