import os
import json
import math
import requests
import subprocess
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import yfinance as yf


# =========================
# 設定
# =========================

START = "2015-01-01"
TP = 0.30
SL = -0.18
MAX_HOLD = 20

STATE_PATH = "state.json"

LINE_TOKEN = os.environ["LINE_TOKEN"]

# GitHub Actions で state.json を commit/push するために使う
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")  # 例: dachang82/soxl-line-bot


# =========================
# 共通関数
# =========================

def send_line(msg: str) -> None:
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messages": [
            {"type": "text", "text": msg}
        ]
    }
    r = requests.post(url, headers=headers, json=data, timeout=30)
    r.raise_for_status()


def safe_float(x):
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    try:
        return float(x)
    except Exception:
        return None


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {
            "position": "CASH",
            "entry_price": None,
            "entry_date": None,
            "hold_days": 0
        }
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    # 足りないキーがあっても落ちないように
    state.setdefault("position", "CASH")
    state.setdefault("entry_price", None)
    state.setdefault("entry_date", None)
    state.setdefault("hold_days", 0)
    return state


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def push_state_to_github() -> None:
    """
    state.json の更新を GitHub に commit / push する
    """
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print("Skip push_state_to_github: missing GITHUB_TOKEN or GITHUB_REPOSITORY")
        return

    repo_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"

    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", STATE_PATH], check=True)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False
    )

    # 差分がないなら何もしない
    if diff.returncode == 0:
        print("No state change to commit.")
        return

    subprocess.run(["git", "commit", "-m", "Update state.json"], check=True)
    subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    yfinance の列が MultiIndex のときでも普通の列にする
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def calc_rsi2(close: pd.Series) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(2).mean()
    avg_loss = loss.rolling(2).mean()

    rs = avg_gain / avg_loss
    rsi2 = 100 - (100 / (1 + rs))
    return rsi2


def fetch_data() -> pd.DataFrame:
    soxl = yf.download("SOXL", start=START, auto_adjust=False, progress=False)
    qqq = yf.download("QQQ", start=START, auto_adjust=False, progress=False)
    vix = yf.download("^VIX", start=START, auto_adjust=False, progress=False)

    soxl = flatten_columns(soxl)
    qqq = flatten_columns(qqq)
    vix = flatten_columns(vix)

    df = pd.DataFrame(index=soxl.index)

    df["open"] = soxl["Open"]
    df["high"] = soxl["High"]
    df["low"] = soxl["Low"]
    df["close"] = soxl["Close"]

    df["qqq"] = qqq["Close"]
    df["vix"] = vix["Close"]

    df["rsi2"] = calc_rsi2(df["close"])
    df["qqq_ma150"] = df["qqq"].rolling(150).mean()
    df["qqq_ma200"] = df["qqq"].rolling(200).mean()

    df = df.dropna().copy()

    df["sig_soxl"] = (
        (df["vix"] >= 20) &
        (df["rsi2"] < 6) &
        (df["qqq"] > df["qqq_ma150"])
    ).fillna(False)

    return df


def is_business_day_indexed(df: pd.DataFrame, date_str: str) -> bool:
    if not date_str:
        return False
    try:
        ts = pd.Timestamp(date_str)
        return ts in df.index
    except Exception:
        return False


def count_hold_days(df: pd.DataFrame, entry_date: str, current_date: pd.Timestamp) -> int:
    """
    entry_date から current_date までの営業日数を index ベースで数える
    entry日を1日目として数える
    """
    if not is_business_day_indexed(df, entry_date):
        return 0

    entry_ts = pd.Timestamp(entry_date)
    sliced = df.loc[(df.index >= entry_ts) & (df.index <= current_date)]
    return int(len(sliced))


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def build_message(today, state_before, state_after, action, action_reason) -> str:
    qqq_vs_150 = today["qqq"] / today["qqq_ma150"] - 1
    qqq_vs_200 = today["qqq"] / today["qqq_ma200"] - 1

    lines = []
    lines.append("SOXL Strategy")
    lines.append("")
    lines.append(f"Date: {today.name.date()}")
    lines.append("")
    lines.append(f"SOXL RSI2: {today['rsi2']:.2f}")
    lines.append(f"VIX: {today['vix']:.2f}")
    lines.append(f"QQQ vs 150MA: {qqq_vs_150 * 100:.2f}%")
    lines.append(f"QQQ vs 200MA: {qqq_vs_200 * 100:.2f}%")
    lines.append("")
    lines.append(f"Before: {state_before['position']}")
    lines.append(f"Action: {action}")
    lines.append(f"Reason: {action_reason}")
    lines.append(f"After: {state_after['position']}")

    if state_after["position"] == "SOXL":
        lines.append(f"Entry Price: {state_after['entry_price']:.2f}")
        lines.append(f"Entry Date: {state_after['entry_date']}")
        lines.append(f"Hold Days: {state_after['hold_days']}")

    return "\n".join(lines)


