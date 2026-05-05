# ============================================================
# SOXL Strategy v18 (SOXS_ma修正) - GitHub Actions + LINE通知
# ------------------------------------------------------------
# 構造：ユーザー様提供のスクリプトを 100% 継承し復元（省略一切なし）
# 変更点 (V17 -> V18)：
# SOXS_MA の条件を 75MA乖離 40%以上 60%以下 + ヒゲ条件 に変更
# ============================================================

import os
import json
import requests
import subprocess
from typing import Optional
import pandas as pd
import numpy as np
import yfinance as yf

# 指数表記を禁止し、通常の小数(4桁)で表示する設定
pd.set_option('display.float_format', '{:.4f}'.format)
pd.set_option("display.max_columns", None)

# =========================
# 1. 設定・パラメータ
# =========================
START          = "2015-01-01"
QQQ_GAP_BASE   = 0.010

# SOXS_MA 条件
SOXS_MA_MIN_DEV = 0.40
SOXS_MA_MAX_DEV = 0.60

# 条件別TP/SL/hold（V17確定値 + サブ口座）
PARAMS = {
    "base_normal": {"tp": 0.26, "sl": -0.15, "hold": 30},
    "base_alert":  {"tp": 0.26, "sl": -0.09, "hold": 30},
    "bb":          {"tp": 0.32, "sl": -0.12, "hold": 30},
    "sc":          {"tp": 0.30, "sl": -0.15, "hold": 15},
    "or4":         {"tp": 0.18, "sl": -0.15, "hold": 15},
    "DIP_REBOUND": {"tp": 0.14, "sl": -0.14, "hold": 10}, 
    "TREND_GC":    {"tp": 0.20, "sl": -0.12, "hold": 20},
    "SOXS_PRE_DC": {"tp": 0.14, "sl": -0.06, "hold": 6},
    "SOXS_BB":     {"tp": 0.18, "sl": -0.07, "hold": 6},
    "SOXS_MA":     {"tp": 0.10, "sl": -0.10, "hold": 6},
    "SNIPER":      {"tp": 0.16, "sl": -0.10, "hold": 20}, # サブ口座(先読み)用
}

STATE_PATH         = "state.json"
LINE_TOKEN         = os.environ.get("LINE_TOKEN", "")
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY  = os.environ.get("GITHUB_REPOSITORY", "")

# =========================
# 2. GitHub push / LINE送信
# =========================
def push_state_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print("Skip push: missing token/repo")
        return
    repo_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"
    subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", STATE_PATH], check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        print("No state change.")
        return
    subprocess.run(["git", "commit", "-m", "Update state.json v17 final"], check=True)
    subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)

