import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import os

# --- AYARLAR ---
COIN_LIMIT = 40 
TIMEFRAME = '4h'

def analyze_market():
    # Binance bağlantısı
    exchange = ccxt.binance()
    
    # Analiz edilecek popüler coinler
    symbols = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'LINK/USDT',
        'MATIC/USDT', 'LTC/USDT', 'SHIB/USDT', 'TRX/USDT', 'UNI/USDT',
        'NEAR/USDT', 'FIL/USDT', 'ARB/USDT', 'OP/USDT', 'TIA/USDT'
    ]
    
    results = []
    print(f"{len(symbols)} adet coin analiz ediliyor...")

    for symbol in symbols:
        try:
            # Mum verilerini çek
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # RSI ve MACD hesapla
            df['RSI'] = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'])
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_S'] = macd['MACDs_12_26_9']
            
            last = df.iloc[-1]
            rsi_val = last['RSI']
            score = 0
            signals = []

            # Basit Puanlama
            if rsi_val < 30: 
                score += 1; signals.append("RSI Düşük")
            elif rsi_val > 70: 
                score -= 1; signals.append("RSI Yüksek")
            
            if last['MACD'] > last['MACD_S']: 
                score += 1; signals.append("MACD Al")
            else: 
                score -= 1; signals.append("MACD Sat")

            res = "NÖTR"
            color = "white"
            if score >= 2: res = "GÜÇLÜ AL"; color = "#00ff00"
            elif score == 1: res = "AL"; color = "#adff2f"
            elif score == -1: res = "SAT"; color = "#ff7f50"
            elif score <= -2: res = "GÜÇLÜ SAT"; color = "#ff0000"

            results.append({
                'symbol': symbol.split('/')[0],
                'price': last['close'],
                'rsi': round(rsi_val, 2),
                'score': score,
                'decision': res,
                'color': color,
                'signals': ", ".join(signals)
            })
            time.sleep(0.1) # API limitine takılmamak için
        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue
    return results

def create_html(data):
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BasedVector - Crypto Analysis</title>
        <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #0f0f0f; color: #e0e0e0; font-family: sans-serif; }}
            .table {{ background: #1a1a1a; color: #fff; border-color: #333; }}
            .badge-puan {{ font-size: 1.1em; padding: 5px 10px; }}
        </style>
    </head>
    <body>
        <div class="container py-5">
            <h1 class="text-center mb-2">BASEDVECTOR.COM</h1>
            <p class="text-center text-muted mb-5 small">Son Güncelleme: {now} (Otomatik)</p>
            <div class="table-responsive">
                <table class="table table-dark table-hover align-middle">
                    <thead><tr><th>Koin</th><th>Fiyat</th><th>RSI</th><th>Sinyal</th><th>Karar</th></tr></thead>
                    <tbody>
    """
    for item in sorted(data, key=lambda x: x['score'], reverse=True):
        html += f"""
        <tr>
            <td><strong>{item['symbol']}</strong></td>
            <td>${item['price']}</td>
            <td>{item['rsi']}</td>
            <td><small>{item['signals']}</small></td>
            <td style="color:{item['color']}; font-weight:bold;">{item['decision']}</td>
        </tr>
        """
    html += "</tbody></table></div></div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
    print("İşlem başarıyla tamamlandı.")
