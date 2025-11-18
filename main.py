# main.py
import sys
import os
from credentials_manager import CredentialsManager
from adspower_manager import AdsPowerManager
from proxy_manager import SOAXProxyManager, ThreeXUIManager
from account_creator import AccountCreator
from utils import (
    setup_directories, setup_logging, print_header, print_section,
    get_user_input, get_yes_no, clear_screen, print_success, 
    print_error, print_info, print_warning
)
import logging

logger = None

def initialize_system():
    """Inicializa el sistema completo"""
    global logger
    
    # Crear directorios necesarios
    setup_directories()
    
    # Configurar logging
    logger = setup_logging()
    
    print_header("🚀 SISTEMA DE CREACIÓN DE CUENTAS HUMANIZADAS")
    print("Sistema profesional para crear perfiles de navegador humanizados")
    print("con AdsPower, SOAX y precalentamiento automático.\n")
    
    # Cargar credenciales
    print_section("Cargando configuración")
    try:
        creds = CredentialsManager()
        print_success("Credenciales cargadas correctamente")
    except ValueError as e:
        print_error("Error cargando credenciales")
        print(str(e))
        print("\n💡 Ejecuta primero: python setup_credentials.py")
        sys.exit(1)
    
    # Inicializar AdsPower
    print_info("Conectando con AdsPower...")
    try:
        adspower = AdsPowerManager(
            api_url=creds.adspower_url,
            api_key=creds.adspower_api_key
        )
    except Exception as e:
        print_error(f"No se pudo conectar con AdsPower: {e}")
        sys.exit(1)
    
    # Inicializar SOAX
    print_info("Configurando gestor de proxies SOAX...")
    proxy_manager = SOAXProxyManager(
        username=creds.soax_username,
        password=creds.soax_password,
        host=creds.soax_host,
        port=creds.soax_port
    )
    
    # Inicializar 3x-ui si está habilitado
    threexui = None
    if creds.use_3xui:
        print_info("Conectando con 3x-ui...")
        try:
            threexui = ThreeXUIManager(
                panel_url=creds.threexui_panel_url,
                username=creds.threexui_username,
                password=creds.threexui_password,
                inbound_id=creds.threexui_inbound_id
            )
        except Exception as e:
            print_warning(f"No se pudo conectar con 3x-ui: {e}")
    
    # Crear account creator
    creator = AccountCreator(adspower, proxy_manager, threexui)
    
    print_success("Sistema inicializado correctamente\n")
    
    return creator, creds

def show_main_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 70)
    print("MENÚ PRINCIPAL".center(70))
    print("=" * 70)
    print("\n1. Crear un solo perfil")
    print("2. Crear múltiples perfiles")
    print("3. Precalentar perfil existente")
    print("4. Ver perfiles existentes")
    print("5. Eliminar perfiles")
    print("6. Salir")
    print("\n" + "=" * 70)

def create_single_profile(creator: AccountCreator, creds: CredentialsManager):
    """Flujo para crear un solo perfil"""
    clear_screen()
    print_header("CREAR PERFIL INDIVIDUAL")
    
    # Seleccionar tipo de proxy
    print("Tipo de proxy:")
    print("1. Residential (Desktop)")
    print("2. Mobile (Móvil)")
    
    proxy_choice = get_user_input("Selecciona una opción", default="1", input_type=int)
    proxy_type = 'mobile' if proxy_choice == 2 else 'residential'
    
    print_info(f"Tipo seleccionado: {proxy_type.upper()}")
    
    # País
    country = get_user_input("Código de país", default=creds.default_country)
    
    # Ciudad
    print("\nCiudades disponibles en Ecuador:")
    print("  - Quito (Pichincha)")
    print("  - Guayaquil (Guayas)")
    print("  - Cuenca (Azuay)")
    print("  - Machala (El Oro)")
    print("  - Ambato (Tungurahua)")
    print("  - Loja (Loja)")
    
    city = input("Ciudad (Enter para aleatorio): ").strip() or None
    
    # Región (opcional, se calculará automáticamente de la ciudad)
    region = None
    
    # Warmup
    do_warmup = get_yes_no("¿Precalentar el perfil?", default=True)
    
    warmup_type = 'basic'
    warmup_duration = 30
    
    if do_warmup:
        print("\nTipo de precalentamiento:")
        print("1. Básico (navegación simple, 30 min)")
        print("2. Avanzado (búsquedas + redes sociales, 60 min)")
        
        warmup_choice = get_user_input("Selecciona una opción", default="1", input_type=int)
        
        if warmup_choice == 2:
            warmup_type = 'advanced'
            warmup_duration = 60
        
        custom_duration = input(f"Duración en minutos [{warmup_duration}]: ").strip()
        if custom_duration:
            try:
                warmup_duration = int(custom_duration)
            except:
                pass
    
    # Confirmación
    print("\n" + "-" * 70)
    print("RESUMEN:")
    print(f"  • Tipo de proxy: {proxy_type.upper()}")
    print(f"  • País: {country.upper()}")
    if city:
        print(f"  • Ciudad: {city.title()}")
    print(f"  • Warmup: {'Sí' if do_warmup else 'No'}")
    if do_warmup:
        print(f"  • Tipo warmup: {warmup_type.upper()}")
        print(f"  • Duración: {warmup_duration} minutos")
    print("-" * 70)
    
    if not get_yes_no("\n¿Proceder con la creación?", default=True):
        print_info("Operación cancelada")
        return
    
    # Crear perfil
    print()
    result = creator.create_single_profile(
        proxy_type=proxy_type,
        country=country,
        city=city,
        region=region,  # Se calculará automáticamente
        warmup=do_warmup,
        warmup_type=warmup_type,
        warmup_duration=warmup_duration
    )
    
    if result['success']:
        print_success(f"\n✨ Perfil creado exitosamente: {result['profile_id']}")
    else:
        print_error(f"\n❌ Error: {result['error']}")
    
    input("\nPresiona Enter para continuar...")
    