def send_line(msg: str):
    if not LINE_TOKEN:
        print("Skip LINE: missing token")
        print(msg)
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
# 3. 状態管理
# =========================
def load_state() -> dict:
    default = {
        "position":                  "CASH", # ★ V17: 平時はCASH
        "sig_type":                  None,
        "entry_price":               None,
        "entry_date":                None,
        "hold_days":                 0,
        "pending_entry":             None,
        "pending_entry_signal_date": None,
        "pending_entry_sig_type":    None,
        "pending_exit_next_open":    False,
        "pending_exit_reason":       None,
        "last_soxs_ma_sl_date":      None,
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
# 4. データ取得・指標計算
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
    # ★ V17: CORE用のティッカーを削除し軽量化
    tickers = {
        "SOXL": "SOXL", "SOXS": "SOXS", "QQQ": "QQQ", "SMH": "SMH",
        "TLT": "TLT", "TNX": "^TNX", "VIX": "^VIX",  "VVIX": "^VVIX"
    }
    raw = {k: flatten_cols(yf.download(v, start=START,
                           auto_adjust=False, progress=False))
           for k, v in tickers.items()}

    df = pd.DataFrame(index=raw["SOXL"].index)
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c.lower()] = raw["SOXL"][c]
        if c in ["Open", "High", "Low", "Close"]:
            df[f"soxs_{c.lower()}"] = raw["SOXS"][c]
            
    for c in ["QQQ", "SMH", "VIX", "VVIX", "TLT", "TNX"]:
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
        
    df["tlt_ma150"] = df["tlt"].rolling(150).mean() 
    df["tnx_ma50"]  = df["tnx"].rolling(50).mean()  
    
    df["bb_mid"]   = df["close"].rolling(20).mean()
    df["bb_sigma"] = df["close"].rolling(20).std()
    df["bb_lower"] = df["bb_mid"] - 2.5 * df["bb_sigma"]
    df["bb_z"]     = (df["close"] - df["bb_mid"]) / df["bb_sigma"]
    
    df["bb40_mid"]   = df["close"].rolling(40).mean()
    df["bb40_std"]   = df["close"].rolling(40).std(ddof=0)
    df["bb40_upper"] = df["bb40_mid"] + 2.8 * df["bb40_std"]
    df["ma75"]       = df["close"].rolling(75).mean()
    df["ma75_dev"]   = df["close"] / df["ma75"] - 1.0
    
    candle_range = (df["high"] - df["low"]).replace(0, np.nan)
    df["prev_upper_wick_ratio"] = ((df["high"] - np.maximum(df["open"], df["close"])) / candle_range).clip(lower=0).shift(1)
    df["t1_upper_wick_ratio"]   = ((df["high"] - np.maximum(df["open"], df["close"])) / candle_range).clip(lower=0)
    
    df["smh_ma_20"] = df["smh"].rolling(20).mean()
    df["smh_ma_50"] = df["smh"].rolling(50).mean()

    # 先読み系
    df["soxl_ma_20"] = df["close"].rolling(20).mean()
    df["soxl_ma_50"] = df["close"].rolling(50).mean()
    df["soxl_dist"]  = (df["soxl_ma_20"] - df["soxl_ma_50"]) / df["soxl_ma_50"]

    df = df.dropna().copy()

    # === シグナル定義 ===
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
    
    # DIP_REBOUND
    df["sig_dip_rebound"] = ((df["qqq"] > df["qqq_ma150"]) & (df["smh"] > df["smh_ma150"]) & 
                             (df["rsi2"] <= 30) & (df["ret1"].shift(1) >= 0.025))
    
    # TREND_GC
    cond_gc = ((df["smh_ma_20"].shift(1) <= df["smh_ma_50"].shift(1)) &
               (df["smh_ma_20"] > df["smh_ma_50"]))
    hybrid_filter = (df["tlt"] > df["tlt_ma150"]) | (df["tnx"] < df["tnx_ma50"])
    
    df["sig_trend_gc"] = (cond_gc & (df["vix"] < 20) & hybrid_filter &
                          (df["smh_obv"] > df["smh_obv_ma20"])) & ~(df["sig_or3"] | df["sig_or4"] | df["sig_dip_rebound"])
    
    # ショート
    df["sig_soxs_pre_dc"] = ((df["soxl_ma_20"] > df["soxl_ma_50"]) & (df["close"] < df["soxl_ma_20"]) & (df["soxl_dist"] < 0.010) & (df["vix_ret5"] > 0.10))
    df["sig_soxs_bb"] = (df["close"] >= df["bb40_upper"])
    df["sig_soxs_ma"] = (
        (df["ma75_dev"] >= SOXS_MA_MIN_DEV) &
        (df["ma75_dev"] <= SOXS_MA_MAX_DEV) &
        (df["prev_upper_wick_ratio"] >= 0.10) &
        (df["t1_upper_wick_ratio"] >= 0.05)
    )

    # Sniper (サブ)
    df["sig_sniper"] = ((df["soxl_ma_20"] < df["soxl_ma_50"]) &
                        (df["soxl_dist"] > -0.004) &
                        (df["close"] > df["soxl_ma_20"]) &
                        (df["vix"] < 20) &
                        (df["smh_obv"] > df["smh_obv_ma20"])).fillna(False)
    
    # 市場終了前ガード
    now_utc     = pd.Timestamp.utcnow()
    latest_date = df.index[-1].date()
    if now_utc.hour < 21 and latest_date >= now_utc.date():
        print(f"⚠️ スキップ: {latest_date}")
        send_line(f"⚠️ 市場終了前のため本日の送信をスキップします\n実行時刻(UTC): {now_utc.strftime('%H:%M')}\n最新データ日: {latest_date}")
        raise SystemExit(0)

    return df

