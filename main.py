def create_html(data):
    full_update = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    corr_html = ""
    for item in data:
        if 'BTC_Corr' in item['details']:
            c = item['details']['BTC_Corr']
            color = "border-green-500" if c > 0.6 else ("border-red-500" if c < 0 else "border-gray-500")
            corr_html += f'<div class="p-2 rounded-lg text-center border-b-2 {color} corr-card" style="background:rgba(100,100,100,0.1)"><div class="text-xs font-bold corr-sym">{item["symbol"]}</div><div class="text-sm font-mono font-bold corr-val">{c}</div></div>'

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>BasedVector Alpha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ 
            --bg: #050505; --card: #0a0a0a; --text: #f8fafc; --border: #333; 
            --modal-bg: #0e0e0e; --modal-text: #f8fafc; --corr-text: #fff; 
        }}
        .light {{ 
            --bg: #f1f5f9; --card: #ffffff; --text: #0f172a; --border: #cbd5e1; 
            --modal-bg: #ffffff; --modal-text: #0f172a; --corr-text: #0f172a; 
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; padding-top: 100px; transition: 0.3s; }}
        
        /* BasedVector Özel Logo Rengi */
        .brand-logo {{
            background: linear-gradient(90deg, #8b0000, #ff0000, #808080, #008000, #006400);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }}

        .legal-top {{ background: #1f2937; color: #e5e7eb; text-align: center; padding: 10px; font-size: 11px; position: fixed; top: 0; width: 100%; z-index: 100; border-bottom: 2px solid #dc2626; }}
        .card {{ border-radius: 12px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: var(--card); }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        
        /* Modal İyileştirmeleri */
        #modal-content {{ background: var(--modal-bg); color: var(--modal-text); border: 1px solid var(--border); }}
        .modal-label {{ opacity: 0.6; color: var(--modal-text); }}
        .modal-value {{ font-weight: bold; color: var(--modal-text); }}
        
        .ai-box {{ background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 15px; color: var(--modal-text); }}
        .live-indicator {{ width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; margin-right: 5px; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }} }}
    </style></head>
    <body>
        <div class="legal-top"><strong>⚠️ LEGAL DISCLAIMER:</strong> Not financial advice. Technicals + AI Logic. <strong>High Risk.</strong></div>
        <div class="max-w-7xl mx-auto p-4">
            <header class="flex justify-between items-center mb-8">
                <h1 class="text-4xl font-black italic tracking-tighter brand-logo">BasedVector</h1>
                <div class="flex items-center gap-4">
                    <button onclick="toggleTheme()" class="p-2 bg-gray-800 text-white rounded-full" id="theme-toggle">🌙</button>
                    <div class="text-[10px] font-mono opacity-60 flex items-center">
                        <span class="live-indicator"></span> UPDATED: {full_update} UTC
                    </div>
                </div>
            </header>
            <div class="grid grid-cols-5 md:grid-cols-10 gap-2 mb-8">{corr_html}</div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <input type="text" id="search" placeholder="Search..." class="bg-transparent border border-gray-500 p-3 rounded-lg w-full">
                <select id="sort" class="bg-transparent border border-gray-500 p-3 rounded-lg cursor-pointer w-full text-current">
                    <option value="score-desc">🔥 Score: High</option>
                    <option value="score-asc">❄️ Score: Low</option>
                </select>
                <button id="fav-btn" class="bg-blue-600 text-white p-3 rounded-lg font-bold w-full hover:bg-blue-700 transition">⭐ Watchlist</button>
            </div>
            <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    """

    for i in data:
        detail_json = json.dumps(i['details'])
        encoded_details = base64.b64encode(detail_json.encode()).decode()
        intensity = abs(i['score']) / 3 * 50
        bar_pos = f"width:{intensity}%; left:50%;" if i['score'] >= 0 else f"width:{intensity}%; left:{50-intensity}%;"
        
        # Kart arka planı için tema uyumlu soft renk dokunuşu
        card_style = f"border-color: {i['border']}; border-bottom-width: 4px;"
        
        html += f"""
        <div class="card p-4 flex flex-col justify-between" 
             style="{card_style}"
             data-symbol="{i['symbol']}" data-score="{i['score']}" 
             data-info="{encoded_details}" onclick="showSafeDetails(this)">
            <div class="flex justify-between items-center">
                <span class="font-bold text-lg font-mono">{i['symbol']}</span>
                <button onclick="event.stopPropagation();" class="text-gray-400">★</button>
            </div>
            <div class="text-center my-4">
                <div class="text-xl font-bold">${i['price']}</div>
                <div class="h-1 bg-gray-300/20 rounded-full mt-2 relative">
                    <div class="absolute h-full" style="{bar_pos} background:{i['bar']}"></div>
                </div>
            </div>
            <div class="flex justify-between items-center text-[10px] opacity-60 font-mono">
                <span class="font-bold text-sm" style="color:{i['bar']}">{i['score']}</span>
                <span>{i['update_time']}</span>
            </div>
        </div>
        """

    html += """
        </div></div>
        <div id="modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 z-50" onclick="this.classList.add('hidden')">
            <div id="modal-content" class="p-8 rounded-2xl max-w-md w-full relative shadow-2xl" onclick="event.stopPropagation()">
                <button onclick="document.getElementById('modal').classList.add('hidden')" class="absolute top-4 right-4 opacity-50 text-2xl">&times;</button>
                <h3 id="m-title" class="text-3xl font-bold mb-6 border-b border-gray-500/20 pb-2"></h3>
                <div id="m-body" class="space-y-3 font-mono text-sm"></div>
                <div id="m-ai" class="ai-box italic text-sm"></div>
            </div>
        </div>
        <script>
            function toggleTheme() {
                document.body.classList.toggle('light');
                const isLight = document.body.classList.contains('light');
                document.getElementById('theme-toggle').innerText = isLight ? '☀️' : '🌙';
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
            }
            function showSafeDetails(el) {
                const sym = el.dataset.symbol;
                const details = JSON.parse(atob(el.dataset.info)); 
                document.getElementById('m-title').innerText = sym;
                let content = "";
                for (const [k, v] of Object.entries(details)) {
                    if (k !== 'AI_Eval') content += `<div class="flex justify-between border-b border-gray-500/10 py-2"><span class="modal-label">${k}</span><span class="modal-value">${v}</span></div>`;
                }
                document.getElementById('m-body').innerHTML = content;
                document.getElementById('m-ai').innerHTML = "<b>AI ANALYSIS:</b><br>" + details.AI_Eval;
                document.getElementById('modal').classList.remove('hidden');
            }
            function render() {
                const term = document.getElementById('search').value.toUpperCase();
                const sortVal = document.getElementById('sort').value; 
                let cards = Array.from(document.querySelectorAll('.card'));
                cards.forEach(c => {
                    c.style.display = c.dataset.symbol.includes(term) ? 'flex' : 'none';
                });
                const grid = document.getElementById('grid');
                cards.sort((a, b) => sortVal === 'score-desc' ? b.dataset.score - a.dataset.score : a.dataset.score - b.dataset.score);
                cards.forEach(c => grid.appendChild(c));
            }
            document.getElementById('search').addEventListener('input', render);
            document.getElementById('sort').addEventListener('change', render);
            window.onload = () => { 
                if(localStorage.getItem('theme')==='light') toggleTheme(); 
                render(); 
            };
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)
