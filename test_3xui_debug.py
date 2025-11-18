#!/usr/bin/env python3
# test_3xui_debug.py
"""
Script de diagnóstico para verificar integración con 3x-ui
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def test_3xui_detailed():
    """Prueba exhaustiva de 3x-ui API"""
    
    panel_url = os.getenv('THREEXUI_PANEL_URL', 'http://localhost:54321').rstrip('/')
    username = os.getenv('THREEXUI_USERNAME', 'admin')
    password = os.getenv('THREEXUI_PASSWORD', 'admin')
    inbound_id = int(os.getenv('THREEXUI_INBOUND_ID', '1'))
    
    print("=" * 80)
    print("DIAGNÓSTICO DE 3X-UI")
    print("=" * 80)
    print(f"\n📡 Configuración:")
    print(f"   URL: {panel_url}")
    print(f"   Usuario: {username}")
    print(f"   Password: {'*' * len(password)}")
    print(f"   Inbound ID: {inbound_id}")
    
    session = requests.Session()
    
    # ============================================
    # TEST 1: Login
    # ============================================
    print("\n" + "-" * 80)
    print("TEST 1: Login en el panel")
    print("-" * 80)
    
    try:
        response = session.post(
            f"{panel_url}/login",
            data={
                'username': username,
                'password': password
            },
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login exitoso")
            
            # Verificar si hay cookie de sesión
            cookies = session.cookies.get_dict()
            print(f"   Cookies: {list(cookies.keys())}")
            
        else:
            print(f"   ❌ Login falló")
            print(f"   Response: {response.text[:200]}")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # ============================================
    # TEST 2: Listar todos los Inbounds
    # ============================================
    print("\n" + "-" * 80)
    print("TEST 2: Listar Inbounds")
    print("-" * 80)
    
    try:
        response = session.get(
            f"{panel_url}/panel/api/inbounds/list",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                inbounds = data.get('obj', [])
                print(f"   ✅ {len(inbounds)} inbound(s) encontrado(s)")
                
                for inbound in inbounds:
                    print(f"\n   📍 Inbound ID: {inbound.get('id')}")
                    print(f"      Puerto: {inbound.get('port')}")
                    print(f"      Protocolo: {inbound.get('protocol')}")
                    print(f"      Remark: {inbound.get('remark', 'N/A')}")
                    print(f"      Habilitado: {inbound.get('enable')}")
                    
                    # Ver clientes
                    if 'settings' in inbound:
                        try:
                            settings = json.loads(inbound['settings'])
                            clients = settings.get('clients', [])
                            print(f"      Clientes: {len(clients)}")
                            
                            for i, client in enumerate(clients[:3], 1):  # Mostrar primeros 3
                                print(f"         {i}. {client.get('email', 'N/A')} - UUID: {client.get('id', 'N/A')[:8]}...")
                                
                        except:
                            print(f"      ⚠️ No se pudo parsear settings")
                
            else:
                print(f"   ❌ API retornó success=false")
                
        else:
            print(f"   ❌ Error HTTP")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # ============================================
    # TEST 3: Obtener Inbound específico
    # ============================================
    print("\n" + "-" * 80)
    print(f"TEST 3: Obtener Inbound ID {inbound_id}")
    print("-" * 80)
    
    try:
        response = session.get(
            f"{panel_url}/panel/api/inbounds/get/{inbound_id}",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                inbound = data.get('obj', {})
                print(f"   ✅ Inbound encontrado")
                print(f"      ID: {inbound.get('id')}")
                print(f"      Puerto: {inbound.get('port')}")
                print(f"      Protocolo: {inbound.get('protocol')}")
                
                # Parsear clientes
                if 'settings' in inbound:
                    try:
                        settings = json.loads(inbound['settings'])
                        clients = settings.get('clients', [])
                        
                        print(f"\n   👥 CLIENTES ACTUALES: {len(clients)}")
                        print("   " + "-" * 76)
                        
                        if clients:
                            for i, client in enumerate(clients, 1):
                                email = client.get('email', 'N/A')
                                uuid = client.get('id', 'N/A')
                                enabled = client.get('enable', False)
                                total_gb = client.get('totalGB', 0)
                                up = client.get('up', 0)
                                down = client.get('down', 0)
                                
                                print(f"\n   {i}. Email: {email}")
                                print(f"      UUID: {uuid}")
                                print(f"      Habilitado: {'✅' if enabled else '❌'}")
                                print(f"      Límite: {total_gb / (1024**3):.2f} GB")
                                print(f"      Upload: {up / (1024**2):.2f} MB")
                                print(f"      Download: {down / (1024**2):.2f} MB")
                                print(f"      Total: {(up + down) / (1024**2):.2f} MB")
                                
                                # Verificar si está vinculado a un perfil
                                sub_id = client.get('subId', '')
                                if sub_id:
                                    print(f"      🔗 Perfil vinculado: {sub_id}")
                        else:
                            print("   ⚠️ No hay clientes en este inbound")
                            
                    except Exception as e:
                        print(f"   ❌ Error parseando clientes: {e}")
                        
            else:
                print(f"   ❌ Inbound no encontrado o success=false")
                
        else:
            print(f"   ❌ Error HTTP")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # ============================================
    # TEST 4: Crear cliente de prueba
    # ============================================
    print("\n" + "-" * 80)
    print("TEST 4: Crear cliente de prueba")
    print("-" * 80)
    
    import uuid
    import time
    
    test_client_uuid = str(uuid.uuid4())
    test_client_email = f"test_client_{int(time.time())}"
    
    client_data = {
        'id': test_client_uuid,
        'email': test_client_email,
        'enable': True,
        'expiryTime': int(time.time() * 1000) + (30 * 24 * 60 * 60 * 1000),  # 30 días
        'totalGB': 10 * 1024 * 1024 * 1024,  # 10 GB
        'flow': '',
        'subId': 'test_profile_123'
    }
    
    print(f"   Creando cliente: {test_client_email}")
    print(f"   UUID: {test_client_uuid}")
    
    try:
        response = session.post(
            f"{panel_url}/panel/api/inbounds/addClient",
            json={
                'id': inbound_id,
                'settings': json.dumps({
                    'clients': [client_data]
                })
            },
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"   ✅ Cliente creado exitosamente")
                print(f"\n   🎉 INTEGRACIÓN FUNCIONANDO CORRECTAMENTE")
                print(f"      El cliente debería aparecer en la interfaz web")
                print(f"      Ve a: Inbounds → Click en Inbound {inbound_id} → Expandir")
            else:
                print(f"   ❌ API retornó success=false")
                print(f"   Mensaje: {result.get('msg', 'N/A')}")
        else:
            print(f"   ❌ Error al crear cliente")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # ============================================
    # RESUMEN
    # ============================================
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print("\n💡 Para ver los clientes en la interfaz web:")
    print("   1. Ve a: Inbounds (menú lateral)")
    print("   2. Busca el Inbound con ID:", inbound_id)
    print("   3. Haz clic en los 3 puntos (⋮) o en el icono de expandir")
    print("   4. Se mostrará la lista de clientes dentro de ese inbound")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_3xui_detailed()