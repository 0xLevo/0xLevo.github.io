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
            
            # Colors based on explicit logic (Background tint + Border)
            if avg_score == 0:
                bg_color = "rgba(148, 163, 184, 0.15)"
                border_color = "rgba(148, 163, 184, 0.4)"
                bar_color = "#94a3b8"
            elif -1.5 <= avg_score < 0:
                bg_color = "rgba(239, 68, 68, 0.15)"
                border_color = "rgba(239, 68, 68, 0.4)"
                bar_color = "#ef4444"
            elif avg_score < -1.5:
                bg_color = "rgba(127, 29, 29, 0.35)" 
                border_color = "rgba(185, 28, 28, 0.8)"
                bar_color = "#dc2626"
            elif 0 < avg_score <= 1.5:
                bg_color = "rgba(34, 197, 94, 0.15)"
                border_color = "rgba(34, 197, 94, 0.4)"
                bar_color = "#22c55e"
            else: # 1.5 < avg_score <= 3
                bg_color = "rgba(6, 78, 59, 0.35)" 
                border_color = "rgba(5, 150, 105, 0.8)"
                bar_color = "#10b981"

            results.append({
                'symbol': symbol,
                'price': f"{df['close'].iloc[-1]:.5g}",
                'bg_color': bg_color,
                'border_color': border_color,
                'bar_color': bar_color,
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
    
    # CSS: Style definitions
    css_style = """
        :root {
            --bg-body: #050505;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --bg-panel: #0a0a0a;
            --border-panel: #171717;
            --input-bg: #000000;
            --input-border: #262626;
            --star-idle: #475569;
            --modal-bg: #0a0a0a;
            --modal-border: #262626;
        }
        
        .light {
            --bg-body: #f1f5f9;
            --text-primary: #0f172a; 
            --text-secondary: #475569;
            --bg-panel: #ffffff;
            --border-panel: #cbd5e1;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --star-idle: #94a3b8;
            --modal-bg: #ffffff;
            --modal-border: #e2e8f0;
        }
        
        body { 
            background-color: var(--bg-body); 
            color: var(--text-primary); 
            font-family: 'Space Grotesk', sans-serif; 
            transition: all 0.3s ease; 
        }
        
        .card { 
            transition: all 0.2s ease; 
            border-radius: 12px; 
            cursor: pointer; 
            position: relative;
            overflow: hidden;
            border-width: 1px;
            border-style: solid;
        }
        .card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15); 
        }
        
        .glass-panel {
            background-color: var(--bg-panel);
            border: 1px solid var(--border-panel);
        }
        
        .based-gradient {
            background: linear-gradient(90deg, 
                #ef4444 0%, 
                #f87171 25%, 
                #94a3b8 50%, 
                #4ade80 75%, 
                #10b981 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }

        .star-btn { 
            font-size: 1.4rem;
            cursor: pointer; 
            color: var(--star-idle); 
            transition: all 0.2s;
            z-index: 20;
            padding: 4px;
        }
        .star-btn:hover { color: #eab308; transform: scale(1.1); }
        .star-btn.active { color: #eab308; opacity: 1; text-shadow: 0 0 10px rgba(234, 179, 8, 0.3); }
        
        .custom-input {
            background-color: var(--input-bg);
            color: var(--text-primary);
            border: 1px solid var(--input-border);
        }
        
        .score-bar-bg { background-color: #1f2937; }
        .light .score-bar-bg { background-color: #e2e8f0; }
        
        .modal-backdrop { background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(4px); }
        .light .modal-backdrop { background: rgba(0, 0, 0, 0.3); }
        
        /* Legal Banner */
        .legal-banner {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            font-size: 0.75rem;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        body { padding-top: 40px; } /* Space for banner */
    """

    # HTML Header
    html_header = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Alpha Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
        <style>{css_style}</style>
    </head>
    <body class="p-4 md:p-8">
        <div class="legal-banner">
            ⚠️ YASAL UYARI: Bu platformdaki analizler yatırım tavsiyesi değildir. Kripto varlıklar yüksek risk içerir.
        </div>
        <div class="max-w-7xl mx-auto">
            <header class="mb-8">
                <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                    <div class="flex items-center gap-3">
                        <h1 class="text-5xl tracking-tighter">
                            <span class="based-gradient">BasedVector</span>
                        </h1>
                        <span class="text-xs font-bold font-mono px-2 py-1 rounded bg-blue-500/10 text-blue-500 border border-blue-500/20">ALPHA</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <div class="text-right hidden md:block">
                            <p class="text-xs uppercase tracking-wider" style="color: var(--text-secondary)">Market Status</p>
                            <p class="font-mono font-bold text-sm text-blue-500">{now} UTC</p>
                        </div>
                        <button onclick="toggleTheme()" id="theme-toggle" class="w-10 h-10 rounded-full flex items-center justify-center bg-gray-800 text-white hover:bg-gray-700 transition-colors">🌙</button>
                    </div>
                </div>
                
                <div class="glass-panel p-4 rounded-xl flex flex-col md:flex-row gap-3 shadow-sm">
                    <input type="text" id="search" placeholder="🔍 Search Assets..." class="custom-input p-3 rounded-lg w-full text-sm outline-none focus:ring-2 focus:ring-blue-500/50">
                    <select id="sort" class="custom-input p-3 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500/50 cursor-pointer">
                        <option value="score-desc">Score: High to Low</option>
                        <option value="score-asc">Score: Low to High</option>
                    </select>
                    <button onclick="toggleView()" id="view-toggle" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-sm font-bold shadow-lg transition-all flex items-center gap-2 whitespace-nowrap">
                        ⭐ My Watchlist
                    </button>
                </div>
            </header>
            <div id="coin-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """
    
    # HTML Content Loop
    html_content = ""
    for item in data:
        intensity = abs(item['score']) / 3 * 50 
        
        if item['score'] >= 0:
            bar_style = f"width: {intensity}%; left: 50%; background-color: {item['bar_color']};"
        else:
            bar_style = f"width: {intensity}%; left: {50 - intensity}%; background-color: {item['bar_color']};"
            
        html_content += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="background-color: {item['bg_color']}; border-color: {item['border_color']};"
             data-symbol="{item['symbol']}" data-score="{item['score']}"
             onclick="showDetails('{item['symbol']}')">
             
            <div class="flex justify-between items-start mb-2">
                <span class="font-bold text-lg font-mono tracking-tight" style="color: var(--text-primary)">{item['symbol']}</span>
                <button onclick="event.stopPropagation(); toggleFavorite(this, '{item['symbol']}')" class="star-btn">★</button>
            </div>
            
            <div class="text-center mt-1">
                <p class="text-2xl font-bold font-mono mb-2" style="color: var(--text-primary)">${item['price']}</p>
                <div class="score-bar-bg h-2 rounded-full relative overflow-hidden w-full">
                    <div class="score-center-line absolute top-0 left-1/2 w-0.5 h-full transform -translate-x-1/2 z-10" style="background-color: var(--text-secondary); opacity:0.3"></div>
                    <div class="absolute top-0 h-full rounded-full transition-all duration-500" style="{bar_style}"></div>
                </div>
                <div class="flex justify-between text-[10px] font-mono mt-1" style="color: var(--text-secondary)">
                    <span>Bear</span>
                    <span class="font-bold" style="color: {item['bar_color']}">{item['score']}</span>
                    <span>Bull</span>
                </div>
            </div>
        </div>
        """
    
    # HTML Footer & JS (FIXED SORT LOGIC)
    html_footer = f"""
            </div>
            
            <div id="details-modal" class="hidden fixed inset-0 modal-backdrop z-50 flex items-center justify-center p-4" onclick="closeDetails(event)">
                <div class="card p-6 w-full max-w-sm shadow-2xl transform transition-all scale-100" style="background: var(--modal-bg); border-color: var(--modal-border);" onclick="event.stopPropagation()">
                    <div class="flex justify-between items-center mb-6 border-b border-gray-700/20 pb-4">
                        <h3 id="modal-title" class="text-xl font-bold" style="color: var(--text-primary)"></h3>
                        <button onclick="closeDetails()" class="text-2xl leading-none hover:text-red-500" style="color: var(--text-secondary)">×</button>
                    </div>
                    <div id="modal-content" class="space-y-3 text-sm font-mono"></div>
                </div>
            </div>
            
            <script>
                const data = {data_json};
                const grid = document.getElementById('coin-grid');
                const searchInput = document.getElementById('search');
                const viewToggle = document.getElementById('view-toggle');
                const sortSelect = document.getElementById('sort');
                const themeToggle = document.getElementById('theme-toggle');
                let showingFavorites = false;

                function toggleTheme() {{
                    document.body.classList.toggle('light');
                    const isLight = document.body.classList.contains('light');
                    localStorage.setItem('theme', isLight ? 'light' : 'dark');
                    themeToggle.innerText = isLight ? '☀️' : '🌙';
                    themeToggle.className = isLight ? 
                        'w-10 h-10 rounded-full flex items-center justify-center bg-yellow-400 text-white hover:bg-yellow-500 transition-colors shadow-lg' : 
                        'w-10 h-10 rounded-full flex items-center justify-center bg-gray-800 text-white hover:bg-gray-700 transition-colors';
                }}
                
                if (localStorage.getItem('theme') === 'light') {{
                    toggleTheme();
                }}

                function loadFavorites() {{
                    const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    document.querySelectorAll('.card').forEach(card => {{
                        const symbol = card.dataset.symbol;
                        const star = card.querySelector('.star-btn');
                        if (favs.includes(symbol)) star.classList.add('active');
                    }});
                }}
                loadFavorites();

                function toggleFavorite(btn, symbol) {{
                    let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    
                    if (favs.includes(symbol)) {{
                        favs = favs.filter(f => f !== symbol);
                        btn.classList.remove('active');
                    }} else {{
                        favs.push(symbol);
                        btn.classList.add('active');
                    }}
                    
                    localStorage.setItem('favs', JSON.stringify(favs));
                    if (showingFavorites) renderGrid();
                }}

                // --- FIXED SORTING & FILTERING LOGIC ---
                function renderGrid() {{
                    const term = searchInput.value.toUpperCase();
                    const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    const sortOrder = sortSelect.value;
                    
                    let cards = Array.from(document.querySelectorAll('.card'));
                    
                    // Filter
                    cards.forEach(card => {{
                        const symbol = card.dataset.symbol;
                        const matchesSearch = symbol.includes(term);
                        const matchesFav = favs.includes(symbol);
                        
                        let isVisible = matchesSearch;
                        if (showingFavorites) {{
                            isVisible = matchesSearch && matchesFav;
                        }}
                        card.style.display = isVisible ? 'flex' : 'none';
                    }});
                    
                    // Sort
                    cards.sort((a, b) => {{
                        const scoreA = parseFloat(a.dataset.score);
                        const scoreB = parseFloat(b.dataset.score);
                        return sortOrder === 'score-desc' ? scoreB - scoreA : scoreA - scoreB;
                    }});
                    
                    // Re-append to grid in sorted order
                    cards.forEach(card => {{
                        if (card.style.display !== 'none') grid.appendChild(card);
                    }});
                }}

                searchInput.addEventListener('input', renderGrid);
                sortSelect.addEventListener('change', renderGrid);

                function toggleView() {{
                    showingFavorites = !showingFavorites;
                    viewToggle.innerHTML = showingFavorites ? '🌐 Show All' : '⭐ My Watchlist';
                    viewToggle.className = showingFavorites ? 
                        'bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg text-sm font-bold shadow-lg transition-all flex items-center gap-2 whitespace-nowrap' :
                        'bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-sm font-bold shadow-lg transition-all flex items-center gap-2 whitespace-nowrap';
                    renderGrid();
                }}
                
                function showDetails(symbol) {{
                    const details = data[symbol];
                    document.getElementById('modal-title').innerText = symbol + ' Analysis';
                    let content = '';
                    for (const [key, value] of Object.entries(details)) {{
                        let colorClass = 'text-gray-500';
                        if(value > 0) colorClass = 'text-green-500 font-bold';
                        if(value < 0) colorClass = 'text-red-500 font-bold';
                        
                        content += `<div class='flex justify-between items-center p-2 rounded hover:bg-gray-500/5 transition'>
                            <span style="color: var(--text-secondary)">${{key}}</span>
                            <span class='${{colorClass}} text-lg'>${{value}}</span>
                        </div>`;
                    }}
                    document.getElementById('modal-content').innerHTML = content;
                    document.getElementById('details-modal').classList.remove('hidden');
                }}
                
                function closeDetails(event) {{
                    if (event && event.target.id !== 'details-modal') return;
                    document.getElementById('details-modal').classList.add('hidden');
                }}
                
                // Initial Sort
                renderGrid();
            </script>
            
            <footer class="mt-16 mb-8 text-center">
                <p class="text-xs font-bold opacity-50 tracking-widest" style="color: var(-
