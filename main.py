import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime, timezone
import json 
import random 
import base64
import os

# --- ASSET LIST ---
CMC_TOP_100 = [
    'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 
    'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 
    'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 
    'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 
    'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 
    'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 
    'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 
    'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 
    'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 
    'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 
    'ENS', 'ANKR', 'MASK'
]

def get_ai_eval(score):
    if score >= 4: return "STRONG BUY: Multiple technical confirmations. Trend is your friend."
    elif 3 <= score < 4: return "BULLISH: Positive alignment. Good entry potential."
    elif score == 2: return "NEUTRAL: Mixed signals. Watch for a breakout."
    else: return "CAUTION: Weak technicals. Wait for volume confirmation."

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=60)
            if len(bars) < 30: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- 5 KRİTER HESAPLAMA ---
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
            bb = ta.bbands(df['close'], length=20, std=2)
            vol_avg = df['volume'].rolling(10).mean().iloc[-1]
            sma = ta.sma(df['close'], length=20).iloc[-1]
            curr_price = df['close'].iloc[-1]
            
            star_count = 0
            if rsi < 50: star_count += 1      # 1. RSI Pozitif
            if mfi < 50: star_count += 1      # 2. Para Akışı Pozitif
            if curr_price < bb.iloc[-1, 1]: star_count += 1 # 3. BB Orta Bant Altı (Ucuz)
            if df['volume'].iloc[-1] > vol_avg: star_count += 1 # 4. Hacim Desteği
            if curr_price > sma: star_count += 1 # 5. Trend Üstü (Boğa)
            
            # Renk belirleme
            color_map = {
                5: "#22c55e", 4: "#4ade80", 3: "#94a3b8", 2: "#fb7185", 1: "#ef4444", 0: "#b91c1c"
            }
            bar_color = color_map.get(star_count, "#94a3b8")

            details = {
                "RSI": round(rsi, 1),
                "MFI": round(mfi, 1),
                "Price_vs_SMA": "Above" if curr_price > sma else "Below",
                "Volume_Status": "Strong" if df['volume'].iloc[-1] > vol_avg else "Weak",
                "AI_Eval": get_ai_eval(star_count)
            }

            results.append({
                'symbol': symbol, 'price': f"{curr_price:.5g}",
                'score': star_count, 'details': details, 'bar': bar_color,
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
        .light {{ --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --border: #e2e8f0; --modal-bg: #fff; --modal-text: #0f172a; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 100px; transition: 0.3s; }}
        .brand-logo {{
            background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
        }}
        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
        .card {{ border-radius: 12px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: var(--card); overflow: hidden; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }}
        #modal-content {{ background: var(--modal-bg); color: var(--modal-text); border: 1px solid var(--border); }}
        .ai-box {{ background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 15px; }}
        .star-filled {{ color: #eab308; }}
        .star-empty {{ color: #4b5563; opacity: 0.3; }}
        .live-indicator {{ width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; margin-right: 5px; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }} }}
    </style></head>
    <body>
        <div class="legal-top"><strong>⚠️ LEGAL DISCLAIMER:</strong> Not financial advice. Technicals + AI Logic.</div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl italic tracking-tighter brand-logo">BasedVector</h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full w-10 h-10 flex items-center justify-center" id="theme-toggle">🌙</button>
                    <div class="text-[10px] font-mono opacity-60">UPDATED: {full_update} UTC</div>
                </div>
            </header>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <input type="text" id="search" placeholder="Search..." class="bg-transparent border border-gray-500 p-3 rounded-lg w-full text-current outline-none">
                <select id="sort" class="bg-transparent border border-gray-500 p-3 rounded-lg cursor-pointer w-full text-current">
                    <option value="score-desc">🔥 Stars: High</option>
                    <option value="score-asc">❄️ Stars: Low</option>
                </select>
            </div>
            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """

    for i in data:
        detail_json = json.dumps(i['details'])
        encoded_details = base64.b64encode(detail_json.encode()).decode()
        
        # Yıldızları oluştur
        stars_html = ""
        for s in range(5):
            if s < i['score']:
                stars_html += '<span class="star-filled text-lg">★</span>'
            else:
                stars_html += '<span class="star-empty text-lg">★</span>'

        html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="border-bottom: 4px solid {i['bar']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" 
             data-info="{encoded_details}" onclick="showSafeDetails(this)">
            <div class="font-bold text-lg font-mono mb-2">{i['symbol']}</div>
            <div class="text-center">
                <div class="text-2xl font-bold">${i['price']}</div>
                <div class="flex justify-center gap-1 my-2">
                    {stars_html}
                </div>
            </div>
            <div class="flex justify-between items-center text-[10px] opacity-60 font-mono mt-2">
                <span class="font-bold">{i['score']}/5 Criteria</span>
                <span>{i['update_time']}</span>
            </div>
        </div>
        """

    html += """
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div id="modal-content" class="p-8 rounded-2xl max-w-md w-full relative" onclick="event.stopPropagation()">
                <button onclick="document.getElementById('modal').classList.add('hidden')" class="absolute top-4 right-4 text-2xl opacity-50">&times;</button>
                <h3 id="m-title" class="text-3xl font-bold mb-6 border-b border-gray-500/20 pb-2"></h3>
                <div id="m-body" class="space-y-3 font-mono text-sm"></div>
                <div id="m-ai" class="ai-box italic text-sm"></div>
            </div>
        </div>
        <script>
            function toggleTheme() {
                document.body.classList.toggle('light');
                const isLight = document.body.classList.contains('light');
                document.getElementById('theme-toggle').innerText = isLight ? '☀️' : '🌙';
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
            }
            function showSafeDetails(el) {
                const sym = el.dataset.symbol;
                const details = JSON.parse(atob(el.dataset.info)); 
                document.getElementById('m-title').innerText = sym;
                let content = "";
                for (const [k, v] of Object.entries(details)) {
                    if (k !== 'AI_Eval') content += `<div class="flex justify-between border-b border-gray-500/10 py-3"><span style="opacity:0.6">${k}</span><b>${v}</b></div>`;
                }
                document.getElementById('m-body').innerHTML = content;
                document.getElementById('m-ai').innerHTML = "<b>AI ANALYSIS:</b><br>" + details.AI_Eval;
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
    market_data = analyze_market()
    create_html(market_data)
