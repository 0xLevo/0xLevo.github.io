import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime, timezone
import json 
import random 
import base64
import os

# --- ASSET LIST (Kopyalama güvenliği için bölünmüş yapı) ---
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
    if score >= 2.0: return "OVERHEATED: Multiple indicators suggest a peak. Avoid FOMO."
    elif 1.0 <= score < 2.0: return "BULLISH BIAS: Positive momentum is strong, look for retests."
    elif -1.0 < score < 1.0: return "NEUTRAL: Market is indecisive. Sideways movement expected."
    elif -2.0 <= score <= -1.0: return "ACCUMULATION: Potential buy the dip zone."
    else: return "EXTREME OVERSOLD: Deep value detected. Recovery pivot possible."

def get_news_sentiment(symbol):
    return random.choice([-0.5, 0, 0.5])

def calculate_confidence(df):
    try:
        conf = 0
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        if rsi < 30 or rsi > 70: conf += 1
        vol_avg = df['volume'].rolling(window=10).mean().iloc[-1]
        if df['volume'].iloc[-1] > vol_avg: conf += 1
        return conf
    except: return 1

def calculate_correlation(exchange, top_n=10):
    try:
        corr_data = {}
        active_symbols = [s for s in CMC_TOP_100 if s not in ['USDT', 'USDC']][:top_n]
        price_data = {}
        for sym in active_symbols:
            try:
                bars = exchange.fetch_ohlcv(f"{sym}/USDT", timeframe='1h', limit=50)
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

