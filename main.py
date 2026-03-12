import requests
import yfinance as yf
import pandas as pd
import numpy as np
import os

# =========================
# LINE設定
# =========================

LINE_TOKEN = os.environ["LINE_TOKEN"]

def send_line(msg):

    url = "https://api.line.me/v2/bot/message/broadcast"

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messages":[
            {"type":"text","text":msg}
        ]
    }

    requests.post(url, headers=headers, json=data)


# =========================
# データ取得
# =========================

start = "2015-01-01"

soxl = yf.download("SOXL", start=start)
qqq  = yf.download("QQQ", start=start)
vix  = yf.download("^VIX", start=start)

soxl = soxl.droplevel(1, axis=1)
qqq  = qqq.droplevel(1, axis=1)
vix  = vix.droplevel(1, axis=1)

df = pd.DataFrame(index=soxl.index)

df["close"] = soxl["Close"]
df["qqq"] = qqq["Close"]
df["vix"] = vix["Close"]

# =========================
# RSI2
# =========================

delta = df["close"].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(2).mean()
avg_loss = loss.rolling(2).mean()

rs = avg_gain / avg_loss

df["rsi2"] = 100 - (100 / (1 + rs))

# =========================
# MA
# =========================

df["qqq_ma150"] = df["qqq"].rolling(150).mean()
df["qqq_ma200"] = df["qqq"].rolling(200).mean()

# =========================
# signal
# =========================

df["sig_soxl"] = (
    (df["vix"] >= 20) &
    (df["rsi2"] < 6) &
    (df["qqq"] > df["qqq_ma150"])
)

# =========================
# 最新判定
# =========================

row = df.iloc[-1]

if row["sig_soxl"]:
    pos = "SOXL"
elif row["qqq"] > row["qqq_ma200"]:
    pos = "QQQ"
else:
    pos = "CASH"


msg = f"""
SOXL Strategy

Date: {df.index[-1].date()}

SOXL RSI2: {row["rsi2"]:.2f}
VIX: {row["vix"]:.2f}
QQQ vs150MA: {(row["qqq"]/row["qqq_ma150"]-1)*100:.2f}%

Signal: {pos}
"""

send_line(msg)

print(msg)
