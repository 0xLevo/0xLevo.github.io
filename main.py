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
    print("Market Analizi Başlatılıyor...")
    
    for symbol in CMC_TOP_100:
        pair = f"{symbol}/USDT"
        try:
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 50: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            macd_df = ta.macd(df['close'])
            macd, signal = macd_df.iloc[-1, 0], macd_df.iloc[-1, 2]
            cci = ta.cci(df['high'], df['low'], df['close'], length=20).iloc[-1]
            
            s1, s2, s3 = get_rsi_score(rsi), get_macd_score(macd, signal), get_cci_score(cci)
            avg_score = round((s1 + s2 + s3) / 3, 1)
            
            # Renk Skalası (Arka Plan ve Bar)
            if avg_score == 0:
                bg, border, bar = "rgba(148, 163, 184, 0.1)", "rgba(148, 163, 184, 0.3)", "#94a3b8"
            elif -1.5 <= avg_score < 0:
                bg, border, bar = "rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.3)", "#ef4444"
            elif avg_score < -1.5:
                bg, border, bar = "rgba(153, 27, 27, 0.3)", "rgba(185, 28, 28, 0.6)", "#b91c1c"
            elif 0 < avg_score <= 1.5:
                bg, border, bar = "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)", "#22c55e"
            else:
                bg, border, bar = "rgba(6, 78, 59, 0.3)", "rgba(16, 185, 129, 0.6)", "#10b981"

            results.append({
                'symbol': symbol, 'price': f"{df['close'].iloc[-1]:.5g}",
                'bg_color': bg, 'border_color': border, 'bar_color': bar,
                'score': avg_score, 'details': {'RSI': s1, 'MACD': s2, 'CCI': s3}
            })
            time.sleep(0.02)
        except: continue
    return results

def create_html(data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    data_json = json.dumps({item['symbol']: item['details'] for item in data})
    
    # CSS ve Tasarım
    css = """
        :root { --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --sec: #94a3b8; }
        .light { --bg: #f1f5f9; --card: #ffffff; --text: #0f172a; --sec: #475569; }
        body { background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; transition: 0.3s; padding-top: 40px; }
        .legal-top { background: #ef4444; color: white; text-align: center; padding: 8px; font-weight: bold; font-size: 12px; position: fixed; top: 0; width: 100%; z-index: 100; }
        .card { border-radius: 12px; border: 1px solid; cursor: pointer; transition: 0.2s; position: relative; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .based-gradient { background: linear-gradient(90deg, #ef4444, #94a3b8, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .star-btn { font-size: 1.5rem; color: #334155; transition: 0.2s; }
        .star-btn.active { color: #eab308 !important; }
        .custom-input { background: var(--card); border: 1px solid #262626; color: var(--text); }
    """

    html_start = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>{css}</style></head><body>
    <div class="legal-top">⚠️ YASAL UYARI: Burada yer alan bilgiler yatırım tavsiyesi değildir. Kripto paralar yüksek risk içerir.</div>
    <div class="max-w-7xl mx-auto p-4">
        <header class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 mt-4">
            <h1 class="text-5xl based-gradient tracking-tighter">BasedVector</h1>
            <div class="flex gap-4">
                <button onclick="toggleTheme()" class="p-2 bg-gray-800 rounded-full">🌙</button>
                <div class="text-right text-xs text-blue-500 font-mono">{now} UTC</div>
            </div>
        </header>
        <div class="bg-gray-900/10 p-4 rounded-xl flex flex-col md:flex-row gap-4 mb-8">
            <input type="text" id="search" placeholder="Asset Ara..." class="custom-input p-3 rounded-lg w-full outline-none">
            <select id="sort" class="custom-input p-3 rounded-lg outline-none cursor-pointer">
                <option value="score-desc">Puan: Yüksekten Düşüğe</option>
                <option value="score-asc">Puan: Düşükten Yükseğe</option>
            </select>
            <button onclick="toggleFavView()" id="fav-btn" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold">⭐ İzleme Listesi</button>
        </div>
        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """

    cards_html = ""
    for i in data:
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        
        cards_html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="background: {i['bg_color']}; border-color: {i['border_color']};"
             data-symbol="{i['symbol']}" data-score="{i['score']}" onclick="showDetails('{i['symbol']}')">
            <div class="flex justify-between items-center mb-4">
                <span class="font-bold text-xl font-mono">{i['symbol']}</span>
                <button onclick="event.stopPropagation(); toggleFavorite(this, '{i['symbol']}')" class="star-btn">★</button>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold mb-3">${i['price']}</div>
                <div class="h-1.5 bg-gray-700/30 rounded-full relative overflow-hidden">
                    <div class="absolute h-full transition-all" style="{bar_pos} background:{i['bar_color']}"></div>
                </div>
                <div class="flex justify-between text-[10px] mt-1 opacity-60 uppercase font-bold">
                    <span>Bear</span><span>{i['score']}</span><span>Bull</span>
                </div>
            </div>
        </div>
        """

    html_end = f"""
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl max-w-sm w-full" onclick="event.stopPropagation()">
                <h3 id="m-title" class="text-2xl font-bold mb-6 text-center"></h3>
                <div id="m-body" class="space-y-4 font-mono"></div>
            </div>
        </div>
        <script>
            const data = {data_json};
            let onlyFavs = false;

            function toggleTheme() {{ document.body.classList.toggle('light'); }}

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
                const sort = document.getElementById('sort').value;
                const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                const cards = Array.from(document.querySelectorAll('.card'));

                cards.forEach(c => {{
                    const sym = c.dataset.symbol;
                    const matchesSearch = sym.includes(term);
                    const isFav = favs.includes(sym);
                    c.style.display = (matchesSearch && (!onlyFavs || isFav)) ? 'flex' : 'none';
                    c.querySelector('.star-btn').classList.toggle('active', isFav);
                }});

                cards.sort((a, b) => {{
                    const sA = parseFloat(a.dataset.score);
                    const sB = parseFloat(b.dataset.score);
                    return sort === 'score-desc' ? sB - sA : sA - sB;
                }}).forEach(c => document.getElementById('grid').appendChild(c));
            }}

            function toggleFavView() {{
                onlyFavs = !onlyFavs;
                document.getElementById('fav-btn').innerText = onlyFavs ? '🌐 Hepsini Göster' : '⭐ İzleme Listesi';
                render();
            }}

            function showDetails(sym) {{
                const d = data[sym];
                document.getElementById('m-title').innerText = sym + " Analizi";
                document.getElementById('m-body').innerHTML = Object.entries(d).map(([k,v]) => `
                    <div class="flex justify-between border-b border-gray-800 pb-2">
                        <span class="text-gray-400">${{k}}</span>
                        <span class="${{v > 0 ? 'text-green-400' : 'text-red-400'}} font-bold">${{v}}</span>
                    </div>
                `).join('');
                document.getElementById('modal').classList.remove('hidden');
            }}

            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            window.onload = render;
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_start + cards_html + html_end)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
