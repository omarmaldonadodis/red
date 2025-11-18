# test_adspower_detailed.py
import requests

def test_adspower_all_methods():
    """Prueba todas las formas posibles de enviar API key"""
    
    api_url = "http://local.adspower.net:50325"
    api_key = "0cbbd771ae5f6fad7ff4917bc66c95be"
    
    print("="*70)
    print("TEST EXHAUSTIVO DE ADSPOWER API")
    print("="*70)
    


    # Método 3: Header Authorization
    print("\n3️⃣  Header: Authorization")
    try:
        response = requests.get(
            f"{api_url}/api/v1/user/list",
            headers={'Authorization': f'Bearer {api_key}'},
            params={'page': 1, 'page_size': 1}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Método 4: Header X-API-Key
    print("\n4️⃣  Header: X-API-Key")
    try:
        response = requests.get(
            f"{api_url}/api/v1/user/list",
            headers={'X-API-Key': api_key},
            params={'page': 1, 'page_size': 1}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Método 5: Header api-key
    print("\n5️⃣  Header: api-key")
    try:
        response = requests.get(
            f"{api_url}/api/v1/user/list",
            headers={'api-key': api_key},
            params={'page': 1, 'page_size': 1}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Método 6: En la URL directamente
    print("\n6️⃣  En URL: ?api_key=XXX")
    try:
        response = requests.get(
            f"{api_url}/api/v1/user/list?api_key={api_key}&page=1&page_size=1"
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Método 7: POST en lugar de GET
    print("\n7️⃣  POST con api_key en params")
    try:
        response = requests.post(
            f"{api_url}/api/v1/user/list",
            params={'api_key': api_key},
            json={'page': 1, 'page_size': 1}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_adspower_all_methods()