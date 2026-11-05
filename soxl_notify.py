# -*- coding: utf-8 -*-
"""SOXL Strategy v20 — GitHub Actions / LINE 日次通知（差し替え用）

本体の各戦略は通常100%。R3・YBは購入直前資産の50%（購入費用込み）。
R3: SOXS / TP18%・SL6%・4日目引け。
YB: SOXL / TP15%・SL9%・10日目引け。以前のYHは採用しない。
本体最優先。ハーフ同士は先着・切替なし。同時点灯だけR3 > YB。
本体の保有期限は翌営業日寄り。Sniperは従来どおり独立したサブ口座。

既存のスクリプトと差し替え、state.json と既存の環境変数を引き継ぐ。
必要パッケージ: pandas, numpy, yfinance, requests
環境変数: LINE_TOKEN / GITHUB_TOKEN / GITHUB_REPOSITORY
任意: STATE_PATH=state.json / STATE_BRANCH=main / DRY_RUN=1
確認だけ: python soxl_strategy_v20_line.py --dry-run
DRY_RUNでは状態保存・LINE送信・Git操作を行わない（価格取得だけ行う）。

NY16:30より前は当日日足を除外。確定済みの各営業日を一度だけ処理する。
GitHub Actionsでは同じworkflowの concurrency を設定すること。
workflowの最上位に次を追加（既存の同等設定があればそのままでよい）:
  concurrency:
    group: soxl-v20-line
    cancel-in-progress: false
実行時刻はNY16:30以降。UTC21:45なら夏冬とも確定後（日本時間06:45）。
本スクリプトは発注せず、日足から判定した予約・約定想定を通知する。
"""

import base64
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar, GoodFriday
import requests
import yfinance as yf

