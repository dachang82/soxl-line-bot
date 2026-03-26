# ============================================================
# SOXL Strategy v7+OR4 - GitHub Actions + LINE通知
# Core: QQQ/SMH/XLE/GLD/VHT rotation (3M+6M, top2)
# SOXL: OR3（条件別最適TP/SL）+ OR4補助シグナル
# ============================================================

import os
import json
import requests
import subprocess
from typing import Optional
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# 設定
# =========================
START          = "2015-01-01"
BB_SIGMA       = 2.5
BB_WINDOW      = 20
QQQ_GAP        = 0.005

# 条件別TP/SL/hold（v7確定値）
PARAMS = {
    "base": {"tp": 0.25, "sl": -0.15, "hold": 30},
    "bb":   {"tp": 0.30, "sl": -0.12, "hold": 30},
    "sc":   {"tp": 0.30, "sl": -0.15, "hold": 15},
    "or4":  {"tp": 0.18, "sl": -0.15, "hold": 15},
}

CORE_TICKERS       = ["QQQ", "SMH", "XLE", "GLD", "VHT"]
STATE_PATH         = "state.json"
LINE_TOKEN         = os.environ["LINE_TOKEN"]
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY  = os.environ.get("GITHUB_REPOSITORY", "")

# =========================
# GitHub push
# =========================
def push_state_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print("Skip push: missing token/repo")
        return
    repo_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"
    subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email",
                    "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", STATE_PATH], check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        print("No state change.")
        return
    subprocess.run(["git", "commit", "-m", "Update state.json"], check=True)
    subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)

# =========================
# LINE送信
# =========================
def send_line(msg: str):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers,
                      json={"messages": [{"type": "text", "text": msg}]},
                      timeout=30)
    r.raise_for_status()

# =========================
# state管理
# =========================
def load_state() -> dict:
    default = {
        "position":                  "CORE",
        "sig_type":                  None,
        "entry_price":               None,
        "entry_date":                None,
        "hold_days":                 0,
        "pending_entry":             None,
        "pending_entry_signal_date": None,
        "pending_entry_sig_type":    None,
        "pending_exit_next_open":    False,
        "pending_exit_reason":       None,
        "core_asset1":               "",
        "core_asset2":               "",
    }
    if not os.path.exists(STATE_PATH):
        return default
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)
    for k, v in default.items():
        state.setdefault(k, v)
    return state

def save_state(state: dict):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# =========================
# データ取得・指標計算
# =========================
def flatten_cols(x):
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)
    return x

def calc_rsi2(close, period=2):
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_data() -> pd.DataFrame:
    tickers = {
        "SOXL": "SOXL", "QQQ": "QQQ", "SMH": "SMH",
        "XLE": "XLE",   "GLD": "GLD", "VHT": "VHT",
        "VIX": "^VIX"
    }
    raw = {k: flatten_cols(yf.download(v, start=START,
                           auto_adjust=False, progress=False))
           for k, v in tickers.items()}

    df = pd.DataFrame(index=raw["SOXL"].index)
    df["open"]  = raw["SOXL"]["Open"]
    df["high"]  = raw["SOXL"]["High"]
    df["low"]   = raw["SOXL"]["Low"]
    df["close"] = raw["SOXL"]["Close"]
    df["qqq"]   = raw["QQQ"]["Close"]
    df["smh"]   = raw["SMH"]["Close"]
    df["xle"]   = raw["XLE"]["Close"]
    df["gld"]   = raw["GLD"]["Close"]
    df["vht"]   = raw["VHT"]["Close"]
    df["vix"]   = raw["VIX"]["Close"]

    df["rsi2"]      = calc_rsi2(df["close"])
    df["qqq_ma200"] = df["qqq"].rolling(200).mean()
    df["smh_ma200"] = df["smh"].rolling(200).mean()
    df["smh_ma150"] = df["smh"].rolling(150).mean()
    df["bb_mid"]    = df["close"].rolling(BB_WINDOW).mean()
    df["bb_sigma"]  = df["close"].rolling(BB_WINDOW).std()
    df["bb_lower"]  = df["bb_mid"] - BB_SIGMA * df["bb_sigma"]
    df["bb_z"]      = (df["close"] - df["bb_mid"]) / df["bb_sigma"]

    df = df.dropna().copy()

    # シグナル
    df["sig_base"] = (
        (df["vix"] >= 20) & (df["rsi2"] < 6) &
        (df["smh"] > df["smh_ma200"]) &
        (df["qqq"] > df["qqq_ma200"] * (1 + QQQ_GAP))
    ).fillna(False)

    df["sig_bb"] = (
        (df["close"] < df["bb_lower"]) &
        (df["smh"] > df["smh_ma150"])
    ).fillna(False)

    df["sig_sc"] = (
        (df["vix"] >= 35) & (df["rsi2"] < 10)
    ).fillna(False)

    df["sig_or3"] = (
        df["sig_base"] | df["sig_bb"] | df["sig_sc"]
    ).fillna(False)

    df["sig_or4_raw"] = (
        (df["qqq"]  > df["qqq_ma200"]) &
        (df["smh"]  > df["smh_ma200"]) &
        (df["vix"]  >= 20) & (df["vix"] < 22) &
        (df["bb_z"] <= -1.7) & (df["bb_z"] > -2.5)
    ).fillna(False)

    df["sig_or4"] = (
        df["sig_or4_raw"] & (~df["sig_or3"])
    ).fillna(False)

    # 市場終了前ガード
    now_utc     = pd.Timestamp.utcnow()
    latest_date = df.index[-1].date()
    today_utc   = now_utc.date()
    if now_utc.hour < 21 and latest_date >= today_utc:
        msg = (
            f"⚠️ 市場終了前のため本日の送信をスキップします\n"
            f"実行時刻(UTC): {now_utc.strftime('%H:%M')}\n"
            f"最新データ日: {latest_date}"
        )
        print(msg)
        send_line(msg)
        raise SystemExit(0)

    return df

