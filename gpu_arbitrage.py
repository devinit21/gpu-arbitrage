import os, requests, time, json
print("🚀 GPU Arbitrage Bot v1.0 - Deployed!")

# API Keys from Render environment
HETZNER_API = os.getenv('HETZNER_API', 'demo')
VULTR_API = os.getenv('VULTR_API', 'demo')
VASTAI_KEY = os.getenv('VASTAI_KEY', 'demo')

def scan_vast_ai():
    headers = {'Authorization': f'Bearer {VASTAI_KEY}'}
    resp = requests.get('https://api.vast.ai/models?limit=10', headers=headers)
    if resp.status_code == 200:
        models = resp.json()['models']
        print(f"💰 Found {len(models)} GPU offers")
        for m in models[:3]:
            print(f"  {m['name']}: ${m.get('price_per_hour',0):.2f}/hr")

while True:
    print(f"[{time.strftime('%H:%M:%S')}] Scanning...")
    scan_vast_ai()
    time.sleep(30)
