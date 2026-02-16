import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# --- SETTINGS ---
COIN_COUNT = 100  # Top 100 coins by volume
TIMEFRAME = '4h'

def analyze_market():
    exchange = ccxt.mexc()
    results = []
    
    try:
        print("Fetching market data...")
        tickers = exchange.fetch_tickers()
        # Filter USDT pairs and sort by volume
        usdt_pairs = [symbol for symbol in tickers if symbol.endswith('/USDT') and 'BEAR' not in symbol and 'BULL' not in symbol]
        sorted_pairs = sorted(usdt_pairs, key=lambda x: tickers[x]['quoteVolume'], reverse=True)[:COIN_COUNT]
        
        print(f"Analyzing Top {len(sorted_pairs)} coins by volume...")
        
        for symbol in sorted_pairs:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=70)
                if len(bars) < 30: continue

                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                
                # Indicators
                df['RSI'] = ta.rsi(df['close'], length=14)
                macd = ta.macd(df['close'])
                ema_20 = ta.ema(df['close'], length=20)
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                
                rsi_val = last['RSI']
                curr_price = last['close']
                
                # Enhanced Scoring Logic
                score = 0
                signals = []
                
                # RSI Logic
                if rsi_val < 30: score += 2; signals.append("Oversold")
                elif rsi_val < 40: score += 1; signals.append("Low RSI")
                elif rsi_val > 70: score -= 2; signals.append("Overbought")
                
                # MACD Logic
                if macd.iloc[-1, 0] > macd.iloc[-1, 2]: score += 1; signals.append("MACD Bullish")
                else: score -= 1; signals.append("MACD Bearish")
                
                # EMA Logic
                if curr_price > ema_20.iloc[-1]: score += 1; signals.append("Above EMA20")
                else: score -= 1; signals.append("Below EMA20")

                # Color & Status
                decision = "NEUTRAL"
                color = "#94a3b8" # Slate
                if score >= 3: decision = "STRONG BUY"; color = "#22c55e" # Green
                elif score >= 1: decision = "BUY"; color = "#84cc16" # Lime
                elif score <= -3: decision = "STRONG SELL"; color = "#ef4444" # Red
                elif score <= -1: decision = "SELL"; color = "#f97316" # Orange

                results.append({
                    'symbol': symbol.replace('/USDT', ''),
                    'price': f"{curr_price:g}",
                    'rsi': round(rsi_val, 1) if not pd.isna(rsi_val) else 0,
                    'decision': decision,
                    'color': color,
                    'signals': " • ".join(signals),
                    'score': score
                })
                time.sleep(0.1) # Safe delay for 100 coins
            except Exception: continue
            
    except Exception as e:
        print(f"Main Error: {e}")
        
    return results

def create_html(data):
    now = datetime.now().strftime('%d %b, %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector | Alpha Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #020617; color: #f8fafc; }}
            .glass {{ background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }}
            .card-hover:hover {{ border-color: rgba(255,255,255,0.2); background: rgba(30, 41, 59, 0.5); }}
        </style>
    </head>
    <body class="p-4 md:p-10">
        <div class="max-w-6xl mx-auto">
            <header class="flex flex-col md:flex-row justify-between items-center mb-10 gap-4">
                <div>
                    <h1 class="text-4xl font-800 tracking-tighter italic">BASEDVECTOR<span class="text-blue-500">.COM</span></h1>
                    <p class="text-slate-500 font-medium">Real-time Market Alpha Terminal</p>
                </div>
                <div class="glass px-4 py-2 rounded-full text-sm font-semibold text-slate-400">
                    Last Scan: <span class="text-blue-400">{now} UTC</span>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    """
    
    if not data:
        html += "<div class='col-span-full text-center py-20 text-slate-500 text-xl'>Initializing Neural Network... Data will arrive shortly.</div>"
    else:
        for item in sorted(data, key=lambda x: x['score'], reverse=True):
            html += f"""
            <div class="glass p-5 rounded-2xl card-hover transition-all duration-300">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-2xl font-800 tracking-tight">{item['symbol']}</h3>
                        <p class="text-blue-400 font-mono text-sm">${item['price']}</p>
                    </div>
                    <span class="px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider" style="background: {item['color']}22; color: {item['color']}; border: 1px solid {item['color']}44;">
                        {item['decision']}
                    </span>
                </div>
                <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-500">RSI (14)</span>
                        <span class="font-semibold {'text-red-400' if item['rsi'] > 70 else 'text-green-400' if item['rsi'] < 30 else 'text-slate-300'}">{item['rsi']}</span>
                    </div>
                    <div class="pt-2 border-t border-white/5 text-[10px] text-slate-500 uppercase font-bold tracking-widest">
                        {item['signals']}
                    </div>
                </div>
            </div>
            """
            
    html += """
            </div>
            <footer class="mt-20 text-center text-slate-600 text-xs border-t border-white/5 pt-10">
                &copy; 2026 BASEDVECTOR. All data provided by MEXC Global. Trading involves risk.
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