# =========================
# Core Rotation計算
# =========================
def calc_core_rotation(df: pd.DataFrame):
    prices = df[["qqq","smh","xle","gld","vht"]].copy()
    prices.columns = CORE_TICKERS
    monthly = prices.resample("ME").last()

    # v8: 3M + 6M + 12M
    score = monthly.pct_change(3) + monthly.pct_change(6) + monthly.pct_change(12)

    results = []
    for i in range(len(monthly)):
        s = score.iloc[i].dropna()
        if len(s) < 2:
            results.append(("", ""))
            continue
        top2 = s.nlargest(2).index.tolist()
        results.append((top2[0], top2[1]))

    monthly_assets = pd.DataFrame(
        results, index=monthly.index, columns=["asset1","asset2"]
    )

    today          = df.index[-1]
    prev_month_end = (today.to_period("M") - 1).to_timestamp("M")
    this_month_end = today.to_period("M").to_timestamp("M")

    def get_assets(month_end):
        valid = monthly_assets[monthly_assets.index <= month_end]
        if len(valid) == 0:
            return "", ""
        row = valid.iloc[-1]
        return row["asset1"], row["asset2"]

    cur_a1,  cur_a2  = get_assets(prev_month_end)
    next_a1, next_a2 = get_assets(this_month_end)
    return cur_a1, cur_a2, next_a1, next_a2

# =========================
# 保有日数カウント
# =========================
def count_hold_days(df, entry_date, current_date) -> int:
    if not entry_date:
        return 0
    try:
        entry_ts = pd.Timestamp(entry_date)
        sliced   = df.loc[(df.index >= entry_ts) & (df.index <= current_date)]
        return int(len(sliced))
    except Exception:
        return 0

