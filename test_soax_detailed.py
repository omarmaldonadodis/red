# test_soax_detailed.py
import requests
import urllib3
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_soax_comprehensive():
    """Test exhaustivo de SOAX con diferentes configuraciones"""
    
    username_base = "package-325126-ses"
    password = "2mNJwoSLzShSkzf7"
    host = "proxy.soax.com"
    port = 5000
    
    print("="*70)
    print("TEST EXHAUSTIVO DE SOAX PROXY")
    print("="*70)
    
    # Test 1: Verificar DNS
    print("\n1️⃣  Test DNS de proxy.soax.com")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✅ DNS resuelve a: {ip}")
    except Exception as e:
        print(f"   ❌ Error DNS: {e}")
        return
    
    # Test 2: Verificar conectividad al puerto
    print(f"\n2️⃣  Test conectividad a {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"   ✅ Puerto {port} está abierto")
        else:
            print(f"   ❌ Puerto {port} cerrado o inaccesible")
            print(f"   💡 Intenta verificar el puerto en tu dashboard SOAX")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Configuraciones a probar
    configs = [
        {
            'name': 'HTTP - Username base',
            'protocol': 'http',
            'username': username_base
        },
        {
            'name': 'HTTP - Con sessionid',
            'protocol': 'http',
            'username': f"{username_base}ionid-test123-sessionlength-300"
        },
        {
            'name': 'HTTP - Con sessionid (guión)',
            'protocol': 'http',
            'username': f"{username_base}-sessionid-test123-sessionlength-300"
        },
        {
            'name': 'SOCKS5 - Username base',
            'protocol': 'socks5',
            'username': username_base
        },
        {
            'name': 'SOCKS5 - Con sessionid',
            'protocol': 'socks5',
            'username': f"{username_base}ionid-test123-sessionlength-300"
        }
    ]
    
    for i, config in enumerate(configs, 3):
        print(f"\n{i}️⃣  {config['name']}")
        
        proxy_url = f"{config['protocol']}://{config['username']}:{password}@{host}:{port}"
        print(f"   URL: {config['protocol']}://{config['username'][:30]}...@{host}:{port}")
        
        try:
            # Intentar obtener IP
            response = requests.get(
                'http://api.ipify.org?format=json',  # HTTP en lugar de HTTPS
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                },
                timeout=20,
                verify=False
            )
            
            ip = response.json()['ip']
            print(f"   ✅ FUNCIONA! IP obtenida: {ip}")
            
            # Si funciona, obtener más info
            try:
                response = requests.get(
                    'http://ip-api.com/json/',
                    proxies={
                        'http': proxy_url,
                        'https': proxy_url
                    },
                    timeout=15,
                    verify=False
                )
                data = response.json()
                print(f"   📍 País: {data.get('country')}")
                print(f"   🏙️  Ciudad: {data.get('city')}")
                print(f"   🌐 ISP: {data.get('isp')}")
            except:
                pass
            
            return True  # Si encontramos una config que funciona, salir
            
        except requests.exceptions.ProxyError as e:
            print(f"   ❌ Error de proxy")
            error_str = str(e)
            if "407" in error_str:
                print(f"   💡 Error 407: Autenticación requerida - verifica credenciales")
            elif "Connection refused" in error_str:
                print(f"   💡 Conexión rechazada - verifica puerto y servidor")
            else:
                print(f"   💡 {error_str[:100]}")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout (>20s)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*70)
    print("❌ NINGUNA CONFIGURACIÓN FUNCIONÓ")
    print("\n💡 Posibles soluciones:")
    print("   1. Verifica credenciales en https://soax.com/dashboard")
    print("   2. Verifica que tengas saldo/créditos activos")
    print("   3. Revisa el puerto correcto en tu dashboard")
    print("   4. Contacta soporte de SOAX si persiste")
    print("="*70)
    
    return False

if __name__ == "__main__":
    test_soax_comprehensive()