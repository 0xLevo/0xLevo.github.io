import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from datetime import datetime, timezone
import json 
import base64

# --- ASSET LIST ---
CMC_TOP_100 = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 
    'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'BCH', 'ATOM', 'UNI', 'NEAR', 'INJ', 
    'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 
    'KAS', 'ETC', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'FTM', 'SAND'
] # Örnek olması için listeyi kısa tuttum, istersen hepsini ekleyebilirsin.

def get_rainbow_status(df):
    """Logaritmik Regresyon (Rainbow) Hesaplama"""
    try:
        y = np.log(df['close'].values)
        x = np.arange(len(y))
        # Doğrusal regresyon fit (log-log alanı)
        slope, intercept = np.polyfit(x, y, 1)
        expected_log_price = slope * x[-1] + intercept
        current_log_price = y[-1]
        
        # Beklenen fiyattan ne kadar uzakta? (-1 ile +1 arası normalize)
        diff = current_log_price - expected_log_price
        
        if diff < -0.5: return 1.0, "FIRE SALE", "#00ff00" # Koyu Yeşil
        elif diff < -0.2: return 0.8, "BUY", "#a3e635"     # Açık Yeşil
        elif diff < 0.2: return 0.5, "NEUTRAL", "#94a3b8" # Gri
        elif diff < 0.5: return 0.2, "FOMO", "#facc15"    # Sarı
        else: return 0.0, "BUBBLE", "#ff0000"             # Kırmızı
    except:
        return 0.5, "UNKNOWN", "#94a3b8"

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 50: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- TEKNİK KRİTERLER (5 YILDIZ) ---
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
            bb = ta.bbands(df['close'], length=20, std=2)
            sma = ta.sma(df['close'], length=20).iloc[-1]
            curr_price = df['close'].iloc[-1]
            
            star_count = 0
            if rsi < 45: star_count += 1
            if mfi < 45: star_count += 1
            if curr_price < bb.iloc[-1, 1]: star_count += 1
            if df['volume'].iloc[-1] > df['volume'].rolling(10).mean().iloc[-1]: star_count += 1
            if curr_price > sma: star_count += 1
            
            # --- RAINBOW KRİTERİ ---
            rb_score, rb_text, rb_color = get_rainbow_status(df)

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': star_count, 'rb_text': rb_text, 'rb_color': rb_color,
                'details': {
                    "RSI": round(rsi, 1), "MFI": round(mfi, 1), "Rainbow": rb_text
                },
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.05)
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Rainbow</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --border: #333; }}
        .light {{ --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --border: #cbd5e1; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 100px; transition: 0.3s; }}
        .brand-logo {{ background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }}
        .card {{ border-radius: 16px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: var(--card); overflow: hidden; }}
        .card:hover {{ transform: scale(1.02); box-shadow: 0 20px 30px -10px rgba(0,0,0,0.5); }}
        .rainbow-badge {{ font-size: 10px; padding: 2px 8px; border-radius: 99px; font-weight: bold; color: #000; text-transform: uppercase; }}
        .star-filled {{ color: #eab308; }}
        .star-empty {{ color: #4b5563; opacity: 0.2; }}
        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
    </style></head>
    <body>
        <div class="legal-top"><strong>⚠️ RAINBOW ALGORITHM ACTIVE:</strong> Regression models are probabilistic, not certain.</div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl italic tracking-tighter brand-logo">BasedVector</h1>
                <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full">🌙</button>
            </header>
            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
    """

    for i in data:
        stars = "".join(['<span class="star-filled">★</span>' if s < i['score'] else '<span class="star-empty">★</span>' for s in range(5)])
        
        html += f"""
        <div class="card p-5 flex flex-col justify-between" onclick="alert('Symbol: {i['symbol']}')">
            <div class="flex justify-between items-start mb-4">
                <span class="font-bold text-xl">{i['symbol']}</span>
                <span class="rainbow-badge" style="background:{i['rb_color']}">{i['rb_text']}</span>
            </div>
            <div class="text-center">
                <div class="text-2xl font-black mb-1">${i['price']}</div>
                <div class="flex justify-center gap-1 mb-4">{stars}</div>
            </div>
            <div class="flex justify-between items-center text-[10px] opacity-50 border-t border-gray-800 pt-3">
                <span>TECH: {i['score']}/5</span>
                <span>{i['update_time']}</span>
            </div>
        </div>
        """

    html += """
        </div></div>
        <script>
            function toggleTheme() {
                document.body.classList.toggle('light');
                localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
            }
            window.onload = () => { if(localStorage.getItem('theme')==='light') toggleTheme(); };
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    create_html(analyze_market())
