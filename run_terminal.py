import subprocess
import time
from datetime import datetime

def run_bot():
    wait_minutes = 10  # Her tarama bittikten sonra ne kadar beklesin? (Dakika)
    
    while True:
        now = datetime.now().strftime('%H:%M:%S')
        print(f"\n--- [{now}] YENİ TARAMA BAŞLATILIYOR ---")
        
        try:
            # main.py dosyasını çalıştırır
            process = subprocess.Popen(['python', 'main.py'])
            process.wait() # Tarama bitene kadar bekler
            
            print(f"\n--- [{datetime.now().strftime('%H:%M:%S')}] TARAMA TAMAMLANDI ---")
            print(f"Sistem {wait_minutes} dakika dinlenmeye geçiyor (Ban koruması)...")
            
            # Bekleme süresi (Dakika * 60 saniye)
            time.sleep(wait_minutes * 60)
            
        except KeyboardInterrupt:
            print("\nOtomasyon kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            time.sleep(60) # Hata durumunda 1 dakika bekle ve tekrar dene

if __name__ == "__main__":
    run_bot()
