import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# --- SETTINGS ---
TIMEFRAME = '4h'

def analyze_market():
    # Binance yerine MEXC kullanıyoruz (GitHub dostu)
    exchange = ccxt.mexc() 
    
    symbols = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'LINK/USDT',
        'MATIC/USDT', 'LTC/USDT', 'NEAR/USDT', 'FIL/USDT', 'TIA/USDT'
    ]
    
    results = []
    print(f"Fetching data from MEXC for {len(symbols)} coins...")

    for symbol in symbols:
        try:
            # Veri çekme
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
            if not bars: continue

            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # Teknik Göstergeler
            df['RSI'] = ta.rsi(df['close'], length=14)
            macd_df = ta.macd(df['close'])
            
            df['MACD'] = macd_df.iloc[:, 0]
            df['MACD_S'] = macd_df.iloc[:, 2]
            
            last = df.iloc[-1]
            rsi_val = last['RSI']
            score = 0
            signals = []

            # Analiz Mantığı
            if rsi_val < 35: score += 1; signals.append("RSI Oversold")
            elif rsi_val > 65: score -= 1; signals.append("RSI Overbought")
            
            if last['MACD'] > last['MACD_S']: score += 1; signals.append("MACD Bullish")
            else: score -= 1; signals.append("MACD Bearish")

            decision = "NEUTRAL"
            color = "#ffffff"
            if score >= 2: decision = "STRONG BUY"; color = "#00ff00"
            elif score == 1: decision = "BUY"; color = "#adff2f"
            elif score == -1: decision = "SELL"; color = "#ff7f50"
            elif score <= -2: decision = "STRONG SELL"; color = "#ff0000"

            results.append({
                'symbol': symbol.split('/')[0],
                'price': last['close'],
                'rsi': round(rsi_val, 2) if not pd.isna(rsi_val) else 0,
                'score': score,
                'decision': decision,
                'color': color,
                'signals': ", ".join(signals)
            })
            print(f"Analyzed: {symbol}")
            time.sleep(0.2) 
        except Exception as e:
            print(f"Error skipping {symbol}: {e}")
            continue
    return results

def create_html(data):
    now = datetime.now().strftime('%d %b %Y %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>BasedVector - Analysis</title>
        <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #0a0a0a; color: #f0f0f0; font-family: sans-serif; }}
            .table {{ background: #141414; border: 1px solid #333; border-radius: 8px; overflow: hidden; }}
            .table-dark {{ --bs-table-bg: #141414; }}
            .update-time {{ color: #777; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container py-5 text-center">
            <h1 class="fw-bold mb-1">BASEDVECTOR.COM</h1>
            <p class="update-time mb-5">Last Update: {now} (UTC)</p>
            <div class="table-responsive text-start">
                <table class="table table-dark table-hover align-middle">
                    <thead>
                        <tr style="border-bottom: 2px solid #444;">
                            <th>Asset</th><th>Price</th><th>RSI</th><th>Signals</th><th>Decision</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    if not data:
        html += "<tr><td colspan='5' class='text-center py-5 text-danger'>Data source is temporarily unavailable. Retrying in next cycle...</td></tr>"
    else:
        for item in sorted(data, key=lambda x: x['score'], reverse=True):
            html += f"""
            <tr style="border-bottom: 1px solid #222;">
                <td><strong>{item['symbol']}</strong></td>
                <td>${item['price']:,}</td>
                <td>{item['rsi']}</td>
                <td><small class='text-muted'>{item['signals']}</small></td>
                <td style="color:{item['color']}; font-weight:bold;">{item['decision']}</td>
            </tr>
            """
    html += "</tbody></table></div></div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    market_data = analyze_market()
    create_html(market_data)
