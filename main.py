import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import json 

# --- CMC TOP 100 LIST (Ordered by Market Cap) ---
CMC_TOP_100 = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK']

def get_pro_score(df):
    """Calculates a weighted score based on 6 professional indicators."""
    try:
        # 1. Momentum (RSI & MFI) - 30% Weight
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
        
        m_score = 0
        if rsi < 30 or mfi < 25: m_score += 1.5
        if rsi > 70 or mfi > 75: m_score -= 1.5
        
        # 2. Volatility (Bollinger Bands) - 30% Weight
        bb = ta.bbands(df['close'], length=20, std=2)
        curr_price = df['close'].iloc[-1]
        lower_band = bb.iloc[-1, 0]
        upper_band = bb.iloc[-1, 2]
        
        v_score = 0
        if curr_price <= lower_band: v_score += 1.5 # Oversold relative to volatility
        elif curr_price >= upper_band: v_score -= 1.5 # Overbought relative to volatility
        
        # 3. Trend & Strength (EMA Cross & ADX) - 40% Weight
        ema20 = ta.ema(df['close'], length=20).iloc[-1]
        ema50 = ta.ema(df['close'], length=50).iloc[-1]
        adx = ta.adx(df['high'], df['low'], df['close'], length=14).iloc[-1, 0]
        
        t_score = 1.0 if ema20 > ema50 else -1.0
        strength_multiplier = 2.0 if adx > 25 else 0.5 # Double the score if trend is strong
        
        final_score = (m_score) + (v_score) + (t_score * strength_multiplier)
        return round(max(min(final_score, 3), -3), 1), {
            "RSI": round(rsi, 1),
            "MFI": round(mfi, 1),
            "ADX": round(adx, 1),
            "Trend": "Bull" if ema20 > ema50 else "Bear"
        }
    except:
        return 0, {}

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    print("Executing Alpha Terminal Analysis...")
    
    for index, symbol in enumerate(CMC_TOP_100):
        pair = f"{symbol}/USDT"
        try:
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 60: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            score, details = get_pro_score(df)
            
            # Color Mapping
            if score >= 1.5: bg, border, bar = "rgba(6, 78, 59, 0.3)", "rgba(16, 185, 129, 0.6)", "#10b981"
            elif 0 < score < 1.5: bg, border, bar = "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)", "#22c55e"
            elif -1.5 < score < 0: bg, border, bar = "rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.3)", "#ef4444"
            elif score <= -1.5: bg, border, bar = "rgba(153, 27, 27, 0.3)", "rgba(185, 28, 28, 0.6)", "#b91c1c"
            else: bg, border, bar = "rgba(148, 163, 184, 0.1)", "rgba(148, 163, 184, 0.3)", "#94a3b8"

            results.append({
                'symbol': symbol, 'price': f"{df['close'].iloc[-1]:.5g}",
                'rank': index + 1, 'bg_color': bg, 'border_color': border, 'bar_color': bar,
                'score': score, 'details': details
            })
            time.sleep(0.02)
        except: continue
    return results

def create_html(data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    data_json = json.dumps({item['symbol']: item['details'] for item in data})
    
    css = """
        :root { --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --sec: #94a3b8; }
        .light { --bg: #f1f5f9; --card: #ffffff; --text: #0f172a; --sec: #475569; }
        body { background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; transition: 0.3s; padding-top: 50px; }
        .legal-top { background: #dc2626; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        .card { border-radius: 16px; border: 1px solid; cursor: pointer; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; }
        .card:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 15px 30px rgba(0,0,0,0.4); z-index: 10; }
        .based-gradient { background: linear-gradient(90deg, #ef4444, #94a3b8, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .star-btn { font-size: 1.5rem; color: #334155; transition: 0.2s; }
        .star-btn.active { color: #eab308 !important; }
        .custom-input { background: var(--card); border: 1px solid #262626; color: var(--text); }
    """

    html_start = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>BasedVector | Professional Alpha Terminal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>{css}</style></head><body>
    <div class="legal-top">⚠️ TRADING RISK WARNING: High volatility. Analysis is mathematical, not financial advice. BasedVector does not guarantee profits.</div>
    <div class="max-w-7xl mx-auto p-4">
        <header class="flex flex-col lg:flex-row justify-between items-center mb-10 gap-6 mt-6">
            <h1 class="text-6xl based-gradient tracking-tighter">BasedVector</h1>
            <div class="flex items-center gap-6">
                <div class="text-right hidden sm:block">
                    <div class="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Global Market Scan</div>
                    <div class="text-sm text-blue-500 font-mono font-bold">{now} UTC</div>
                </div>
                <button onclick="toggleTheme()" class="w-12 h-12 flex items-center justify-center bg-gray-800/40 rounded-full hover:bg-gray-700 transition border border-gray-700">🌙</button>
            </div>
        </header>

        <div class="bg-gray-900/30 backdrop-blur-sm border border-gray-800/50 p-6 rounded-2xl flex flex-col xl:flex-row gap-4 mb-10 shadow-xl">
            <input type="text" id="search" placeholder="Filter by Ticker..." class="custom-input p-4 rounded-xl w-full outline-none focus:border-blue-500/50 transition font-mono">
            
            <div class="flex flex-wrap md:flex-nowrap gap-4">
                <select id="sort" class="custom-input p-4 rounded-xl outline-none cursor-pointer text-sm min-w-[220px]">
                    <option value="score-desc">🔥 Score: High to Low</option>
                    <option value="score-asc">❄️ Score: Low to High</option>
                    <option value="cap-desc">💎 Market Cap: Top 1st</option>
                    <option value="cap-asc">📊 Market Cap: 100th</option>
                </select>

                <select id="layout" class="custom-input p-4 rounded-xl outline-none cursor-pointer text-sm font-bold">
                    <option value="grid-cols-2">2 COL VIEW</option>
                    <option value="grid-cols-4" selected>4 COL VIEW</option>
                    <option value="grid-cols-5">5 COL VIEW</option>
                </select>

                <button onclick="toggleFavView()" id="fav-btn" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold transition-all flex items-center gap-2 shadow-lg shadow-blue-900/20">
                    <span>⭐</span> WATCHLIST
                </button>
            </div>
        </div>

        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-6 transition-all duration-500">
    """

    cards_html = ""
    for i in data:
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        
        cards_html += f"""
        <div class="card p-6 flex flex-col justify-between" 
             style="background: {i['bg_color']}; border-color: {i['border_color']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" data-rank="{i['rank']}"
             onclick="showDetails('{i['symbol']}')">
            
            <div class="flex justify-between items-start mb-6">
                <div>
                    <span class="text-[10px] font-black text-gray-500/80 font-mono mb-1 block">MCAP RANK #{i['rank']}</span>
                    <span class="font-bold text-3xl font-mono leading-none tracking-tighter">{i['symbol']}</span>
                </div>
                <button onclick="event.stopPropagation(); toggleFavorite(this, '{i['symbol']}')" class="star-btn">★</button>
            </div>

            <div class="text-center">
                <div class="text-3xl font-bold mb-6 tracking-tight text-white">${i['price']}</div>
                <div class="h-2.5 bg-gray-700/30 rounded-full relative overflow-hidden mb-3">
                    <div class="absolute h-full transition-all duration-1000 cubic-bezier(0.4, 0, 0.2, 1)" style="{bar_pos} background:{i['bar_color']}; box-shadow: 0 0 10px {i['bar_color']}80;"></div>
                </div>
                <div class="flex justify