# =========================
# メイン判定
# =========================

def main():
    df = fetch_data()
    today = df.iloc[-1]
    today_date = df.index[-1]

    state_before = load_state()
    state_after = dict(state_before)

    action = "HOLD"
    action_reason = "No change"

    # -------------------------
    # SOXL保有中: exit判定優先
    # -------------------------
    if state_before["position"] == "SOXL" and state_before["entry_price"] is not None:
        entry_price = float(state_before["entry_price"])

        # 営業日数を再計算
        hold_days = count_hold_days(df, state_before["entry_date"], today_date)
        state_after["hold_days"] = hold_days

        tp_price = entry_price * (1 + TP)
        sl_price = entry_price * (1 + SL)

        hit_tp = safe_float(today["high"]) is not None and float(today["high"]) >= tp_price
        hit_sl = safe_float(today["low"]) is not None and float(today["low"]) <= sl_price

        if hit_tp and hit_sl:
            # 同日両ヒットなら SL優先
            action = "EXIT_SOXL"
            action_reason = f"SL priority both hit (TP {tp_price:.2f}, SL {sl_price:.2f})"
            state_after = {
                "position": "QQQ" if today["qqq"] > today["qqq_ma200"] else "CASH",
                "entry_price": None,
                "entry_date": None,
                "hold_days": 0
            }

        elif hit_sl:
            action = "EXIT_SOXL"
            action_reason = f"SL hit ({sl_price:.2f})"
            state_after = {
                "position": "QQQ" if today["qqq"] > today["qqq_ma200"] else "CASH",
                "entry_price": None,
                "entry_date": None,
                "hold_days": 0
            }

        elif hit_tp:
            action = "EXIT_SOXL"
            action_reason = f"TP hit ({tp_price:.2f})"
            state_after = {
                "position": "QQQ" if today["qqq"] > today["qqq_ma200"] else "CASH",
                "entry_price": None,
                "entry_date": None,
                "hold_days": 0
            }

        elif hold_days >= MAX_HOLD:
            action = "EXIT_SOXL"
            action_reason = f"MAX_HOLD reached ({hold_days} days)"
            state_after = {
                "position": "QQQ" if today["qqq"] > today["qqq_ma200"] else "CASH",
                "entry_price": None,
                "entry_date": None,
                "hold_days": 0
            }

        else:
            action = "HOLD_SOXL"
            action_reason = "SOXL position continues"

    # -------------------------
    # SOXL非保有: 新規判定
    # -------------------------
    if state_after["position"] != "SOXL":
        if bool(today["sig_soxl"]):
            action = "ENTER_SOXL"
            action_reason = "VIX>=20, RSI2<6, QQQ>150MA"
            state_after = {
                "position": "SOXL",
                "entry_price": float(today["open"]),
                "entry_date": str(today_date.date()),
                "hold_days": 1
            }
        else:
            core_pos = "QQQ" if today["qqq"] > today["qqq_ma200"] else "CASH"

            if state_after["position"] != core_pos:
                action = f"ROTATE_TO_{core_pos}"
                action_reason = "No SOXL signal; core rule applied"

            state_after = {
                "position": core_pos,
                "entry_price": None,
                "entry_date": None,
                "hold_days": 0
            }

    # state保存
    save_state(state_after)

    # 通知文作成
    msg = build_message(
        today=today,
        state_before=state_before,
        state_after=state_after,
        action=action,
        action_reason=action_reason
    )

    print(msg)
    send_line(msg)

    # GitHub に state.json を push
    push_state_to_github()


if __name__ == "__main__":
    main()
