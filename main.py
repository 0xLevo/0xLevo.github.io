import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from datetime import datetime, timezone
import json 
import base64
import random

# --- FULL ASSET LIST (CMC TOP 100) ---
CMC_TOP_100 = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 
    'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'BCH', 'ATOM', 'UNI', 'NEAR', 'INJ', 
    'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 
    'KAS', 'ETC', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'FTM', 'SAND',
    'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 
    'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 
    'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 
    'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 
    'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK'
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
        
        if diff < -0.4: return "FIRE SALE", "#16a34a"  # Koyu Yeşil
        elif diff < -0.15: return "BUY", "#86efac"     # Açık Yeşil
        elif diff < 0.15: return "NEUTRAL", "#94a3b8"  # Gri
        elif diff < 0.4: return "FOMO", "#facc15"      # Sarı
        else: return "BUBBLE", "#dc2626"               # Kırmızı
    except: return "UNKNOWN", "#94a3b8"

def get_ai_eval(score, rb):
    if score >= 4 and rb in ["FIRE SALE", "BUY"]: return "ALPHA OPPORTUNITY: Technicals and historical valuation are perfectly aligned for entry."
    if score <= 2 and rb == "BUBBLE": return "HIGH RISK: Overextended on all timeframes. Extreme caution advised."
    return "MARKET NOISE: Stay patient. Look for a convergence between star rating and rainbow zone."

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
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
            
            rb_text, rb_color = get_rainbow_status(df)

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': star_count, 'rb_text': rb_text, 'rb_color': rb_color,
                'details': {
                    "RSI": round(rsi, 1), "MFI": round(mfi, 1),
                    "SMA20": "Above" if curr_price > sma else "Below",
                    "Rainbow": rb_text, "Stars": f"{star_count}/5",
                    "AI_Eval": get_ai_eval(star_count, rb_text)
                },
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.05)
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --border: #333; --modal-bg: #111; --modal-text: #f8fafc; }}
        .light {{ --bg: #f1f5f9; --card: #ffffff; --text: #0f172a; --border: #cbd5e1; --modal-bg: #fff; --modal-text: #0f172a; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 100px; transition: 0.3s; }}
        
        .brand-logo {{
            background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
        }}
        
        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
        .card {{ border-radius: 16px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: var(--card); overflow: hidden; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 20px 30px -10px rgba(0,0,0,0.3); }}
        
        .rainbow-badge {{ font-size: 9px; padding: 2px 8px; border-radius: 99px; font-weight: bold; color: #000; }}
        .star-filled {{ color: #eab308; text-shadow: 0 0 10px rgba(234, 179, 8, 0.4); }}
        .star-empty {{ color: #4b5563; opacity: 0.2; }}
        
        #modal-content {{ background: var(--modal-bg); color: var(--modal-text); border: 1px solid var(--border); }}
        .ai-box {{ background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 15px; }}
    </style></head>
    <body>
        <div class="legal-top"><strong>⚠️ SYSTEM NOTICE:</strong> Combining 5-Star Technicals with Logarithmic Regression.</div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl italic tracking-tighter brand-logo">BasedVector</h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full w-10 h-10 flex items-center justify-center" id="theme-toggle">🌙</button>
                    <div class="text-[10px] font-mono opacity-60">UPDATED: {full_update} UTC</div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <input type="text" id="search" placeholder="Search Assets..." class="bg-transparent border border-gray-500 p-3 rounded-xl w-full text-current outline-none focus:border-blue-500">
                <select id="sort" class="bg-transparent border border-gray-500 p-3 rounded-xl cursor-pointer w-full text-current">
                    <option value="score-desc">🔥 Best Technicals (Stars)</option>
                    <option value="score-asc">❄️ Weak Technicals</option>
                </select>
            </div>

            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
    """

    for i in data:
        encoded_info = base64.b64encode(json.dumps(i['details']).encode()).decode()
        stars = "".join(['<span class="star-filled">★</span>' if s < i['score'] else '<span class="star-empty">★</span>' for s in range(5)])
        
        html += f"""
        <div class="card p-5 flex flex-col justify-between" 
             style="border-bottom: 4px solid {i['rb_color']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" 
             data-info="{encoded_info}" onclick="showDetails(this)">
            <div class="flex justify-between items-start mb-4">
                <span class="font-bold text-xl font-mono">{i['symbol']}</span>
                <span class="rainbow-badge" style="background:{i['rb_color']}">{i['rb_text']}</span>
            </div>
            <div class="text-center my-2">
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
            function toggleTheme() {
                document.body.classList.toggle('light');
                const isLight = document.body.classList.contains('light');
                document.getElementById('theme-toggle').innerText = isLight ? '☀️' : '🌙';
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
            }
            function showDetails(el) {
                const details = JSON.parse(atob(el.dataset.info)); 
                document.getElementById('m-title').innerText = el.dataset.symbol;
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
                cards.forEach(c => c.style.display = c.dataset.symbol.includes(term) ? 'flex' : 'none');
                const grid = document.getElementById('grid');
                cards.sort((a, b) => sortVal === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score);
                cards.forEach(c => grid.appendChild(c));
            }
            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            window.onload = () => { if(localStorage.getItem('theme')==='light') toggleTheme(); render(); };
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    create_html(analyze_market())
