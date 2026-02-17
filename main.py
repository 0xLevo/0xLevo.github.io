name: Update Market Data

on:
  schedule:
    - cron: '*/15 * * * *'  # Her 15 dakikada bir çalışır
  workflow_dispatch:        # Elle "Run workflow" diyebilmek için

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Repo'yu Çek
      uses: actions/checkout@v3

    - name: Python Kur
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Kütüphaneleri Yükle
      run: |
        pip install ccxt pandas pandas_ta numpy

    - name: Analizi Çalıştır
      run: python main.py

    - name: Değişiklikleri Kaydet ve Gönder (Commit & Push)
      run: |
        git config --global user.name 'BasedVector Bot'
        git config --global user.email 'bot@noreply.github.com'
        git add index.html
        git commit -m "📈 Market Update: $(date)" || echo "Değişiklik yok"
        git push