# =========================
# 通知メッセージ生成
# =========================
def build_message(today, state_after, action, action_reason,
                  cur_a1, cur_a2, next_a1, next_a2) -> str:

    date_str    = str(today.name.date())
    qqq_vs_200  = today["qqq"] / today["qqq_ma200"] - 1
    smh_vs_200  = today["smh"] / today["smh_ma200"] - 1
    smh_vs_150  = today["smh"] / today["smh_ma150"] - 1
    qqq_filter  = today["qqq"] > today["qqq_ma200"] * (1 + QQQ_GAP)
    bb_z_val    = today["bb_z"]

    sig1    = bool(today["sig_base"])
    sig2    = bool(today["sig_bb"])
    sig3    = bool(today["sig_sc"])
    sig_or3 = bool(today["sig_or3"])
    sig_or4 = bool(today["sig_or4"])

    def yn(b): return "✅" if b else "❌"

    lines = []
    lines.append(f"【SOXL戦略 日次レポート {date_str}】")
    lines.append("")

    # マーケット指標
    lines.append("📊 マーケット指標")
    lines.append(f"VIX       : {today['vix']:.2f}")
    lines.append(f"SOXL RSI2 : {today['rsi2']:.2f}")
    lines.append(f"SOXL bb_z : {bb_z_val:.2f}")
    lines.append(f"QQQ vs MA200: {qqq_vs_200*100:+.2f}%  "
                 f"{'(>+0.5% ✅)' if qqq_filter else '(<+0.5% ❌)'}")
    lines.append(f"SMH vs MA200: {smh_vs_200*100:+.2f}%")
    lines.append(f"SMH vs MA150: {smh_vs_150*100:+.2f}%")
    lines.append("")

    # シグナル状況
    lines.append("📡 シグナル状況")
    lines.append(f"条件1(RSI2): {yn(sig1)}  "
                 f"[VIX>=20, RSI2<6, SMH>MA200, QQQ>MA200+0.5%]")
    lines.append(f"条件2(BB)  : {yn(sig2)}  "
                 f"[close<BB下限(20日,2.5σ), SMH>MA150]")
    lines.append(f"条件3(SC)  : {yn(sig3)}  "
                 f"[VIX>=35, RSI2<10]")
    lines.append(f"OR3シグナル: {yn(sig_or3)}")
    lines.append(f"OR4シグナル: {yn(sig_or4)}  "
                 f"[VIX 20〜22, bb_z -2.5〜-1.7, QQQ/SMH>MA200]")
    lines.append("")

    # アクション
    lines.append("🏃 本日のアクション")
    lines.append(f"Action : {action}")
    lines.append(f"Reason : {action_reason}")
    lines.append("")

    # ポジション
    lines.append("💼 ポジション状況")
    pos = state_after["position"]
    lines.append(f"現在ポジション: {pos}")
    if state_after.get("pending_entry"):
        sig_t = state_after.get("pending_entry_sig_type", "")
        tp_v  = PARAMS.get(sig_t, {}).get("tp", "?")
        sl_v  = PARAMS.get(sig_t, {}).get("sl", "?")
        hd_v  = PARAMS.get(sig_t, {}).get("hold", "?")
        lines.append(f"⚠️ 翌日寄り: SOXLエントリー予約済み "
                     f"[{sig_t}] TP+{int(tp_v*100)}%/SL{int(sl_v*100)}%/hold{hd_v}日")
    if state_after.get("pending_exit_next_open"):
        lines.append("⚠️ 翌日寄り: SOXL売却予定（保有上限到達）")
    lines.append("")

    # SOXL保有中の詳細
    if pos == "SOXL" and state_after.get("entry_price"):
        ep      = float(state_after["entry_price"])
        sig_t   = state_after.get("sig_type", "base")
        p       = PARAMS.get(sig_t, PARAMS["base"])
        tp_val  = ep * (1 + p["tp"])
        sl_val  = ep * (1 + p["sl"])
        pnl     = today["close"] / ep - 1
        hd      = state_after.get("hold_days", 0)
        max_hd  = p["hold"]
        lines.append("📈 SOXL保有情報")
        lines.append(f"シグナル種別  : {sig_t}")
        lines.append(f"エントリー価格: {ep:.2f}")
        lines.append(f"エントリー日  : {state_after['entry_date']}")
        lines.append(f"保有日数      : {hd} / {max_hd}日")
        lines.append(f"含み損益      : {pnl*100:+.2f}%")
        lines.append(f"TP目標        : {tp_val:.2f} (+{int(p['tp']*100)}%)")
        lines.append(f"SL水準        : {sl_val:.2f} ({int(p['sl']*100)}%)")
        if hd >= max_hd - 2:
            lines.append(f"⚠️ 保有期限まで残り{max_hd - hd}日")
        lines.append("")

    # Core Rotation
    lines.append("🔄 Core Rotation")
    lines.append(f"今月保有  : {cur_a1} + {cur_a2}")
    lines.append(f"来月予定  : {next_a1} + {next_a2}")
    if (cur_a1 != next_a1 or cur_a2 != next_a2):
        lines.append("⚠️ 来月切り替えあり（月末リバランス）")

    return "\n".join(lines)

