# test_credentials.py
import requests
import urllib3
from dotenv import load_dotenv
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

def test_adspower():
    """Prueba AdsPower API con Bearer token"""
    print("\n" + "="*70)
    print("PROBANDO ADSPOWER")
    print("="*70)
    
    api_url = os.getenv('ADSPOWER_API_URL', 'http://local.adspower.net:50325')
    api_key = os.getenv('ADSPOWER_API_KEY')
    
    print(f"URL: {api_url}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}" if api_key else "API Key: NO CONFIGURADA")
    
    if not api_key:
        print("❌ API Key no encontrada en .env")
        return False
    
    try:
        # Usar Bearer token en header
        response = requests.get(
            f"{api_url}/api/v1/user/list",
            headers={'Authorization': f'Bearer {api_key}'},
            params={'page': 1, 'page_size': 1},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        result = response.json()
        
        if result.get('code') == 0:
            print(f"\n✅ AdsPower OK!")
            # El 'total' puede no estar en todas las versiones de AdsPower
            profiles = result.get('data', {}).get('list', [])
            print(f"Perfiles encontrados: {len(profiles)}")
            if profiles:
                print(f"Último perfil: {profiles[0].get('name')}")
            return True
        else:
            print(f"\n❌ Error: {result.get('msg')}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_soax():
    """Prueba SOAX proxy con formato correcto"""
    print("\n" + "="*70)
    print("PROBANDO SOAX")
    print("="*70)
    
    username = os.getenv('SOAX_USERNAME')
    password = os.getenv('SOAX_PASSWORD')
    port = os.getenv('SOAX_PROXY_PORT', '5000')
    
    # Extraer package ID
    if username and username.startswith('package-'):
        parts = username.split('-')
        if len(parts) >= 2:
            package_id = f"{parts[0]}-{parts[1]}"  # package-325126
        else:
            package_id = username
    else:
        package_id = username
    
    print(f"Package ID: {package_id}")
    print(f"Password: {'*' * len(password) if password else 'NO CONFIGURADA'}")
    print(f"Port: {port}")
    
    if not package_id or not password:
        print("❌ Credenciales no encontradas en .env")
        return False
    
    # Generar session ID
    import random
    import string
    session_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    # Formato correcto SOAX
    username_final = f"{package_id}-sessionid-{session_id}-sessionlength-300"
    proxy_url = f"http://{username_final}:{password}@proxy.soax.com:{port}"
    
    print(f"\nUsername: {username_final[:60]}...")
    print(f"Probando conexión...")
    
    try:
        # Probar con checker de SOAX
        response = requests.get(
            'http://checker.soax.com/api/ipinfo',
            proxies={'http': proxy_url, 'https': proxy_url},
            timeout=25,
            verify=False
        )
        
        print(f"\n✅ SOAX FUNCIONA!")
        print(f"Status Code: {response.status_code}")
        
        # Intentar parsear respuesta
        try:
            data = response.json()
            print(f"Respuesta JSON: {data}")
            
            # Extraer IP de diferentes formatos posibles
            ip = data.get('ip') or data.get('query') or data.get('ipAddress')
            country = data.get('country') or data.get('countryCode')
            city = data.get('city')
            isp = data.get('isp') or data.get('org') or data.get('as')
            
            if ip:
                print(f"\n📍 Información del Proxy:")
                print(f"   IP: {ip}")
                if country:
                    print(f"   País: {country}")
                if city:
                    print(f"   Ciudad: {city}")
                if isp:
                    print(f"   ISP: {isp}")
            
        except:
            # Si no es JSON, mostrar texto
            print(f"Respuesta (texto): {response.text[:200]}")
        
        return True
        
    except requests.exceptions.ProxyError as e:
        print(f"❌ Error de proxy: {str(e)[:150]}")
        print("   Verifica credenciales en SOAX dashboard")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout (>25s)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:150]}")
        return False

def test_3xui():
    """Prueba 3x-ui"""
    print("\n" + "="*70)
    print("PROBANDO 3X-UI")
    print("="*70)
    
    use_3xui = os.getenv('USE_3XUI', 'false').lower() == 'true'
    
    if not use_3xui:
        print("⏭️  3x-ui deshabilitado en .env")
        return True
    
    panel_url = os.getenv('THREEXUI_PANEL_URL')
    username = os.getenv('THREEXUI_USERNAME')
    password = os.getenv('THREEXUI_PASSWORD')
    
    print(f"URL: {panel_url}")
    print(f"Usuario: {username}")
    
    try:
        response = requests.post(
            f"{panel_url.rstrip('/')}/login",
            data={'username': username, 'password': password},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 3x-ui OK!")
            return True
        else:
            print(f"❌ Error de login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("DIAGNÓSTICO COMPLETO DE CREDENCIALES")
    print("="*70)
    
    adspower_ok = test_adspower()
    soax_ok = test_soax()
    threexui_ok = test_3xui()
    
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    print(f"AdsPower:  {'✅ OK' if adspower_ok else '❌ FALLO'}")
    print(f"SOAX:      {'✅ OK' if soax_ok else '❌ FALLO'}")
    print(f"3x-ui:     {'✅ OK' if threexui_ok else '❌ FALLO'}")
    print("="*70)
    
    all_ok = adspower_ok and soax_ok and threexui_ok
    
    if all_ok:
        print("\n🎉 ¡TODO FUNCIONANDO! Puedes ejecutar: python3 main.py")
    else:
        print("\n⚠️  Hay problemas que resolver antes de continuar")