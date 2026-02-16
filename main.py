import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import json 

# --- CMC TOP 100 LIST ---
CMC_TOP_100 = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK']

def get_rsi_score(rsi):
    if rsi < 20: return 3
    if rsi < 30: return 2
    if rsi < 40: return 1
    if rsi < 50: return 0
    if rsi < 60: return -1
    if rsi < 70: return -2
    return -3

def get_macd_score(macd, signal):
    diff = macd - signal
    if diff > 0.5: return 3
    if diff > 0.1: return 2
    if diff > 0: return 1
    if diff > -0.1: return -1
    if diff > -0.5: return -2
    return -3

def get_cci_score(cci):
    if cci < -200: return 3
    if cci < -100: return 2
    if cci < -50: return 1
    if cci < 50: return 0
    if cci < 100: return -1
    if cci < 200: return -2
    return -3

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    print("Starting Advanced Analysis...")
    
    for symbol in CMC_TOP_100:
        pair = f"{symbol}/USDT"
        try:
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 50: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # Indicators
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            macd_df = ta.macd(df['close'])
            macd = macd_df.iloc[-1, 0]
            signal = macd_df.iloc[-1, 2]
            cci = ta.cci(df['high'], df['low'], df['close'], length=20).iloc[-1]
            
            # Scoring
            s1 = get_rsi_score(rsi)
            s2 = get_macd_score(macd, signal)
            s3 = get_cci_score(cci)
            avg_score = (s1 + s2 + s3) / 3
            
            # Decision Colors & BasedVector Text Colors
            if avg_score == 0:
                bg_color = "rgba(51, 65, 85, 0.2)"; border_color = "rgba(51, 65, 85, 0.5)" # Gray
                bar_color = "#64748b"; text_color = "#94a3b8"
            elif -1.5 <= avg_score < 0:
                bg_color = "rgba(239, 68, 68, 0.15)"; border_color = "rgba(239, 68, 68, 0.4)" # Light Red
                bar_color = "#ef4444"; text_color = "#f87171"
            elif avg_score < -1.5:
                bg_color = "rgba(185, 28, 28, 0.25)"; border_color = "rgba(185, 28, 28, 0.6)" # Dark Red
                bar_color = "#b91c1c"; text_color = "#ef4444"
            elif 0 < avg_score <= 1.5:
                bg_color = "rgba(34, 197, 94, 0.15)"; border_color = "rgba(34, 197, 94, 0.4)" # Light Green
                bar_color = "#22c55e"; text_color = "#4ade80"
            else: # 1.5 < avg_score <= 3
                bg_color = "rgba(16, 185, 129, 0.25)"; border_color = "rgba(16, 185, 129, 0.6)" # Dark Green
                bar_color = "#10b981"; text_color = "#10b981"

            results.append({
                'symbol': symbol,
                'price': f"{df['close'].iloc[-1]:.5g}",
                'bg_color': bg_color,
                'border_color': border_color,
                'bar_color': bar_color,
                'text_color': text_color,
                'score': round(avg_score, 1),
                'details': {
                    'RSI (14)': s1,
                    'MACD': s2,
                    'CCI (20)': s3
                }
            })
            time.sleep(0.05)
        except Exception: continue
    return results