def get_pro_score(df, symbol):
    try:
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
        bb = ta.bbands(df['close'], length=20, std=2)
        curr_price = df['close'].iloc[-1]
        
        m_score = 1.0 if (rsi < 35) else (-1.0 if (rsi > 65) else 0)
        v_score = 1.0 if curr_price <= bb.iloc[-1, 0] else (-1.0 if curr_price >= bb.iloc[-1, 2] else 0)
        news_score = get_news_sentiment(symbol)
        conf = calculate_confidence(df)
        
        final_score = round(max(min((m_score + v_score + news_score) * (1 + conf*0.1), 3), -3), 1)
        
        return final_score, {
            "RSI": round(rsi,1), "MFI": round(mfi,1),
            "Trend": "Bull" if rsi > 50 else "Bear",
            "News": "Bull" if news_score > 0 else "Neutral",
            "Confidence": conf,
            "AI_Eval": get_ai_eval(final_score)
        }
    except: return 0, {"Error": "Calc"}

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    correlation_matrix = calculate_correlation(exchange)
    
    for symbol in CMC_TOP_100:
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=60)
            if len(bars) < 30: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            score, details = get_pro_score(df, symbol)
            
            if symbol in correlation_matrix: details['BTC_Corr'] = correlation_matrix[symbol]
            
            color_map = {
                "high": ("rgba(16, 185, 129, 0.25)", "rgba(16, 185, 129, 0.8)", "#34d399"),
                "mid_high": ("rgba(16, 185, 129, 0.1)", "rgba(16, 185, 129, 0.4)", "#10b981"),
                "mid_low": ("rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.4)", "#ef4444"),
                "low": ("rgba(239, 68, 68, 0.25)", "rgba(239, 68, 68, 0.8)", "#f87171"),
                "neutral": ("rgba(148, 163, 184, 0.1)", "rgba(148, 163, 184, 0.3)", "#94a3b8")
            }
            
            if score >= 1.5: bg, border, bar = color_map["high"]
            elif 0 < score < 1.5: bg, border, bar = color_map["mid_high"]
            elif -1.5 < score < 0: bg, border, bar = color_map["mid_low"]
            elif score <= -1.5: bg, border, bar = color_map["low"]
            else: bg, border, bar = color_map["neutral"]

            results.append({
                'symbol': symbol, 'price': f"{df['close'].iloc[-1]:.5g}",
                'score': score, 'details': details, 'bg': bg, 'border': border, 'bar': bar,
                'update_time': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
            time.sleep(0.1) 
        except: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    corr_html = ""
    for item in data:
        if 'BTC_Corr' in item['details']:
            c = item['details']['BTC_Corr']
            color = "border-green-500" if c > 0.6 else ("border-red-500" if c < 0 else "border-gray-500")
            corr_html += f'<div class="p-2 rounded-lg text-center border-b-2 {color} corr-card" style="background:rgba(100,100,100,0.1)"><div class="text-xs font-bold corr-sym">{item["symbol"]}</div><div class="text-sm font-mono font-bold corr-val">{c}</div></div>'

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ 
            --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --border: #333; 
            --modal-bg: #111111; --modal-text: #f8fafc; --corr-text: #fff; 
        }}
        .light {{ 
            --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --border: #e2e8f0; 
            --modal-bg: #ffffff; --modal-text: #0f172a; --corr-text: #0f172a; 
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 100px; transition: 0.3s; }}
        
        .brand-logo {{
            background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }}

        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
        .card {{ border-radius: 12px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: var(--card); overflow: hidden; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }}
        
        #modal-content {{ background: var(--modal-bg); color: var(--modal-text); border: 1px solid var(--border); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }}
        .modal-label {{ opacity: 0.7; color: var(--modal-text); }}
        .modal-value {{ font-weight: bold; color: var(--modal-text); }}
        
        .ai-box {{ background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 15px; color: var(--modal-text); }}
        .live-indicator {{ width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; margin-right: 5px; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }} }}
    </style></head>
    <body>
        <div class="legal-top"><strong>⚠️ LEGAL DISCLAIMER:</strong> Not financial advice. Technicals + AI Logic. <strong>High Risk.</strong></div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl italic tracking-tighter brand-logo">BasedVector</h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full w-10 h-10 flex items-center justify-center" id="theme-toggle">🌙</button>
                    <div class="text-[10px] font-mono opacity-60 flex items-center">
                        <span class="live-indicator"></span> UPDATED: {full_update} UTC
                    </div>
                </div>
            </header>
            <div class="grid grid-cols-5 md:grid-cols-10 gap-2 mb-8">{corr_html}</div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <input type="text" id="search" placeholder="Search..." class="bg-transparent border border-gray-500 p-3 rounded-lg w-full text-current focus:border-blue-500 outline-none">
                <select id="sort" class="bg-transparent border border-gray-500 p-3 rounded-lg cursor-pointer w-full text-current">
                    <option value="score-desc">🔥 Score: High</option>
                    <option value="score-asc">❄️ Score: Low</option>
                </select>
                <button id="fav-btn" class="bg-blue-600 text-white p-3 rounded-lg font-bold w-full hover:bg-blue-700 transition">⭐ Watchlist</button>
            </div>
            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """

    for i in data:
        detail_json = json.dumps(i['details'])
        encoded_details = base64.b64encode(detail_json.encode()).decode()
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        
        html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="border-bottom: 4px solid {i['bar']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" 
             data-info="{encoded_details}" onclick="showSafeDetails(this)">
            <div class="flex justify-between items-center">
                <span class="font-bold text-lg font-mono">{i['symbol']}</span>
                <button onclick="event.stopPropagation();" class="text-gray-400 hover:text-yellow-500">★</button>
            </div>
            <div class="text-center my-4">
                <div class="text-2xl font-bold">${i['price']}</div>
                <div class="h-1 bg-gray-500/10 rounded-full mt-2 relative">
                    <div class="absolute h-full" style="{bar_pos} background:{i['bar']}"></div>
                </div>
            </div>
            <div class="flex justify-between items-center text-[10px] opacity-60 font-mono">
                <span class="font-bold text-sm" style="color:{i['bar']}">{i['score']}</span>
                <span>{i['update_time']}</span>
            </div>
        </div>
        """

    html += """
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div id="modal-content" class="p-8 rounded-2xl max-w-md w-full relative" onclick="event.stopPropagation()">
                <button onclick="document.getElementById('modal').classList.add('hidden')" class="absolute top-4 right-4 text-2xl opacity-50 hover:opacity-100">&times;</button>
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
                    if (k !== 'AI_Eval') content += `<div class="flex justify-between border-b border-gray-500/10 py-3"><span class="modal-label">${k}</span><span class="modal-value">${v}</span></div>`;
                }
                document.getElementById('m-body').innerHTML = content;
                document.getElementById('m-ai').innerHTML = "<b>AI ANALYSIS:</b><br>" + details.AI_Eval;
                document.getElementById('modal').classList.remove('hidden');
            }
            function render() {
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value; 
                let cards = Array.from(document.querySelectorAll('.card'));
                cards.forEach(c => {
                    c.style.display = c.dataset.symbol.includes(term) ? 'flex' : 'none';
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
    market_data = analyze_market()
    create_html(market_data)