# =========================
# 5. メッセージ構築
# =========================
def count_hold_days(df, entry_date, current_date) -> int:
    if not entry_date:
        return 0
    try:
        return int(len(df.loc[pd.Timestamp(entry_date):current_date]))
    except:
        return 0

def build_message(today, state_after, action, action_reason,
                  soxs_ma_locked, lock_days_passed, df, today_date,
                  sniper_action, sniper_reason) -> str:

    date_str    = str(today.name.date())
    qqq_vs_200  = today["qqq"] / today["qqq_ma200"] - 1
    smh_vs_200  = today["smh"] / today["smh_ma200"] - 1
    qqq_filter  = today["qqq"] > today["qqq_ma200"] * (1 + QQQ_GAP_BASE)
    vix_r5 = today["vix_ret5"]
    vvix_r5 = today["vvix_ret5"]
    obv_vs_ma = today["smh_obv"] > today["smh_obv_ma20"]

    def yn(b):
        return "✅" if b else "❌"

    lines = []
    lines.append(f"【SOXL戦略 v17 日次レポート {date_str}】")
    lines.append("")

    lines.append("📊 マーケット指標")
    lines.append(f"VIX        : {today['vix']:.2f} (5日 {vix_r5*100:+.1f}%)")
    lines.append(f"VVIX       : {today['vvix']:.2f} (5日 {vvix_r5*100:+.1f}%)")
    lines.append(f"SOXL RSI2  : {today['rsi2']:.2f}")
    lines.append(f"SOXL bb_z  : {today['bb_z']:.2f}")
    lines.append(f"QQQ vs 200 : {qqq_vs_200*100:+.2f}% {'(>+1.0% ✅)' if qqq_filter else '(<+1.0% ❌)'}")
    lines.append(f"SMH vs 200 : {smh_vs_200*100:+.2f}%")
    lines.append(f"SMH OBV    : {yn(obv_vs_ma)} (>MA20)")
    lines.append("")

    lines.append("🎯 サブ口座 (SOXL Sniper)")
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

    lines.append("📡 メイン口座 シグナル")
    lines.append(f"OR3(V9) : {yn(today['sig_or3'])}")
    if bool(today['sig_base_alert']):
        lines.append(" └ Base(Alert) ✅")
    elif bool(today['sig_base_normal']):
        lines.append(" └ Base(Normal) ✅")
    elif bool(today['sig_sc']):
        lines.append(" └ SC ✅")
    elif bool(today['sig_bb']):
        lines.append(" └ BB ✅")
        
    lines.append(f"OR4(V9) : {yn(today['sig_or4'])}")
    lines.append(f"DIP_REB : {yn(today['sig_dip_rebound'])}")
    lines.append(f"TREND_GC: {yn(today['sig_trend_gc'])}")
    lines.append(f"SOXS_PRE: {yn(today['sig_soxs_pre_dc'])}")
    lines.append(f"SOXS_BB : {yn(today['sig_soxs_bb'])}")
    
    sig_soxs_ma_text = yn(today['sig_soxs_ma']) if not soxs_ma_locked else "❌ (防衛ガード)"
    lines.append(f"SOXS_MA : {sig_soxs_ma_text}")
    if soxs_ma_locked:
        lines.append(f" └ 🔒 防衛ロック中 (解除まであと{4 - lock_days_passed}日)")
    lines.append("")

    lines.append("🏃 メイン口座 アクション")
    lines.append(f"Action : {action}")
    lines.append(f"Reason : {action_reason}")
    lines.append("")

    lines.append("💼 メイン口座 ポジション")
    pos = state_after["position"]
    lines.append(f"現在ポジション: {pos}")
    if state_after.get("pending_entry"):
        asset_t = state_after.get("pending_entry")
        sig_t   = state_after.get("pending_entry_sig_type", "")
        p_val   = PARAMS.get(sig_t, {})
        tp_v    = p_val.get("tp", "?")
        sl_v    = p_val.get("sl", "?")
        hd_v    = p_val.get("hold", "?")
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

    return "\n".join(lines)

