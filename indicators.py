import numpy as np
import pandas as pd


def calculate_indicators(df):
    # pytse-client normally returns date/open/high/low/close/volume.
    # Strip accidental whitespace so both column variants are supported.
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]

    required = {"close", "high", "low", "volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing market-data columns: {', '.join(sorted(missing))}")

    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")

    valid = close.notna() & high.notna() & low.notna() & volume.notna()
    close, high, low, volume = close[valid], high[valid], low[valid], volume[valid]
    if len(close) < 30:
        raise ValueError("Not enough valid price history")

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    typical = (high + low + close) / 3
    money_flow = typical * volume
    positive_flow = money_flow.where(typical.diff() > 0, 0).rolling(14).sum()
    negative_flow = money_flow.where(typical.diff() < 0, 0).rolling(14).sum()
    mfi = 100 - 100 / (1 + positive_flow / negative_flow.replace(0, np.nan))

    average_volume = volume.tail(20).mean()
    volume_ratio = float(volume.iloc[-1] / average_volume) if average_volume and average_volume > 0 else 0.0

    return {
        "close": float(close.iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
        "macd_hist": float((macd - signal).iloc[-1]),
        "ema20": float(close.ewm(span=20, adjust=False).mean().iloc[-1]),
        "ema50": float(close.ewm(span=50, adjust=False).mean().iloc[-1]),
        "sma200": float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else np.nan,
        "volume_ratio": volume_ratio,
        "mfi": float(mfi.iloc[-1]) if pd.notna(mfi.iloc[-1]) else 50.0,
        "return5": float(close.pct_change(5).iloc[-1] * 100),
        "return20": float(close.pct_change(20).iloc[-1] * 100),
    }
