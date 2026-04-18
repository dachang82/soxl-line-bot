# ============================================================
# SOXL Strategy v14 - GitHub Actions + LINE通知
# Core: QQQ/SMH/XLE/GLD/VHT rotation (3M+6M+12M, top2)
# SOXL: V9(OR3+OR4) + TREND + TREND_GC(OBV)
# SOXS: SOXS_BB + SOXS_MA (v14 新・黄金比 + 2重防衛システム)
# Sub : SOXL先読み戦略 (完全独立管理)
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
QQQ_GAP_BASE   = 0.010

# 条件別TP/SL/hold（v14確定値 + サブ口座）
PARAMS = {
    "base_normal": {"tp": 0.26, "sl": -0.15, "hold": 30},
    "base_alert":  {"tp": 0.26, "sl": -0.09, "hold": 30},
    "bb":          {"tp": 0.32, "sl": -0.12, "hold": 30},
    "sc":          {"tp": 0.30, "sl": -0.15, "hold": 15},
    "or4":         {"tp": 0.18, "sl": -0.15, "hold": 15},
    "TREND":       {"tp": 0.14, "sl": -0.14, "hold": 10},
    "TREND_GC":    {"tp": 0.20, "sl": -0.12, "hold": 20},
    "SOXS_BB":     {"tp": 0.18, "sl": -0.07, "hold": 6},
    "SOXS_MA":     {"tp": 0.10, "sl": -0.10, "hold": 6},
    "SNIPER":      {"tp": 0.16, "sl": -0.10, "hold": 20}, # サブ口座(先読み)用
}

CORE_TICKERS       = ["QQQ", "SMH", "XLE", "GLD", "VHT"]
STATE_PATH         = "state.json"
LINE_TOKEN         = os.environ.get("LINE_TOKEN", "")
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
    if not LINE_TOKEN:
        print("Skip LINE: missing token")
        return
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
        "last_soxs_ma_sl_date":      None,
        # --- サブ口座(先読み)用 独立ステータス ---
        "sniper_pos":                False,
        "sniper_ep":                 None,
        "sniper_ed":                 None,
        "sniper_pending_entry":      False,
        "sniper_pending_exit":       False,
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

