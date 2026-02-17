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
    """Logaritmik Regresyon (Rainbow) Hesaplama"""
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

def get_color_by_stars(score, rainbow):
    """
    Yıldız sayısına göre renk ve Badge ataması.
    """
    # 5 Yıldız: Koyu Yeşil
    if score == 5: return "#15803d", "STRONG BUY"
    # 4 Yıldız: Açık Yeşil
    elif score == 4: return "#22c55e", "BUY"
    # 0 Yıldız: Koyu Kırmızı
    elif score == 0: return "#991b1b", "STRONG SELL"
    # 1 Yıldız: Açık Kırmızı
    elif score == 1: return "#ef4444", "SELL"
    
    # 2 ve 3 Yıldız için Rainbow öncelikli mantık
    if score == 3:
        if rainbow in ["FIRE SALE", "BUY"]: return "#22c55e", "BUY"
        elif rainbow in ["BUBBLE", "FOMO"]: return "#ef4444", "SELL"
        else: return "#a3e635", "NEUTRAL" # 3 yıldız, nötr rainbow -> Açık Yeşil

    if score == 2:
        if rainbow in ["FIRE SALE", "BUY"]: return "#22c55e", "BUY"
        elif rainbow in ["BUBBLE", "FOMO"]: return "#ef4444", "SELL"
        else: return "#f87171", "NEUTRAL" # 2 yıldız, nötr rainbow -> Açık Kırmızı
        
    return "#94a3b8", "NEUTRAL" # Varsayılan

def get_ai_eval(score, rb):
    if score >= 4:
        if rb == "BUBBLE": return "HIGH CONFIDENCE: Strong technicals, but historical price is overheated. Proceed with caution."
        return "STRONG BUY: Technical indicators align with historical value. High probability setup."
    elif score == 3:
        if rb == "FIRE SALE" or rb == "BUY": return "BULLISH: Good technicals and great historical price point."
        return "NEUTRAL: Mixed signals. Market is consolidating."
    else: # 2/5 veya 1/5 teknik skor
        if rb == "FIRE SALE": return "ACCUMULATION: Price is historically cheap, but technicals are not yet bullish."
        return "CAUTION: Both technicals and historical trend suggest weakness or overvaluation."