# =========================
# 6. メイン (V17ロジック・優先順位)
# =========================
def main():
    df         = fetch_data()
    today      = df.iloc[-1]
    today_date = df.index[-1]
    state_before = load_state()
    state_after  = dict(state_before)

    # --- サブ口座 (SOXL Sniper) 処理 ---
    sniper_action = "なし"
    sniper_reason = "変化なし"
    if state_before.get("sniper_pending_exit"):
        exit_px = today["open"]
        ep = state_before.get("sniper_ep", exit_px)
        ret = exit_px / ep - 1
        state_after["sniper_pos"] = False
        state_after["sniper_ep"] = None
        state_after["sniper_ed"] = None
        state_after["sniper_pending_exit"] = False
        sniper_action = "SOXL売却完了"
        sniper_reason = f"期限到達による寄り付き売却 (損益: {ret*100:+.2f}%)"
    elif state_before.get("sniper_pending_entry"):
        state_after["sniper_pos"] = True
        state_after["sniper_ep"] = float(today["open"])
        state_after["sniper_ed"] = str(today_date.date())
        state_after["sniper_pending_entry"] = False
        sniper_action = "SOXL買付完了"
        sniper_reason = f"前日シグナルによる寄り付き買付 (Open: {today['open']:.2f})"
    elif state_after.get("sniper_pos") and state_after.get("sniper_ep"):
        ep = float(state_after["sniper_ep"])
        hd = count_hold_days(df, state_after["sniper_ed"], today_date)
        hit_tp = today["high"] >= ep * 1.16
        hit_sl = today["low"] <= ep * 0.90
        if hit_sl:
            sniper_action = "SOXL売却 (SL)"
            sniper_reason = "損切り水準到達"
            state_after["sniper_pos"] = False
            state_after["sniper_ep"] = state_after["sniper_ed"] = None
        elif hit_tp:
            sniper_action = "SOXL売却 (TP)"
            sniper_reason = "利確水準到達"
            state_after["sniper_pos"] = False
            state_after["sniper_ep"] = state_after["sniper_ed"] = None
        elif hd >= 20:
            sniper_action = "SOXL売却予約 (期限)"
            sniper_reason = "保有20日到達 → 翌寄り売却"
            state_after["sniper_pending_exit"] = True
        else:
            sniper_action = "SOXL保有継続"
            sniper_reason = f"保有{hd}日目"
    if not state_after.get("sniper_pos") and not state_after.get("sniper_pending_entry") and not state_after.get("sniper_pending_exit"):
        if bool(today["sig_sniper"]):
            state_after["sniper_pending_entry"] = True
            sniper_action = "SOXLエントリー予約"
            sniper_reason = "先読みシグナル点灯 → 翌寄り買付"

    # --- メイン口座 (V17 CASH待機版) 処理 ---
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

    action = "HOLD"
    action_reason = "変化なし"

    if state_before.get("pending_exit_next_open", False):
        asset = state_before["position"]
        exit_px = today["open"] if asset == "SOXL" else today["soxs_open"]
        ep = state_before.get("entry_price", exit_px)
        trade_ret = (exit_px / ep) - 1
        state_after["position"] = "CASH" # ★ V17: 売却後はCASHに戻る
        state_after["sig_type"] = None
        state_after["entry_price"] = None
        state_after["entry_date"] = None
        state_after["hold_days"] = 0
        state_after["pending_exit_next_open"] = False
        state_after["pending_exit_reason"] = None
        action = f"{asset}売却実行"
        action_reason = f"翌日寄り売却 (Open: {exit_px:.2f}, 損益: {trade_ret*100:+.2f}%)"

    entered_today = False
    if state_before.get("pending_entry"):
        asset_to_enter = state_before.get("pending_entry")
        sig_t = state_before.get("pending_entry_sig_type", "base_normal")
        entry_px = today["open"] if asset_to_enter == "SOXL" else today["soxs_open"]
        state_after["position"] = asset_to_enter
        state_after["sig_type"] = sig_t
        state_after["entry_price"] = float(entry_px)
        state_after["entry_date"] = str(today_date.date())
        state_after["hold_days"] = 1
        state_after["pending_entry"] = None
        state_after["pending_entry_sig_type"] = None
        state_after["pending_entry_signal_date"] = None
        entered_today = True
        action = f"{asset_to_enter}買付完了"
        action_reason = f"寄り付きエントリー済み [{sig_t}]"

    if state_after["position"] in ["SOXL", "SOXS"] and state_after.get("entry_price"):
        pos = state_after["position"]
        ep = float(state_after["entry_price"])
        sig_t = state_after.get("sig_type", "base_normal")
        p = PARAMS.get(sig_t, PARAMS["base_normal"])
        hd = count_hold_days(df, state_after["entry_date"], today_date)
        state_after["hold_days"] = hd
        t_h = float(today["high"]) if pos == "SOXL" else float(today["soxs_high"])
        t_l = float(today["low"]) if pos == "SOXL" else float(today["soxs_low"])
        tp_px = ep * (1 + p["tp"])
        sl_px = ep * (1 + p["sl"])
        if t_l <= sl_px:
            action = f"{pos}売却(SL)"
            action_reason = f"SLヒット ({sl_px:.2f})"
            state_after["position"] = "CASH" # ★ V17: SL後もCASH
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0
            state_after["sig_type"] = None
            if pos == "SOXS" and sig_t == "SOXS_MA":
                state_after["last_soxs_ma_sl_date"] = str(today_date.date())
        elif t_h >= tp_px:
            action = f"{pos}売却(TP)"
            action_reason = f"TPヒット ({tp_px:.2f})"
            state_after["position"] = "CASH" # ★ V17: TP後もCASH
            state_after["entry_price"] = None
            state_after["entry_date"] = None
            state_after["hold_days"] = 0
            state_after["sig_type"] = None
        elif hd >= p["hold"]:
            action = f"{pos}売却予約(期限)"
            state_after["pending_exit_next_open"] = True

    # ★ V17 優先順位判定 (V9 > DIP > GC > SOXS)
    v9_sig = bool(today["sig_or3"]) or bool(today["sig_or4"])
    dip_sig = bool(today["sig_dip_rebound"])
    gc_sig = bool(today["sig_trend_gc"])
    soxs_sig = bool(today["sig_soxs_pre_dc"]) or bool(today["sig_soxs_bb"]) or bool(today["sig_soxs_ma"])

    def get_v9_type(row):
        if bool(row["sig_sc"]):
            return "sc"
        if bool(row["sig_base_alert"]):
            return "base_alert"
        if bool(row["sig_base_normal"]):
            return "base_normal"
        if bool(row["sig_bb"]):
            return "bb"
        return "or4"

    if state_after["position"] == "CASH": # ★ V17: CASH時に新規エントリー判定
        target = None
        if v9_sig:
            sig_n = get_v9_type(today)
            target = ("SOXL", sig_n)
        elif dip_sig:
            target = ("SOXL", "DIP_REBOUND")
        elif gc_sig:
            target = ("SOXL", "TREND_GC")
        elif soxs_sig:
            if bool(today["sig_soxs_pre_dc"]):
                sig_n = "SOXS_PRE_DC"
            elif bool(today["sig_soxs_bb"]):
                sig_n = "SOXS_BB"
            else:
                sig_n = "SOXS_MA"
            target = ("SOXS", sig_n) if not (sig_n == "SOXS_MA" and soxs_ma_locked) else None
        
        if target:
            state_after["pending_entry"] = target[0]
            state_after["pending_entry_sig_type"] = target[1]
            state_after["pending_entry_signal_date"] = str(today_date.date())
            action = f"{target[0]}予約"
            action_reason = f"シグナル発生 [{target[1]}]"

    elif state_after["position"] == "SOXS":
        if v9_sig or dip_sig or gc_sig:
            state_after["pending_exit_next_open"] = True
            action = "スイッチ予約"
            sig_n = get_v9_type(today) if v9_sig else ("DIP_REBOUND" if dip_sig else "TREND_GC")
            state_after["pending_entry"] = "SOXL"
            state_after["pending_entry_sig_type"] = sig_n
            state_after["pending_entry_signal_date"] = str(today_date.date())

    save_state(state_after)
    msg = build_message(today, state_after, action, action_reason, soxs_ma_locked, lock_days_passed, df, today_date, sniper_action, sniper_reason)
    print(msg)
    send_line(msg)
    push_state_to_github()

if __name__ == "__main__":
    main()
