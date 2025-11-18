#!/usr/bin/env python3
# test_3xui_autoconfig.py
"""
Prueba el sistema de autoconfiguración de 3x-ui
"""

from dotenv import load_dotenv
import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Importar el nuevo manager
from proxy_manager import ThreeXUIManager

def test_autoconfig():
    """Prueba la autoconfiguración"""
    
    print("=" * 80)
    print("TEST DE AUTOCONFIGURACIÓN DE 3X-UI")
    print("=" * 80)
    
    panel_url = os.getenv('THREEXUI_PANEL_URL', 'http://localhost:54321')
    username = os.getenv('THREEXUI_USERNAME', 'admin')
    password = os.getenv('THREEXUI_PASSWORD', 'admin')
    inbound_id_env = os.getenv('THREEXUI_INBOUND_ID', '')
    
    print(f"\n📋 Configuración desde .env:")
    print(f"   URL: {panel_url}")
    print(f"   Usuario: {username}")
    print(f"   Inbound ID: {inbound_id_env if inbound_id_env else 'AUTO-DETECTAR'}")
    
    # Convertir inbound_id
    if inbound_id_env and inbound_id_env.strip():
        try:
            inbound_id = int(inbound_id_env)
        except:
            inbound_id = None
    else:
        inbound_id = None
    
    print("\n" + "-" * 80)
    print("INICIALIZANDO 3X-UI MANAGER...")
    print("-" * 80)
    
    try:
        # Inicializar (hará login y auto-configuración)
        manager = ThreeXUIManager(
            panel_url=panel_url,
            username=username,
            password=password,
            inbound_id=inbound_id
        )
        
        print("\n✅ Manager inicializado exitosamente")
        
        # Obtener info del inbound seleccionado
        print("\n" + "-" * 80)
        print("INFORMACIÓN DEL INBOUND SELECCIONADO")
        print("-" * 80)
        
        inbound_info = manager.get_inbound_info()
        
        if inbound_info:
            print(f"\n📍 Inbound ID: {inbound_info.get('id')}")
            print(f"   Puerto: {inbound_info.get('port')}")
            print(f"   Protocolo: {inbound_info.get('protocol')}")
            print(f"   Remark: {inbound_info.get('remark', 'N/A')}")
            print(f"   Habilitado: {'✅' if inbound_info.get('enabled') else '❌'}")
            print(f"   Clientes: {inbound_info.get('client_count', 0)}")
            print(f"   Upload total: {inbound_info.get('up', 0) / (1024**2):.2f} MB")
            print(f"   Download total: {inbound_info.get('down', 0) / (1024**2):.2f} MB")
        
        # Crear cliente de prueba
        print("\n" + "-" * 80)
        print("CREANDO CLIENTE DE PRUEBA")
        print("-" * 80)
        
        import time
        test_email = f"test_autoconfig_{int(time.time())}"
        
        result = manager.create_client(
            email=test_email,
            total_gb=10,
            expiry_days=30,
            profile_id="test_profile_autoconfig"
        )
        
        if 'error' in result:
            print(f"\n❌ Error creando cliente: {result['error']}")
        else:
            print(f"\n✅ Cliente creado exitosamente:")
            print(f"   Email: {result['email']}")
            print(f"   UUID: {result['uuid']}")
            print(f"   Límite: {result['total_gb']} GB")
            print(f"   Inbound ID: {result['inbound_id']}")
            
            # Verificar tráfico
            print("\n" + "-" * 80)
            print("VERIFICANDO TRÁFICO DEL CLIENTE")
            print("-" * 80)
            
            traffic = manager.get_client_traffic(test_email)
            
            if 'error' in traffic:
                print(f"\n⚠️  No se pudo obtener tráfico: {traffic['error']}")
            else:
                print(f"\n📊 Tráfico del cliente:")
                print(f"   Usado: {traffic['total_used_mb']:.2f} MB")
                print(f"   Límite: {traffic['total_limit_mb']:.2f} MB")
                print(f"   Porcentaje: {traffic['percentage_used']:.1f}%")
        
        # Resumen final
        print("\n" + "=" * 80)
        print("RESUMEN")
        print("=" * 80)
        print("\n🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
        print(f"\n💡 El sistema está usando el Inbound ID: {manager.inbound_id}")
        print("\n📝 Para actualizar tu .env:")
        print(f"   THREEXUI_INBOUND_ID={manager.inbound_id}")
        print("\n   (Déjalo vacío para que siempre auto-detecte)")
        print("\n🌐 Para ver los clientes en la interfaz web:")
        print(f"   1. Ve a: {panel_url}")
        print(f"   2. Click en Inbounds")
        print(f"   3. Busca el Inbound ID {manager.inbound_id}")
        print(f"   4. Click en los 3 puntos (⋮) para expandir")
        print(f"   5. Verás el cliente: {test_email if 'error' not in result else 'N/A'}")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_autoconfig()