def calculate_correlation(exchange, top_n=10):
    try:
        corr_data = {}
        active_symbols = [s for s in CMC_TOP_100 if s not in ['USDT', 'USDC']][:top_n]
        price_data = {}
        for sym in active_symbols:
            try:
                bars = exchange.fetch_ohlcv(f"{sym}/USDT", timeframe='1h', limit=100)
                price_data[sym] = [bar[4] for bar in bars]
            except: continue
        if not price_data: return {}
        df_corr = pd.DataFrame(price_data)
        matrix = df_corr.corr()
        for sym in active_symbols:
            if sym != 'BTC' and sym in matrix.columns:
                corr_data[sym] = round(matrix['BTC'][sym], 2)
        return corr_data
    except: return {}

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    # Korelasyonları çek
    corr_matrix = calculate_correlation(exchange)
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=80)
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
            if curr_price < bb.iloc[-1, 1]: star_count += 1
            if df['volume'].iloc[-1] > vol_avg: star_count += 1
            if curr_price > sma: star_count += 1
            
            rb_text = get_rainbow_status(df)
            
            # Renk ve Badge'i yıldıza göre belirle
            card_color, action_text = get_color_by_stars(star_count, rb_text)

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': star_count, 'action_text': action_text, 'card_color': card_color,
                'details': {
                    "RSI": round(rsi, 1), "MFI": round(mfi, 1),
                    "SMA20": "Above" if curr_price > sma else "Below",
                    "Rainbow": rb_text, "Stars": f"{star_count}/5",
                    "BTC_Corr": corr_matrix.get(symbol, "N/A"),
                    "AI_Eval": get_ai_eval(star_count, rb_text)
                },
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.05)
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    # Korelasyon kutucukları
    corr_html = ""
    for item in data:
        if isinstance(item['details']['BTC_Corr'], float):
            c = item['details']['BTC_Corr']
            color = "border-sky-500" if c > 0.5 else ("border-orange-500" if c < 0 else "border-gray-500")
            corr_html += f'<div class="p-2 rounded-lg text-center border-b-2 {color}" style="background:rgba(100,100,100,0.1)"><div class="text-xs font-bold opacity-70">{item["symbol"]}</div><div class="text-sm font-mono font-bold">{c}</div></div>'

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ 
            --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --border: #333; 
            --modal-bg: #111; --modal-text: #f8fafc; 
        }}
        .light {{ 
            --bg: #f1f5f9; --card: #ffffff; --text: #0f172a; --border: #cbd5e1; 
            --modal-bg: #fff; --modal-text: #0f172a; 
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 140px; transition: 0.3s; }}
        
        .brand-logo {{
            background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
        }}
        
        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
        .card {{ border-radius: 16px; border: 1px solid var(--border); transition: 0.2s; overflow: hidden; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
        
        .action-badge {{ font-size: 10px; padding: 4px 10px; border-radius: 99px; font-weight: bold; color: #fff; text-transform: uppercase; }}
        
        /* Yıldız Renkleri */
        .star-filled {{ color: #22c55e; text-shadow: 0 0 5px rgba(34, 197, 94, 0.5); }}
        .star-empty {{ color: #ef4444; opacity: 0.6; }}
        
        /* Favori Yıldızı */
        .fav-star {{ cursor: pointer; color: #d1d5db; font-size: 20px; transition: 0.2s; }}
        .fav-star.active {{ color: #eab308; text-shadow: 0 0 10px rgba(234, 179, 8, 0.5); }}
        
        #modal-content {{ background: var(--modal-bg); color: var(--modal-text); border: 1px solid var(--border); }}
        .ai-box {{ background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 15px; }}
    </style></head>
    <body>
        <div class="legal-top">
            <strong>⚠️ SYSTEM NOTICE:</strong> Colors based on 5-Star Technicals + Rainbow Priority. 
            <br><em>Stars (5:Strong Buy, 0:Strong Sell). Action Text & Colors based on technical score + historical price position.</em>
        </div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl italic tracking-tighter brand-logo">BasedVector</h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full w-10 h-10 flex items-center justify-center" id="theme-toggle">🌙</button>
                    <div class="text-[10px] font-mono opacity-60">UPDATED: {full_update} UTC</div>
                </div>
            </header>

            <div class="mb-8">
                <h2 class="text-sm font-bold opacity-60 mb-3">BTC CORRELATION (TOP 10)</h2>
                <div class="grid grid-cols-5 md:grid-cols-10 gap-2">{corr_html}</div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <input type="text" id="search" placeholder="Search Assets..." class="bg-transparent border border-gray-500 p-3 rounded-xl w-full text-current outline-none focus:border-blue-500">
                <select id="sort" class="bg-transparent border border-gray-500 p-3 rounded-xl cursor-pointer w-full text-current">
                    <option value="score-desc">🔥 Best Technicals (Stars)</option>
                    <option value="score-asc">❄️ Weak Technicals</option>
                </select>
                <button onclick="toggleFavs()" id="fav-btn" class="bg-gray-800 text-white p-3 rounded-xl font-bold hover:bg-gray-700">★ Show Favorites</button>
            </div>

            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
    """

    for i in data:
        encoded_info = base64.b64encode(json.dumps(i['details']).encode()).decode()
        stars = "".join(['<span class="star-filled">★</span>' if s < i['score'] else '<span class="star-empty">★</span>' for s in range(5)])
        
        # Arka plan rengini yıldıza göre doldur
        html += f"""
        <div class="card p-5 flex flex-col justify-between" 
             style="border: 2px solid {i['card_color']}; background: {i['card_color']}20;"
             data-symbol="{i['symbol']}" data-score="{i['score']}">
            <div class="flex justify-between items-start mb-4">
                <div class="flex items-center gap-2">
                    <span class="fav-star" onclick="toggleFav(this, '{i['symbol']}')">★</span>
                    <span class="font-bold text-xl font-mono">{i['symbol']}</span>
                </div>
                <span class="action-badge" style="background:{i['card_color']}">{i['action_text']}</span>
            </div>
            
            <div class="text-center my-2 cursor-pointer" 
                 data-info="{encoded_info}" onclick="showDetails(this)">
                <div class="text-2xl font-black mb-1">${i['price']}</div>
                <div class="flex justify-center gap-1">
                    {stars}
                </div>
            </div>
            
            <div class="flex justify-between items-center text-[10px] opacity-50 mt-4 border-t border-gray-500/10 pt-2">
                <span>{i['score']}/5 Score</span>
                <span>{i['update_time']}</span>
            </div>
        </div>
        """

    html += """
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div id="modal-content" class="p-8 rounded-3xl max-w-md w-full relative shadow-2xl" onclick="event.stopPropagation()">
                <button onclick="document.getElementById('modal').classList.add('hidden')" class="absolute top-5 right-5 text-2xl opacity-50">&times;</button>
                <h3 id="m-title" class="text-3xl font-bold mb-6 border-b border-gray-500/10 pb-2"></h3>
                <div id="m-body" class="space-y-3 font-mono text-sm"></div>
                <div id="m-ai" class="ai-box italic text-sm text-blue-400"></div>
            </div>
        </div>
        <script>
            let showOnlyFavs = false;
            let favorites = JSON.parse(localStorage.getItem('favs') || '[]');

            function toggleTheme() {
                document.body.classList.toggle('light');
                const isLight = document.body.classList.contains('light');
                document.getElementById('theme-toggle').innerText = isLight ? '☀️' : '🌙';
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
            }
            
            function toggleFav(el, symbol) {
                el.classList.toggle('active');
                if (favorites.includes(symbol)) {
                    favorites = favorites.filter(s => s !== symbol);
                } else {
                    favorites.push(symbol);
                }
                localStorage.setItem('favs', JSON.stringify(favorites));
                render();
            }

            function toggleFavs() {
                showOnlyFavs = !showOnlyFavs;
                document.getElementById('fav-btn').innerText = showOnlyFavs ? '☆ Show All' : '★ Show Favorites';
                render();
            }

            function showDetails(el) {
                const details = JSON.parse(atob(el.dataset.info));
                const card = el.closest('.card');
                document.getElementById('m-title').innerText = card.dataset.symbol;
                let content = "";
                for (const [k, v] of Object.entries(details)) {
                    if (k !== 'AI_Eval') content += `<div class="flex justify-between border-b border-gray-500/10 py-3"><span class="opacity-60">${k}</span><b>${v}</b></div>`;
                }
                document.getElementById('m-body').innerHTML = content;
                document.getElementById('m-ai').innerHTML = "<b>AI INSIGHT:</b><br>" + details.AI_Eval;
                document.getElementById('modal').classList.remove('hidden');
            }
            
            function render() {
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value; 
                let cards = Array.from(document.querySelectorAll('.card'));
                
                cards.forEach(c => {
                    const symbol = c.dataset.symbol;
                    const isFav = favorites.includes(symbol);
                    
                    // Fav yıldızını güncelle
                    const star = c.querySelector('.fav-star');
                    if (isFav) star.classList.add('active'); else star.classList.remove('active');
                    
                    // Filtreleme
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
            window.onload = () => { 
                if(localStorage.getItem('theme')==='light') toggleTheme(); 
                render(); 
            };
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    create_html(analyze_market())
