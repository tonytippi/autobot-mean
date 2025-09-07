import os, time, json, yaml
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from binance_client import get_klines
from strategy_mean_rsi import MeanRSIParams, generate_signal
from telegram_notifier import send as tg_send
from database import init_db, save_signal

DATA_DIR = os.getenv("DATA_DIR", "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
os.makedirs(DATA_DIR, exist_ok=True)

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)

def already_processed(state, key, last_open_time_iso):
    return state.get(key) == last_open_time_iso

def mark_processed(state, key, last_open_time_iso):
    state[key] = last_open_time_iso
    save_state(state)

def fmt_signal_msg(symbol: str, interval: str, sig: dict):
    return (
        f"*{symbol}* `{interval}` — *Mean‑RSI BUY*\n"
        f"Close: `{sig['close']:.6f}`  |  RSI14: `{sig['rsi']:.1f}`\n"
        f"SMA20: `{sig['sma20']:.6f}`  |  Thr(SMA20-k·σ): `{sig['thr']:.6f}`\n"
        f"ATR14: `{sig['atr14']:.6f}`\n"
        f"TP≈ `{sig['suggested_tp']:.6f}`  |  SL≈ `{sig['suggested_sl']:.6f}`\n"
        f"Bar: `{sig['signal_bar_open_time']} → {sig['signal_bar_close_time']}`\n"
        f"_Note_: {sig['entry_note']}"
    )

def main():
    cfg = load_config()
    symbols = cfg.get("symbols", ["APTUSDT"])
    timeframes = cfg.get("timeframes", ["4h","1d"])
    params = MeanRSIParams(
        k=float(os.getenv("K_STD", cfg.get("k", 1.0))),
        rsi_min=float(os.getenv("RSI_MIN", cfg.get("rsi_min", 30))),
        sl_atr_mult=float(os.getenv("SL_ATR_MULT", cfg.get("sl_atr_mult", 1.5))),
    )
    poll_seconds = int(cfg.get("poll_seconds", 60))

    # DB init
    init_db()

    state = load_state()
    print("[INFO] Mean‑RSI bot started. Poll every", poll_seconds, "sec")
    print("[INFO] Symbols:", symbols, "Timeframes:", timeframes)
    while True:
        loop_start = time.time()
        now_ts = datetime.utcnow().replace(tzinfo=timezone.utc)
        for s in symbols:
            for tf in timeframes:
                key = f"{s}_{tf}"
                try:
                    kl = get_klines(s, tf, limit=300)
                    if len(kl) < 60:
                        continue
                    idx = -2 if now_ts < kl['close_time'].iloc[-1] else -1
                    last_open_iso = kl['open_time'].iloc[idx].isoformat()
                    if already_processed(state, key, last_open_iso):
                        continue
                    sig = generate_signal(kl, params, now_ts)
                    if sig:
                        # persist to DB
                        sig_row = save_signal(
                            symbol=s, interval=tf, side=sig["side"],
                            close=sig["close"], rsi=sig["rsi"], sma20=sig["sma20"],
                            thr=sig["thr"], atr14=sig["atr14"],
                            suggested_tp=sig["suggested_tp"], suggested_sl=sig["suggested_sl"],
                            bar_open_time=pd.to_datetime(sig["signal_bar_open_time"]),
                            bar_close_time=pd.to_datetime(sig["signal_bar_close_time"]),
                        )
                        # send Telegram
                        msg = fmt_signal_msg(s, tf, sig)
                        print("[SIGNAL]", s, tf, sig_row.id)
                        tg_send(msg)
                    else:
                        print("[NO SIGNAL]", s, tf, last_open_iso)
                    mark_processed(state, key, last_open_iso)
                except Exception as e:
                    print("[ERROR]", s, tf, "=>", repr(e))
                    # do not mark processed on error
        elapsed = time.time() - loop_start
        to_sleep = max(0, poll_seconds - elapsed)
        time.sleep(to_sleep)

if __name__ == "__main__":
    main()
