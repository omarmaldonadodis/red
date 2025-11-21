# main_advanced.py - Sistema Completo con Control Total
import sys
from credentials_manager import CredentialsManager
from adspower_manager import AdsPowerManager
from proxy_manager import SOAXProxyManager
from account_creator import AccountCreator
from advanced_account_creator import AdvancedAccountCreator, ProfileRequest, get_interest_websites
from mobile_devices import list_devices_menu, get_all_device_ids, MOBILE_DEVICES
from utils import *
import logging

logger = None

def initialize_system():
    """Inicializa el sistema completo"""
    global logger
    
    setup_directories()
    os.makedirs('profiles/warmup_reports', exist_ok=True)
    logger = setup_logging()
    
    print_header("🚀 SISTEMA AVANZADO DE CREACIÓN DE PERFILES MÓVILES")
    print("Control total sobre nombres, dispositivos, intereses y warmup\n")
    
    # Cargar credenciales
    print("📋 Cargando configuración...")
    try:
        creds = CredentialsManager()
        print_success("Credenciales cargadas")
    except ValueError as e:
        print_error("Error cargando credenciales")
        print(str(e))
        sys.exit(1)
    
    # Inicializar componentes
    print_info("Conectando con AdsPower...")
    adspower = AdsPowerManager(
        api_url=creds.adspower_url,
        api_key=creds.adspower_api_key
    )
    
    print_info("Configurando gestor de proxies SOAX...")
    proxy_manager = SOAXProxyManager(
        username=creds.soax_username,
        password=creds.soax_password,
        host=creds.soax_host,
        port=creds.soax_port
    )
    
    # Crear account creator
    base_creator = AccountCreator(adspower, proxy_manager)
    advanced_creator = AdvancedAccountCreator(base_creator)
    
    print_success("Sistema inicializado\n")
    
    return advanced_creator, creds

def show_main_menu():
    """Muestra el menú principal avanzado"""
    print("\n" + "=" * 70)
    print("MENÚ PRINCIPAL - CONTROL AVANZADO".center(70))
    print("=" * 70)
    print("\n📱 CREACIÓN INDIVIDUAL:")
    print("  1. Crear perfil MÓVIL con control total")
    print("  2. Crear perfil RESIDENTIAL (desktop)")
    print("\n👥 CREACIÓN MASIVA:")
    print("  3. Crear múltiples perfiles en PARALELO")
    print("  4. Crear múltiples perfiles secuenciales")
    print("\n⚙️  CONFIGURACIÓN:")
    print("  5. Ver dispositivos móviles disponibles")
    print("  6. Ver sitios web por intereses")
    print("  7. Ver perfiles existentes")
    print("\n  8. Salir")
    print("\n" + "=" * 70)

