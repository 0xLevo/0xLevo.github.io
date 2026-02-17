import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import json 

# --- CMC TOP 100 LIST ---
CMC_TOP_100 = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK']

def get_pro_score(df):
    try:
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).iloc[-1]
        m_score = 1.5 if (rsi < 30 or mfi < 25) else (-1.5 if (rsi > 70 or mfi > 75) else 0)
        
        bb = ta.bbands(df['close'], length=20, std=2)
        curr_price = df['close'].iloc[-1]
        l_band, u_band = bb.iloc[-1, 0], bb.iloc[-1, 2]
        v_score = 1.5 if curr_price <= l_band else (-1.5 if curr_price >= u_band else 0)
        
        ema20 = ta.ema(df['close'], length=20).iloc[-1]
        ema50 = ta.ema(df['close'], length=50).iloc[-1]
        adx = ta.adx(df['high'], df['low'], df['close'], length=14).iloc[-1, 0]
        
        t_dir = 1.0 if ema20 > ema50 else -1.0
        strength = 1.8 if adx > 25 else 0.6 
        
        final_score = round(max(min((m_score + v_score + (t_dir * strength)), 3), -3), 1)
        return final_score, {"RSI": round(rsi,1), "MFI": round(mfi,1), "ADX": round(adx,1), "Trend": "Bull" if ema20 > ema50 else "Bear"}
    except: return 0, {"Error": "Calc"}

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')} UTC] Starting Safe Global Scan...")
    
    for index, symbol in enumerate(CMC_TOP_100):
        try:
            pair = f"{symbol}/USDT"
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 60: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            score, details = get_pro_score(df)
            
            # Coin-Specific Update Time (UTC)
            coin_time = datetime.utcnow().strftime('%H:%M:%S')
            
            # UI Colors
            if score >= 1.5: bg, border, bar = "rgba(6, 78, 59, 0.25)", "rgba(16, 185, 129, 0.6)", "#10b981"
            elif 0 < score < 1.5: bg, border, bar = "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)", "#22c55e"
            elif -1.5 < score < 0: bg, border, bar = "rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.3)", "#ef4444"
            elif score <= -1.5: bg, border, bar = "rgba(153, 27, 27, 0.3)", "rgba(185, 28, 28, 0.6)", "#b91c1c"
            else: bg, border, bar = "rgba(148, 163, 184, 0.1)", "rgba(148, 163, 184, 0.3)", "#94a3b8"

            results.append({
                'symbol': symbol, 'price': f"{df['close'].iloc[-1]:.5g}",
                'rank': index + 1, 'bg': bg, 'border': border, 'bar': bar,
                'score': score, 'details': details, 'update_time': coin_time
            })
            
            print(f"[{coin_time}] OK: {symbol} (Rank {index+1})")
            time.sleep(10) # 10 saniye bekleme (Ban koruması + 30dk tazelik dengesi)
        except Exception: continue
    return results

