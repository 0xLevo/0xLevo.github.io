import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

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
            
            # Decision
            if avg_score > 1.5: decision = "STRONG BUY"; color = "#22c55e"
            elif avg_score > 0.5: decision = "BUY"; color = "#84cc16"
            elif avg_score > -0.5: decision = "NEUTRAL"; color = "#94a3b8"
            elif avg_score > -1.5: decision = "SELL"; color = "#f97316"
            else: decision = "STRONG SELL"; color = "#ef4444"

            results.append({
                'symbol': symbol,
                'price': f"{df['close'].iloc[-1]:.5g}",
                'decision': decision,
                'color': color,
                'score': round(avg_score, 1)
            })
            time.sleep(0.05)
        except Exception: continue
    return results

def create_html(data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Alpha Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
        <style>
            body {{ background-color: #020617; color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }}
            .card {{ background: #0f172a; border: 1px solid #1e293b; transition: all 0.3s; border-radius: 12px; }}
            .card:hover {{ border-color: #3b82f6; transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1); }}
            .trend-badge {{ font-size: 0.65rem; padding: 3px 8px; border-radius: 6px; font-weight: 800; }}
            .star-btn {{ font-size: 1.2rem; cursor: pointer; color: #475569; }}
            .star-btn.active {{ color: #eab308; }}
        </style>
    </head>
    <body class="p-4 md:p-8">
        <div class="max-w-7xl mx-auto">
            <header class="mb-10 pb-6 border-b border-slate-800">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-4xl font-bold tracking-tighter text-white">
                        <span class="text-blue-500">Based</span>Vector <span class="text-xs font-mono bg-blue-950 text-blue-300 px-2 py-0.5 rounded">ALPHA</span>
                    </h1>
                    <div class="text-right text-sm">
                        <p class="text-slate-400">Data Source: MEXC Global</p>
                        <p class="font-mono text-blue-400">{now} UTC</p>
                    </div>
                </div>
                
                <div class="flex flex-col md:flex-row gap-4 glass p-4 rounded-xl bg-slate-900 border border-slate-800">
                    <input type="text" id="search" placeholder="🔍 Search Assets (e.g. BTC)..." class="bg-slate-950 p-3 rounded-lg w-full text-sm border border-slate-700 text-white placeholder-slate-500">
                    <button onclick="toggleView()" id="view-toggle" class="bg-slate-800 hover:bg-slate-700 text-white px-5 py-3 rounded-lg text-sm font-bold flex items-center gap-2">
                        ⭐ My Watchlist
                    </button>
                </div>
            </header>

            <div id="coin-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """
    
    for item in data:
        html += f"""
        <div class="card p-4 flex flex-col justify-between" data-symbol="{item['symbol']}">
            <div class="flex justify-between items-center mb-3">
                <span class="font-bold text-lg text-white font-mono">{item['symbol']}</span>
                <button onclick="toggleFavorite(this, '{item['symbol']}')" class="star-btn">★</button>
            </div>
            
            <div class="flex justify-between items-end">
                <p class="text-xl font-bold text-white font-mono mb-1">${item['price']}</p>
                <span class="trend-badge mb-1" style="background: {item['color']}22; color: {item['color']}; border: 1px solid {item['color']}44;">{item['decision']}</span>
            </div>
            
            <div class="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-400 flex justify-between">
                <span>Score: <span class="font-bold text-white">{item['score']}/3</span></span>
                <span class="font-mono">4H Timeframe</span>
            </div>
        </div>
        """
            
    html += """
            </div>
            
            <script>
                const grid = document.getElementById('coin-grid');
                const searchInput = document.getElementById('search');
                const viewToggle = document.getElementById('view-toggle');
                let showingFavorites = false;

                // Load favorites and update stars
                function loadFavorites() {
                    const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    document.querySelectorAll('.card').forEach(card => {
                        const symbol = card.dataset.symbol;
                        const star = card.querySelector('.star-btn');
                        if (favs.includes(symbol)) {
                            star.classList.add('active');
                        }
                    });
                }
                loadFavorites();

                // Toggle Favorite
                function toggleFavorite(btn, symbol) {
                    let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    if (favs.includes(symbol)) {
                        favs = favs.filter(f => f !== symbol);
                        btn.classList.remove('active');
                    } else {
                        favs.push(symbol);
                        btn.classList.add('active');
                    }
                    localStorage.setItem('favs', JSON.stringify(favs));
                    if (showingFavorites) renderGrid();
                }

                // Search & Filter
                function renderGrid() {
                    const term = searchInput.value.toUpperCase();
                    const favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    
                    document.querySelectorAll('.card').forEach(card => {
                        const symbol = card.dataset.symbol;
                        const matchesSearch = symbol.includes(term);
                        const matchesFav = favs.includes(symbol);
                        
                        if (showingFavorites) {
                            card.style.display = (matchesSearch && matchesFav) ? 'flex' : 'none';
                        } else {
                            card.style.display = matchesSearch ? 'flex' : 'none';
                        }
                    });
                }

                searchInput.addEventListener('input', renderGrid);

                // Toggle View (All / Favorites)
                function toggleView() {
                    showingFavorites = !showingFavorites;
                    viewToggle.innerHTML = showingFavorites ? '🌐 All Assets' : '⭐ My Watchlist';
                    viewToggle.classList.toggle('bg-blue-600');
                    renderGrid();
                }
            </script>
            
            <footer class="mt-20 p-8 card text-slate-500 text-sm text-center">
                <h3 class="font-bold text-slate-100 mb-3">⚠️ Legal Disclaimer</h3>
                <p>All analysis, charts, and signals shared on BasedVector.com are <strong>for informational purposes only</strong>. This information does not constitute investment advice or financial consultancy. Cryptocurrency markets involve high risk, and you may lose your entire capital. You are solely responsible for your actions. BasedVector accepts no liability.</p>
                <p class="text-xs text-slate-600 mt-6 uppercase tracking-widest">© 2026 BASED VECTOR ALPHA TERMINAL</p>
            </footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
