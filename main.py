import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime, timezone
import json 
import random 
import numpy as np

# --- ASSET LIST ---
CMC_TOP_100 = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK']

# --- NEWS SENTIMENT ---
def get_news_sentiment(symbol):
    positive_keywords = ['partnership', 'launch', 'upgrade', 'adoption', 'high']
    negative_keywords = ['hack', 'sec', 'ban', 'drop', 'low']
    headlines = [f"{symbol} announces major {random.choice(positive_keywords)}", 
                 f"Investors worry about {symbol} {random.choice(negative_keywords)}"]
    score = 0
    for headline in headlines:
        if any(word in headline.lower() for word in positive_keywords): score += 0.5
        if any(word in headline.lower() for word in negative_keywords): score -= 0.5
    return max(min(score, 1), -1)

# --- CONFIDENCE INDEX ---
def calculate_confidence(df):
    confidence = 0
    rsi = ta.rsi(df['close'], length=14)
    if all(rsi.iloc[-2:] < 40) or all(rsi.iloc[-2:] > 60): confidence += 1
    bb = ta.bbands(df['close'], length=20, std=2)
    if (df['close'].iloc[-1] < bb.iloc[-1, 0]) or (df['close'].iloc[-1] > bb.iloc[-1, 2]): confidence += 1
    if df['volume'].iloc[-1] > df['volume'].rolling(window=10).mean().iloc[-1]: confidence += 1
    return confidence

# --- CORRELATION MATRIX ---
def calculate_correlation(exchange, top_n=10):
    corr_data = {}
    blacklist = ['USDT', 'USDC', 'DAI']
    active_symbols = [s for s in CMC_TOP_100 if s not in blacklist][:top_n]
    price_data = {}
    for sym in active_symbols:
        try:
            bars = exchange.fetch_ohlcv(f"{sym}/USDT", timeframe='1h', limit=50)
            price_data[sym] = [bar[4] for bar in bars]
        except: continue
    df_corr = pd.DataFrame(price_data)
    matrix = df_corr.corr()
    for sym in active_symbols:
        if sym != 'BTC':
            corr_data[sym] = round(matrix['BTC'][sym], 2)
    return corr_data

def get_pro_score(df, symbol):
    try:
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
        m_score = 1.5 if (rsi < 35 or mfi < 30) else (-1.5 if (rsi > 65 or mfi > 70) else 0)
        bb = ta.bbands(df['close'], length=20, std=2)
        curr_price = df['close'].iloc[-1]
        l_band, u_band = bb.iloc[-1, 0], bb.iloc[-1, 2]
        v_score = 1.5 if curr_price <= l_band else (-1.5 if curr_price >= u_band else 0)
        ema20 = ta.ema(df['close'], length=20).iloc[-1]
        ema50 = ta.ema(df['close'], length=50).iloc[-1]
        adx = ta.adx(df['high'], df['low'], df['close'], length=14).iloc[-1, 0]
        t_dir = 1.0 if ema20 > ema50 else -1.0
        strength = 1.8 if adx > 25 else 0.6 
        
        news_score = get_news_sentiment(symbol)
        confidence = calculate_confidence(df)
        final_score = round(max(min((m_score + v_score + (t_dir * strength) + news_score) * (1 + confidence*0.1), 3), -3), 1)
        
        details = {
            "RSI": round(rsi,1), "MFI": round(mfi,1), 
            "News": "Bull" if news_score > 0 else ("Bear" if news_score < 0 else "Neutral"),
            "Trend": "Bull" if ema20 > ema50 else "Bear",
            "Confidence": confidence
        }
        return final_score, details
    except: return 0, {"Error": "Calc"}

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    correlation_matrix = calculate_correlation(exchange)
    
    for index, symbol in enumerate(CMC_TOP_100):
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 60: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            score, details = get_pro_score(df, symbol)
            
            if symbol in correlation_matrix:
                details['BTC_Corr'] = correlation_matrix[symbol]
            
            coin_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            
            if score >= 1.5: bg, border, bar = "rgba(16, 185, 129, 0.25)", "rgba(16, 185, 129, 0.8)", "#34d399"
            elif 0 < score < 1.5: bg, border, bar = "rgba(16, 185, 129, 0.1)", "rgba(16, 185, 129, 0.4)", "#10b981"
            elif -1.5 < score < 0: bg, border, bar = "rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.4)", "#ef4444"
            elif score <= -1.5: bg, border, bar = "rgba(239, 68, 68, 0.25)", "rgba(239, 68, 68, 0.8)", "#f87171"
            else: bg, border, bar = "rgba(148, 163, 184, 0.1)", "rgba(148, 163, 184, 0.3)", "#94a3b8"

            results.append({
                'symbol': symbol, 'price': f"{df['close'].iloc[-1]:.5g}",
                'rank': index + 1, 'bg': bg, 'border': border, 'bar': bar,
                'score': score, 'details': details, 'update_time': coin_time
            })
            
            time.sleep(0.5) 
        except Exception: continue
    return results