def calc_rsi(close, period=14):
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_data() -> pd.DataFrame:
    tickers = {
        "SOXL": "SOXL", "SOXS": "SOXS", "QQQ": "QQQ", "SMH": "SMH",
        "XLE": "XLE",   "GLD": "GLD", "VHT": "VHT",
        "VIX": "^VIX",  "VVIX": "^VVIX"
    }
    raw = {k: flatten_cols(yf.download(v, start=START,
                           auto_adjust=False, progress=False))
           for k, v in tickers.items()}

    df = pd.DataFrame(index=raw["SOXL"].index)
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c.lower()] = raw["SOXL"][c]
        if c in ["Open", "High", "Low", "Close"]:
            df[f"soxs_{c.lower()}"] = raw["SOXS"][c]
            
    for c in ["QQQ", "SMH", "XLE", "GLD", "VHT", "VIX", "VVIX"]:
        df[c.lower()] = raw[c]["Close"]
        
    df["smh_vol"]  = raw["SMH"]["Volume"]
    df = df.ffill()

    # 指標計算
    df["rsi2"] = calc_rsi(df["close"], 2)
    df["ret1"] = df["close"].pct_change()
    df["vix_ret5"] = df["vix"].pct_change(5)
    df["vvix_ret5"] = df["vvix"].pct_change(5)
    
    # OBV
    df["smh_obv"] = np.where(df["smh"] > df["smh"].shift(1), df["smh_vol"], 
                             np.where(df["smh"] < df["smh"].shift(1), -df["smh_vol"], 0)).cumsum()
    df["smh_obv_ma20"] = df["smh_obv"].rolling(20).mean()

    for n in [150, 200]:
        df[f"qqq_ma{n}"] = df["qqq"].rolling(n).mean()
        df[f"smh_ma{n}"] = df["smh"].rolling(n).mean()
        
    df["bb_mid"]   = df["close"].rolling(20).mean()
    df["bb_sigma"] = df["close"].rolling(20).std()
    df["bb_lower"] = df["bb_mid"] - 2.5 * df["bb_sigma"]
    df["bb_z"]     = (df["close"] - df["bb_mid"]) / df["bb_sigma"]
    
    df["bb40_mid"]   = df["close"].rolling(40).mean()
    df["bb40_std"]   = df["close"].rolling(40).std(ddof=0)
    df["bb40_upper"] = df["bb40_mid"] + 2.8 * df["bb40_std"]
    df["ma75"]       = df["close"].rolling(75).mean()
    df["ma75_dev"]   = df["close"] / df["ma75"] - 1.0
    
    # v14 SOXS MA ロジック
    candle_range = (df["high"] - df["low"]).replace(0, np.nan)
    df["prev_upper_wick_ratio"] = ((df["high"] - np.maximum(df["open"], df["close"])) / candle_range).clip(lower=0).shift(1)
    df["t1_upper_wick_ratio"]   = ((df["high"] - np.maximum(df["open"], df["close"])) / candle_range).clip(lower=0)
    
    df["smh_ma_20"] = df["smh"].rolling(20).mean()
    df["smh_ma_50"] = df["smh"].rolling(50).mean()

    # サブ口座 (SOXL先読み) 用
    df["soxl_ma_20"] = df["close"].rolling(20).mean()
    df["soxl_ma_50"] = df["close"].rolling(50).mean()
    df["soxl_dist"]  = (df["soxl_ma_20"] - df["soxl_ma_50"]) / df["soxl_ma_50"]

    df = df.dropna().copy()

    # === シグナル定義 (メイン口座) ===
    cond_base = (df["vix"] >= 20) & (df["rsi2"] < 6) & (df["qqq"] > df["qqq_ma200"] * (1 + QQQ_GAP_BASE))
    cond_alert = (df["vix_ret5"] >= 0.15) & (df["vix_ret5"] <= 0.40) & (df["vvix_ret5"] >= 0.05) & (df["vvix_ret5"] <= 0.25)
    
    df["sig_base_alert"]  = cond_base & cond_alert
    df["sig_base_normal"] = cond_base & ~cond_alert
    df["sig_base"]        = cond_base

    df["sig_bb"] = (df["close"] < df["bb_lower"]) & (df["smh"] > df["smh_ma150"])
    df["sig_sc"] = (df["vix"] >= 35) & (df["rsi2"] < 10)
    df["sig_or3"] = cond_base | df["sig_bb"] | df["sig_sc"]
    
    df["sig_or4_raw"] = ((df["qqq"] > df["qqq_ma200"]) & (df["smh"] > df["smh_ma200"]) & 
                         (df["vix"] >= 20) & (df["vix"] < 22) & 
                         (df["bb_z"] <= -1.7) & (df["bb_z"] > -2.5))
    df["sig_or4"] = df["sig_or4_raw"] & (~df["sig_or3"])
    
    df["sig_trend_best"] = ((df["qqq"] > df["qqq_ma150"]) & (df["smh"] > df["smh_ma150"]) & 
                            (df["rsi2"] <= 30) & (df["ret1"].shift(1) >= 0.025))
    
    cond_gc = ((df["smh_ma_20"].shift(1) <= df["smh_ma_50"].shift(1)) &
               (df["smh_ma_20"] > df["smh_ma_50"]) &
               (df["vix"] < 20) &
               (df["smh_obv"] > df["smh_obv_ma20"]))
    df["sig_trend_gc"] = cond_gc & ~(df["sig_or3"] | df["sig_or4"] | df["sig_trend_best"])
    
    df["sig_soxs_bb"] = (df["close"] >= df["bb40_upper"])
    
    SOXS_T1_WICK_TH = 0.05
    df["sig_soxs_ma"] = ((df["ma75_dev"] >= 0.40) & 
                         (df["prev_upper_wick_ratio"] >= 0.10) &
                         (df["t1_upper_wick_ratio"] >= SOXS_T1_WICK_TH))

    # === シグナル定義 (サブ口座: SOXL先読み) ===
    df["sig_sniper"] = ((df["soxl_ma_20"] < df["soxl_ma_50"]) &
                        (df["soxl_dist"] > -0.004) &
                        (df["close"] > df["soxl_ma_20"]) &
                        (df["vix"] < 20) &
                        (df["smh_obv"] > df["smh_obv_ma20"])).fillna(False)
    
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
                  cur_a1, cur_a2, next_a1, next_a2, soxs_ma_locked, lock_days_passed, df, today_date,
                  sniper_action, sniper_reason) -> str:

    date_str    = str(today.name.date())
    qqq_vs_200  = today["qqq"] / today["qqq_ma200"] - 1
    smh_vs_200  = today["smh"] / today["smh_ma200"] - 1
    qqq_filter  = today["qqq"] > today["qqq_ma200"] * (1 + QQQ_GAP_BASE)
    
    vix_r5 = today["vix_ret5"]
    vvix_r5 = today["vvix_ret5"]
    obv_vs_ma = today["smh_obv"] > today["smh_obv_ma20"]

    def yn(b): return "✅" if b else "❌"

    lines = []
    lines.append(f"【SOXL戦略 v14 日次レポート {date_str}】")
    lines.append("")

    # マーケット指標
    lines.append("📊 マーケット指標")
    lines.append(f"VIX        : {today['vix']:.2f} (5日 {vix_r5*100:+.1f}%)")
    lines.append(f"VVIX       : {today['vvix']:.2f} (5日 {vvix_r5*100:+.1f}%)")
    lines.append(f"SOXL RSI2  : {today['rsi2']:.2f}")
    lines.append(f"SOXL bb_z  : {today['bb_z']:.2f}")
    lines.append(f"QQQ vs 200 : {qqq_vs_200*100:+.2f}% {'(>+1.0% ✅)' if qqq_filter else '(<+1.0% ❌)'}")
    lines.append(f"SMH vs 200 : {smh_vs_200*100:+.2f}%")
    lines.append(f"SMH OBV    : {yn(obv_vs_ma)} (>MA20)")
    lines.append("")

    # === サブ口座 (SOXL先読み) ===
    lines.append("🎯 サブ口座 (SOXL先読み)")
    lines.append(f"シグナル : {yn(today['sig_sniper'])}")
    lines.append(f"Action   : {sniper_action}")
    if sniper_action != "なし":
        lines.append(f"Reason   : {sniper_reason}")

    if state_after.get("sniper_pos") and state_after.get("sniper_ep"):
        s_ep = float(state_after["sniper_ep"])
        s_hd = count_hold_days(df, state_after["sniper_ed"], today_date)
        s_pnl = (today["close"] / s_ep) - 1
        lines.append(f"📈 保有中: {s_ep:.2f}買付 (保有{s_hd}/20日) 含み損益 {s_pnl*100:+.2f}%")
        lines.append(f"   TP目標: {s_ep*1.16:.2f} (+16%) / SL水準: {s_ep*0.90:.2f} (-10%)")
    elif state_after.get("sniper_pending_entry"):
        lines.append("⚠️ 翌日寄り: SOXLエントリー予約済み (先読みシグナル)")
    elif state_after.get("sniper_pending_exit"):
        lines.append("⚠️ 翌日寄り: SOXL売却予定 (保有期限20日到達)")
    lines.append("")

    # シグナル状況 (メイン口座)
    lines.append("📡 メイン口座 シグナル")
    lines.append(f"OR3(V9) : {yn(today['sig_or3'])}")
    if bool(today['sig_base_alert']):
        lines.append(f" └ Base(Alert) ✅")
    elif bool(today['sig_base_normal']):
        lines.append(f" └ Base(Normal) ✅")
    elif bool(today['sig_sc']):
        lines.append(f" └ SC ✅")
    elif bool(today['sig_bb']):
        lines.append(f" └ BB ✅")
        
    lines.append(f"OR4(V9) : {yn(today['sig_or4'])}")
    lines.append(f"TREND   : {yn(today['sig_trend_best'])}")
    lines.append(f"TREND_GC: {yn(today['sig_trend_gc'])}")
    lines.append(f"SOXS_BB : {yn(today['sig_soxs_bb'])}")
    
    sig_soxs_ma_text = yn(today['sig_soxs_ma']) if not soxs_ma_locked else "❌ (条件満たすもガード)"
    lines.append(f"SOXS_MA : {sig_soxs_ma_text}")
    if soxs_ma_locked:
        lines.append(f" └ 🔒 防衛ロック中 (解除まであと{4 - lock_days_passed}日)")
    lines.append("")

    # アクション (メイン口座)
    lines.append("🏃 メイン口座 アクション")
    lines.append(f"Action : {action}")
    lines.append(f"Reason : {action_reason}")
    lines.append("")

    # ポジション (メイン口座)
    lines.append("💼 メイン口座 ポジション")
    pos = state_after["position"]
    lines.append(f"現在ポジション: {pos}")
    if state_after.get("pending_entry"):
        asset_t = state_after.get("pending_entry")
        sig_t   = state_after.get("pending_entry_sig_type", "")
        tp_v    = PARAMS.get(sig_t, {}).get("tp", "?")
        sl_v    = PARAMS.get(sig_t, {}).get("sl", "?")
        hd_v    = PARAMS.get(sig_t, {}).get("hold", "?")
        lines.append(f"⚠️ 翌日寄り: {asset_t}エントリー予約済み "
                     f"[{sig_t}] TP+{int(tp_v*100)}%/SL{int(sl_v*100)}%/hold{hd_v}日")
    if state_after.get("pending_exit_next_open"):
        lines.append(f"⚠️ 翌日寄り: {pos}売却予定（保有上限等）")
    lines.append("")

    if pos in ["SOXL", "SOXS"] and state_after.get("entry_price"):
        ep      = float(state_after["entry_price"])
        sig_t   = state_after.get("sig_type", "base_normal")
        p       = PARAMS.get(sig_t, PARAMS["base_normal"])
        tp_val  = ep * (1 + p["tp"])
        sl_val  = ep * (1 + p["sl"])
        today_c = today["close"] if pos == "SOXL" else today["soxs_close"]
        pnl     = today_c / ep - 1
        hd      = state_after.get("hold_days", 0)
        max_hd  = p["hold"]
        
        lines.append(f"📈 {pos}保有情報")
        lines.append(f"シグナル種別  : {sig_t}")
        lines.append(f"エントリー価格: {ep:.2f}")
        lines.append(f"エントリー日  : {state_after['entry_date']}")
        lines.append(f"保有日数      : {hd} / {max_hd}日")
        lines.append(f"含み損益      : {pnl*100:+.2f}%")
        lines.append(f"TP目標        : {tp_val:.2f} (+{int(p['tp']*100)}%)")
        lines.append(f"SL水準        : {sl_val:.2f} ({int(p['sl']*100)}%)")
        if hd >= max_hd - 2:
            lines.append(f"⚠️ 保休期限まで残り{max_hd - hd}日")
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

    # ----------------------------------------------------
    # サブ口座 (SOXL先読み) の処理
    # ----------------------------------------------------
    sniper_action = "なし"
    sniper_reason = "変化なし"
    
    # 1. 翌寄り売却（期限到達時）
    if state_before.get("sniper_pending_exit"):
        exit_px = today["open"]
        ep = state_before.get("sniper_ep", exit_px)
        ret = exit_px / ep - 1
        state_after["sniper_pos"] = False
        state_after["sniper_ep"] = None
        state_after["sniper_ed"] = None
        state_after["sniper_pending_exit"] = False
        sniper_action = "SOXL売却完了"
        sniper_reason = f"保有上限到達による寄り付き売却 (損益: {ret*100:+.2f}%)"

    # 2. 翌寄りエントリー実行
    elif state_before.get("sniper_pending_entry"):
        state_after["sniper_pos"] = True
        state_after["sniper_ep"] = float(today["open"])
        state_after["sniper_ed"] = str(today_date.date())
        state_after["sniper_pending_entry"] = False
        sniper_action = "SOXL買付完了"
        sniper_reason = f"前日シグナルによる寄り付き買付 (Open: {today['open']:.2f})"

    # 3. 保有中の出口判定 (TP/SL/TIME)
    elif state_after.get("sniper_pos") and state_after.get("sniper_ep"):
        ep = float(state_after["sniper_ep"])
        hd = count_hold_days(df, state_after["sniper_ed"], today_date)
        tp_px = ep * (1 + PARAMS["SNIPER"]["tp"])
        sl_px = ep * (1 + PARAMS["SNIPER"]["sl"])
        
        hit_tp = today["high"] >= tp_px
        hit_sl = today["low"] <= sl_px

        if hit_tp and hit_sl:
            sniper_action = "SOXL売却 (SL優先)"
            sniper_reason = "同日TP/SL両ヒット → SL優先"
            state_after["sniper_pos"] = False
            state_after["sniper_ep"] = state_after["sniper_ed"] = None
        elif hit_sl:
            sniper_action = "SOXL売却 (SL)"
            sniper_reason = f"損切り水準到達 ({sl_px:.2f})"
            state_after["sniper_pos"] = False
            state_after["sniper_ep"] = state_after["sniper_ed"] = None
        elif hit_tp:
            sniper_action = "SOXL売却 (TP)"
            sniper_reason = f"利確水準到達 ({tp_px:.2f})"
            state_after["sniper_pos"] = False
            state_after["sniper_ep"] = state_after["sniper_ed"] = None
        elif hd >= PARAMS["SNIPER"]["hold"]:
            sniper_action = "SOXL売却予約 (期限)"
            sniper_reason = f"保有{hd}日到達 → 翌寄り売却"
            state_after["sniper_pending_exit"] = True
        else:
            sniper_action = "SOXL保有継続"
            sniper_reason = f"保有{hd}日目"

    # 4. 新規シグナルの検出 (ポジションなし時)
    if not state_after.get("sniper_pos") and not state_after.get("sniper_pending_entry") and not state_after.get("sniper_pending_exit"):
        if bool(today["sig_sniper"]):
            state_after["sniper_pending_entry"] = True
            sniper_action = "SOXLエントリー予約"
            sniper_reason = "先読みシグナル点灯 → 翌寄り買付"


    # ----------------------------------------------------
    # メイン口座の処理 (V14)
    # ----------------------------------------------------
    lock_days_passed = 0
    soxs_ma_locked = False
    if state_before.get("last_soxs_ma_sl_date"):
        lock_days_passed = count_hold_days(df, state_before["last_soxs_ma_sl_date"], today_date) - 1
        if lock_days_passed <= 3:
            soxs_ma_locked = True
        else:
            state_after["last_soxs_ma_sl_date"] = None

    if float(today["vix"]) >= 20.0 or soxs_ma_locked:
        df.loc[df.index[-1], "sig_soxs_ma"] = False
        today = df.iloc[-1]

    action        = "HOLD"
    action_reason = "変化なし"

    cur_a1, cur_a2, next_a1, next_a2 = calc_core_rotation(df)
    state_after["core_asset1"] = cur_a1
    state_after["core_asset2"] = cur_a2

    if state_before.get("pending_exit_next_open", False):
        asset = state_after["position"]
        exit_px = today["open"] if asset == "SOXL" else today["soxs_open"]
        ep = state_before.get("entry_price", exit_px)
        trade_ret = (exit_px / ep) - 1
        
        state_after["position"]               = "CORE"
        state_after["sig_type"]               = None
        state_after["entry_price"]            = None
        state_after["entry_date"]             = None
        state_after["hold_days"]              = 0
        state_after["pending_exit_next_open"] = False
        state_after["pending_exit_reason"]    = None
        action        = f"{asset}売却実行（翌寄り）"
        action_reason = f"保有上限到達による翌日寄り売却 (Open: {exit_px:.2f}, 損益: {trade_ret*100:+.2f}%)"

    entered_today = False
    if state_before.get("pending_entry"):
        asset_to_enter = state_before.get("pending_entry")
        sig_t = state_before.get("pending_entry_sig_type", "base_normal")
        entry_px = today["open"] if asset_to_enter == "SOXL" else today["soxs_open"]
        
        state_after["position"]    = asset_to_enter
        state_after["sig_type"]    = sig_t
        state_after["entry_price"] = float(entry_px)
        state_after["entry_date"]  = str(today_date.date())
        state_after["hold_days"]   = 1
        state_after["pending_entry"]             = None
        state_after["pending_entry_sig_type"]    = None
        state_after["pending_entry_signal_date"] = None
        entered_today = True
        action        = f"{asset_to_enter}エントリー実行（翌寄り）"
        action_reason = f"前日シグナル[{sig_t}]による本日寄り付きエントリー (open: {entry_px:.2f})"

    if state_after["position"] in ["SOXL", "SOXS"] and state_after.get("entry_price"):
        pos   = state_after["position"]
        ep    = float(state_after["entry_price"])
        sig_t = state_after.get("sig_type", "base_normal")
        p     = PARAMS.get(sig_t, PARAMS["base_normal"])
        hd    = count_hold_days(df, state_after["entry_date"], today_date)
        state_after["hold_days"] = hd

        t_h = float(today["high"]) if pos == "SOXL" else float(today["soxs_high"])
        t_l = float(today["low"])  if pos == "SOXL" else float(today["soxs_low"])

        tp_px  = ep * (1 + p["tp"])
        sl_px  = ep * (1 + p["sl"])
        hit_tp = t_h >= tp_px
        hit_sl = t_l <= sl_px

        if hit_tp and hit_sl:
            action        = f"{pos}売却（SL優先）"
            action_reason = f"同日TP/SL両ヒット → SL優先 (SL: {sl_px:.2f} / {int(p['sl']*100)}%)"
            state_after["position"]    = "CORE"
            state_after["sig_type"]    = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]   = 0
            if pos == "SOXS" and sig_t == "SOXS_MA":
                state_after["last_soxs_ma_sl_date"] = str(today_date.date())
                action_reason += " ⚠️ SOXS_MA防衛発動: 以降3営業日ロック"

        elif hit_sl:
            action        = f"{pos}売却（SL）"
            action_reason = f"SLヒット ({sl_px:.2f}) / {int(p['sl']*100)}%"
            state_after["position"]    = "CORE"
            state_after["sig_type"]    = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]   = 0
            if pos == "SOXS" and sig_t == "SOXS_MA":
                state_after["last_soxs_ma_sl_date"] = str(today_date.date())
                action_reason += " ⚠️ SOXS_MA防衛発動: 以降3営業日ロック"

        elif hit_tp:
            action        = f"{pos}売却（TP）"
            action_reason = f"TPヒット ({tp_px:.2f}) / +{int(p['tp']*100)}% [{sig_t}]"
            state_after["position"]    = "CORE"
            state_after["sig_type"]    = None
            state_after["entry_price"] = state_after["entry_date"] = None
            state_after["hold_days"]   = 0

        elif hd >= p["hold"]:
            action        = f"{pos}売却予約（保有上限）"
            action_reason = f"保有{hd}日が上限{p['hold']}日に到達 [{sig_t}] → 翌日寄り売却予定"
            state_after["pending_exit_next_open"] = True
            state_after["pending_exit_reason"]    = action_reason

        else:
            if entered_today:
                action        = f"{pos}エントリー完了"
                action_reason = f"本日寄り付きエントリー済み [{sig_t}]"
            else:
                action        = f"{pos}保有継続"
                action_reason = f"保有{hd}日目 [{sig_t}] / TP: {tp_px:.2f} / SL: {sl_px:.2f}"

    v9_sig    = bool(today["sig_or3"]) or bool(today["sig_or4"])
    trend_sig = bool(today["sig_trend_best"])
    gc_sig    = bool(today["sig_trend_gc"])
    soxs_bb   = bool(today["sig_soxs_bb"])
    soxs_ma   = bool(today["sig_soxs_ma"])
    soxs_sig  = soxs_bb or soxs_ma

    def get_v9_sig_type(row):
        if bool(row["sig_sc"]): return "sc"
        if bool(row["sig_base_alert"]): return "base_alert"
        if bool(row["sig_base_normal"]): return "base_normal"
        if bool(row["sig_bb"]): return "bb"
        if bool(row["sig_or4"]): return "or4"
        return "base_normal"

    if state_after["position"] == "CORE":
        if v9_sig:
            sig_t = get_v9_sig_type(today)
            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = sig_t
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXLエントリー予約（翌日寄り）"
            action_reason = f"V9シグナル発生 [{sig_t}]"
        elif trend_sig:
            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = "TREND"
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXLエントリー予約（翌日寄り）"
            action_reason = "TRENDシグナル発生"
        elif gc_sig:
            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = "TREND_GC"
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXLエントリー予約（翌日寄り）"
            action_reason = "TREND_GCシグナル発生"
        elif soxs_sig:
            sig_t = "SOXS_BB" if soxs_bb else "SOXS_MA"
            state_after["pending_entry"]             = "SOXS"
            state_after["pending_entry_sig_type"]    = sig_t
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "SOXSエントリー予約（翌日寄り）"
            action_reason = f"ショートシグナル発生 [{sig_t}]"
        elif not entered_today:
            action        = "CORE保有継続"
            action_reason = f"シグナルなし / Core: {cur_a1}+{cur_a2}"

    elif state_after["position"] == "SOXS":
        if v9_sig or trend_sig or gc_sig:
            sig_t = "TREND"
            if v9_sig: sig_t = get_v9_sig_type(today)
            elif gc_sig: sig_t = "TREND_GC"
            
            state_after["pending_exit_next_open"]    = True
            state_after["pending_entry"]             = "SOXL"
            state_after["pending_entry_sig_type"]    = sig_t
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action        = "ドテン・SOXLスイッチ予約（翌日寄り）"
            action_reason = f"SOXS保有中にSOXLシグナル発生 [{sig_t}] → 翌寄りSOXS売却＆SOXL買付"

    save_state(state_after)

    msg = build_message(
        today=today,
        state_after=state_after,
        action=action,
        action_reason=action_reason,
        cur_a1=cur_a1, cur_a2=cur_a2,
        next_a1=next_a1, next_a2=next_a2,
        soxs_ma_locked=soxs_ma_locked,
        lock_days_passed=lock_days_passed,
        df=df, today_date=today_date,
        sniper_action=sniper_action, 
        sniper_reason=sniper_reason
    )

    print(msg)
    send_line(msg)
    push_state_to_github()

if __name__ == "__main__":
    main()
