import os
import json
import requests
import subprocess
from typing import Optional

import pandas as pd
import yfinance as yf


# =========================
# 設定
# =========================

START = "2015-01-01"

SOXL_TP = 0.25
SOXL_SL = -0.15
SOXL_MAX_HOLD = 25

QQQ_BAND = 0.01  # 1% hysteresis

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


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
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


def load_state() -> dict:
    default_state = {
        "position": "CASH",          # "SOXL", "QQQ", "CASH"
        "core_position": "CASH",     # QQQ/CASH の内部状態（ヒステリシス用）
        "entry_price": None,         # SOXL entry price
        "entry_date": None,          # SOXL entry date
        "hold_days": 0,              # SOXL hold days
        "pending_entry": None,       # "SOXL" or None
        "pending_entry_signal_date": None,
        "pending_exit_next_open": False,
        "pending_exit_reason": None,
    }

    if not os.path.exists(STATE_PATH):
        return default_state

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    for k, v in default_state.items():
        state.setdefault(k, v)

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
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True
    )
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


def fetch_data() -> pd.DataFrame:
    soxl = yf.download("SOXL", start=START, auto_adjust=False, progress=False)
    qqq = yf.download("QQQ", start=START, auto_adjust=False, progress=False)
    smh = yf.download("SMH", start=START, auto_adjust=False, progress=False)
    vix = yf.download("^VIX", start=START, auto_adjust=False, progress=False)

    soxl = flatten_columns(soxl)
    qqq = flatten_columns(qqq)
    smh = flatten_columns(smh)
    vix = flatten_columns(vix)

    df = pd.DataFrame(index=soxl.index)

    df["open"] = soxl["Open"]
    df["high"] = soxl["High"]
    df["low"] = soxl["Low"]
    df["close"] = soxl["Close"]

    df["qqq"] = qqq["Close"]
    df["smh"] = smh["Close"]
    df["vix"] = vix["Close"]

    df["rsi2"] = calc_rsi2(df["close"])

    df["qqq_ma200"] = df["qqq"].rolling(200).mean()
    df["smh_ma200"] = df["smh"].rolling(200).mean()

    df = df.dropna().copy()

    df["sig_soxl"] = (
        (df["vix"] >= 20) &
        (df["rsi2"] < 6) &
        (df["smh"] > df["smh_ma200"])
    ).fillna(False)

    return df


def is_business_day_indexed(df: pd.DataFrame, date_str: Optional[str]) -> bool:
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


def update_core_position(qqq_price: float, qqq_ma200: float, current_core: str, band: float) -> str:
    """
    QQQ/CASH のヒステリシス判定
    """
    upper = qqq_ma200 * (1 + band)
    lower = qqq_ma200 * (1 - band)

    if current_core not in ["QQQ", "CASH"]:
        current_core = "CASH"

    if current_core == "CASH":
        if qqq_price > upper:
            return "QQQ"
        return "CASH"

    # current_core == "QQQ"
    if qqq_price < lower:
        return "CASH"
    return "QQQ"


def build_message(today, state_before, state_after, action, action_reason) -> str:
    qqq_vs_200 = today["qqq"] / today["qqq_ma200"] - 1
    smh_vs_200 = today["smh"] / today["smh_ma200"] - 1

    lines = []
    lines.append("SOXL / QQQ Regime Strategy")
    lines.append("")
    lines.append(f"Date: {today.name.date()}")
    lines.append("")
    lines.append(f"SOXL RSI2: {today['rsi2']:.2f}")
    lines.append(f"VIX: {today['vix']:.2f}")
    lines.append(f"QQQ vs200MA: {qqq_vs_200 * 100:.2f}%")
    lines.append(f"SMH vs200MA: {smh_vs_200 * 100:.2f}%")
    lines.append("")
    lines.append(f"SOXL Signal: {bool(today['sig_soxl'])}")
    lines.append(f"Core Position: {state_after['core_position']}")
    lines.append(f"Action: {action}")
    lines.append(f"Reason: {action_reason}")
    lines.append(f"Final Position: {state_after['position']}")

if state_after["position"] == "SOXL":
    lines.append(f"Entry Price: {state_after['entry_price']:.2f}")
    lines.append(f"Entry Date: {state_after['entry_date']}")
    lines.append(f"Hold Days: {state_after['hold_days']} / {SOXL_MAX_HOLD}")
    pnl = today["close"] / state_after["entry_price"] - 1
    lines.append(f"Unrealized PnL: {pnl*100:.2f}%")

if state_after.get("pending_entry") == "SOXL":
    lines.append("Pending: ENTER_SOXL_NEXT_OPEN")