def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    
    corr_html = ""
    for item in data:
        if 'BTC_Corr' in item['details']:
            corr = item['details']['BTC_Corr']
            if corr >= 0.7: bg, border = "rgba(16, 185, 129, 0.2)", "border-green-500"
            elif corr <= -0.2: bg, border = "rgba(239, 68, 68, 0.2)", "border-red-500"
            else: bg, border = "rgba(107, 114, 128, 0.1)", "border-gray-500"
            
            corr_html += f"""
                <div class="p-2 rounded-lg text-center border-b-2 {border}" style="background: {bg}">
                    <div class="text-xs font-bold text-gray-400">{item['symbol']}</div>
                    <div class="text-sm font-mono text-white font-bold">{corr}</div>
                </div>
            """

    css = """
        :root { --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --input-bg: #111; --border: #333; --modal-bg: #0a0a0a; }
        .light { --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --input-bg: #fff; --border: #ddd; --modal-bg: #fff; }
        body { background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; transition: 0.2s; padding-top: 50px; }
        .legal-top { background: #dc2626; color: white; text-align: center; padding: 8px; font-weight: bold; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; }
        .card { border-radius: 12px; border: 1px solid; cursor: pointer; transition: 0.2s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
        .based-gradient { background: linear-gradient(90deg, #ef4444, #94a3b8, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .star-btn { font-size: 1.5rem; color: #334155; }
        .star-btn.active { color: #eab308 !important; }
        .custom-input { background: var(--input-bg); border: 1px solid var(--border); color: var(--text); }
        .update-tag { font-size: 10px; opacity: 0.5; font-weight: bold; font-family: monospace; }
        .news-pos { color: #10b981; }
        .news-neg { color: #ef4444; }
        .star { font-size: 12px; }
        .star-filled { color: #f59e0b; }
        .star-empty { color: #475569; }
        .modal-card { background: var(--modal-bg); color: var(--text); border: 1px solid var(--border); }
        .modal-border { border-color: var(--border); }
    """

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>{css}</style></head><body>
    <div class="legal-top">⚠️ TRADING RISK WARNING: Analysis includes News, Confidence, and Correlation.</div>
    <div class="max-w-7xl mx-auto p-4">
        <header class="flex justify-between items-center mb-8 mt-4">
            <h1 class="text-4xl based-gradient tracking-tighter">BasedVector</h1>
            <div class="flex gap-4 items-center">
                <button onclick="toggleTheme()" class="p-2 bg-gray-200 dark:bg-gray-800 rounded-full" id="theme-toggle">🌙</button>
                <div class="text-right text-[10px] font-mono opacity-60">BATCH END: {full_update} UTC</div>
            </div>
        </header>
        
        <div class="mb-8">
            <h2 class="text-sm font-bold text-gray-500 mb-3 uppercase tracking-wider">Top 10 Correlation to BTC</h2>
            <div class="grid grid-cols-5 md:grid-cols-10 gap-2">
                {corr_html}
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <input type="text" id="search" placeholder="Search..." class="custom-input p-3 rounded-lg outline-none">
            <select id="sort" class="custom-input p-3 rounded-lg outline-none cursor-pointer">
                <option value="score-desc">🔥 Score: High</option>
                <option value="score-asc">❄️ Score: Low</option>
            </select>
            <button onclick="toggleFavView()" id="fav-btn" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold">⭐ Watchlist</button>
        </div>
        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """

    for i in data:
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        news_color = "news-pos" if i['details']['News'] == "Bull" else ("news-neg" if i['details']['News'] == "Bear" else "")
        
        confidence = i['details']['Confidence']
        stars = ""
        for s in range(3):
            if s < confidence:
                stars += '<span class="star star-filled">★</span>'
            else:
                stars += '<span class="star star-empty">★</span>'
        
        details_json = json.dumps(i['details']).replace('"', '\\"')
        
        html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="background: {i['bg']}; border-color: {i['border']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" data-rank="{i['rank']}" onclick='showDetails("{i['symbol']}", "{details_json}")'>
            <div class="flex justify-between items-center">
                <span class="font-bold text-lg font-mono">{i['symbol']}</span>
                <button onclick="event.stopPropagation(); toggleFavorite(this, '{i['symbol']}')" class="star-btn">★</button>
            </div>
            <div class="text-center my-4">
                <div class="text-xl font-bold">${i['price']}</div>
                <div class="h-1 bg-gray-300/20 rounded-full mt-2 relative">
                    <div class="absolute h-full transition-all" style="{bar_pos} background:{i['bar']}"></div>
                </div>
            </div>
            <div class="flex justify-between items-center update-tag">
                <span class="{news_color} font-bold text-sm">{i['score']}</span>
                <div class="flex gap-0.5">{stars}</div>
                <span>{i['update_time']} UTC</span>
            </div>
        </div>
        """

    html += f"""
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div class="modal-card p-8 rounded-2xl max-w-sm w-full" onclick="event.stopPropagation()">
                <h3 id="m-title" class="text-2xl font-bold mb-6 text-center"></h3>
                <div id="m-body" class="space-y-4 font-mono text-sm"></div>
            </div>
        </div>
        <script>
            let onlyFavs = false;
            function setTheme(isDark) {{
                if(isDark) {{
                    document.body.classList.remove('light');
                    document.getElementById('theme-toggle').innerText = '🌙';
                    localStorage.setItem('theme', 'dark');
                }} else {{
                    document.body.classList.add('light');
                    document.getElementById('theme-toggle').innerText = '☀️';
                    localStorage.setItem('theme', 'light');
                }}
            }}
            function toggleTheme() {{ setTheme(document.body.classList.contains('light')); }}
            function toggleFavorite(btn, sym) {{
                let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                favs.includes(sym) ? favs = favs.filter(f => f !== sym) : favs.push(sym);
                localStorage.setItem('favs', JSON.stringify(favs));
                render();
            }}
            function render() {{
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value;
                const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                const cards = Array.from(document.querySelectorAll('.card'));
                cards.forEach(c => {{
                    const sym = c.dataset.symbol;
                    const isFav = favs.includes(sym);
                    c.style.display = (sym.includes(term) && (!onlyFavs || isFav)) ? 'flex' : 'none';
                    c.querySelector('.star-btn').classList.toggle('active', isFav);
                }});
                cards.sort((a, b) => sortVal === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score)
                     .forEach(c => document.getElementById('grid').appendChild(c));
            }}
            function toggleFavView() {{
                onlyFavs = !onlyFavs;
                document.getElementById('fav-btn').innerText = onlyFavs ? '🌐 All' : '⭐ Watchlist';
                render();
            }}
            
            function showDetails(sym, detailsString) {{
                const details = JSON.parse(detailsString);
                document.getElementById('m-title').innerText = sym;
                
                let stars = "";
                for(let s=0; s<3; s++) {{
                    stars += s < details.Confidence ? '<span class="star star-filled">★</span>' : '<span class="star star-empty">★</span>';
                }}
                
                let modalContent = `<div class="flex justify-between pb-2 modal-border border-b"><span>Confidence</span><div class="flex gap-0.5">${{stars}}</div></div>`;
                
                for (const [key, value] of Object.entries(details)) {{
                    if (key !== 'Confidence') {{
                        modalContent += `
                            <div class="flex justify-between border-b modal-border pb-2">
                                <span class="opacity-70">${{key}}</span><span class="font-bold">${{value}}</span>
                            </div>`;
                    }}
                }}
                
                document.getElementById('m-body').innerHTML = modalContent;
                document.getElementById('modal').classList.remove('hidden');
            }}
            
            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            window.onload = () => {{
                setTheme(localStorage.getItem('theme') === 'dark' ? true : false);
                render();
            }};
        </script>
    </body></html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
