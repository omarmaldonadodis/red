import requests

proxy_config = {
    "host": "proxy.soax.com",  
    "port": 5000,            
    "username": "package-325401-country-ec-region-pichincha-city-quito-sessionid-WcYsbipcTJwBPWVF-sessionlength-300-opt-lookalike",
    "password": "uTiG2ei048ORzVSX",
}

proxies = {
    "http": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}",
    "https": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
}

try:
    r = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=60)
    print("✅ Proxy funciona:", r.json())
except Exception as e:
    print("❌ Proxy falla:", e)
