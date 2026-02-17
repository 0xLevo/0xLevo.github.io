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

def get_ui_colors(score, rainbow):
    # KART RENGİ (Skora göre kenarlık)
    if score >= 4: card_color = "#22c55e" # Yeşil
    elif score == 3: card_color = "#84cc16" # Açık Yeşil
    elif score == 2: card_color = "#f97316" # Turuncu/Açık Kırmızı
    else: card_color = "#ef4444" # Kırmızı
    return card_color

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 40: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- 5 KRİTER HESAPLAMA ---
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
            bb = ta.bbands(df['close'], length=20, std=2)
            sma = ta.sma(df['close'], length=20).iloc[-1]
            vol_avg = df['volume'].rolling(10).mean().iloc[-1]
            curr_price = df['close'].iloc[-1]
            
            star_count = 0
            if rsi < 45: star_count += 1
            if mfi < 45: star_count += 1
            if not bb.empty and curr_price < bb.iloc[-1, 1]: star_count += 1
            if df['volume'].iloc[-1] > vol_avg: star_count += 1
            if curr_price > sma: star_count += 1
            
            rb_text = get_rainbow_status(df)
            
            # --- AKSİYON & ROZET RENGİ ---
            if star_count >= 4: action_text = "Strong Buy" if rb_text != "BUBBLE" else "Buy"
            elif star_count <= 1: action_text = "Strong Sell"
            elif star_count == 3: action_text = "Buy" if rb_text in ["BUY", "FIRE SALE"] else "Neutral"
            elif star_count == 2: action_text = "Sell" if rb_text in ["BUBBLE", "FOMO"] else "Neutral"
            else: action_text = "Neutral"

            card_c = get_ui_colors(star_count, rb_text)
            
            # Rozet Rengi (Kelimeye göre - Nötr ise Gri)
            if "BUY" in action_text.upper(): badge_c = "#22c55e"
            elif "SELL" in action_text.upper(): badge_c = "#ef4444"
            else: badge_c = "#64748b" # NEUTRAL = GRİ

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': star_count, 'action_text': action_text, 
                'card_color': card_c, 'badge_color': badge_c,
                'details': {
                    "RSI (14)": round(rsi, 2),
                    "MFI (14)": round(mfi, 2),
                    "SMA 20": "Above" if curr_price > sma else "Below",
                    "Rainbow": rb_text,
                    "Stars": f"{star_count}/5",
                    "Volume": "High" if df['volume'].iloc[-1] > vol_avg else "Low"
                },
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.05)
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector Alpha</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #050505; --card: #111; --text: #ffffff; --border: #222; --input: #1a1a1a;
            }}
            body.light-mode {{
                --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --border: #e2e8f0; --input: #ffffff;
            }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; transition: 0.3s; padding-top: 60px; }}
            
            .main-header {{ position: fixed; top: 0; width: 100%; z-index: 50; background: var(--bg); border-bottom: 1px solid var(--border); padding: 10px 0; }}
            .crypto-card {{ 
                background: var(--card); border: 1px solid var(--border); border-radius: 20px; 
                transition: 0.3s; position: relative; cursor: pointer;
            }}
            .crypto-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
            
            .action-badge {{
                position: absolute; top: 15px; right: 15px;
                padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800;
                color: white; text-transform: uppercase;
            }}
            
            .fav-star {{ font-size: 20px; cursor: pointer; color: #334155; transition: 0.2s; }}
            .fav-star.active {{ color: #eab308 !important; }}
            
            #modal-overlay {{ background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); }}
            .modal-content {{ background: var(--card); border: 1px solid var(--border); color: var(--text); }}
            
            .input-style {{ background: var(--input); border: 1px solid var(--border); color: var(--text); }}
        </style>
    </head>
    <body>
        <div class="main-header">
            <div class="max-w-7xl mx-auto px-6 flex justify-between items-center">
                <h1 class="text-2xl font-black italic">BASED<span class="text-red-600">VECTOR</span></h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" id="theme-btn" class="p-2 rounded-full border border-gray-700">🌙</button>
                    <span class="text-[10px] font-mono opacity-50">UTC: {full_update}</span>
                </div>
            </div>
        </div>

        <div class="max-w-7xl mx-auto p-6 mt-10">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                <input type="text" id="search" placeholder="Search..." class="input-style p-4 rounded-2xl outline-none focus:ring-2 ring-red-500/50">
                <select id="sort" class="input-style p-4 rounded-2xl outline-none cursor-pointer">
                    <option value="score-desc">Best Technicals</option>
                    <option value="score-asc">Worst Technicals</option>
                </select>
                <button onclick="toggleFavs()" id="fav-toggle-btn" class="input-style font-bold p-4 rounded-2xl">Show Favorites ★</button>
            </div>

            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
    """

    for i in data:
        encoded = base64.b64encode(json.dumps(i).encode()).decode()
        stars = "".join(['<span class="text-green-500">★</span>' if s < i['score'] else '<span class="opacity-20">★</span>' for s in range(5)])
        
        html += f"""
        <div class="crypto-card p-6 border-l-4" 
             style="border-left-color: {i['card_color']};"
             onclick="showModal('{encoded}')"
             data-symbol="{i['symbol']}" data-score="{i['score']}">
            
            <div class="action-badge" style="background: {i['badge_color']};">{i['action_text']}</div>
            
            <div class="flex items-center gap-2 mb-6">
                <span class="fav-star" onclick="event.stopPropagation(); toggleFav(this, '{i['symbol']}')">★</span>
                <span class="text-xl font-bold">{i['symbol']}</span>
            </div>

            <div class="mt-4">
                <div class="text-2xl font-black mb-1">${i['price']}</div>
                <div class="flex gap-1 text-xs">{stars}</div>
            </div>
        </div>
        """

    html += """
        </div>
    </div>

    <div id="modal-overlay" class="fixed inset-0 hidden z-[100] flex items-center justify-center p-4" onclick="closeModal()">
        <div class="modal-content p-8 rounded-3xl max-w-sm w-full shadow-2xl" onclick="event.stopPropagation()">
            <div class="flex justify-between items-center mb-6">
                <h2 id="m-symbol" class="text-3xl font-black italic"></h2>
                <button onclick="closeModal()" class="text-2xl opacity-50">&times;</button>
            </div>
            <div id="m-details" class="space-y-4 font-mono"></div>
            <div class="mt-8 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs italic text-blue-400">
                💡 These indicators are calculated on 4-hour candles for mid-term analysis.
            </div>
        </div>
    </div>

    <script>
        let showOnlyFavs = false;
        let favorites = JSON.parse(localStorage.getItem('bv_favs') || '[]');

        function toggleTheme() {
            document.body.classList.toggle('light-mode');
            const isLight = document.body.classList.contains('light-mode');
            document.getElementById('theme-btn').innerText = isLight ? '☀️' : '🌙';
            localStorage.setItem('bv_theme', isLight ? 'light' : 'dark');
        }

        function toggleFav(el, sym) {
            el.classList.toggle('active');
            if(favorites.includes(sym)) favorites = favorites.filter(x => x !== sym);
            else favorites.push(sym);
            localStorage.setItem('bv_favs', JSON.stringify(favorites));
            render();
        }

        function toggleFavs() {
            showOnlyFavs = !showOnlyFavs;
            document.getElementById('fav-toggle-btn').classList.toggle('bg-yellow-500/20');
            render();
        }

        function showModal(dataRaw) {
            const data = JSON.parse(atob(dataRaw));
            document.getElementById('m-symbol').innerText = data.symbol;
            let detHtml = '';
            for(const [k, v] of Object.entries(data.details)) {
                detHtml += `<div class="flex justify-between border-b border-gray-500/10 py-2"><span class="opacity-50">${k}</span><span class="font-bold">${v}</span></div>`;
            }
            document.getElementById('m-details').innerHTML = detHtml;
            document.getElementById('modal-overlay').classList.remove('hidden');
        }

        function closeModal() { document.getElementById('modal-overlay').classList.add('hidden'); }

        function render() {
            const term = document.getElementById('search').value.toUpperCase();
            const sort = document.getElementById('sort').value;
            let cards = Array.from(document.querySelectorAll('.crypto-card'));

            cards.forEach(c => {
                const sym = c.dataset.symbol;
                const isFav = favorites.includes(sym);
                const star = c.querySelector('.fav-star');
                if(isFav) star.classList.add('active'); else star.classList.remove('active');

                const matchSearch = sym.includes(term);
                const matchFav = showOnlyFavs ? isFav : true;
                c.style.display = (matchSearch && matchFav) ? 'block' : 'none';
            });

            const grid = document.getElementById('grid');
            cards.sort((a,b) => sort === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score);
            cards.forEach(c => grid.appendChild(c));
        }

        document.getElementById('search').addEventListener('input', render);
        document.getElementById('sort').addEventListener('change', render);
        window.onload = () => {
            if(localStorage.getItem('bv_theme') === 'light') toggleTheme();
            render();
        };
    </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    create_html(analyze_market())