# 検証版v20と同じ開始時点から、候補判定用の基準保有・固定枠を再現する。
# 実際の通知口座は state.json を引き継ぎ、過去の保有で上書きしない。
START = '2010-01-01'
QQQ_GAP_BASE = .010
SOXS_MA_MIN_DEV, SOXS_MA_MAX_DEV = .40, .60
SOXS_LOCK_DAYS = SC_LOCK_DAYS = 3
COST = .001
STATE_PATH = Path(os.environ.get('STATE_PATH', 'state.json'))
STATE_BRANCH = os.environ.get('STATE_BRANCH', 'main')
LINE_TOKEN = os.environ.get('LINE_TOKEN', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY', '')

PARAMS = {
    'base_normal': {'tp': .26, 'sl': -.15, 'hold': 30},
    'base_alert': {'tp': .26, 'sl': -.09, 'hold': 30},
    'bb': {'tp': .32, 'sl': -.12, 'hold': 30},
    'SC': {'tp': .30, 'sl': -.15, 'hold': 15},
    'OR4': {'tp': .18, 'sl': -.15, 'hold': 15},
    'DIP_REBOUND': {'tp': .14, 'sl': -.14, 'hold': 10},
    'TREND_GC': {'tp': .20, 'sl': -.12, 'hold': 20},
    'SOXS_PRE_DC': {'tp': .14, 'sl': -.06, 'hold': 6},
    'SOXS_BB': {'tp': .18, 'sl': -.07, 'hold': 6},
    'SOXS_MA': {'tp': .10, 'sl': -.10, 'hold': 6},
    'R3': {'tp': .18, 'sl': -.06, 'hold': 4},
    'YB': {'tp': .15, 'sl': -.09, 'hold': 10},
    'SNIPER': {'tp': .16, 'sl': -.10, 'hold': 20},
}
LABELS = {
    'SC': 'SC', 'base_alert': 'Base Alert', 'base_normal': 'Base Normal',
    'bb': 'BB', 'OR4': 'OR4', 'DIP_REBOUND': 'DIP_REBOUND',
    'TREND_GC': 'TREND_GC', 'SOXS_PRE_DC': 'SOXS_PRE_DC',
    'SOXS_BB': 'SOXS_BB', 'SOXS_MA': 'SOXS_MA',
    'R3': 'R3（20MA回復失敗）', 'YB': 'YB（金利確認付き40日高値突破）',
    'SNIPER': 'Sniper',
}
HALF_ORDER = ('R3', 'YB')
HALF_ASSETS = {'R3': 'SOXS', 'YB': 'SOXL'}

def canonical_tag(tag):
    return {'sc': 'SC', 'or4': 'OR4', 'YB_40D_TNX': 'YB'}.get(tag, tag)

def strategy_label(tag):
    tag = canonical_tag(tag)
    if tag not in LABELS:
        raise ValueError('state.json の戦略名を識別できません。元の状態を確認してください。')
    return LABELS[tag]

def lot_for(tag):
    return .5 if canonical_tag(tag) in HALF_ORDER else 1.

def lot_label(tag):
    return '半量50%' if lot_for(tag) == .5 else '通常100%'

def finalized_cutoff(now_utc=None):
    now = pd.Timestamp.now(tz='UTC') if now_utc is None else pd.Timestamp(now_utc)
    now = now.tz_localize('UTC') if now.tzinfo is None else now.tz_convert('UTC')
    ny = now.tz_convert('America/New_York')
    day = ny.tz_localize(None).normalize()
    return day if (ny.hour, ny.minute) >= (16, 30) else day - pd.Timedelta(days=1)

def clean_price_frame(frame, cutoff):
    frame = flatten_cols(frame.copy())
    if frame.empty:
        raise ValueError('日次価格が空です。状態は更新しません。')
    frame.index = pd.to_datetime(frame.index)
    if frame.index.tz is not None:
        frame.index = frame.index.tz_convert('America/New_York').tz_localize(None)
    frame.index = frame.index.normalize()
    if not frame.index.is_unique or not frame.columns.is_unique:
        raise ValueError('日次価格の日付・列に重複があります。')
    return frame.sort_index().loc[lambda x: x.index <= cutoff]

def flatten_cols(x):
    if isinstance(x.columns, pd.MultiIndex): x.columns = x.columns.get_level_values(0)
    return x

def calc_rsi(close, period=14):
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_data(now_utc=None, raw_override=None):
    print("確定済み日足を取得中…", flush=True)
    start = START
    cutoff = finalized_cutoff(now_utc)
    # 不要なティッカーを削除し軽量化
    tickers = {"SOXL": "SOXL", "QQQ": "QQQ", "SMH": "SMH", "TLT": "TLT", "TNX": "^TNX", "VIX": "^VIX", "VVIX": "^VVIX", "SOXS": "SOXS"}
    raw = ({k: clean_price_frame(yf.download(v, start=start, auto_adjust=False,
                back_adjust=False, repair=False, keepna=True, actions=False,
                progress=False, threads=False, timeout=30), cutoff)
            for k, v in tickers.items()} if raw_override is None else
           {k: clean_price_frame(raw_override[k], cutoff) for k in tickers})
    if any(p.empty for p in raw.values()):
        raise ValueError('必要な日次価格が空です。状態は更新しません。')
    latest = raw['SOXL'].index[-1]
    # 最新日の主要入力が欠けたときは、本体の過去のffillと区別して停止。
    for name, fields in [('SOXL', ['Open','High','Low','Close']),
                         ('SOXS', ['Open','High','Low','Close']),
                         ('SMH', ['Open','High','Low','Close','Volume']),
                         ('QQQ', ['Close']), ('TLT', ['Close']),
                         ('VIX', ['Close']), ('VVIX', ['Close'])]:
        if latest not in raw[name].index or not np.isfinite(raw[name].loc[latest, fields]).all():
            raise ValueError(f'{name}の最新確定日足が不足しています。状態は更新しません。')

    df = pd.DataFrame(index=raw["SOXL"].index)
    for c in ["Open", "High", "Low", "Close"]:
        df[c.lower()] = raw["SOXL"][c]
        df[f"soxs_{c.lower()}"] = raw["SOXS"][c]

    for c in ["QQQ", "SMH", "TLT", "TNX", "VIX", "VVIX"]:
        df[c.lower()] = raw[c]["Close"]

    df["smh_vol"]  = raw["SMH"]["Volume"]
    df = df.ffill()

    # インジケーター
    df["rsi2"] = calc_rsi(df["close"], 2)
    df["ret1"] = df["close"].pct_change()
    df["vix_ret5"] = df["vix"].pct_change(5)
    df["vvix_ret5"] = df["vvix"].pct_change(5)

    df["smh_obv"] = np.where(df["smh"] > df["smh"].shift(1), df["smh_vol"],
                             np.where(df["smh"] < df["smh"].shift(1), -df["smh_vol"], 0)).cumsum()
    df["smh_obv_ma20"] = df["smh_obv"].rolling(20).mean()

    for n in [150, 200]:
        df[f"qqq_ma{n}"] = df["qqq"].rolling(n).mean()
        df[f"smh_ma{n}"] = df["smh"].rolling(n).mean()

    df["tlt_ma150"] = df["tlt"].rolling(150).mean()
    df["tnx_ma50"] = df["tnx"].rolling(50).mean()

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
    df["t1_upper_wick_ratio"] = ((df["high"] - np.maximum(df["open"], df["close"])) / candle_range).clip(lower=0)

    df["smh_ma_20"] = df["smh"].rolling(20).mean()
    df["smh_ma_50"] = df["smh"].rolling(50).mean()

    df["soxl_ma_20"] = df["close"].rolling(20).mean()
    df["soxl_ma_50"] = df["close"].rolling(50).mean()
    df["soxl_dist"] = (df["soxl_ma_20"] - df["soxl_ma_50"]) / df["soxl_ma_50"]

    df = df.dropna(subset=["qqq_ma200", "smh_ma200", "tlt_ma150", "tnx_ma50"]).copy()

    # --- シグナル生成 ---
    cond_base = (df["vix"] >= 20) & (df["rsi2"] < 6) & (df["qqq"] > df["qqq_ma200"] * (1 + QQQ_GAP_BASE))
    cond_alert = (df["vix_ret5"] >= 0.15) & (df["vix_ret5"] <= 0.40) & (df["vvix_ret5"] >= 0.05) & (df["vvix_ret5"] <= 0.25)
    df["sig_base_alert"]  = (cond_base & cond_alert).fillna(False)
    df["sig_base_normal"] = (cond_base & ~cond_alert).fillna(False)
    df["sig_bb"] = ((df["close"] < df["bb_lower"]) & (df["smh"] > df["smh_ma150"])).fillna(False)
    df["sig_sc"] = ((df["vix"] >= 35) & (df["rsi2"] < 10)).fillna(False)
    df["sig_or3"] = (cond_base | df["sig_bb"] | df["sig_sc"]).fillna(False)
    df["sig_or4"] = (((df["qqq"] > df["qqq_ma200"]) & (df["smh"] > df["smh_ma200"]) & (df["vix"] >= 20) & (df["vix"] < 22) & (df["bb_z"] <= -1.7) & (df["bb_z"] > -2.5)) & (~df["sig_or3"])).fillna(False)

    df["sig_dip_rebound"] = ((df["qqq"] > df["qqq_ma150"]) & (df["smh"] > df["smh_ma150"]) & (df["rsi2"] <= 30) & (df["ret1"].shift(1) >= 0.025)).fillna(False)

    cond_gc = ((df["smh_ma_20"].shift(1) <= df["smh_ma_50"].shift(1)) & (df["smh_ma_20"] > df["smh_ma_50"]))
    hybrid_filter = (df["tlt"] > df["tlt_ma150"]) | (df["tnx"] < df["tnx_ma50"])

    df["sig_trend_gc"] = (cond_gc & (df["vix"] < 20) & hybrid_filter & (df["smh_obv"] > df["smh_obv_ma20"]) & ~(df["sig_or3"] | df["sig_or4"] | df["sig_dip_rebound"])).fillna(False)

    # ショート
    df["sig_soxs_pre"] = ((df["soxl_ma_20"] > df["soxl_ma_50"]) & (df["close"] < df["soxl_ma_20"]) & (df["soxl_dist"] < 0.010) & (df["vix_ret5"] > 0.10)).fillna(False)
    df["sig_soxs_bb"] = (df["close"] >= df["bb40_upper"]).fillna(False)
    df["sig_soxs_ma"] = ((df["ma75_dev"] >= SOXS_MA_MIN_DEV) & (df["ma75_dev"] <= SOXS_MA_MAX_DEV) & (df["prev_upper_wick_ratio"] >= 0.10) & (df["t1_upper_wick_ratio"] >= 0.05)).fillna(False)

    df['sig_sniper'] = ((df['soxl_ma_20'] < df['soxl_ma_50']) &
        (df['soxl_dist'] > -.004) & (df['close'] > df['soxl_ma_20']) &
        (df['vix'] < 20) & (df['smh_obv'] > df['smh_obv_ma20'])).fillna(False)
    if len(df) < 60:
        raise ValueError('指標を計算できる日足が不足しています。')
    df['smh_close'] = df['smh']
    df['smh_high'] = raw['SMH']['High'].reindex(df.index)
    df['smh_low'] = raw['SMH']['Low'].reindex(df.index)
    df['smh_ma20'], df['smh_ma50'] = df['smh_ma_20'], df['smh_ma_50']
    if not np.isfinite(df[['smh_high','smh_low','smh_close']]).all().all():
        raise ValueError('R3/YB用SMH価格に欠損があります。補完せず停止します。')
    smh_ohlc = raw['SMH'][['Open','High','Low','Close']].reindex(df.index)
    if (smh_ohlc.le(0).any().any() or
            smh_ohlc.High.lt(smh_ohlc.max(axis=1)-1e-8).any() or
            smh_ohlc.Low.gt(smh_ohlc.min(axis=1)+1e-8).any()):
        raise ValueError('SMHの日足に不正値があります。')
    df.attrs['unfilled_trade_ohlc'] = pd.concat([
        raw['SOXL'][['Open','High','Low','Close']].rename(columns=str.lower),
        raw['SOXS'][['Open','High','Low','Close']].rename(columns=lambda x:'soxs_'+x.lower())],axis=1).reindex(df.index)
    df.attrs['smh_history'] = raw['SMH'][['Close','High','Low']].rename(
        columns={'Close':'close','High':'high','Low':'low'})
    # 本体は従来どおり。YBだけは補完前の^TNXから判定する。
    df.attrs['tnx_raw'] = raw['TNX'][['Close']].rename(columns={'Close':'TNX'}).reindex(
        raw['TNX'].index.union(pd.DatetimeIndex([df.index[-1]])))
    yields = df.attrs['tnx_raw'].TNX.dropna()
    if not np.isfinite(yields).all() or yields.le(0).any() or (yields.index.day_of_week >= 5).any():
        raise ValueError('^TNXの日次価格に不正値があります。別系列へ置き換えず停止します。')
    return df

# 候補用の本体/R3再現。検証版と同じルールで固定枠を作る。
BASELINE_CORE_RULES = {tag: (p['tp'], p['sl'], p['hold'])
                       for tag, p in PARAMS.items() if tag not in (*HALF_ORDER, 'SNIPER')}
BASELINE_COST, BASELINE_HALF_WEIGHT = COST, .5
BASELINE_R3_TP, BASELINE_R3_SL, BASELINE_R3_HOLD = .18, .06, 4
BASELINE_YB_HOLD, BASELINE_RECENT = 10, 5
BASELINE_YIELD_LOOKBACK, BASELINE_STOCK_LOOKBACK = 10, 40
BASELINE_SOXS_LOCK, BASELINE_SC_LOCK = SOXS_LOCK_DAYS, SC_LOCK_DAYS
BASELINE_CORE_COLS = ['owner','sig_type','asset','signal_date','entry_date','exit_date',
    'entry_px','exit_px','exit_reason','timing','hold_days','gross_%','net_%','both_hit','status']

def baseline_core_events(d):
    # 元v19だけを先に再現し、日ごとの売買イベントを記録する。
    state = pd.DataFrame({"v19_pos": "未判定", "v19_next": "", "v19_free": False}, index=d.index)
    actions = [[] for _ in range(len(d))]
    trades = []
    pos, tag, pending, pending_exit = "CASH", None, None, False
    last_ma_sl = last_sc_sl = -999
    entry_i, entry_px = 0, np.nan
    tp = sl = hold = None

    def sell(i, px, reason, timing):
        actions[i].append(("SELL", tag, pos, float(px), reason, timing))
        trades.append((d.index[entry_i], d.index[i], tag, pos, reason, px / entry_px - 1))

    for i in range(1, len(d)):
        row = d.iloc[i]
        if pending_exit and pos != "CASH":
            sell(i, row.open if pos == "SOXL" else row.soxs_open, "TIME", "寄り")
            pos, pending_exit = "CASH", False
        if pending is not None and pos == "CASH":
            tag = pending
            if tag == "_PRIMARY":
                prev = d.iloc[i - 1]
                tag = next((name for col, name in [("sig_sc", "SC"), ("sig_base_alert", "base_alert"),
                            ("sig_base_normal", "base_normal"), ("sig_bb", "bb")]
                            if bool(prev[col])), "OR4")
            pos = "SOXS" if tag.startswith("SOXS") else "SOXL"
            entry_i, entry_px = i, float(row.soxs_open if pos == "SOXS" else row.open)
            tp, sl, hold = BASELINE_CORE_RULES[tag]
            actions[i].append(("BUY", tag, pos, entry_px, "", "寄り"))
            pending = None
        if pos != "CASH":
            prefix = "soxs_" if pos == "SOXS" else ""
            o, h, l = [float(row[prefix + x]) for x in ["open", "high", "low"]]
            upper, lower = entry_px * (1 + tp), entry_px * (1 + sl)
            px, reason, timing = None, None, "日中"
            if o >= upper:
                px, reason, timing = o, "TP", "寄り"
            elif o <= lower:
                px, reason, timing = o, "SL", "寄り"
            elif l <= lower:
                px, reason = lower, "SL"
            elif h >= upper:
                px, reason = upper, "TP"
            if reason is not None:
                sell(i, px, reason, timing)
                if tag == "SOXS_MA":
                    last_ma_sl = i if reason == "SL" else -999
                if tag == "SC":
                    last_sc_sl = i if reason == "SL" else -999
                pos, pending_exit = "CASH", False
            elif i - entry_i + 1 >= hold:
                pending_exit = True
        primary = bool(row.sig_or3 or row.sig_or4)
        if row.sig_sc and i - last_sc_sl <= BASELINE_SC_LOCK:
            primary = bool(row.sig_base_alert or row.sig_base_normal or row.sig_bb or row.sig_or4)
        long_tag = ("_PRIMARY" if primary else "DIP_REBOUND" if row.sig_dip_rebound
                    else "TREND_GC" if row.sig_trend_gc else None)
        ma = bool(row.sig_soxs_ma and row.vix < 20 and i - last_ma_sl > BASELINE_SOXS_LOCK)
        short_tag = ("SOXS_PRE_DC" if row.sig_soxs_pre else "SOXS_BB" if row.sig_soxs_bb
                     else "SOXS_MA" if ma else None)
        if pos == "CASH":
            pending = long_tag or short_tag
        elif pos == "SOXS" and long_tag:
            pending_exit, pending = True, long_tag
        state.loc[d.index[i]] = [pos, pending or "", pos == "CASH" and pending is None]
    cols = ["entry_date", "exit_date", "sig_type", "asset", "exit_reason", "ret"]
    return state, pd.DataFrame(trades, columns=cols), actions

def baseline_rejection_flags(d):
    close, ma = d.smh_close, d.smh_ma20
    valid = (close.rolling(10).mean().notna() & ma.notna()
             & d.smh_ma50.shift(10).notna() & d.smh_low.shift(1).rolling(3).min().notna())
    valid.iloc[0] = False
    trend = valid & close.lt(d.smh_ma50) & d.smh_ma50.lt(d.smh_ma50.shift(10))
    above = close.ge(ma)
    recent = above.shift(1, fill_value=False).rolling(3, min_periods=1).max().eq(1)
    candidate = (trend & recent & close.lt(ma) & close.lt(d.smh_low.shift(1))).fillna(False)
    flags = pd.Series(False, index=d.index)
    last_above, used = -10**9, True
    for i in range(len(d)):
        if above.iloc[i]:
            last_above, used = i, False
        elif not used and i - last_above <= 3 and candidate.iloc[i]:
            flags.iloc[i], used = True, True
    # QQQ条件は最初のR3点灯日だけで判定。後日条件が揃っても追いかけない。
    qma = d.qqq.rolling(50).mean()
    return flags, d.qqq.lt(qma), qma

def baseline_reference_r3(d, state, actions, eligible, sl, cost, r3_weight):
    cash, qty, position, pending_r3 = 1.0, 0.0, None, False
    equity, held, ledger = np.ones(len(d)), np.zeros(len(d), bool), []
    skipped = 0
    exposure = np.zeros(len(d))

    def buy(i, owner, tag, asset, px):
        nonlocal cash, qty, position
        if position is not None:
            raise AssertionError("保有が重複しました")
        budget = cash * (r3_weight if owner == "R3" else 1.0)
        qty, cash = budget / (px * (1 + cost)), cash - budget
        position = {"owner": owner, "sig_type": tag, "asset": asset,
                    "signal_date": d.index[i - 1], "entry_date": d.index[i],
                    "entry_px": px, "entry_i": i}

    def sell(i, px, reason, timing, both=False):
        nonlocal cash, qty, position
        if position is None:
            raise AssertionError("未保有の決済です")
        rec = position.copy()
        entry = rec.pop("entry_i")
        cash, qty = cash + qty * px * (1 - cost), 0.0
        rec.update(exit_date=d.index[i], exit_px=px, exit_reason=reason, timing=timing,
                   hold_days=i - entry + (timing != "寄り"),
                   both_hit=both, status="CLOSED")
        rec["gross_%"] = (px / rec["entry_px"] - 1) * 100
        rec["net_%"] = (px / rec["entry_px"] * (1 - cost) / (1 + cost) - 1) * 100
        ledger.append(rec)
        position = None

    for i in range(1, len(d)):
        row = d.iloc[i]
        if pending_r3:
            buy(i, "R3", "R3", "SOXS", float(row.soxs_open))
            pending_r3 = False
        for kind, tag, asset, px, reason, timing in actions[i]:
            if kind == "BUY":
                if position is not None and position["owner"] == "R3":
                    sell(i, float(row.soxs_open), "v19:" + tag, "寄り")
                buy(i, "v19", tag, asset, px)
            else:
                if position is None or position["owner"] != "v19" or position["sig_type"] != tag:
                    raise AssertionError("元v19の決済と不一致です")
                sell(i, px, reason, timing)
        if position is not None and position["owner"] == "R3":
            px = position["entry_px"]
            upper, lower = px * (1 + BASELINE_R3_TP), px * (1 - sl)
            o, h, l = float(row.soxs_open), float(row.soxs_high), float(row.soxs_low)
            if o >= upper:
                sell(i, o, "TP", "寄り")
            elif o <= lower:
                sell(i, o, "SL", "寄り")
            elif l <= lower:
                sell(i, lower, "SL", "日中", h >= upper)
            elif h >= upper:
                sell(i, upper, "TP", "日中")
            elif i - position["entry_i"] + 1 >= BASELINE_R3_HOLD:
                sell(i, float(row.soxs_close), "TIME", "引け")
        if state.v19_pos.iloc[i] != "CASH":
            if position is None or position["owner"] != "v19" or position["asset"] != state.v19_pos.iloc[i]:
                raise AssertionError("元v19の保有が維持されていません")
        elif position is not None and position["owner"] == "v19":
            raise AssertionError("元v19の保有と不一致です")
        held[i] = position is not None
        mark = (float(row.soxs_close) if position["asset"] == "SOXS" else float(row.close)) if held[i] else 0
        equity[i] = cash + qty * mark
        exposure[i] = qty * mark / equity[i]
        if eligible.iloc[i]:
            if not state.v19_free.iloc[i]:
                raise AssertionError("v19の空き時間以外でR3注文が出ました")
            if position is None:
                pending_r3 = True
            else:
                skipped += 1
    if position is not None:
        rec = position.copy()
        entry = rec.pop("entry_i")
        rec.update(exit_date=pd.NaT, exit_px=mark, exit_reason="OPEN", timing="評価中",
                   hold_days=len(d) - entry, both_hit=False, status="OPEN")
        rec["gross_%"] = (mark / rec["entry_px"] - 1) * 100
        rec["net_%"] = (mark / rec["entry_px"] / (1 + cost) - 1) * 100
        ledger.append(rec)
    return (pd.Series(equity, index=d.index), pd.Series(held, index=d.index),
            pd.DataFrame(ledger, columns=BASELINE_CORE_COLS), skipped, pending_r3,
            pd.Series(exposure, index=d.index))

def baseline_rate_calendar(raw):
    holidays = USFederalHolidayCalendar().holidays(start=raw.index[0], end=raw.index[-1])
    holidays = holidays.union(GoodFriday.dates(raw.index[0], raw.index[-1]))
    expected = pd.bdate_range(raw.index[0], raw.index[-1]).difference(holidays)
    # 休場の近似。実値がある休日は採用。通常営業日の未取得はNaNのまま残す。
    return expected.union(raw.index[raw.TNX.notna()]).sort_values()

def baseline_available_rates(observations, stock_index):
    # pandas 3系では自動生成した日付の精度がs/us等で異なる。値は動かさずnsに統一。
    stock_index = pd.DatetimeIndex(stock_index).as_unit('ns')
    observations = observations.copy()
    observations.index = pd.DatetimeIndex(observations.index).as_unit('ns')
    observations['assumed_release_date'] = pd.to_datetime(
        observations['assumed_release_date']).astype('datetime64[ns]')
    if not stock_index.is_monotonic_increasing or not stock_index.is_unique:
        raise ValueError('株式営業日は昇順・重複なしが必要です。')
    right = observations.reset_index().sort_values(['assumed_release_date', 'observation_date'])
    known = pd.merge_asof(pd.DataFrame({'decision_date': stock_index}), right,
        left_on='decision_date', right_on='assumed_release_date', direction='backward',
        allow_exact_matches=True).set_index('decision_date')
    known.index.name = stock_index.name
    result = known[['observation_date', 'assumed_release_date', 'TNX', 'previous_high10']].copy()
    result['rate_valid'] = known.valid.eq(True)
    slots = stock_index.searchsorted(right.assumed_release_date.to_numpy(dtype='datetime64[ns]'))
    keep = right.break_up.to_numpy(bool) & (slots < len(stock_index))
    chosen = slots[keep]
    result['available_break_up'] = stock_index.isin(stock_index[np.unique(chosen)])
    events = pd.Series(pd.NaT, index=stock_index, dtype='datetime64[ns]')
    for slot, observed in zip(chosen, right.loc[keep, 'observation_date']):
        events.iloc[slot] = observed
    result['recent_break_up'] = result.rate_valid & result.available_break_up.rolling(BASELINE_RECENT, min_periods=1).max().eq(1)
    result['recent_event_observation'] = events.ffill().where(result.recent_break_up)
    result['input_asof_date'] = stock_index
    visible = result.observation_date.notna()
    if not (result.loc[visible, 'observation_date'].le(result.loc[visible, 'assumed_release_date']).all()
            and result.loc[visible, 'assumed_release_date'].le(result.index[visible]).all()):
        raise AssertionError('^TNXの利用開始日前に判定しています。')
    return result

def baseline_build_shadow_slots(d, positions, buys):
    # 金利通過・実Cの早期決済に関係なく、10日または既存注文まで仮想枠を占有。
    positions = np.asarray(positions, dtype=int)
    if len(positions) and (positions.min() < 1 or positions.max() >= len(d)
                          or (np.diff(positions) <= 0).any()):
        raise ValueError('仮想枠の候補日は昇順・重複なし・検証期間内が必要です。')
    candidates, buy_set = set(positions.tolist()), set(np.asarray(buys, dtype=int).tolist())
    pending, active, rows, audit = None, None, [], []
    def record(signal, entry, out, reason, timing, status):
        return {'signal_date': d.index[signal],
            'entry_date': d.index[entry] if entry is not None else pd.NaT,
            'exit_date': d.index[out] if out is not None else pd.NaT,
            'exit_reason': reason, 'timing': timing,
            'hold_days': (out-entry+(timing != '寄り') if out is not None else
                          len(d)-entry if entry is not None else 0), 'status': status}
    for i in range(1, len(d)):
        if pending is not None:
            if active is not None or i in buy_set:
                raise AssertionError('仮想枠の購入と既存注文が重複しています。')
            active, pending = (pending, i), None
        if active is not None:
            signal, entry = active
            switch = i > entry and i in buy_set
            if switch or i == entry + BASELINE_YB_HOLD - 1:
                rows.append(record(signal, entry, i, '既存へ交代' if switch else 'TIME',
                                   '寄り' if switch else '引け', 'CLOSED'))
                active = None
        if i in candidates:
            chosen = active is None
            audit.append({'signal_date': d.index[i], '基準枠採用': chosen,
                          '基準枠起点': d.index[i if chosen else active[0]]})
            if chosen:
                pending = i
    if active is not None:
        rows.append(record(*active, None, 'OPEN', '評価中', 'OPEN'))
    if pending is not None:
        rows.append(record(pending, None, None, 'WAITING', '未購入', 'WAITING'))
    columns = ['signal_date', 'entry_date', 'exit_date', 'exit_reason', 'timing', 'hold_days', 'status']
    decisions = pd.DataFrame(audit, columns=['signal_date', '基準枠採用', '基準枠起点'])
    decisions = decisions.set_index('signal_date').reindex(d.index[positions].rename('signal_date'))
    decisions['基準枠採用'] = decisions['基準枠採用'].astype(bool)
    decisions['基準枠起点'] = pd.to_datetime(decisions['基準枠起点'])
    return pd.DataFrame(rows, columns=columns), decisions

def baseline_yield_observations(raw):
    p = raw.reindex(baseline_rate_calendar(raw)).copy().rename_axis('observation_date')
    y = p.TNX
    p['previous_high10'] = y.shift(1).rolling(BASELINE_YIELD_LOOKBACK,min_periods=BASELINE_YIELD_LOOKBACK).max()
    p['valid'] = np.isfinite(p[['TNX','previous_high10']]).all(axis=1)
    above = p.valid & y.gt(p.previous_high10)
    p['break_up'] = above & ~above.shift(1,fill_value=False)
    p['assumed_release_date'] = p.index
    return p

def baseline_stock_breakout(history):
    previous = history.high.shift(1).rolling(BASELINE_STOCK_LOOKBACK,min_periods=BASELINE_STOCK_LOOKBACK).max()
    valid = np.isfinite(history.close) & np.isfinite(previous)
    above = history.close.gt(previous)
    return (valid & valid.shift(1,fill_value=False) & above & ~above.shift(1,fill_value=False)).astype(bool)

def prepare_candidates(df):
    """実口座の状態を変更せず、採用済みv20と同じ独立候補列を作る。"""
    state, _, actions = baseline_core_events(df)
    r3_raw, _, _ = baseline_rejection_flags(df)
    r3 = r3_raw & state.v19_free
    _, _, trades, _, pending, exposure = baseline_reference_r3(
        df, state, actions, r3, BASELINE_R3_SL, COST, .5)
    reserved = pd.Series(df.index.isin(pd.to_datetime(trades.signal_date)), index=df.index)
    if pending:
        reserved.iloc[-1] = True
    free = state.v19_free & exposure.eq(0) & ~reserved
    history = df.attrs['smh_history']
    observations = baseline_yield_observations(df.attrs['tnx_raw'])
    rates = baseline_available_rates(observations, history.index).reindex(df.index)
    breakout = baseline_stock_breakout(history).reindex(df.index, fill_value=False)
    breakout.iloc[0] = False
    candidate = breakout & free & rates.rate_valid
    buys = np.unique(df.index.get_indexer(pd.to_datetime(trades.entry_date)))
    _, slots = baseline_build_shadow_slots(df, np.flatnonzero(candidate.to_numpy(bool)), buys)
    shadow = slots['基準枠採用'].reindex(df.index, fill_value=False).astype(bool)
    result = pd.DataFrame({'R3': r3, 'YB': shadow & rates.rate_valid & rates.recent_break_up},
                          index=df.index).astype(bool)
    diagnostics = pd.DataFrame({'R3_raw': r3_raw, 'YB_breakout': breakout,
        'baseline_free': free, 'YB_shadow': shadow,
        'rate_valid': rates.rate_valid, 'rate_recent': rates.recent_break_up,
        'TNX': rates.TNX, 'rate_observation_date': rates.observation_date}, index=df.index)
    return result, diagnostics


def count_hold_days(df, entry_date, current_date):
    if not entry_date:
        return 0
    return int(len(df.loc[pd.Timestamp(entry_date):pd.Timestamp(current_date)]))


def days_since(df, previous, current):
    return count_hold_days(df, previous, current) - 1 if previous else 10**9


def core_choice(row, sc_locked, ma_locked):
    # 本体の優先順位・SCロック判定は検証版v20を維持する。
    primary = bool(row.sig_or3 or row.sig_or4)
    if bool(row.sig_sc) and sc_locked:
        primary = bool(row.sig_base_alert or row.sig_base_normal or row.sig_bb or row.sig_or4)
    long = None
    if primary:
        long = next((name for col, name in [('sig_sc', 'SC'),
            ('sig_base_alert', 'base_alert'), ('sig_base_normal', 'base_normal'),
            ('sig_bb', 'bb')] if bool(row[col])), 'OR4')
    elif bool(row.sig_dip_rebound):
        long = 'DIP_REBOUND'
    elif bool(row.sig_trend_gc):
        long = 'TREND_GC'
    short = ('SOXS_PRE_DC' if bool(row.sig_soxs_pre) else
             'SOXS_BB' if bool(row.sig_soxs_bb) else
             'SOXS_MA' if bool(row.sig_soxs_ma) and row.vix < 20 and not ma_locked else None)
    return long, short


def default_state():
    return dict(schema_version=20, position='CASH', sig_type=None,
        entry_price=None, entry_date=None, entry_signal_date=None, hold_days=0, lot_fraction=0.,
        pending_entry=None, pending_entry_sig_type=None, pending_entry_signal_date=None,
        pending_entry_lot_fraction=None, pending_exit_next_open=False,
        pending_exit_reason=None, pending_exit_signal_date=None,
        last_soxs_ma_sl_date=None, last_sc_sl_date=None,
        sniper_pos=False, sniper_ep=None, sniper_ed=None,
        sniper_pending_entry=False, sniper_pending_exit=False,
        sniper_pending_entry_signal_date=None, sniper_pending_exit_signal_date=None,
        last_processed_date=None, half_activation_date=None, outbox=[])

def normalize_state(saved, df):
    """旧stateを保有・予約ごと引き継ぐ。同じ日足を二回売買処理しない。"""
    state = default_state()
    state.update(copy.deepcopy(saved))
    legacy = saved.get('schema_version') != 20
    latest = df.index[-1]
    if state.get('sig_type'):
        state['sig_type'] = canonical_tag(state['sig_type'])
        strategy_label(state['sig_type'])
    if state.get('pending_entry_sig_type'):
        state['pending_entry_sig_type'] = canonical_tag(state['pending_entry_sig_type'])
        strategy_label(state['pending_entry_sig_type'])
    if state['position'] not in ('CASH', 'SOXL', 'SOXS'):
        raise ValueError('state.json の保有銘柄が不正です。')
    if state['position'] != 'CASH':
        if not state.get('sig_type') or not state.get('entry_date') or not state.get('entry_price'):
            raise ValueError('保有中stateの戦略名・買付日・価格が不足しています。')
        state['lot_fraction'] = lot_for(state['sig_type'])
    else:
        state['lot_fraction'] = 0.
    if state.get('pending_entry'):
        if not state.get('pending_entry_sig_type') or not state.get('pending_entry_signal_date'):
            raise ValueError('買付予約の日付・戦略名が不足しています。')
        state['pending_entry_lot_fraction'] = lot_for(state['pending_entry_sig_type'])

    if not state.get('last_processed_date'):
        explicit = os.environ.get('LEGACY_STATE_ASOF', '')
        anchor = pd.Timestamp(explicit) if explicit else None
        if anchor is None and state.get('pending_entry_signal_date'):
            anchor = pd.Timestamp(state['pending_entry_signal_date'])
        if anchor is None and state['position'] != 'CASH' and state.get('hold_days', 0) > 0:
            entry_i = int(df.index.searchsorted(pd.Timestamp(state['entry_date'])))
            asof_i = entry_i + int(state['hold_days']) - 1
            if asof_i >= len(df):
                raise ValueError('旧stateの保有日数が価格期間を超えています。')
            anchor = df.index[asof_i]
        if anchor is None and state.get('sniper_pos'):
            # 旧サブ口座には日次カウンターがない。保有を維持して最新日から再開。
            anchor = latest
        if anchor is None and (state.get('sniper_pending_entry') or state.get('sniper_pending_exit')):
            anchor = latest
        if anchor is None:
            anchor = df.index[-2]
        if anchor > latest or anchor < df.index[0]:
            raise ValueError('state.json の処理日が取得価格の期間外です。')
        state['last_processed_date'] = str(anchor.date())

    anchor = pd.Timestamp(state['last_processed_date'])
    if anchor > latest or anchor < df.index[0]:
        raise ValueError('state.json と価格データの日付が逆転しています。状態は更新しません。')
    if state.get('pending_exit_next_open') and not state.get('pending_exit_signal_date'):
        state['pending_exit_signal_date'] = state['last_processed_date']
    for kind in ('entry', 'exit'):
        key = f'sniper_pending_{kind}_signal_date'
        if state.get(f'sniper_pending_{kind}') and not state.get(key):
            state[key] = state['last_processed_date']
    state['schema_version'] = 20
    state['half_activation_date'] = state.get('half_activation_date') or str(latest.date())
    return state, legacy


def main_step(state, df, i, flags):
    """一つの確定日足を処理する。stateは呼び出し元のコピーだけを変更する。"""
    row, date = df.iloc[i], str(df.index[i].date())
    events = []

    def event(kind, tag, asset, **extra):
        record = dict(date=date, kind=kind, strategy=tag, asset=asset,
                      lot_fraction=lot_for(tag), **extra)
        events.append(record)

    def sell(px, reason, timing, both=False):
        tag, asset, ep = state['sig_type'], state['position'], float(state['entry_price'])
        net = px / ep * (1 - COST) / (1 + COST) - 1
        event('EXIT', tag, asset, price=float(px), reason=reason, timing=timing,
              both_hit=bool(both), net_pct=net*100,
              hold_days=count_hold_days(df, state['entry_date'], date)-(timing == '寄り'),
              entry_date=state['entry_date'])
        if reason in ('TP', 'SL'):
            if tag == 'SC':
                state['last_sc_sl_date'] = date if reason == 'SL' else None
            if tag == 'SOXS_MA':
                state['last_soxs_ma_sl_date'] = date if reason == 'SL' else None
        state.update(position='CASH', sig_type=None, entry_price=None, entry_date=None,
            entry_signal_date=None, hold_days=0, lot_fraction=0.,
            pending_exit_next_open=False, pending_exit_reason=None, pending_exit_signal_date=None)

    def opening(asset):
        return float(row.soxs_open if asset == 'SOXS' else row.open)

    if state.get('pending_exit_next_open') and pd.Timestamp(state['pending_exit_signal_date']) < df.index[i]:
        if state['position'] == 'CASH':
            raise ValueError('未保有の売却予約があります。')
        sell(opening(state['position']), state.get('pending_exit_reason') or 'TIME', '寄り')

    if state.get('pending_entry') and pd.Timestamp(state['pending_entry_signal_date']) < df.index[i]:
        tag = state['pending_entry_sig_type']
        asset = state['pending_entry']
        signal_date = state['pending_entry_signal_date']
        if state['position'] != 'CASH':
            if tag in HALF_ORDER or state['sig_type'] not in HALF_ORDER:
                raise ValueError('許可されていない保有交代です。')
            sell(opening(state['position']), '本体へ交代', '寄り')
        px = opening(asset)
        state.update(position=asset, sig_type=tag, entry_price=px, entry_date=date,
            entry_signal_date=signal_date, hold_days=1, lot_fraction=lot_for(tag),
            pending_entry=None, pending_entry_sig_type=None, pending_entry_signal_date=None,
            pending_entry_lot_fraction=None)
        event('ENTRY', tag, asset, price=px, timing='寄り')

    if state['position'] != 'CASH':
        tag, ep = state['sig_type'], float(state['entry_price'])
        p = PARAMS[tag]
        hd = count_hold_days(df, state['entry_date'], date)
        state['hold_days'] = hd
        prefix = 'soxs_' if state['position'] == 'SOXS' else ''
        o, h, l = [float(row[prefix+k]) for k in ('open', 'high', 'low')]
        upper, lower = ep*(1+p['tp']), ep*(1+p['sl'])
        eps = ep*1e-10 if tag == 'YB' else 0.
        if o >= upper-eps:
            sell(o, 'TP', '寄り')
        elif o <= lower+eps:
            sell(o, 'SL', '寄り')
        elif l <= lower+eps:
            sell(lower, 'SL', '日中', h >= upper-eps)
        elif h >= upper-eps:
            sell(upper, 'TP', '日中')
        elif hd >= p['hold']:
            if tag in HALF_ORDER:
                sell(float(row[prefix+'close']), 'TIME', '引け')
            else:
                state.update(pending_exit_next_open=True, pending_exit_reason='TIME',
                             pending_exit_signal_date=date)
                event('EXIT_ORDER', tag, state['position'], reason='TIME')

    sc_locked = days_since(df, state.get('last_sc_sl_date'), date) <= SC_LOCK_DAYS
    ma_locked = days_since(df, state.get('last_soxs_ma_sl_date'), date) <= SOXS_LOCK_DAYS
    long, short = core_choice(row, sc_locked, ma_locked)
    tag = long or short
    held_half = state['sig_type'] in HALF_ORDER
    full_switch = state['position'] == 'SOXS' and not held_half and bool(long)
    if tag and (state['position'] == 'CASH' or held_half or full_switch):
        tag = long if full_switch else tag
        if full_switch:
            state.update(pending_exit_next_open=True, pending_exit_reason='本体ロングへ交代',
                         pending_exit_signal_date=date)
        state.update(pending_entry='SOXS' if tag.startswith('SOXS') else 'SOXL',
            pending_entry_sig_type=tag, pending_entry_signal_date=date,
            pending_entry_lot_fraction=1.)
        event('ENTRY_ORDER', tag, state['pending_entry'],
              replaces=state['sig_type'] if state['position'] != 'CASH' else None)

    active = not state.get('half_activation_date') or df.index[i] >= pd.Timestamp(state['half_activation_date'])
    for tag in HALF_ORDER:
        if not active or not bool(flags[tag]):
            continue
        if state['position'] == 'CASH' and not state.get('pending_entry'):
            state.update(pending_entry=HALF_ASSETS[tag], pending_entry_sig_type=tag,
                pending_entry_signal_date=date, pending_entry_lot_fraction=.5)
            event('ENTRY_ORDER', tag, HALF_ASSETS[tag], replaces=None)
        else:
            event('SKIP', tag, HALF_ASSETS[tag], reason='保有・本体注文を優先（後追いなし）')
    return events


def sniper_step(state, df, i):
    """旧版のサブ口座ロジックを維持。メインの半量枠とは独立。"""
    row, date = df.iloc[i], str(df.index[i].date())
    events = []
    if state.get('sniper_pending_exit') and pd.Timestamp(state['sniper_pending_exit_signal_date']) < df.index[i]:
        events.append(f'{date} SOXL売却完了：期限・寄り {row.open:.2f}')
        state.update(sniper_pos=False, sniper_ep=None, sniper_ed=None,
            sniper_pending_exit=False, sniper_pending_exit_signal_date=None)
    elif state.get('sniper_pending_entry') and pd.Timestamp(state['sniper_pending_entry_signal_date']) < df.index[i]:
        state.update(sniper_pos=True, sniper_ep=float(row.open), sniper_ed=date,
            sniper_pending_entry=False, sniper_pending_entry_signal_date=None)
        events.append(f'{date} SOXL買付完了：寄り {row.open:.2f}')
    elif state.get('sniper_pos') and state.get('sniper_ep'):
        ep = float(state['sniper_ep'])
        hd = count_hold_days(df, state['sniper_ed'], date)
        if row.low <= ep*.90:
            state.update(sniper_pos=False, sniper_ep=None, sniper_ed=None)
            events.append(f'{date} SOXL売却：SL {ep*.90:.2f}')
        elif row.high >= ep*1.16:
            state.update(sniper_pos=False, sniper_ep=None, sniper_ed=None)
            events.append(f'{date} SOXL売却：TP {ep*1.16:.2f}')
        elif hd >= 20:
            state.update(sniper_pending_exit=True, sniper_pending_exit_signal_date=date)
            events.append(f'{date} SOXL売却予約：20日到達・翌営業日寄り')
    if not state.get('sniper_pos') and not state.get('sniper_pending_entry') and not state.get('sniper_pending_exit'):
        if bool(row.sig_sniper):
            state.update(sniper_pending_entry=True, sniper_pending_entry_signal_date=date)
            events.append(f'{date} SOXL買付予約：翌営業日寄り')
    return events


def advance_state(saved, df, flags):
    state, upgraded = normalize_state(saved, df)
    dates = df.index[df.index > pd.Timestamp(state['last_processed_date'])]
    events, sniper_events = [], []
    for date in dates:
        i = int(df.index.get_loc(date))
        # 前回以降に欠損日があれば、不完全なOHLCで約定判定しない。
        required = ['open','high','low','close','soxs_open','soxs_high','soxs_low','soxs_close']
        prices = df.attrs.get('unfilled_trade_ohlc', df).loc[date, required].to_numpy(dtype=float)
        if not np.isfinite(prices).all() or (prices <= 0).any():
            raise ValueError('未処理日の売買価格に欠損・不正値があります。状態は保存しません。')
        for offset in (0, 4):
            o, h, l, c = prices[offset:offset+4]
            if h < max(o, c)-1e-8 or l > min(o, c)+1e-8 or h < l:
                raise ValueError('未処理日のOHLC関係が不正です。状態は保存しません。')
        events.extend(main_step(state, df, i, flags.loc[date]))
        sniper_events.extend(sniper_step(state, df, i))
        state['last_processed_date'] = str(date.date())
    return state, events, sniper_events, bool(len(dates) or upgraded), upgraded


def format_event(e):
    head = f"{e['date']} {strategy_label(e['strategy'])} / {e['asset']} / {lot_label(e['strategy'])}"
    if e['kind'] == 'ENTRY':
        return f"{head}\n  買付想定：寄り {e['price']:.2f}"
    if e['kind'] == 'EXIT':
        both = '（同日両到達・SL優先）' if e.get('both_hit') else ''
        return (f"{head}\n  売却想定：{e['reason']}・{e['timing']} {e['price']:.2f}{both}"
                f" / 購入額比損益 {e['net_pct']:+.2f}%（往復費用込み）")
    if e['kind'] == 'ENTRY_ORDER':
        replacement = f"（{strategy_label(e['replaces'])}保有から本体へ交代）" if e.get('replaces') else ''
        return f"{head}\n  翌営業日寄りの買付予約{replacement}"
    if e['kind'] == 'EXIT_ORDER':
        return f"{head}\n  保有期限到達：翌営業日寄りの売却予約"
    return f"{head}\n  見送り：{e['reason']}"


def build_message(df, state, flags, diagnostics, events, sniper_events, upgraded=False):
    row, day = df.iloc[-1], df.index[-1]
    yn = lambda value: '✅' if bool(value) else '❌'
    sc_age = days_since(df, state.get('last_sc_sl_date'), day)
    ma_age = days_since(df, state.get('last_soxs_ma_sl_date'), day)
    sc_locked, ma_locked = sc_age <= SC_LOCK_DAYS, ma_age <= SOXS_LOCK_DAYS
    diag = diagnostics.iloc[-1]
    lines = [f'【SOXL戦略 v20 日次レポート {day.date()}】']
    if upgraded:
        lines.append('通知形式を更新。既存の保有・予約を引き継ぎました。')
    lines.extend(['', '📊 マーケット指標',
        f"VIX：{row.vix:.2f}（5日 {row.vix_ret5*100:+.1f}%）",
        f"VVIX：{row.vvix:.2f}（5日 {row.vvix_ret5*100:+.1f}%）",
        f"SOXL RSI2：{row.rsi2:.2f} / bb_z：{row.bb_z:.2f}",
        f"QQQ vs 200MA：{(row.qqq/row.qqq_ma200-1)*100:+.2f}%",
        f"SMH vs 200MA：{(row.smh/row.smh_ma200-1)*100:+.2f}%",
        f"SMH OBV > MA20：{yn(row.smh_obv > row.smh_obv_ma20)}",
        f"^TNX 上方10日ブレイク・直近5日：{yn(diag.rate_valid and diag.rate_recent)}",
        '', '📡 メイン口座 シグナル（戦略ごと）'])
    signal_names = [('sig_sc', 'SC'), ('sig_base_alert', 'base_alert'),
        ('sig_base_normal', 'base_normal'), ('sig_bb', 'bb'), ('sig_or4', 'OR4'),
        ('sig_dip_rebound', 'DIP_REBOUND'), ('sig_trend_gc', 'TREND_GC'),
        ('sig_soxs_pre', 'SOXS_PRE_DC'), ('sig_soxs_bb', 'SOXS_BB'),
        ('sig_soxs_ma', 'SOXS_MA')]
    for col, tag in signal_names:
        enabled = bool(row[col])
        note = ''
        if tag == 'SC' and sc_locked:
            note = f' / 🔒SL後ロック中（あと{SC_LOCK_DAYS+1-sc_age}営業日）'
        if tag == 'SOXS_MA':
            enabled = enabled and row.vix < 20 and not ma_locked
            if ma_locked:
                note = f' / 🔒SL後ロック中（あと{SOXS_LOCK_DAYS+1-ma_age}営業日）'
            elif row.vix >= 20:
                note = ' / VIX条件外'
        lines.append(f'{strategy_label(tag)} / {lot_label(tag)}：{yn(enabled)}{note}')
    for tag in HALF_ORDER:
        note = ''
        if tag == 'R3' and bool(diag.R3_raw) and not bool(flags[tag].iloc[-1]):
            note = ' / 条件点灯・基準の空き枠なし'
        if tag == 'YB' and not bool(diag.rate_valid):
            note = ' / 金利データ不足のため見送り'
        lines.append(f'{strategy_label(tag)} / {lot_label(tag)}：{yn(flags[tag].iloc[-1])}{note}')

    lines.extend(['', '🏃 メイン口座 アクション'])
    if events:
        lines.extend(format_event(e) for e in events)
    else:
        lines.append('売買・新規予約の変更なし')
    lines.extend(['', '💼 メイン口座 ポジション'])
    if state['position'] == 'CASH':
        lines.append('現在：現金')
    else:
        tag, ep = state['sig_type'], float(state['entry_price'])
        p = PARAMS[tag]
        mark = float(row.soxs_close if state['position'] == 'SOXS' else row.close)
        lines.extend([f"現在：{state['position']} / {strategy_label(tag)} / {lot_label(tag)}",
            f"買付：{state['entry_date']} {ep:.2f} / 保有{state['hold_days']}/{p['hold']}日",
            f"購入額比の含み損益：{(mark/ep-1)*100:+.2f}%（費用前）",
            f"TP：{ep*(1+p['tp']):.2f}（+{p['tp']*100:g}%） / SL：{ep*(1+p['sl']):.2f}（{p['sl']*100:g}%）"])
    if state.get('pending_exit_next_open'):
        lines.append(f"翌営業日寄り：{strategy_label(state['sig_type'])} / {lot_label(state['sig_type'])}を売却予定")
    if state.get('pending_entry'):
        tag = state['pending_entry_sig_type']
        p = PARAMS[tag]
        lines.extend([f"翌営業日寄りの買付予約：{state['pending_entry']} / {strategy_label(tag)} / {lot_label(tag)}",
            f"TP+{p['tp']*100:g}% / SL{p['sl']*100:g}% / {p['hold']}日",
            '保有から交代する場合は、旧保有を寄りで全売却してから買付。' if state['position'] != 'CASH' else ''])
    lines.extend(['半量50%＝買付直前資産の50%を購入費用込みで投入。残りは現金。',
        '本体優先。ハーフ同士は先着・切替なし。同時点灯だけR3 > YB。',
        '', '🎯 サブ口座：SOXL Sniper（独立枠）', f"シグナル：{yn(row.sig_sniper)}"])
    lines.extend(sniper_events or ['売買・予約の変更なし'])
    if state.get('sniper_pos'):
        ep = float(state['sniper_ep'])
        hd = count_hold_days(df, state['sniper_ed'], day)
        lines.extend([f'SOXL保有中：買付 {ep:.2f} / 保有{hd}/20日',
            f'購入額比の含み損益：{(row.close/ep-1)*100:+.2f}%（費用前）',
            f'TP：{ep*1.16:.2f}（+16%） / SL：{ep*.90:.2f}（-10%）'])
    if state.get('sniper_pending_exit'):
        lines.append('翌営業日寄り：SOXL売却予定（20日到達）')
    if state.get('sniper_pending_entry'):
        lines.append('翌営業日寄り：SOXL買付予約')
    lines.extend(['', '確定済み日足による判定・約定想定です。実際の約定を取得する機能はありません。',
                  'ギャップは寄り値を使用。SLは損失上限ではありません。'])
    return '\n'.join(line for line in lines if line is not None)


def load_state():
    if not STATE_PATH.exists():
        return {}
    with STATE_PATH.open(encoding='utf-8') as f:
        state = json.load(f)
    if not isinstance(state, dict):
        raise ValueError('state.json の形式が不正です。')
    return state


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_name(STATE_PATH.name + '.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STATE_PATH)


def git_environment():
    # extraheaderは追記型。checkoutの認証をコマンド内だけリセットしてから一つ設定する。
    # .git/configに保存済みのcheckout設定自体は変更しない。
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    if not GITHUB_TOKEN:
        return env
    try:
        count = int(env.get('GIT_CONFIG_COUNT', '0'))
        if count < 0:
            raise ValueError
    except ValueError:
        raise RuntimeError('Gitの環境設定GIT_CONFIG_COUNTが不正です。') from None
    root_key = 'http.https://github.com/.extraheader'
    repo_key = (f'http.https://github.com/{GITHUB_REPOSITORY}.git.extraheader'
                if GITHUB_REPOSITORY else root_key)
    encoded = base64.b64encode(('x-access-token:'+GITHUB_TOKEN).encode()).decode()
    pairs = [(root_key, '')]
    if repo_key != root_key:
        pairs.append((repo_key, ''))
    pairs.append((repo_key, 'AUTHORIZATION: basic '+encoded))
    for key, value in pairs:
        env[f'GIT_CONFIG_KEY_{count}'] = key
        env[f'GIT_CONFIG_VALUE_{count}'] = value
        count += 1
    env['GIT_CONFIG_COUNT'] = str(count)
    return env


def sanitize_git_error(text):
    text = text.decode('utf-8', errors='replace') if isinstance(text, bytes) else str(text or '')
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    if GITHUB_TOKEN:
        encoded = base64.b64encode(('x-access-token:'+GITHUB_TOKEN).encode()).decode()
        for secret in (GITHUB_TOKEN, encoded):
            text = text.replace(secret, '[認証情報非表示]')
    text = re.sub(r'(https?://)[^/\s@]+@', r'\1[認証情報非表示]@', text)
    text = re.sub(r'(?i)(\b(?:proxy-)?authorization\s*[:=]\s*)(?:basic|bearer)\s+\S+',
                  r'\1[認証情報非表示]', text)
    text = re.sub(r'\b(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+', '[認証情報非表示]', text)
    return text.strip()[:2000]


def git_command(args, *, check=True):
    # トークンはURL・引数に含めない。失敗時は認証情報を伏せたGitの詳細を出す。
    phase = str(args[0]) if args else 'command'
    try:
        result = subprocess.run(['git', *args], env=git_environment(), capture_output=True,
                                text=True, check=False, timeout=60)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f'GitHub状態同期のgit {phase}が60秒でタイムアウトしました。'
                           '状態処理・LINE送信を進めずに停止します。') from None
    if check and result.returncode != 0:
        detail = sanitize_git_error(result.stderr or result.stdout) or 'Gitから詳細メッセージがありません。'
        if phase == 'fetch':
            hint = f'取得先ブランチ: {STATE_BRANCH}。認証エラーならGITHUB_TOKENの参照先と権限を確認してください。'
        elif phase == 'push':
            hint = 'GITHUB_TOKENのcontents: write権限・ブランチ保護・同時実行の有無を確認してください。'
        else:
            hint = '上記のGit詳細を確認してください。'
        raise RuntimeError(f'GitHub状態同期のgit {phase}に失敗しました（終了コード{result.returncode}）。\n'
                           f'Git詳細: {detail}\n{hint}\nLINE送信前なら送信を停止しています。') from None
    return result


def sync_state_from_github():
    if not (GITHUB_TOKEN and GITHUB_REPOSITORY):
        return
    url = f'https://github.com/{GITHUB_REPOSITORY}.git'
    git_command(['fetch', url, STATE_BRANCH])
    # Actionsの古いcheckoutから、前回のstateを巻き戻さない。
    git_command(['merge', '--ff-only', 'FETCH_HEAD'])


def push_state_to_github():
    if not (GITHUB_TOKEN and GITHUB_REPOSITORY):
        print('GitHub保存なし：トークンまたはリポジトリ指定がありません。')
        return
    git_command(['config', 'user.name', 'github-actions[bot]'])
    git_command(['config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'])
    git_command(['add', '--', str(STATE_PATH)])
    diff = git_command(['diff', '--cached', '--quiet', '--', str(STATE_PATH)], check=False)
    if diff.returncode == 0:
        return
    if diff.returncode != 1:
        raise RuntimeError('state.json の変更確認に失敗しました。')
    git_command(['commit', '-m', 'Update notification state v20 [skip ci]', '--', str(STATE_PATH)])
    git_command(['push', f'https://github.com/{GITHUB_REPOSITORY}.git', f'HEAD:{STATE_BRANCH}'])


def persist_state(state):
    save_state(state)
    push_state_to_github()


def split_line_messages(message):
    # LINEは1テキスト最大5000 UTF-16単位・1リクエスト最大5メッセージ。
    chunks, chunk = [], ''
    for line in message.splitlines(keepends=True):
        if len(line.encode('utf-16-le'))//2 > 4500:
            raise ValueError('通知の1行が長すぎます。')
        if len((chunk+line).encode('utf-16-le'))//2 > 4500:
            chunks.append(chunk.rstrip())
            chunk = ''
        chunk += line
    if chunk:
        chunks.append(chunk.rstrip())
    return [{'type': 'text', 'text': text} for text in chunks]


def enqueue_message(state, message):
    messages = split_line_messages(message)
    for i in range(0, len(messages), 5):
        state.setdefault('outbox', []).append(dict(
            retry_key=str(uuid.uuid4()), created_at=pd.Timestamp.now(tz='UTC').isoformat(),
            messages=messages[i:i+5]))


def send_line(item):
    response = requests.post('https://api.line.me/v2/bot/message/broadcast',
        headers={'Authorization': 'Bearer '+LINE_TOKEN, 'Content-Type': 'application/json',
                 'X-Line-Retry-Key': item['retry_key']},
        json={'messages': item['messages']}, timeout=30)
    if response.status_code == 409 and response.headers.get('x-line-accepted-request-id'):
        return  # 同じリトライキーの通知は受理済み。新しいキーで再送しない。
    response.raise_for_status()


def flush_outbox(state):
    if not LINE_TOKEN:
        print('LINE送信なし：LINE_TOKENがありません。通知は状態に保存して次回再送します。')
        return
    while state.get('outbox'):
        item = state['outbox'][0]
        # 最初の試行から24時間以内は同じキーで再送する。未試行なら古い通知も初回送信できる。
        first = item.get('first_attempt_at')
        if first and pd.Timestamp.now(tz='UTC')-pd.Timestamp(first) >= pd.Timedelta(hours=24):
            raise RuntimeError('初回送信から24時間以上たった未確認LINE通知があります。配信状況を確認するまで自動再送を停止します。')
        if not first:
            item['first_attempt_at'] = pd.Timestamp.now(tz='UTC').isoformat()
            persist_state(state)
        send_line(item)
        state['outbox'].pop(0)
        persist_state(state)


def main(dry_run=None):
    if dry_run is None:
        dry_run = '--dry-run' in sys.argv or os.environ.get('DRY_RUN', '').lower() in ('1','true','yes')
    if not dry_run:
        sync_state_from_github()
    saved = load_state()
    if not dry_run and saved.get('outbox'):
        flush_outbox(saved)
    df = fetch_data()
    flags, diagnostics = prepare_candidates(df)
    state, events, sniper_events, changed, upgraded = advance_state(saved, df, flags)
    if not changed:
        print(f'{df.index[-1].date()}は処理済みです。売買状態と通知を重複更新しません。')
        return
    message = build_message(df, state, flags, diagnostics, events, sniper_events, upgraded)
    print(message)
    if dry_run:
        print('\nDRY_RUN：状態保存・LINE送信・Git操作なし。')
        return
    enqueue_message(state, message)
    # 未送信メッセージと売買状態を先に確定・保存する。失敗後の再実行は同じ通知キーを使用。
    persist_state(state)
    flush_outbox(state)


if __name__ == '__main__':
    main()


