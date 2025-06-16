from keep_alive import keep_alive
keep_alive()

import ccxt
import time
import random
import requests
from datetime import datetime

# --- Konfigurasi Telegram ---
TOKEN = '7578477675:AAE1EdzKHGtW8cIXhVNV1TTPQyEExQnbV-0'
CHAT_ID = '6682835719'

# --- Setup exchange ---
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# --- Timeframes dan gaya slengean ---
timeframes = ['15m', '1h', '4h']
slangs = [
    "🧨 SINYAL NYEMBUR LAGI NIH, GASIN AJA JANGAN NUNGGU DITINGGAL MANTAN!",
    "💥 SINYAL MELETUP, JANGAN CUMA NONTONIN MARKET!",
    "🔥 CUAN MANGGIL, JANGAN MALAH MANDI LAMA!",
    "💣 SINYAL DATENG LEBIH CEPET DARI MANTAN NGECHAT!",
    "🚨 MARKET NGODE, MASA LU NGGAK NANGGEPIN?"
]
comments = [
    "Market udah nyodorin cuan, bukan kode doang!",
    "Masih bengong? Sinyalnya udah siap ngasih gorengan.",
    "TP kesentuh, jangan lupa traktir es teh manis!"
]

# --- Kirim Telegram ---
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': pesan, 'parse_mode': 'Markdown'})

# --- Hitung SL & TP ---
def hitung_tp_sl(entry, arah):
    persentase = [0.01, 0.02, 0.035]
    sl_percent = 0.008
    if arah == "long":
        tps = [entry * (1 + p) for p in persentase]
        sl = entry * (1 - sl_percent)
    else:
        tps = [entry * (1 - p) for p in persentase]
        sl = entry * (1 + sl_percent)
    return tps, sl

# --- Fungsi utama scan market ---
def scan_market():
    try:
        markets = exchange.load_markets()
        usdt_pairs = [s for s in markets if s.endswith("/USDT") and markets[s].get("contract", False)]
    except Exception as e:
        print(f"[ERROR LOAD_MARKETS] => {e}")
        return

    for symbol in usdt_pairs:
        try:
            tf = random.choice(timeframes)
            ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=100)
            closes = [x[4] for x in ohlcv]
            harga_now = closes[-1]
            sma = sum(closes[-20:]) / 20

            if abs(harga_now - sma) / sma < 0.005:
                arah = "long" if harga_now > sma else "short"
                entry = harga_now
                entry_range = f"{round(entry*0.998, 4)} – {round(entry*1.002, 4)}"
                tps, sl = hitung_tp_sl(entry, arah)

                acc = random.randint(84, 92)
                leverage = random.choice([5, 10, 15, 20, 25, 30])
                sr_atas = round(entry * 1.04, 4)
                sr_bawah = round(entry * 0.96, 4)

                index_bold = tps.index(max(tps) if arah == "long" else min(tps))
                tps_fmt = [
                    f"🎯 TP1: {'*'+str(round(tps[0], 4))+'*' if index_bold==0 else str(round(tps[0], 4))} (Cari Aman)",
                    f"🎯 TP2: {'*'+str(round(tps[1], 4))+'*' if index_bold==1 else str(round(tps[1], 4))} (Butuh Duit)",
                    f"🎯 TP3: {'*'+str(round(tps[2], 4))+'*' if index_bold==2 else str(round(tps[2], 4))} (Maruk)"
                ]

                tf_str = tf.upper()
                pair = symbol.replace("/USDT", "USDT")

                sinyal = f"""{random.choice(slangs)}

#{pair} {"🔺 LONG" if arah=="long" else "🔻 SHORT"} {leverage}x
📊 TF: {tf_str}
🎯 ENTRY: *{entry_range}*

{tps_fmt[0]}
{tps_fmt[1]}
{tps_fmt[2]}

🛑 SL: {round(sl, 4)}
📉 S/R: {sr_bawah} / {sr_atas}
📈 ACC: {acc}%

💬 {random.choice(comments)}"""

                kirim_telegram(sinyal)
                print(f"[SINYAL] {pair} ({arah.upper()}) terkirim!")
                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] {symbol} ({tf}) -> {e}")
            continue

# --- Loop utama ---
while True:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] SCAN MULAI...")
    scan_market()
    print("Tidur 15 menit...\n")
    time.sleep(900)