def create_html(data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    data_json = json.dumps({item['symbol']: item['details'] for item in data})
    based_color = data[0]['text_color'] if data else "#3b82f6"
    
    html_header = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Alpha Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-body: #000000;
                --bg-card: #0a0a0a;
                --text-main: #f1f5f9;
                --border-card: #161616;
            }}
            .light {{
                --bg-body: #f8fafc;
                --bg-card: #ffffff;
                --text-main: #0f172a;
                --border-card: #e2e8f0;
            }}
            body {{ background-color: var(--bg-body); color: var(--text-main); font-family: 'Space Grotesk', sans-serif; transition: background 0.3s, color 0.3s; }}
            .card {{ background: var(--bg-card); border: 1px solid var(--border-card); transition: all 0.3s; border-radius: 16px; cursor: pointer; backdrop-filter: blur(10px); }}
            .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(255, 255, 255, 0.05); }}
            .light .card:hover {{ box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .star-btn {{ font-size: 1.2rem; cursor: pointer; color: rgba(100,116,139,0.3); z-index: 10; position: relative;}}
            .light .star-btn {{ color: rgba(100,116,139,0.5); }}
            .star-btn.active {{ color: #eab308; }}
            
            /* Modal Backdrop */
            .modal-backdrop {{ background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); }}
            .light .modal-backdrop {{ background: rgba(0, 0, 0, 0.5); }}
            
            /* Score Bar Styles */
            .score-bar-container {{
                width: 100%;
                height: 8px;
                background-color: #1f2937;
                border-radius: 4px;
                position: relative;
                margin-top: 8px;
                overflow: hidden;
            }}
            .light .score-bar-container {{ background-color: #e2e8f0; }}
            
            .score-bar-fill {{
                height: 100%;
                border-radius: 4px;
                transition: width 0.5s ease-out;
                position: absolute;
                top: 0;
            }}
            .score-bar-center {{
                position: absolute;
                top: 0;
                left: 50%;
                width: 2px;
                height: 100%;
                background-color: #4b5563;
                transform: translateX(-50%);
            }}
        </style>
    </head>
    <body class="p-4 md:p-8">
        <div class="max-w-7xl mx-auto">
            
            <div class="bg-blue-950/30 border border-blue-900/50 text-blue-200 text-xs text-center p-2 rounded-lg mb-6 font-medium">
                ⚠️ Legal Disclaimer: All information is for educational purposes only. Not financial advice.
            </div>

            <header class="mb-10 pb-6 border-b border-slate-900">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-4xl font-bold tracking-tighter text-white">
                        <span style="color: {based_color};">Based</span>Vector 
                        <span class="text-xs font-mono bg-blue-950 text-blue-300 px-2 py-0.5 rounded">ALPHA</span>
                    </h1>
                    <div class="flex items-center gap-3">
                        <div class="text-right text-sm">
                            <p class="text-slate-400">Data Source: MEXC Global</p>
                            <p class="font-mono text-blue-400">{now} UTC</p>
                        </div>
                        <button onclick="toggleTheme()" id="theme-toggle" class="p-2 rounded-full bg-slate-900 text-white">🌙</button>
                    </div>
                </div>
                
                <div class="flex flex-col md:flex-row gap-4 glass p-4 rounded-xl bg-slate-950 border border-slate-900">
                    <input type="text" id="search" placeholder="🔍 Search Assets (e.g. BTC)..." class="bg-black p-3 rounded-lg w-full text-sm border border-slate-800 text-white placeholder-slate-600 focus:border-blue-500 focus:outline-none">
                    <select id="sort" class="bg-black p-3 rounded-lg text-sm border border-slate-800 text-white focus:border-blue-500">
                        <option value="score-desc">Score: High to Low</option>
                        <option value="score-asc">Score: Low to High</option>
                    </select>
                    <button onclick="toggleView()" id="view-toggle" class="bg-slate-900 hover:bg-slate-800 text-white px-5 py-3 rounded-lg text-sm font-bold flex items-center gap-2 border border-slate-800 whitespace-nowrap">
                        ⭐ My Watchlist
                    </button>
                </div>
            </header>

            <div id="coin-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """
    
    html_content = ""
    for item in data:
        intensity = abs(item['score']) / 3 * 50 
        
        if item['score'] >= 0:
            bar_style = f"width: {intensity}%; left: 50%; background-color: {item['bar_color']};"
        else:
            bar_style = f"width: {intensity}%; left: {50 - intensity}%; background-color: {item['bar_color']};"
            
        html_content += f"""
        <div class="card p-5 flex flex-col justify-between" 
             style="background-color: {item['bg_color']}; border: 1px solid {item['border_color']};"
             data-symbol="{item['symbol']}" data-score="{item['score']}"
             onclick="showDetails('{item['symbol']}')">
            <div class="flex justify-between items-center mb-3">
                <div class="flex items-center gap-2">
                    <button onclick="event.stopPropagation(); toggleFavorite(this, '{item['symbol']}')" class="star-btn">★</button>
                    <span class="font-bold text-lg text-white font-mono">{item['symbol']}</span>
                </div>
            </div>
            
            <div class="text-center my-2">
                <p class="text-2xl font-bold text-white font-mono mb-0.5">${item['price']}</p>
                
                <div class="score-bar-container">
                    <div class="score-bar-center"></div>
                    <div class="score-bar-fill" style="{bar_style}"></div>
                </div>
                <div class="flex justify-between text-[10px] text-slate-400 font-mono mt-1">
                    <span>-3</span>
                    <span
