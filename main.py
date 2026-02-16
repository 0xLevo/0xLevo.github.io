import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# --- CMC TOP 100 LIST ---
CMC_TOP_100 = [
    'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
    'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM',
    'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA',
    'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO',
    'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM',
    'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT',
    'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR',
    'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR',
    'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX',
    'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK'
]

TIMEFRAME = '4h'

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    print("Starting professional market scan...")
    
    for symbol in CMC_TOP_100:
        pair = f"{symbol}/USDT"
        try:
            # Fetch data with shorter timeout
            bars = exchange.fetch_ohlcv(pair, timeframe=TIMEFRAME, limit=60)
            if len(bars) < 30: continue

            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # Indicators
            df['RSI'] = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'])
            ema_20 = ta.ema(df['close'], length=20)
            
            last = df.iloc[-1]
            curr_price = last['close']
            rsi_val = last['RSI']
            
            # --- PROFESSIONAL SCORING ---
            score = 0
            signals = []
            
            # RSI Component (-2 to +2)
            if rsi_val < 30: score += 2; signals.append("Oversold")
            elif rsi_val < 40: score += 1; signals.append("Low RSI")
            elif rsi_val > 70: score -= 2; signals.append("Overbought")
            elif rsi_val > 60: score -= 1; signals.append("High RSI")
            
            # Trend Component (-1 to +1)
            if curr_price > ema_20.iloc[-1]: score += 1; signals.append("Bullish Trend")
            else: score -= 1; signals.append("Bearish Trend")

            # Decision Logic
            decision = "NEUTRAL"
            color = "#64748b" # Slate
            if score >= 2: decision = "BUY"; color = "#22c55e" # Green
            elif score <= -2: decision = "SELL"; color = "#ef4444" # Red

            results.append({
                'symbol': symbol,
                'price': f"{curr_price:.5g}",
                'rsi': round(rsi_val, 1) if not pd.isna(rsi_val) else 0,
                'decision': decision,
                'color': color,
                'signals': " • ".join(signals),
                'score': score
            })
            time.sleep(0.05) # Optimized sleep
        except Exception:
            continue
            
    return results

def create_html(data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Header & Styles
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Professional Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0f172a; color: #f1f5f9; font-family: sans-serif; }}
            .glass {{ background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.05); }}
            .sig-badge {{ font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 700; }}
        </style>
    </head>
    <body class="p-4 md:p-6">
        <div class="max-w-7xl mx-auto">
            <header class="flex justify-between items-center mb-8 pb-4 border-b border-slate-700">
                <h1 class="text-3xl font-extrabold tracking-tighter">BASED<span class="text-blue-500">VECTOR</span></h1>
                <div class="text-right text-xs">
                    <p class="text-slate-400">Market Data: MEXC</p>
                    <p class="font-mono text-blue-400">{now} UTC</p>
                </div>
            </header>

            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
    """
    
    # Sort: Strong Buy -> Buy -> Neutral -> Sell
    sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
    
    for item in sorted_data:
        html += f"""
        <div class="glass p-3 rounded-lg flex flex-col justify-between hover:border-slate-500 transition">
            <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-sm">{item['symbol']}</span>
                <span class="sig-badge" style="background: {item['color']}22; color: {item['color']}; border: 1px solid {item['color']}44;">{item['decision']}</span>
            </div>
            <p class="text-xs font-mono text-slate-300 mb-2">${item['price']}</p>
            <div class="flex justify-between items-center pt-1 border-t border-slate-700/50 text-[10px]">
                <span class="text-slate-400">RSI: <span class="font-bold text-white">{item['rsi']}</span></span>
            </div>
        </div>
        """
            
    # --- LEGAL DISCLAIMER ---
    html += """
            </div>
            <div class="mt-16 p-6 glass rounded-lg text-slate-400 text-xs text-center">
                <h3 class="font-bold text-slate-100 mb-2">⚠️ Yasal Sorumluluk Reddi (Disclaimer)</h3>
                <p>BasedVector.com sitesinde paylaşılan tüm analizler, grafikler ve sinyaller <strong>sadece bilgilendirme amaçlıdır</strong>. Bu bilgiler yatırım tavsiyesi veya finansal danışmanlık kapsamında değildir. Kripto para piyasaları yüksek risk içerir ve sermayenizin tamamını kaybedebilirsiniz. Yapacağınız işlemlerden tamamen siz sorumlusunuz. BasedVector hiçbir sorumluluk kabul etmez.</p>
            </div>
            <footer class="mt-8 text-center text-slate-700 text-[10px] uppercase tracking-widest">
                AUTOMATED ALPHA TERMINAL
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
