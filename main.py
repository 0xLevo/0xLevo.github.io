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
]

def get_rainbow_status(df):
    try:
        y = np.log(df['close'].values)
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        expected_log_price = slope * x[-1] + intercept
        current_log_price = y[-1]
        diff = current_log_price - expected_log_price
        if diff < -0.4: return "FIRE SALE"
        elif diff < -0.15: return "BUY"
        elif diff < 0.15: return "NEUTRAL"
        elif diff < 0.4: return "FOMO"
        else: return "BUBBLE"
    except: return "UNKNOWN"

def get_ui_colors(score, action_text):
    """
    Kart rengi (skora göre) ve Rozet rengini (yazıya göre) ayırır.
    """
    # 1. KART RENGİ (Arka plan ve Kenarlık - Skora Göre)
    if score >= 4: card_color = "#15803d" # Yeşil
    elif score == 3: card_color = "#65a30d" # Açık Yeşil
    elif score == 2: card_color = "#b91c1c" # Açık Kırmızı
    else: card_color = "#991b1b" # Koyu Kırmızı

    # 2. ROZET RENGİ (Aksiyon Yazısına Göre)
    action_text = action_text.upper()
    if "BUY" in action_text:
        badge_color = "#22c55e" # Canlı Yeşil
    elif "SELL" in action_text:
        badge_color = "#ef4444" # Canlı Kırmızı
    else:
        badge_color = "#64748b" # Nötr GRİ

    return card_color, badge_color

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=80)
            if len(bars) < 40: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
            bb = ta.bbands(df['close'], length=20, std=2)
            sma = ta.sma(df['close'], length=20).iloc[-1]
            vol_avg = df['volume'].rolling(10).mean().iloc[-1]
            curr_price = df['close'].iloc[-1]
            
            score = 0
            if rsi < 45: score += 1
            if mfi < 45: score += 1
            if curr_price < bb.iloc[-1, 1]: score += 1
            if df['volume'].iloc[-1] > vol_avg: score += 1
            if curr_price > sma: score += 1
            
            rb = get_rainbow_status(df)
            
            # Aksiyon Metni Belirleme
            if score >= 4: action_text = "Strong Buy" if rb != "BUBBLE" else "Buy"
            elif score == 0: action_text = "Strong Sell"
            elif score == 3 and rb in ["BUY", "FIRE SALE"]: action_text = "Buy"
            elif score == 2 and rb in ["BUBBLE", "FOMO"]: action_text = "Sell"
            else: action_text = "Neutral"

            card_c, badge_c = get_ui_colors(score, action_text)

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': score, 'action_text': action_text, 
                'card_color': card_c, 'badge_color': badge_c,
                'details': {
                    "RSI": round(rsi, 1), "MFI": round(mfi, 1),
                    "Rainbow": rb, "Stars": f"{score}/5"
                },
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.02)
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Elite</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #050505; --card-base: #111; --text: #f8fafc; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 80px; }}
        
        /* Kart Tasarımı */
        .crypto-card {{ 
            position: relative; border-radius: 20px; transition: 0.3s; 
            overflow: hidden; display: flex; flex-direction: column;
        }}
        .crypto-card:hover {{ transform: scale(1.02); z-index: 10; }}

        /* Aksiyon Kutucuğu (Badge) */
        .action-box {{
            position: absolute; top: 12px; right: 12px;
            padding: 4px 12px; border-radius: 8px; font-size: 10px;
            font-weight: 800; text-transform: uppercase; color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}

        .fav-star {{ cursor: pointer; color: #444; font-size: 22px; transition: 0.2s; }}
        .fav-star.active {{ color: #eab308 !important; }}
        
        .star-row {{ font-size: 12px; margin-top: 8px; }}
        .star-f {{ color: #22c55e; }} .star-e {{ color: #ef4444; opacity: 0.3; }}
    </style></head>
    <body>
        <div class="max-w-7xl mx-auto p-6">
            <header class="flex justify-between items-center mb-10">
                <h1 class="text-3xl font-black italic tracking-tighter text-white">BASED<span class="text-red-600">VECTOR</span></h1>
                <div class="flex gap-4">
                    <button onclick="toggleFavs()" id="fav-btn" class="bg-white/5 border border-white/10 px-4 py-2 rounded-xl text-sm font-bold">★ Favorites</button>
                    <div class="text-[10px] opacity-40 font-mono text-right">SYSTEM ACTIVE<br>{full_update}</div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
                <input type="text" id="search" placeholder="Search symbol..." class="bg-white/5 border border-white/10 p-4 rounded-2xl w-full outline-none focus:border-red-500/50 transition">
                <select id="sort" class="bg-white/5 border border-white/10 p-4 rounded-2xl cursor-pointer outline-none">
                    <option value="score-desc">Highest Technical Score</option>
                    <option value="score-asc">Lowest Technical Score</option>
                </select>
            </div>

            <div id="grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
    """

    for i in data:
        stars = "".join(['<span class="star-f">★</span>' if s < i['score'] else '<span class="star-e">★</span>' for s in range(5)])
        
        html += f"""
        <div class="crypto-card p-6 border-2" 
             style="border-color: {i['card_color']}; background: {i['card_color']}15;"
             data-symbol="{i['symbol']}" data-score="{i['score']}">
            
            <div class="action-box" style="background: {i['badge_color']};">
                {i['action_text']}
            </div>

            <div class="flex items-center gap-2 mb-4">
                <span class="fav-star" onclick="toggleFav(this, '{i['symbol']}')">★</span>
                <span class="text-2xl font-black tracking-tight">{i['symbol']}</span>
            </div>

            <div class="mt-auto">
                <div class="text-xs opacity-50 font-mono mb-1 tracking-widest">PRICE</div>
                <div class="text-2xl font-bold font-mono">${i['price']}</div>
                <div class="star-row">{stars}</div>
            </div>
        </div>
        """

    html += """
        </div></div>
        <script>
            let showOnlyFavs = false;
            let favorites = JSON.parse(localStorage.getItem('vector_favs') || '[]');

            function toggleFav(el, symbol) {
                el.classList.toggle('active');
                if (favorites.includes(symbol)) {
                    favorites = favorites.filter(s => s !== symbol);
                } else {
                    favorites.push(symbol);
                }
                localStorage.setItem('vector_favs', JSON.stringify(favorites));
                render();
            }

            function toggleFavs() {
                showOnlyFavs = !showOnlyFavs;
                document.getElementById('fav-btn').classList.toggle('bg-yellow-500/20');
                render();
            }

            function render() {
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value; 
                let cards = Array.from(document.querySelectorAll('.crypto-card'));
                
                cards.forEach(c => {
                    const symbol = c.dataset.symbol;
                    const isFav = favorites.includes(symbol);
                    if (isFav) c.querySelector('.fav-star').classList.add('active');
                    
                    const matchesSearch = symbol.includes(term);
                    const matchesFav = showOnlyFavs ? isFav : true;
                    c.style.display = (matchesSearch && matchesFav) ? 'flex' : 'none';
                });
                
                const grid = document.getElementById('grid');
                cards.sort((a, b) => sortVal === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score);
                cards.forEach(c => grid.appendChild(c));
            }
            
            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            window.onload = render;
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    create_html(analyze_market())