def create_multiple_profiles(creator: AccountCreator, creds: CredentialsManager):
    """Flujo para crear múltiples perfiles"""
    clear_screen()
    print_header("CREAR MÚLTIPLES PERFILES")
    
    # Número de perfiles
    count = get_user_input("¿Cuántos perfiles deseas crear?", default=5, input_type=int)
    
    if count < 1 or count > 50:
        print_error("El número debe estar entre 1 y 50")
        input("\nPresiona Enter para continuar...")
        return
    
    # Tipo de proxy
    print("\nTipo de proxy:")
    print("1. Residential (Desktop)")
    print("2. Mobile (Móvil)")
    
    proxy_choice = get_user_input("Selecciona una opción", default="1", input_type=int)
    proxy_type = 'mobile' if proxy_choice == 2 else 'residential'
    
    # País
    country = get_user_input("Código de país", default=creds.default_country)
    
    # Warmup
    do_warmup = get_yes_no("¿Precalentar los perfiles?", default=True)
    
    warmup_type = 'basic'
    warmup_duration = 30
    
    if do_warmup:
        print("\nTipo de precalentamiento:")
        print("1. Básico (más rápido, ~30 min por perfil)")
        print("2. Avanzado (más completo, ~60 min por perfil)")
        
        warmup_choice = get_user_input("Selecciona una opción", default="1", input_type=int)
        
        if warmup_choice == 2:
            warmup_type = 'advanced'
            warmup_duration = 60
    
    # Delay entre creaciones
    print("\nDelay entre creaciones (para evitar detección):")
    min_delay = get_user_input("Delay mínimo en segundos", default=60, input_type=int)
    max_delay = get_user_input("Delay máximo en segundos", default=180, input_type=int)
    
    # Resumen y confirmación
    estimated_time = count * (warmup_duration + (min_delay + max_delay) / 2 / 60)
    
    print("\n" + "-" * 70)
    print("RESUMEN:")
    print(f"  • Perfiles a crear: {count}")
    print(f"  • Tipo de proxy: {proxy_type.upper()}")
    print(f"  • País: {country.upper()}")
    print(f"  • Warmup: {'Sí' if do_warmup else 'No'}")
    if do_warmup:
        print(f"  • Tipo warmup: {warmup_type.upper()}")
        print(f"  • Duración por perfil: {warmup_duration} min")
    print(f"  • Delay entre perfiles: {min_delay}-{max_delay}s")
    print(f"  • Tiempo estimado total: ~{int(estimated_time)} minutos")
    print("-" * 70)
    
    if not get_yes_no("\n¿Proceder con la creación masiva?", default=True):
        print_info("Operación cancelada")
        return
    
    # Crear perfiles
    print()
    result = creator.create_multiple_profiles(
        count=count,
        proxy_type=proxy_type,
        country=country,
        warmup=do_warmup,
        warmup_type=warmup_type,
        warmup_duration=warmup_duration,
        delay_between=(min_delay, max_delay)
    )
    
    print_success(f"\n✨ Proceso completado: {result['successful']}/{result['total']} exitosos")
    
    input("\nPresiona Enter para continuar...")

