import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# --- AYARLAR ---
# Analiz edilecek coin sayısı (Hız için düşük tuttum, artırabilirsiniz)
COIN_LIMIT = 50 
TIMEFRAME = '4h' # 4 Saatlik mumlara bakar

def get_top_coins():
    # Binance public API'ye bağlan (Key gerekmez)
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    
    # USDT paritelerini filtrele
    symbols = [s for s in markets if s.endswith('/USDT')]
    
    # Hacme göre sıralama yapmak karmaşık olabilir, 
    # bu örnekte popüler coinleri manuel listelemek veya
    # basitçe ilk gelenleri almak en garantisidir.
    # Şimdilik örnek bir liste üzerinden gidelim:
    # (Gerçek bir top 100 için CoinGecko API eklenebilir ama kod uzar)
    top_coins = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'TRX/USDT',
        'MATIC/USDT', 'LTC/USDT', 'SHIB/USDT', 'LINK/USDT', 'ATOM/USDT'
        # Buraya istediğiniz kadar coin ekleyebilirsiniz
    ]
    return top_coins, exchange

def analyze_market():
    symbols, exchange = get_top_coins()
    results = []
    
    print("Veriler çekiliyor ve analiz ediliyor...")
    
    for symbol in symbols:
        try:
            # Son 100 mumu çek
            bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # İndikatörleri Hesapla (Pandas TA)
            # RSI (14)
            df['RSI'] = ta.rsi(df['close'], length=14)
            # MACD
            macd = ta.macd(df['close'])
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_SIGNAL'] = macd['MACDs_12_26_9']
            
            # Son veriyi al
            last_row = df.iloc[-1]
            rsi_val = last_row['RSI']
            macd_val = last_row['MACD']
            signal_val = last_row['MACD_SIGNAL']
            close_price = last_row['close']
            
            # --- PUANLAMA MOTORU ---
            score = 0
            reasons = []
            
            # RSI Kuralları
            if rsi_val < 30:
                score += 1
                reasons.append("RSI Aşırı Satım (Ucuz)")
            elif rsi_val > 70:
                score -= 1
                reasons.append("RSI Aşırı Alım (Pahalı)")
            
            # MACD Kuralları
            if macd_val > signal_val:
                score += 1
                reasons.append("MACD Al Sinyali")
            elif macd_val < signal_val:
                score -= 1
                reasons.append("MACD Sat Sinyali")
                
            # Sonuç Kararı
            decision = "NÖTR"
            color = "gray"
            if score >= 2:
                decision = "GÜÇLÜ AL"
                color = "green"
            elif score == 1:
                decision = "AL"
                color = "lightgreen"
            elif score == -1:
                decision = "SAT"
                color = "orange"
            elif score <= -2:
                decision = "GÜÇLÜ SAT"
                color = "red"
                
            results.append({
                'Coin': symbol.replace('/USDT', ''),
                'Fiyat': f"${close_price:.4f}",
                'RSI': f"{rsi_val:.2f}",
                'Puan': score,
                'Karar': decision,
                'Sebep': ", ".join(reasons),
                'Color': color
            })
            
            # API Ban yememek için bekle
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Hata ({symbol}): {e}")

    return results

def create_html(data):
    # HTML Şablonu
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BasedVector - Kripto Analiz</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #121212; color: #ffffff; }}
            .card {{ background-color: #1e1e1e; border: none; margin-bottom: 10px; }}
            .score-box {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4">BasedVector.com Analiz Robotu</h1>
            <p class="text-center text-muted">Son Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="table-responsive">
                <table class="table table-dark table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Coin</th>
                            <th>Fiyat</th>
                            <th>RSI</th>
                            <th>Puan</th>
                            <th>Karar</th>
                            <th>Sinyaller</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for row in data:
        html_content += f"""
        <tr>
            <td><strong>{row['Coin']}</strong></td>
            <td>{row['Fiyat']}</td>
            <td>{row['RSI']}</td>
            <td>{row['Puan']}</td>
            <td style="color: {row['Color']}; font-weight:bold;">{row['Karar']}</td>
            <td><small>{row['Sebep']}</small></td>
        </tr>
        """
        
    html_content += """
                    </tbody>
                </table>
            </div>
            <footer class="text-center mt-5 text-muted">
                <small>Bu veriler yatırım tavsiyesi değildir. Otomatik teknik analiz sonuçlarıdır.</small>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = analyze_market()
    # Puanı yüksek olanlar en üstte görünsün
    data.sort(key=lambda x: x['Puan'], reverse=True)
    create_html(data)
    print("Site başarıyla güncellendi!")
