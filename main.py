import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# --- CMC TOP 100 LIST ---
CMC_TOP_100 = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'DAI', 'BCH', 'ATOM', 'UNI', 'LEO', 'NEAR', 'OKB', 'INJ', 'OP', 'ICP', 'FIL', 'LDO', 'TIA', 'STX', 'APT', 'ARB', 'RNDR', 'VET', 'KAS', 'ETC', 'MNT', 'CRO', 'ALGO', 'RUNE', 'EGLD', 'SEI', 'SUI', 'AAVE', 'ORDI', 'BEAM', 'FLOW', 'MINA', 'FTM', 'SAND', 'THETA', 'MANA', 'AXS', 'CHZ', 'GALA', 'EOS', 'IOTA', 'KCS', 'GRT', 'NEO', 'SNX', 'DYDX', 'CRV', 'MKR', 'WOO', 'LUNC', 'KAVA', 'IMX', 'HBAR', 'QNT', 'BTT', 'JASMY', 'WIF', 'BONK', 'PYTH', 'FLOKI', 'XLM', 'XMR', 'PEPE', 'AR', 'STRK', 'LRC', 'ZEC', 'KLAY', 'BSV', 'PENDLE', 'FET', 'AGIX', 'OCEAN', 'JUP', 'METIS', 'XAI', 'ALT', 'MANTA', 'RON', 'ENS', 'ANKR', 'MASK']

def calculate_score(df):
    """Belirttiğiniz mantığa göre skor hesaplar."""
    if len(df) < 55: return 0
    
    # İndikatörler
    rsi = ta.rsi(df['close'], length=14).iloc[-1]
    macd_df = ta.macd(df['close'])
    macd = macd_df.iloc[-1, 0] # MACD Line
    ema21 = ta.ema(df['close'], length=21).iloc[-1]
    ema55 = ta.ema(df['close'], length=55).iloc[-1]
    
    score = 0
    # Skorlama Mantığı
    if rsi > 50: score += 1
    if macd > 0: score += 1
    if ema21 > ema55: score += 1
    
    return score

def analyze_market():
    exchange = ccxt.mexc({'enableRateLimit': True})
    results = []
    
    print("Starting Multi-Timeframe Analysis...")
    
    for symbol in CMC_TOP_100:
        pair = f"{symbol}/USDT"
        try:
            # 1. 1D (Günlük) Veri Çek ve Analiz Et
            bars_1d = exchange.fetch_ohlcv(pair, timeframe='1d', limit=200)
            if len(bars_1d) < 100: continue
            df_1d = pd.DataFrame(bars_1d, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            score_1d = calculate_score(df_1d)
            
            # 2. 4H (4 Saatlik) Veri Çek ve Analiz Et
            bars_4h = exchange.fetch_ohlcv(pair, timeframe='4h', limit=200)
            if len(bars_4h) < 100: continue
            df_4h = pd.DataFrame(bars_4h, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            score_4h = calculate_score(df_4h)
            
            # 3. Genel Durum Belirleme
            trend = "NEUTRAL"
            color = "#94a3b8" # Slate
            
            # 1D Skor Mantığı
            if score_1d >= 2: trend = "TREND UP"; color = "#22c55e" # Green
            elif score_1d <= -1: trend = "TREND DOWN"; color = "#ef4444" # Red
            
            # 4H ile onaylama
            if trend == "TREND UP" and score_4h < 1: trend = "UP (4H Weak)"
            elif trend == "TREND DOWN" and score_4h > 1: trend = "DOWN (4H Weak)"

            results.append({
                'symbol': symbol,
                'price': f"{df_1d['close'].iloc[-1]:.5g}",
                'score_1d': score_1d,
                'trend': trend,
                'color': color
            })
            time.sleep(0.05) # Rate limit koruması
        except Exception:
            continue
            
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
            <header class="flex justify-between items-center mb-8 pb-4 border-b border-slate-800">
                <h1 class="text-3xl font-extrabold tracking-tighter">BASED<span class="text-blue-500">VECTOR</span></h1>
                <div class="text-right text-xs">
                    <p class="text-slate-400">Veri: MEXC Global</p>
                    <p class="font-mono text-blue-400">{now} UTC</p>
                </div>
            </header>

            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
    """
    
    # Skor yüksekten düşüğe sırala
    sorted_data = sorted(data, key=lambda x: x['score_1d'], reverse=True)
    
    for item in sorted_data:
        # Skor çubuğu rengi
        bar_color = "bg-red-500" if item['score_1d'] < 0 else "bg-green-500"
        bar_width = min(abs(item['score_1d']) * 33.33, 100)
        
        html += f"""
        <div class="card p-3 rounded-lg flex flex-col justify-between">
            <div class="flex justify-between items-center mb-2">
                <span class="font-bold text-sm text-white">{item['symbol']}</span>
                <span class="trend-badge" style="background: {item['color']}22; color: {item['color']}; border: 1px solid {item['color']}44;">{item['trend']}</span>
            </div>
            
            <p class="text-xs font-mono text-slate-400 mb-3">${item['price']}</p>
            
            <div class="space-y-1">
                <div class="flex justify-between text-[10px] text-slate-500">
                    <span>1D Puan</span>
                    <span class="font-bold text-white">{item['score_1d']}/3</span>
                </div>
                <div class="w-full bg-slate-800 rounded-full h-1.5">
                    <div class="{bar_color} h-1.5 rounded-full" style="width: {bar_width}%"></div>
                </div>
            </div>
        </div>
        """
            
    # --- YASAL UYARI ---
    html += """
            </div>
            <div class="mt-16 p-6 card rounded-lg text-slate-500 text-xs text-center">
                <h3 class="font-bold text-slate-200 mb-2">⚠️ Yasal Sorumluluk Reddi (Disclaimer)</h3>
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