def warm_existing_profile(creator: AccountCreator):
    """Flujo para precalentar un perfil existente"""
    clear_screen()
    print_header("PRECALENTAR PERFIL EXISTENTE")
    
    profile_id = input("ID del perfil a precalentar: ").strip()
    
    if not profile_id:
        print_error("ID de perfil requerido")
        input("\nPresiona Enter para continuar...")
        return
    
    # Tipo de warmup
    print("\nTipo de precalentamiento:")
    print("1. Básico (navegación simple, ~30 min)")
    print("2. Avanzado (búsquedas + redes sociales, ~60 min)")
    
    warmup_choice = get_user_input("Selecciona una opción", default="1", input_type=int)
    
    warmup_type = 'advanced' if warmup_choice == 2 else 'basic'
    warmup_duration = 60 if warmup_choice == 2 else 30
    
    # Personalizar duración
    custom_duration = input(f"Duración en minutos [{warmup_duration}]: ").strip()
    if custom_duration:
        try:
            warmup_duration = int(custom_duration)
        except:
            pass
    
    print()
    result = creator.warm_existing_profile(
        profile_id=profile_id,
        warmup_type=warmup_type,
        warmup_duration=warmup_duration
    )
    
    if result['success']:
        print_success("\n✨ Precalentamiento completado")
    else:
        print_error(f"\n❌ Error: {result['error']}")
    
    input("\nPresiona Enter para continuar...")

def view_existing_profiles(creator: AccountCreator):
    """Muestra perfiles existentes"""
    clear_screen()
    print_header("PERFILES EXISTENTES")
    
    try:
        profiles = creator.adspower.get_profile_list(page=1, page_size=50)
        
        if not profiles:
            print_info("No hay perfiles creados aún")
        else:
            print(f"Total de perfiles: {len(profiles)}\n")
            print("-" * 70)
            
            for i, profile in enumerate(profiles, 1):
                print(f"\n{i}. {profile['name']}")
                print(f"   ID: {profile['serial_number']}")
                print(f"   Grupo: {profile.get('group_name', 'Sin grupo')}")
                print(f"   Última modificación: {profile.get('last_open_time', 'N/A')}")
            
            print("\n" + "-" * 70)
    
    except Exception as e:
        print_error(f"Error obteniendo perfiles: {e}")
    
    input("\nPresiona Enter para continuar...")

def delete_profiles(creator: AccountCreator):
    """Elimina perfiles"""
    clear_screen()
    print_header("ELIMINAR PERFILES")
    
    print_warning("⚠️  Esta acción es irreversible")
    
    profile_ids = input("\nIDs de perfiles a eliminar (separados por coma): ").strip()
    
    if not profile_ids:
        print_info("Operación cancelada")
        input("\nPresiona Enter para continuar...")
        return
    
    ids_list = [pid.strip() for pid in profile_ids.split(',')]
    
    print(f"\nSe eliminarán {len(ids_list)} perfil(es)")
    
    if not get_yes_no("¿Estás seguro?", default=False):
        print_info("Operación cancelada")
        input("\nPresiona Enter para continuar...")
        return
    
    try:
        creator.adspower.delete_profile(ids_list)
        print_success(f"✨ {len(ids_list)} perfil(es) eliminado(s)")
    except Exception as e:
        print_error(f"Error eliminando perfiles: {e}")
    
    input("\nPresiona Enter para continuar...")

def main():
    """Función principal"""
    try:
        # Inicializar sistema
        creator, creds = initialize_system()
        
        # Loop del menú
        while True:
            clear_screen()
            show_main_menu()
            
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '1':
                create_single_profile(creator, creds)
            elif choice == '2':
                create_multiple_profiles(creator, creds)
            elif choice == '3':
                warm_existing_profile(creator)
            elif choice == '4':
                view_existing_profiles(creator)
            elif choice == '5':
                delete_profiles(creator)
            elif choice == '6':
                print_info("\n👋 Saliendo del sistema...")
                sys.exit(0)
            else:
                print_warning("\nOpción inválida")
                input("Presiona Enter para continuar...")
    
    except KeyboardInterrupt:
        print_info("\n\n👋 Sistema interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n❌ Error crítico: {e}")
        logger.exception("Error crítico en el sistema")
        sys.exit(1)

if __name__ == "__main__":
    main()