# main.py - SIMPLIFICADO (AdsPower + SOAX)
import sys
import os
from credentials_manager import CredentialsManager
from adspower_manager import AdsPowerManager
from proxy_manager import SOAXProxyManager
from account_creator import AccountCreator
from utils import (
    setup_directories, setup_logging, print_header,
    get_user_input, get_yes_no, clear_screen, 
    print_success, print_error, print_info
)
import logging

logger = None

def initialize_system():
    """Inicializa el sistema completo"""
    global logger
    
    setup_directories()
    logger = setup_logging()
    
    print_header("🚀 SISTEMA DE CREACIÓN DE PERFILES MÓVILES")
    print("Sistema AdsPower + SOAX para perfiles móviles humanizados\n")
    
    # Cargar credenciales
    print("📋 Cargando configuración...")
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
    
    # Crear account creator
    creator = AccountCreator(adspower, proxy_manager)
    
    print_success("Sistema inicializado correctamente\n")
    
    return creator, creds

def show_main_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 70)
    print("MENÚ PRINCIPAL".center(70))
    print("=" * 70)
    print("\n1. Crear un perfil móvil")
    print("2. Crear múltiples perfiles móviles")
    print("3. Crear un perfil residential (desktop)")
    print("4. Ver perfiles existentes")
    print("5. Eliminar perfiles")
    print("6. Salir")
    print("\n" + "=" * 70)

def create_mobile_profile(creator, creds):
    """Crea un perfil móvil"""
    clear_screen()
    print_header("CREAR PERFIL MÓVIL")
    
    # País
    country = get_user_input("Código de país", default=creds.default_country)
    
    # Ciudad
    print("\nCiudades disponibles en Ecuador:")
    print("  - Quito, Guayaquil, Cuenca, Machala, Ambato, Loja")
    city = input("Ciudad (Enter para aleatorio): ").strip() or None
    
    # Warmup
    do_warmup = get_yes_no("¿Precalentar el perfil?", default=True)
    
    warmup_duration = 20
    if do_warmup:
        warmup_duration = get_user_input("Duración en minutos", default=20, input_type=int)
    
    # Confirmación
    print("\n" + "-" * 70)
    print("RESUMEN:")
    print(f"  • Tipo: MÓVIL")
    print(f"  • País: {country.upper()}")
    if city:
        print(f"  • Ciudad: {city.title()}")
    print(f"  • Warmup: {'Sí' if do_warmup else 'No'} ({warmup_duration} min)")
    print("-" * 70)
    
    if not get_yes_no("\n¿Proceder con la creación?", default=True):
        print_info("Operación cancelada")
        return
    
    # Crear perfil
    print()
    result = creator.create_single_profile(
        proxy_type='mobile',
        country=country,
        city=city,
        warmup=do_warmup,
        warmup_duration=warmup_duration
    )
    
    if result['success']:
        print_success(f"\n✨ Perfil móvil creado: {result['profile_id']}")
    else:
        print_error(f"\n❌ Error: {result['error']}")
    
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
                create_mobile_profile(creator, creds)
            elif choice == '6':
                print_info("\n👋 Saliendo del sistema...")
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