# =========================
# メイン
# =========================
def main():
    df         = fetch_data()
    today      = df.iloc[-1]
    today_date = df.index[-1]

    state_before = load_state()
    state_after  = dict(state_before)

    action        = "HOLD"
    action_reason = "変化なし"

    # Core Rotation計算
    cur_a1, cur_a2, next_a1, next_a2 = calc_core_rotation(df)
    state_after["core_asset1"] = cur_a1
    state_after["core_asset2"] = cur_a2

    # --- 1. pending exit（保有上限による翌寄り売却）---
    if state_before.get("pending_exit_next_open", False):
        state_after["position"]              = "CORE"
        state_after["sig_type"]              = None
        state_after["entry_price"]           = None
        state_after["entry_date"]            = None
        state_after["hold_days"]             = 0
        state_after["pending_exit_next_open"] = False
        state_after["pending_exit_reason"]   = None
        action        = "SOXL売却実行（翌寄り）"
        action_reason = "保有上限到達による翌日寄り売却を実行"

    # --- 2. pending entry（翌寄りエントリー実行）---
    entered_today = False
    if state_before.get("pending_entry") == "SOXL":
        sig_t = state_before.get("pending_entry_sig_type", "base")
        state_after["position"]    = "SOXL"
        state_after["sig_type"]    = sig_t
        state_after["entry_price"] = float(today["open"])
        state_after["entry_date"]  = str(today_date.date())
        state_after["hold_days"]   = 1
        state_after["pending_entry"]             = None
        state_after["pending_entry_sig_type"]    = None
        state_after["pending_entry_signal_date"] = None
        entered_today = True
        action        = "SOXLエントリー実行（翌寄り）"
        action_reason = (f"前日シグナル[{sig_t}]による本日寄り付きエントリー "
                        f"(open: {today['open']:.2f})")

    # --- 3. SOXL保有中のexit判定 ---
    if state_after["position"] == "SOXL" and state_after.get("entry_price"):
        ep    = float(state_after["entry_price"])
        sig_t = state_after.get("sig_type", "base")
        p     = PARAMS.get(sig_t, PARAMS["base"])
        hd    = count_hold_days(df, state_after["entry_date"], today_date)
        state_after["hold_days"] = hd

        tp_px  = ep * (1 + p["tp"])
        sl_px  = ep * (1 + p["sl"])
        hit_tp = float(today["high"]) >= tp_px
        hit_sl = float(today["low"])  <= sl_px

        if hit_tp and hit_sl:
            action        = "SOXL売却（SL優先）"
            action_reason = (f"同日TP/SL両ヒット → SL優先 "
                            f"(SL: {sl_px:.2f} / {int(p['sl']*100)}%)")
            state_after["position"]   = "CORE"
            state_after["sig_type"]   = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]  = 0

        elif hit_sl:
            action        = "SOXL売却（SL）"
            action_reason = f"SLヒット ({sl_px:.2f}) / {int(p['sl']*100)}%"
            state_after["position"]   = "CORE"
            state_after["sig_type"]   = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]  = 0

        elif hit_tp:
            action        = "SOXL売却（TP）"
            action_reason = (f"TPヒット ({tp_px:.2f}) / "
                            f"+{int(p['tp']*100)}% [{sig_t}]")
            state_after["position"]   = "CORE"
            state_after["sig_type"]   = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]  = 0

        elif hd >= p["hold"]:
            action        = "SOXL売却予約（保有上限）"
            action_reason = (f"保有{hd}日が上限{p['hold']}日に到達 "
                            f"[{sig_t}] → 翌日寄り売却予定")
            state_after["pending_exit_next_open"] = True
            state_after["pending_exit_reason"]    = action_reason

        else:
            if entered_today:
                action        = "SOXLエントリー完了"
                action_reason = (f"本日寄り付きエントリー済み "
                                f"[{sig_t}] (open: {today['open']:.2f})")
            else:
                tp_px2 = ep * (1 + p["tp"])
                sl_px2 = ep * (1 + p["sl"])
                action        = "SOXL保有継続"
                action_reason = (f"保有{hd}日目 [{sig_t}] / "
                                f"TP: {tp_px2:.2f} / SL: {sl_px2:.2f}")

    # --- 4. SOXL非保有: シグナル確認（OR3優先→OR4）---
    if state_after["position"] != "SOXL":
        if bool(today["sig_or3"]):
            # OR3発動条件の特定
            triggered = []
            sig_t_new = "base"
            if bool(today["sig_sc"]):
                triggered.append("条件3(SC): VIX>=35, RSI2<10")
                sig_t_new = "sc"
            if bool(today["sig_base"]):
                triggered.append("条件1(RSI2): VIX>=20, RSI2<6, "
                                  "SMH>MA200, QQQ>MA200+0.5%")
                if sig_t_new == "base":
                    sig_t_new = "base"
            if bool(today["sig_bb"]):
                triggered.append("条件2(BB): close<BB下限(2.5σ), SMH>MA150")
                if sig_t_new == "base":
                    sig_t_new = "bb"

            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = sig_t_new
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXLエントリー予約（翌日寄り）"
            action_reason = " / ".join(triggered)

        elif bool(today["sig_or4"]):
            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = "or4"
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXLエントリー予約・OR4（翌日寄り）"
            action_reason = (f"OR4: VIX={today['vix']:.1f}(20〜22), "
                            f"bb_z={today['bb_z']:.2f}(-2.5〜-1.7), "
                            f"QQQ/SMH>MA200")
        else:
            action        = "CORE保有継続"
            action_reason = f"シグナルなし / Core: {cur_a1}+{cur_a2}"

    save_state(state_after)

    msg = build_message(
        today=today,
        state_after=state_after,
        action=action,
        action_reason=action_reason,
        cur_a1=cur_a1, cur_a2=cur_a2,
        next_a1=next_a1, next_a2=next_a2,
    )

    print(msg)
    send_line(msg)
    push_state_to_github()

if __name__ == "__main__":
    main()