if state_after.get("pending_exit_next_open"):
    lines.append("Pending: EXIT_SOXL_NEXT_OPEN")

return "\n".join(lines)

# =========================
# メイン判定
# =========================

def main():
    df = fetch_data()

    # 最新営業日
    today = df.iloc[-1]
    today_date = df.index[-1]

    state_before = load_state()
    state_after = dict(state_before)

    action = "HOLD"
    action_reason = "No change"

    # -------------------------
    # 1. core_position を更新
    #    （QQQ/CASHヒステリシス）
    # -------------------------
    state_after["core_position"] = update_core_position(
        qqq_price=float(today["qqq"]),
        qqq_ma200=float(today["qqq_ma200"]),
        current_core=state_before.get("core_position", "CASH"),
        band=QQQ_BAND,
    )

    # -------------------------
    # 2. 前日までに pending exit があれば、今日寄りで実行された扱い
    # -------------------------
    if state_before.get("pending_exit_next_open", False):
        state_after["position"] = state_after["core_position"]
        state_after["entry_price"] = None
        state_after["entry_date"] = None
        state_after["hold_days"] = 0
        state_after["pending_exit_next_open"] = False
        state_after["pending_exit_reason"] = None

        action = "EXECUTE_PENDING_EXIT"
        action_reason = "Previous next-open exit executed"

    # -------------------------
    # 3. 前日までに pending entry があれば、今日寄りでSOXLエントリー
    # -------------------------
    entered_today = False
    if state_before.get("pending_entry") == "SOXL":
        state_after["position"] = "SOXL"
        state_after["entry_price"] = float(today["open"])
        state_after["entry_date"] = str(today_date.date())
        state_after["hold_days"] = 1
        state_after["pending_entry"] = None
        state_after["pending_entry_signal_date"] = None

        entered_today = True
        action = "EXECUTE_SOXL_ENTRY"
        action_reason = "Previous signal executed at today's open"

    # -------------------------
    # 4. SOXL保有中: exit判定優先
    # -------------------------
    if state_after["position"] == "SOXL" and state_after["entry_price"] is not None:
        entry_price = float(state_after["entry_price"])

        # 営業日数を再計算
        hold_days = count_hold_days(df, state_after["entry_date"], today_date)
        state_after["hold_days"] = hold_days

        tp_price = entry_price * (1 + SOXL_TP)
        sl_price = entry_price * (1 + SOXL_SL)

        hit_tp = float(today["high"]) >= tp_price
        hit_sl = float(today["low"]) <= sl_price

        if hit_tp and hit_sl:
            # 同日両ヒットなら SL優先
            action = "EXIT_SOXL"
            action_reason = f"SL priority both hit (TP {tp_price:.2f}, SL {sl_price:.2f})"
            state_after["position"] = state_after["core_position"]
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0
            state_after["pending_exit_next_open"] = False
            state_after["pending_exit_reason"] = None

        elif hit_sl:
            action = "EXIT_SOXL"
            action_reason = f"SL hit ({sl_price:.2f})"
            state_after["position"] = state_after["core_position"]
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0
            state_after["pending_exit_next_open"] = False
            state_after["pending_exit_reason"] = None

        elif hit_tp:
            action = "EXIT_SOXL"
            action_reason = f"TP hit ({tp_price:.2f})"
            state_after["position"] = state_after["core_position"]
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0
            state_after["pending_exit_next_open"] = False
            state_after["pending_exit_reason"] = None

        elif hold_days >= SOXL_MAX_HOLD:
            # max_hold は翌営業日寄りで退出
            action = "EXIT_SOXL_NEXT_OPEN"
            action_reason = f"MAX_HOLD reached ({hold_days} days)"
            state_after["pending_exit_next_open"] = True
            state_after["pending_exit_reason"] = action_reason

        else:
            # SOXL継続
            if entered_today:
                action = "ENTER_SOXL"
                action_reason = "SOXL position entered today"
            else:
                action = "HOLD_SOXL"
                action_reason = "SOXL position continues"

    # -------------------------
    # 5. SOXL非保有: 新規SOXLシグナル判定
    # -------------------------
    if state_after["position"] != "SOXL":
        if bool(today["sig_soxl"]):
            # 翌営業日寄りで SOXL エントリー
            state_after["pending_entry"] = "SOXL"
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action = "ENTER_SOXL_NEXT_OPEN"
            action_reason = "VIX>=20, RSI2<6, SMH>200MA"

        else:
            # SOXLシグナルがないときは core_position に合わせる
            target_core = state_after["core_position"]

            if state_after["position"] != target_core:
                action = f"ROTATE_TO_{target_core}"
                action_reason = "No SOXL signal; QQQ/CASH core rule applied"

            state_after["position"] = target_core
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0

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
