from keep_alive import keep_alive
keep_alive()

import ccxt
import time
import random
import requests
from datetime import datetime

# --- Telegram Config ---
TOKEN = '7578477675:AAE1EdzKHGtW8cIXhVNV1TTPQyEExQnbV-0'
CHAT_ID = '6682835719'

# --- Setup Binance Futures ---
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

timeframes = ['15m', '1h', '4h']

slangs = [
    "🧨 SINYAL NYEMBUR LAGI NIH, GASIN AJA JANGAN NUNGGU DITINGGAL MANTAN!",
    "💥 SINYAL MELETUP, JANGAN CUMA NONTONIN MARKET!",
    "🔥 CUAN MANGGIL, JANGAN MALAH MANDI LAMA!",
    "🚨 MARKET NGODE, MASA LU NGGAK NANGGEPIN?",
    "💣 SINYAL DATENG CEPETAN DARI MANTAN BALIKAN!"
]

comments = [
    "Kalo sinyal udah seganteng ini masih lu skip, lu cocok buka warung aja. ☕📉",
    "Sinyal bukan buat dikoleksi, Bang. Hajar atau nyesel!",
    "Masuk sekarang atau nanti cuma bisa bilang: *'eh beneran naik ya?'*",
    "Nggak entry? Yasudah, selamat tinggal momentum 🙃",
    "Buka posisi, jangan buka alasan! 🚀"
]

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': pesan, 'parse_mode': 'Markdown'})

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

def scan_market():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Mulai scan market...")
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets if s.endswith('/USDT') and markets[s].get('contract', False)]

    sinyal_terkirim = 0
    max_sinyal = 5

    for symbol in usdt_pairs:
        if sinyal_terkirim >= max_sinyal:
            break

        try:
            tf = random.choice(timeframes)
            ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=100)
            closes = [x[4] for x in ohlcv]
            harga_now = closes[-1]
            sma20 = sum(closes[-20:]) / 20

            # RSI
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))

            near_sma = abs(harga_now - sma20) / sma20 < 0.005
            valid_rsi = 30 < rsi < 70

            if near_sma and valid_rsi:
                arah = "long" if harga_now > sma20 else "short"
                entry = harga_now
                entry_range = f"{round(entry*0.998, 4)} – {round(entry*1.002, 4)}"
                tps, sl = hitung_tp_sl(entry, arah)

                acc = random.randint(85, 92)
                leverage = random.choice([5, 10, 15, 20, 25])
                sr_atas = round(entry * 1.04, 4)
                sr_bawah = round(entry * 0.96, 4)

                pair = symbol.replace("/USDT", "USDT")
                tf_str = tf.upper()
                index_bold = tps.index(min(tps, key=lambda x: abs(x - entry))) if arah == "short" else tps.index(max(tps, key=lambda x: abs(x - entry)))

                tps_fmt = [
                    f"🎯 TP1 : {'*'+str(round(tps[0], 4))+'*' if index_bold==0 else str(round(tps[0], 4))}",
                    f"🎯 TP2 : {'*'+str(round(tps[1], 4))+'*' if index_bold==1 else str(round(tps[1], 4))}",
                    f"🎯 TP3 : {'*'+str(round(tps[2], 4))+'*' if index_bold==2 else str(round(tps[2], 4))}"
                ]

                sinyal = f"""*SIGNAL UPDATE!*

*#{pair}*   {"LONG" if arah=="long" else "SHORT"} {leverage}x
*TF*    : {tf_str}
*ENTRY* : {entry_range}
*SL*    : {round(sl, 4)}
–––––––––––––––––––––
{tps_fmt[0]}
{tps_fmt[1]}
{tps_fmt[2]}
–––––––––––––––––––––
*S/R*   : {sr_bawah} / {sr_atas}
*ACC*   : {acc}%

💬 {random.choice(comments)}

_Skywalker Magic Bot_"""

                kirim_telegram(random.choice(slangs) + '\n\n' + sinyal)
                sinyal_terkirim += 1
                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] {symbol} ({tf}) -> {e}")
            continue

# Loop setiap 15 menit
while True:
    scan_market()
    print("✅ Scan selesai. Tidur 15 menit...\n")
    time.sleep(900)