def create_html(data):
    full_update = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    data_json = json.dumps({item['symbol']: item['details'] for item in data})
    
    css = """
        :root { --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --sec: #94a3b8; }
        .light { --bg: #f5f7fa; --card: #ffffff; --text: #1e293b; --sec: #64748b; }
        body { background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; transition: 0.2s; padding-top: 50px; }
        .legal-top { background: #dc2626; color: white; text-align: center; padding: 8px; font-weight: bold; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; }
        .card { border-radius: 12px; border: 1px solid; cursor: pointer; transition: 0.2s; position: relative; overflow: hidden; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .based-gradient { background: linear-gradient(90deg, #ef4444, #94a3b8, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .star-btn { font-size: 1.5rem; color: #334155; transition: 0.2s; }
        .star-btn.active { color: #eab308 !important; }
        .custom-input { background: var(--card); border: 1px solid #262626; color: var(--text); }
        .light .custom-input { border-color: #cbd5e1; }
        .update-tag { font-size: 9px; opacity: 0.5; font-family: monospace; font-weight: bold; }
    """

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>{css}</style></head><body>
    <div class="legal-top">⚠️ TRADING RISK WARNING: High volatility. Analysis is mathematical, not financial advice.</div>
    <div class="max-w-7xl mx-auto p-4">
        <header class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 mt-4">
            <h1 class="text-5xl based-gradient tracking-tighter">BasedVector</h1>
            <div class="flex gap-4">
                <button onclick="toggleTheme()" class="p-2 bg-gray-800 rounded-full text-white" id="theme-toggle">🌙</button>
                <div class="text-right text-xs text-blue-500 font-mono">FINISH: {full_update} UTC</div>
            </div>
        </header>
        <div class="bg-gray-900/10 p-4 rounded-xl flex flex-col md:flex-row gap-4 mb-8">
            <input type="text" id="search" placeholder="Filter Asset..." class="custom-input p-3 rounded-lg w-full outline-none">
            <select id="sort" class="custom-input p-3 rounded-lg outline-none cursor-pointer">
                <option value="score-desc">🔥 Score: High</option>
                <option value="score-asc">❄️ Score: Low</option>
                <option value="cap-desc">💎 Cap: High</option>
                <option value="cap-asc">📊 Cap: Low</option>
            </select>
            <select id="layout" class="custom-input p-3 rounded-lg outline-none cursor-pointer">
                <option value="grid-cols-2">2 COL</option>
                <option value="grid-cols-4" selected>4 COL</option>
                <option value="grid-cols-5">5 COL</option>
            </select>
            <button onclick="toggleFavView()" id="fav-btn" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold">⭐ Watchlist</button>
        </div>
        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-4 transition-all">
    """

    for i in data:
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="background: {i['bg']}; border-color: {i['border']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" data-rank="{i['rank']}" onclick="showDetails('{i['symbol']}')">
            <div class="flex justify-between items-center mb-4">
                <span class="font-bold text-xl font-mono">{i['symbol']}</span>
                <button onclick="event.stopPropagation(); toggleFavorite(this, '{i['symbol']}')" class="star-btn">★</button>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold mb-3">${i['price']}</div>
                <div class="h-1.5 bg-gray-700/30 rounded-full relative overflow-hidden">
                    <div class="absolute h-full transition-all" style="{bar_pos} background:{i['bar']}"></div>
                </div>
                <div class="flex justify-between text-[10px] mt-1 opacity-60 uppercase font-bold">
                    <span>Bear</span><span>{i['score']}</span><span>Bull</span>
                </div>
                <div class="mt-4 flex justify-center">
                    <span class="update-tag uppercase">Updated: {i['update_time']} UTC</span>
                </div>
            </div>
        </div>
        """

    html += f"""
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl max-w-sm w-full" onclick="event.stopPropagation()">
                <h3 id="m-title" class="text-2xl font-bold mb-6 text-center text-white"></h3>
                <div id="m-body" class="space-y-4 font-mono"></div>
            </div>
        </div>
        <script>
            const data = DATA_PLACEHOLDER;
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

            function toggleTheme() {{
                const isDark = document.body.classList.contains('light');
                setTheme(isDark);
            }}

            function toggleFavorite(btn, sym) {{
                let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                if(favs.includes(sym)) {{
                    favs = favs.filter(f => f !== sym);
                    btn.classList.remove('active');
                }} else {{
                    favs.push(sym);
                    btn.classList.add('active');
                }}
                localStorage.setItem('favs', JSON.stringify(favs));
                if(onlyFavs) render();
            }}

            function render() {{
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value;
                const layoutVal = document.getElementById('layout').value;
                const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                const grid = document.getElementById('grid');
                const cards = Array.from(document.querySelectorAll('.card'));

                grid.className = `grid gap-4 transition-all ${{layoutVal}}`;

                cards.forEach(c => {{
                    const sym = c.dataset.symbol;
                    const matchesSearch = sym.includes(term);
                    const isFav = favs.includes(sym);
                    c.style.display = (matchesSearch && (!onlyFavs || isFav)) ? 'flex' : 'none';
                    c.querySelector('.star-btn').classList.toggle('active', isFav);
                }});

                cards.sort((a, b) => {{
                    if(sortVal.startsWith('score')) {{
                        return sortVal === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score;
                    }} else {{
                        return sortVal === 'cap-desc' ? a.dataset.rank - b.dataset.rank : b.dataset.rank - a.dataset.rank;
                    }}
                }}).forEach(c => grid.appendChild(c));
            }}

            function toggleFavView() {{
                onlyFavs = !onlyFavs;
                document.getElementById('fav-btn').innerText = onlyFavs ? '🌐 Show All' : '⭐ Watchlist';
                render();
            }}

            function showDetails(sym) {{
                const d = data[sym];
                document.getElementById('m-title').innerText = sym + " Report";
                document.getElementById('m-body').innerHTML = Object.entries(d).map(([k,v]) => `
                    <div class="flex justify-between border-b border-gray-800 pb-2">
                        <span class="text-gray-400">${{k}}</span>
                        <span class="${{v === 'Bull' || (typeof v === 'number' && v > 50) ? 'text-green-400' : 'text-red-400'}} font-bold">${{v}}</span>
                    </div>
                `).join('');
                document.getElementById('modal').classList.remove('hidden');
            }}

            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            document.getElementById('layout').addEventListener('change', render);
            
            window.onload = () => {{
                const savedTheme = localStorage.getItem('theme') || 'light';
                setTheme(savedTheme === 'dark');
                render();
            }};
        </script>
    </body></html>
    """.replace("DATA_PLACEHOLDER", data_json)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
