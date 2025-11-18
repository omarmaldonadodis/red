# setup_credentials.py
import os
import requests
from dotenv import set_key
import sys

def print_header(text):
    """Imprime un header decorado"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def print_section(text):
    """Imprime una sección"""
    print("\n" + "-" * 70)
    print(f"  {text}")
    print("-" * 70 + "\n")

def print_steps(steps):
    """Imprime una lista de pasos"""
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    print()

def setup_wizard():
    """Asistente interactivo para configurar credenciales"""
    
    print_header("🔧 ASISTENTE DE CONFIGURACIÓN")
    print("Este asistente te ayudará a configurar todas las credenciales")
    print("necesarias para el sistema de creación de cuentas.\n")
    
    env_file = ".env"
    
    # Crear .env si no existe
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# Credenciales del sistema - Generado automáticamente\n")
            f.write(f"# Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # ============================================
    # 1. ADSPOWER
    # ============================================
    print_header("1️⃣  ADSPOWER - Anti-Detect Browser")
    
    print("📋 Pasos para obtener tu API Key de AdsPower:")
    print_steps([
        "Abre AdsPower en tu computadora",
        "Click en ⚙️ (Settings) arriba a la derecha",
        "Ve a 'API Settings' o 'Local API'",
        "Asegúrate que 'Enable Local API' esté activado (ON)",
        "Copia tu 'API Key' (botón Generate si no existe)"
    ])
    
    # API URL
    default_url = "http://local.adspower.net:50325"
    adspower_url = input(f"URL de AdsPower [{default_url}]: ").strip()
    if not adspower_url:
        adspower_url = default_url
    
    # API Key
    adspower_key = input("API Key de AdsPower: ").strip()
    
    if not adspower_key:
        print("⚠️  API Key no proporcionada. Deberás configurarla después en .env")
        print("   El sistema no funcionará sin esta API Key.\n")
    else:
        # Test AdsPower
        print("\n🔍 Probando conexión con AdsPower...")
        try:
            response = requests.get(
                f"{adspower_url}/api/v1/user/list",
                params={'api_key': adspower_key, 'page': 1, 'page_size': 1},
                timeout=10
            )
            result = response.json()
            
            if result.get('code') == 0:
                print("✅ AdsPower conectado correctamente!")
                print(f"   Total de perfiles existentes: {result['data']['total']}")
            else:
                print(f"❌ Error: {result.get('msg')}")
                print("   ⚠️  Verifica tu API Key en AdsPower → Settings → API Settings")
                
        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar a AdsPower")
            print("   ⚠️  Asegúrate de que AdsPower esté abierto y corriendo")
        except Exception as e:
            print(f"⚠️  Error al probar: {e}")
    
    set_key(env_file, "ADSPOWER_API_URL", adspower_url)
    set_key(env_file, "ADSPOWER_API_KEY", adspower_key)
    
   # setup_credentials.py - SECCIÓN SOAX CORREGIDA

    # ============================================
    # 2. SOAX
    # ============================================
    print_header("2️⃣  SOAX - Servicio de Proxies")

    print("📋 Pasos para obtener credenciales SOAX:")
    print_steps([
        "Ve a tu dashboard de SOAX",
        "Click en 'Generate new Proxy node (IP)'",
        "Selecciona 'Login & password'",
        "Copia el 'Login' (ej: package-325126-ses)",
        "Copia el 'Password'",
        "Anota el 'Port' (usualmente 5000)"
    ])

    print("\n💡 FORMATO CORRECTO DE SOAX 2024:")
    print("   Login: package-XXXXXX-ses (es el username BASE)")
    print("   Password: tu_password")
    print("   Server: proxy.soax.com")
    print("   Port: 5000 (o el que muestre tu dashboard)\n")

    soax_username = input("SOAX Login (username BASE): ").strip()
    soax_password = input("SOAX Password: ").strip()
    soax_port = input("SOAX Port [5000]: ").strip() or "5000"

    if soax_username and soax_password:
        set_key(env_file, "SOAX_USERNAME", soax_username)
        set_key(env_file, "SOAX_PASSWORD", soax_password)
        set_key(env_file, "SOAX_PROXY_HOST", "proxy.soax.com")
        set_key(env_file, "SOAX_PROXY_PORT", soax_port)
        
        # Test SOAX
        print("\n🔍 Probando proxy SOAX...")
        print("   (Esto puede tardar 20-30 segundos...)")
        
        # Probar con diferentes protocolos
        test_configs = [
            ('http', f"http://{soax_username}:{soax_password}@proxy.soax.com:{soax_port}"),
            ('https', f"https://{soax_username}:{soax_password}@proxy.soax.com:{soax_port}"),
        ]
        
        success = False
        for protocol, proxy_url in test_configs:
            print(f"\n   Probando con {protocol.upper()}...")
            try:
                response = requests.get(
                    'https://api.ipify.org?format=json',
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=25,
                    verify=False
                )
                ip_data = response.json()
                print(f"   ✅ Funciona con {protocol.upper()}!")
                print(f"   IP obtenida: {ip_data['ip']}")
                success = True
                
                # Verificar ubicación
                try:
                    response = requests.get(
                        'http://ip-api.com/json/',
                        proxies={'http': proxy_url, 'https': proxy_url},
                        timeout=20,
                        verify=False
                    )
                    location = response.json()
                    print(f"   País: {location.get('country', 'N/A')}")
                    print(f"   Ciudad: {location.get('city', 'N/A')}")
                    print(f"   ISP: {location.get('isp', 'N/A')}")
                except:
                    pass
                
                break  # Si funciona, no probar más
                
            except Exception as e:
                print(f"   ❌ No funciona con {protocol.upper()}: {str(e)[:80]}")
        
        if not success:
            print("\n❌ Error probando SOAX")
            print("   ⚠️  Posibles causas:")
            print("   1. Credenciales incorrectas")
            print("   2. Sin saldo/créditos en cuenta SOAX")
            print("   3. Proxy bloqueado en tu red")
            print("   4. Puerto incorrecto (verifica en dashboard)")
    else:
        print("⚠️  Credenciales SOAX no proporcionadas")
    
    # ============================================
    # 3. 3X-UI (OPCIONAL)
    # ============================================
    print_header("3️⃣  3X-UI - Panel VPN (OPCIONAL)")
    
    print("3x-ui es OPCIONAL. Solo necesario si tienes tu propio servidor VPN.")
    print("Si solo usas SOAX, puedes omitir esta sección.\n")
    
    use_3xui = input("¿Deseas configurar 3x-ui? (s/n) [n]: ").strip().lower()
    
    if use_3xui == 's':
        print("\n📋 Necesitarás:")
        print_steps([
            "Un servidor VPS con 3x-ui instalado",
            "La URL del panel (ej: http://tu-ip:2053)",
            "Usuario y contraseña del panel",
            "ID del Inbound que deseas usar"
        ])
        
        threexui_url = input("URL del panel 3x-ui: ").strip()
        threexui_user = input("Usuario 3x-ui [admin]: ").strip() or "admin"
        threexui_pass = input("Password 3x-ui: ").strip()
        threexui_inbound = input("Inbound ID [1]: ").strip() or "1"
        
        set_key(env_file, "USE_3XUI", "true")
        set_key(env_file, "THREEXUI_PANEL_URL", threexui_url)
        set_key(env_file, "THREEXUI_USERNAME", threexui_user)
        set_key(env_file, "THREEXUI_PASSWORD", threexui_pass)
        set_key(env_file, "THREEXUI_INBOUND_ID", threexui_inbound)
        
        print("\n✅ 3x-ui configurado")
    else:
        set_key(env_file, "USE_3XUI", "false")
        print("\n⏭️  3x-ui omitido (usando solo SOAX)")
    
    # ============================================
    # 4. CONFIGURACIÓN REGIONAL
    # ============================================
    print_header("4️⃣  CONFIGURACIÓN REGIONAL")
    
    print("Configuración por defecto para los perfiles:")
    
    country = input("País (código ISO 2 letras) [ec]: ").strip().lower() or "ec"
    timezone = input("Timezone [America/Guayaquil]: ").strip() or "America/Guayaquil"
    language = input("Idioma [es-EC]: ").strip() or "es-EC"
    
    set_key(env_file, "DEFAULT_COUNTRY", country)
    set_key(env_file, "DEFAULT_TIMEZONE", timezone)
    set_key(env_file, "DEFAULT_LANGUAGE", language)
    
    # ============================================
    # 5. CONFIGURACIÓN DE WARMUP
    # ============================================
    print_header("5️⃣  CONFIGURACIÓN DE WARMUP")
    
    print("Configuración para el precalentamiento de perfiles:\n")
    
    warmup_min = input("Duración mínima de warmup en minutos [30]: ").strip() or "30"
    warmup_max = input("Duración máxima de warmup en minutos [60]: ").strip() or "60"
    sites_min = input("Mínimo de sitios a visitar [8]: ").strip() or "8"
    sites_max = input("Máximo de sitios a visitar [15]: ").strip() or "15"
    
    set_key(env_file, "WARMUP_MIN_DURATION", warmup_min)
    set_key(env_file, "WARMUP_MAX_DURATION", warmup_max)
    set_key(env_file, "WARMUP_MIN_SITES", sites_min)
    set_key(env_file, "WARMUP_MAX_SITES", sites_max)
    
    # ============================================
    # RESUMEN FINAL
    # ============================================
    print_header("✅ CONFIGURACIÓN COMPLETADA")
    
    print(f"📁 Archivo guardado en: {os.path.abspath(env_file)}\n")
    
    print("📋 Resumen de configuración:\n")
    print(f"   AdsPower:")
    print(f"     • URL: {adspower_url}")
    print(f"     • API Key: {'✅ Configurada' if adspower_key else '❌ No configurada'}")
    print(f"\n   SOAX:")
    print(f"     • Username: {soax_username if soax_username else '❌ No configurado'}")
    print(f"     • Status: {'✅ Configurado' if soax_username else '❌ No configurado'}")
    print(f"\n   3x-ui:")
    print(f"     • Habilitado: {'Sí' if use_3xui == 's' else 'No'}")
    print(f"\n   Regional:")
    print(f"     • País: {country.upper()}")
    print(f"     • Timezone: {timezone}")
    print(f"     • Idioma: {language}")
    print(f"\n   Warmup:")
    print(f"     • Duración: {warmup_min}-{warmup_max} minutos")
    print(f"     • Sitios: {sites_min}-{sites_max}")
    
    print("\n" + "=" * 70)
    
    # Verificar si puede continuar
    if not adspower_key or not soax_username:
        print("\n⚠️  ADVERTENCIA: Faltan credenciales críticas")
        print("   Debes editar el archivo .env antes de usar el sistema.")
        print("\n   Credenciales faltantes:")
        if not adspower_key:
            print("   • ADSPOWER_API_KEY")
        if not soax_username:
            print("   • SOAX_USERNAME y SOAX_PASSWORD")
    else:
        print("\n🚀 Sistema listo para usar!")
        print("\n   Ejecuta el sistema principal con:")
        print("   python main.py")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        from datetime import datetime
        setup_wizard()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error en la configuración: {e}")
        sys.exit(1)