def create_mobile_advanced(creator, creds):
    """Crea perfil móvil con control total"""
    clear_screen()
    print_header("📱 CREAR PERFIL MÓVIL - CONTROL TOTAL")
    
    request = ProfileRequest()
    
    # === PASO 1: NOMBRE PERSONALIZADO ===
    print_section("1. NOMBRE DEL PERFIL")
    use_custom_name = get_yes_no("¿Usar nombre personalizado?", default=False)
    if use_custom_name:
        request.custom_name = get_user_input("Nombre completo")
        request.age = get_user_input("Edad", default=25, input_type=int)
        request.gender = get_user_input("Género (male/female)", default="male")
    else:
        print_info("Se generará nombre aleatorio realista")
    
    # === PASO 2: UBICACIÓN ===
    print_section("2. UBICACIÓN")
    print("Ciudades disponibles: Quito, Guayaquil, Cuenca, Machala, Ambato, Loja")
    request.country = get_user_input("País (código ISO)", default="ec")
    request.city = input("Ciudad (Enter = aleatorio): ").strip() or None
    
    # === PASO 3: DISPOSITIVO ===
    print_section("3. DISPOSITIVO MÓVIL")
    
    print("\n¿Deseas ver la lista completa de dispositivos?")
    if get_yes_no("Ver dispositivos", default=False):
        list_devices_menu()
    
    print("\nMarcas rápidas:")
    print("  • Samsung: s24_ultra, s23_ultra, s24_plus, a54")
    print("  • iPhone: iphone_15_pro_max, iphone_15_plus, iphone_14_pro_max")
    print("  • Google: pixel_8_pro, pixel_7_pro")
    print("  • Xiaomi: xiaomi_14_ultra, xiaomi_13_pro")
    print("  • OnePlus: oneplus_12, oneplus_11")
    
    device_choice = input("\nID del dispositivo (Enter = aleatorio): ").strip().lower()
    if device_choice:
        # Validar dispositivo
        if device_choice not in get_all_device_ids():
            print_warning(f"Dispositivo '{device_choice}' no encontrado, usando aleatorio")
            device_choice = None
    
    request.device_id = device_choice if device_choice else None
    request.proxy_type = 'mobile'
    
    # === PASO 4: INTERESES ===
    print_section("4. INTERESES")
    
    available_interests = [
        'social_media', 'messaging', 'mobile_gaming', 'photos',
        'tiktok', 'instagram', 'snapchat', 'music_streaming',
        'news_apps', 'banking', 'shopping', 'food_delivery',
        'ride_sharing', 'fitness_apps', 'family_apps', 'health_apps'
    ]
    
    print("\nIntereses disponibles:")
    for i in range(0, len(available_interests), 4):
        row = available_interests[i:i+4]
        print("  " + ", ".join(row))
    
    use_custom_interests = get_yes_no("\n¿Definir intereses personalizados?", default=False)
    if use_custom_interests:
        print("\nEscribe los intereses separados por comas:")
        interests_input = input("Intereses: ").strip()
        if interests_input:
            request.interests = [i.strip() for i in interests_input.split(',')]
        else:
            print_info("Se generarán intereses aleatorios")
    else:
        print_info("Se generarán intereses aleatorios según edad")
    
    # === PASO 5: WARMUP ===
    print_section("5. PRECALENTAMIENTO (WARMUP)")
    
    request.do_warmup = get_yes_no("¿Precalentar el perfil?", default=True)
    
    if request.do_warmup:
        request.warmup_duration = get_user_input("Duración en minutos", default=20, input_type=int)
        
        # Sitios personalizados
        use_custom_sites = get_yes_no("¿Definir sitios web personalizados?", default=False)
        if use_custom_sites:
            # Mostrar sitios sugeridos
            if request.interests:
                suggested = get_interest_websites(request.interests)
                print(f"\n📋 Sitios sugeridos según tus intereses:")
                for i, site in enumerate(suggested[:10], 1):
                    print(f"   {i}. {site}")
            
            print("\n💡 Puedes agregar tus propios sitios o usar los sugeridos")
            sites_input = input("Sitios (separados por comas, Enter = usar sugeridos): ").strip()
            
            if sites_input:
                request.warmup_sites = [s.strip() for s in sites_input.split(',')]
            elif request.interests:
                request.warmup_sites = get_interest_websites(request.interests)
        
        request.accept_cookies_auto = get_yes_no("¿Auto-aceptar cookies?", default=True)
        request.generate_reports = get_yes_no("¿Generar reportes de velocidad?", default=True)
    
    # === RESUMEN ===
    print("\n" + "=" * 70)
    print("RESUMEN DE CONFIGURACIÓN".center(70))
    print("=" * 70)
    print(f"\n👤 Nombre: {request.custom_name if request.custom_name else 'Aleatorio'}")
    print(f"📍 Ubicación: {request.city if request.city else 'Aleatoria'}, {request.country.upper()}")
    print(f"📱 Dispositivo: {request.device_id if request.device_id else 'Aleatorio'}")
    
    if request.device_id and request.device_id in MOBILE_DEVICES:
        device_info = MOBILE_DEVICES[request.device_id]
        print(f"   └─ {device_info['name']} ({device_info['screen_size']})")
    
    print(f"❤️  Intereses: {', '.join(request.interests[:3]) if request.interests else 'Aleatorios'}")
    print(f"🔥 Warmup: {'Sí' if request.do_warmup else 'No'}")
    if request.do_warmup:
        print(f"   ├─ Duración: {request.warmup_duration} minutos")
        if request.warmup_sites:
            print(f"   ├─ Sitios: {len(request.warmup_sites)} personalizados")
        print(f"   ├─ Auto-cookies: {'Sí' if request.accept_cookies_auto else 'No'}")
        print(f"   └─ Reportes: {'Sí' if request.generate_reports else 'No'}")
    
    print("=" * 70)
    
    if not get_yes_no("\n¿Proceder con la creación?", default=True):
        print_info("Operación cancelada")
        return
    
    # === CREAR PERFIL ===
    print()
    result = creator.create_profile_custom(request)
    
    if result['success']:
        print_success(f"\n✨ Perfil creado exitosamente!")
        print(f"   ID: {result['profile_id']}")
        if result.get('warmup_stats'):
            stats = result['warmup_stats']
            print(f"\n📊 Estadísticas de warmup:")
            print(f"   • Sitios visitados: {stats.get('sites_visited', 0)}")
            print(f"   • Sitios fallidos: {stats.get('sites_failed', 0)}")
            print(f"   • Tiempo total: {stats.get('total_time', 0)}s")
            if stats.get('report'):
                print(f"   • Reporte guardado ✅")
    else:
        print_error(f"\n❌ Error: {result['error']}")
    
    input("\nPresiona Enter para continuar...")

