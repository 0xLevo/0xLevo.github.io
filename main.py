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
            # 4H Veri Çek
            bars = exchange.fetch_ohlcv(pair, timeframe='4h', limit=100)
            if len(bars) < 50: continue
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # --- TEKNİK GÖSTERGELER ---
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            macd_df = ta.macd(df['close'])
            macd = macd_df.iloc[-1, 0]
            signal = macd_df.iloc[-1, 2]
            cci = ta.cci(df['high'], df['low'], df['close'], length=20).iloc[-1]
            
            # --- PUANLAMA ---
            s1 = get_rsi_score(rsi)
            s2 = get_macd_score(macd, signal)
            s3 = get_cci_score(cci)
            
            avg_score = (s1 + s2 + s3) / 3
            
            # --- KARAR MANTIĞI ---
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
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Pro Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #020617; color: #f1f5f9; font-family: sans-serif; }}
            .card {{ background: #111827; border: 1px solid #1f2937; transition: all 0.3s; }}
            .card:hover {{ border-color: #3b82f6; transform: translateY(-2px); }}
            .trend-badge {{ font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }}
        </style>
    </head>
    <body class="p-4 md:p-6">
        <div class="max-w-7xl mx-auto">
            <header class="mb-8 pb-4 border-b border-slate-800">
                <div class="flex justify-between items-center mb-4">
                    <h1 class="text-3xl font-extrabold tracking-tighter">BASED<span class="text-blue-500">VECTOR</span></h1>
                    <div class="text-right text-xs">
                        <p class="text-slate-400">Veri: MEXC Global</p>
                        <p class="font-mono text-blue-400">{now} UTC</p>
                    </div>
                </div>
                
                <div class="flex gap-2">
                    <input type="text" id="search" placeholder="Coin ara..." class="bg-slate-800 p-2 rounded w-full text-sm">
                    <button onclick="filterFavorites()" class="bg-yellow-600 p-2 rounded text-sm font-bold">⭐ Takip</button>
                </div>
            </header>

            <div id="coin-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
    """
    
    for item in data:
        html += f"""
        <div class="card p-3 rounded-lg flex flex-col justify-between" data-symbol="{item['symbol']}">
            <div class="flex justify-between items-center mb-2">
                <span class="font-bold text-sm text-white">{item['symbol']}</span>
                <button onclick="toggleFavorite('{item['symbol']}')" class="text-yellow-500">⭐</button>
                <span class="trend-badge" style="background: {item['color']}22; color: {item['color']}; border: 1px solid {item['color']}44;">{item['decision']}</span>
            </div>
            <p class="text-xs font-mono text-slate-400 mb-3">${item['price']}</p>
        </div>
        """
            
    html += """
            </div>
            
            <script>
                // Arama Fonksiyonu
                document.getElementById('search').addEventListener('input', function(e) {
                    const term = e.target.value.toUpperCase();
                    document.querySelectorAll('.card').forEach(card => {
                        card.style.display = card.dataset.symbol.includes(term) ? 'block' : 'none';
                    });
                });

                // Favori Ekleme/Çıkarma
                function toggleFavorite(symbol) {
                    let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    if (favs.includes(symbol)) {
                        favs = favs.filter(f => f !== symbol);
                    } else {
                        favs.push(symbol);
                    }
                    localStorage.setItem('favs', JSON.stringify(favs));
                }

                // Sadece Favorileri Göster
                function filterFavorites() {
                    let favs = JSON.parse(localStorage.getItem('favs') || '[]');
                    document.querySelectorAll('.card').forEach(card => {
                        card.style.display = favs.includes(card.dataset.symbol) ? 'block' : 'none';
                    });
                }
            </script>
            
            <div class="mt-16 p-6 card rounded-lg text-slate-500 text-xs text-center">
                <p>⚠️ <strong>Yasal Uyarı:</strong> Yatırım tavsiyesi değildir.</p>
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