def create_multiple_parallel(creator, creds):
    """Crea múltiples perfiles en paralelo"""
    clear_screen()
    print_header("👥 CREACIÓN MASIVA EN PARALELO")
    
    num_profiles = get_user_input("¿Cuántos perfiles crear?", default=3, input_type=int)
    max_parallel = get_user_input("¿Cuántos en paralelo? (max 5)", default=3, input_type=int)
    max_parallel = min(max_parallel, 5)  # Límite de seguridad
    
    # Configuración común
    print_section("CONFIGURACIÓN COMÚN")
    
    country = get_user_input("País", default="ec")
    proxy_type = 'mobile' if get_yes_no("¿Usar proxies MÓVILES?", default=True) else 'residential'
    
    do_warmup = get_yes_no("¿Precalentar perfiles?", default=True)
    warmup_duration = 15
    if do_warmup:
        warmup_duration = get_user_input("Duración warmup (minutos)", default=15, input_type=int)
    
    # Crear requests
    requests = []
    for i in range(num_profiles):
        req = ProfileRequest(
            country=country,
            proxy_type=proxy_type,
            do_warmup=do_warmup,
            warmup_duration=warmup_duration,
            accept_cookies_auto=True,
            generate_reports=True
        )
        requests.append(req)
    
    print(f"\n📋 Se crearán {num_profiles} perfiles")
    print(f"   • Tipo: {proxy_type.upper()}")
    print(f"   • En paralelo: {max_parallel}")
    print(f"   • Warmup: {'Sí' if do_warmup else 'No'}")
    
    if not get_yes_no("\n¿Proceder?", default=True):
        print_info("Cancelado")
        return
    
    print("\n🚀 Iniciando creación paralela...")
    print("   (Esto puede tardar varios minutos)\n")
    
    results = creator.create_multiple_parallel(requests, max_parallel=max_parallel)
    
    print_success(f"\n✨ Proceso completado!")
    print(f"   • Exitosos: {results['successful']}/{results['total']}")
    print(f"   • Fallidos: {results['failed']}/{results['total']}")
    
    if results['profiles']:
        print("\n📝 Perfiles creados:")
        for p in results['profiles']:
            print(f"   {p['index']}. {p['name']} (ID: {p['profile_id']})")
    
    if results['errors']:
        print("\n❌ Errores:")
        for e in results['errors']:
            print(f"   {e['index']}. {e['error'][:80]}...")
    
    input("\nPresiona Enter para continuar...")

def show_devices(creator, creds):
    """Muestra dispositivos disponibles"""
    clear_screen()
    list_devices_menu()
    input("\nPresiona Enter para continuar...")

def show_interest_sites(creator, creds):
    """Muestra sitios web por intereses"""
    clear_screen()
    print_header("🌐 SITIOS WEB POR INTERESES")
    
    interests = [
        'social_media', 'messaging', 'news_apps', 'banking',
        'shopping', 'technology', 'sports', 'music_streaming'
    ]
    
    print("Selecciona intereses (separados por comas):")
    for i, interest in enumerate(interests, 1):
        print(f"  {i}. {interest}")
    
    selection = input("\nIntereses (ej: 1,3,5): ").strip()
    
    if selection:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected = [interests[i] for i in indices if 0 <= i < len(interests)]
            
            sites = get_interest_websites(selected, lightweight_only=True)
            
            print(f"\n📋 Sitios sugeridos (LIGEROS Y RÁPIDOS):")
            for i, site in enumerate(sites, 1):
                print(f"   {i}. {site}")
            
            print(f"\nTotal: {len(sites)} sitios")
        except:
            print_error("Selección inválida")
    
    input("\nPresiona Enter para continuar...")

def main():
    """Función principal"""
    try:
        creator, creds = initialize_system()
        
        while True:
            clear_screen()
            show_main_menu()
            
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '1':
                create_mobile_advanced(creator, creds)
            elif choice == '3':
                create_multiple_parallel(creator, creds)
            elif choice == '5':
                show_devices(creator, creds)
            elif choice == '6':
                show_interest_sites(creator, creds)
            elif choice == '8':
                print_info("\n👋 Saliendo...")
                sys.exit(0)
            else:
                print_info("\nOpción no implementada aún")
                input("Presiona Enter para continuar...")
    
    except KeyboardInterrupt:
        print_info("\n\n👋 Sistema interrumpido")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n❌ Error: {e}")
        logger.exception("Error crítico")
        sys.exit(1)

if __name__ == "__main__":
    main()