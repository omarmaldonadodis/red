## account_creator.py - LIMPIO (AdsPower + SOAX directo)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from adspower_manager import AdsPowerManager
from proxy_manager import SOAXProxyManager
from profile_warmer import ProfileWarmer
from config import ProfileGenerator
from typing import Dict, Optional
import time
import random
import logging
from datetime import datetime
from utils import save_profile_data, print_success, print_error, print_info

logger = logging.getLogger(__name__)

class AccountCreator:
    """Orquestador principal para crear y humanizar cuentas"""
    
    def __init__(self, adspower_manager: AdsPowerManager, proxy_manager: SOAXProxyManager):
        """
        Inicializa el creador de cuentas
        
        Args:
            adspower_manager: Gestor de AdsPower
            proxy_manager: Gestor de proxies SOAX
        """
        self.adspower = adspower_manager
        self.proxy_manager = proxy_manager
    
    def create_single_profile(self,
                            proxy_type: str = 'mobile',
                            country: str = 'ec',
                            city: Optional[str] = None,
                            region: Optional[str] = None,
                            warmup: bool = True,
                            warmup_type: str = 'basic',
                            warmup_duration: int = 20) -> Dict:
        """
        Crea un solo perfil completo y humanizado
        
        Args:
            proxy_type: 'mobile' o 'residential'
            country: Código de país
            city: Ciudad específica (opcional)
            region: Región específica (opcional)
            warmup: Si se debe precalentar
            warmup_type: Tipo de warmup ('basic' o 'advanced')
            warmup_duration: Duración del warmup en minutos
        
        Returns:
            Dict con resultado de la creación
        """
        logger.info("=" * 70)
        logger.info("CREANDO NUEVO PERFIL")
        logger.info("=" * 70)
        
        result = {
            'success': False,
            'profile_id': None,
            'profile_data': None,
            'warmup_stats': None,
            'error': None
        }
        
        try:
            # ==================================================
            # PASO 0: NORMALIZAR CIUDAD Y REGIÓN
            # ==================================================
            city_to_region_map = {
                'quito': 'pichincha',
                'guayaquil': 'guayas',
                'cuenca': 'azuay',
                'santo domingo': 'santo-domingo-de-los-tsachilas',
                'machala': 'el-oro',
                'ambato': 'tungurahua',
                'portoviejo': 'manabi',
                'loja': 'loja'
            }
            
            if city:
                city_normalized = city.lower().strip()
                if not region and city_normalized in city_to_region_map:
                    region = city_to_region_map[city_normalized]
            else:
                city_normalized = None
            
            # ==================================================
            # PASO 1: GENERAR PERFIL
            # ==================================================
            print_info(f"Paso 1/4: Generando perfil {proxy_type.upper()}...")

            profile_config = ProfileGenerator.generate_profile(proxy_type=proxy_type)

            # Sobrescribir ciudad si se especificó
            if city_normalized:
                city_display = city.title()
                profile_config.city = city_display
                
                ecuadorian_cities = {
                    'Quito': {'timezone': 'America/Guayaquil'},
                    'Guayaquil': {'timezone': 'America/Guayaquil'},
                    'Cuenca': {'timezone': 'America/Guayaquil'},
                    'Santo Domingo': {'timezone': 'America/Guayaquil'},
                    'Machala': {'timezone': 'America/Guayaquil'},
                    'Ambato': {'timezone': 'America/Guayaquil'},
                    'Portoviejo': {'timezone': 'America/Guayaquil'},
                    'Loja': {'timezone': 'America/Guayaquil'}
                }
                
                if city_display in ecuadorian_cities:
                    profile_config.timezone = ecuadorian_cities[city_display]['timezone']
            else:
                city_normalized = profile_config.city.lower()
                city_display = profile_config.city
                
                if not region and city_normalized in city_to_region_map:
                    region = city_to_region_map[city_normalized]

            # ==========================================
            # LOGGING DETALLADO DEL PERFIL
            # ==========================================
            logger.info(f"Perfil generado:")
            logger.info(f"  Nombre: {profile_config.name}")
            logger.info(f"  Edad: {profile_config.age}")
            logger.info(f"  Ciudad: {city_display}")
            logger.info(f"  Región: {region or 'No especificada'}")
            logger.info(f"  Dispositivo: {profile_config.device_type}")
            logger.info(f"  Tipo Proxy: {proxy_type}")

            # ==========================================
            # LOGGING DE FINGERPRINTS MÓVILES
            # ==========================================
            if profile_config.device_type == 'mobile':
                logger.info(f"\n📱 FINGERPRINTS MÓVILES:")
                logger.info(f"  ├─ Dispositivo: {profile_config.device_name}")
                logger.info(f"  ├─ Resolución: {profile_config.screen_resolution}")
                logger.info(f"  ├─ Viewport: {profile_config.viewport}")
                logger.info(f"  ├─ Pixel Ratio: {profile_config.pixel_ratio}x")
                logger.info(f"  ├─ CPU Cores: {profile_config.hardware_concurrency}")
                logger.info(f"  ├─ RAM: {profile_config.device_memory}GB")
                logger.info(f"  ├─ Touch Points: {profile_config.max_touch_points}")
                logger.info(f"  ├─ Platform: {profile_config.platform}")
                logger.info(f"  ├─ Renderer: {profile_config.renderer}")
                logger.info(f"  └─ User Agent: {profile_config.user_agent[:80]}...")
            else:
                logger.info(f"  User Agent: {profile_config.user_agent[:80]}...")

            logger.info(f"  Intereses: {', '.join(profile_config.interests)}")
                        
            # ==================================================
            # PASO 2: CONFIGURAR PROXY SOAX
            # ==================================================
            print_info(f"Paso 2/4: Configurando proxy SOAX {proxy_type.upper()} para {city_display}...")
            
            proxy_config = self.proxy_manager.get_proxy_config(
                proxy_type=proxy_type,
                country=country,
                city=city_normalized,
                region=region,
                sticky_session=True,
                session_lifetime=3600,
            )
            
            # Probar proxy
            print_info("Probando conexión del proxy...")
            proxy_test = self.proxy_manager.test_proxy(proxy_config, timeout=20)
            
            if not proxy_test['success']:
                raise Exception(f"Proxy no funciona: {proxy_test['error']}")
            
            logger.info(f"✅ Proxy {proxy_type.upper()} funcionando:")
            logger.info(f"  IP: {proxy_test['ip']}")
            logger.info(f"  País: {proxy_test['country']}")
            logger.info(f"  Ciudad: {proxy_test['city']}")
            logger.info(f"  ISP: {proxy_test['isp']}")
            logger.info(f"  Tipo: {proxy_test['connection_type']}")
            
            # ==================================================
            # PASO 3: CREAR PERFIL EN ADSPOWER
            # ==================================================
            print_info("Paso 3/4: Creando perfil en AdsPower...")
            
            profile_id = self.adspower.create_profile(
                profile_config=profile_config,
                proxy_config=proxy_config
            )
            
            result['profile_id'] = profile_id
            
            # Guardar datos del perfil
            profile_data = {
                'profile_id': profile_id,
                'profile_config': profile_config.to_dict(),
                'proxy_config': {
                    'type': proxy_config['proxy_type'],
                    'session_id': proxy_config['session_id'],
                    'country': country,
                    'city': city_display,
                    'region': region
                },
                'proxy_test': proxy_test,
                'created_at': datetime.now().isoformat(),
                'warmup_completed': False
            }
            
            result['profile_data'] = profile_data
            
            # ==================================================
            # PASO 4: PRECALENTAR PERFIL (OPCIONAL)
            # ==================================================
            if warmup:
                print_info(f"Paso 4/4: Precalentando perfil ({warmup_type})...")
                
                warmer = ProfileWarmer(self.adspower, profile_config)
                
                if not warmer.connect_to_browser(profile_id):
                    raise Exception("No se pudo conectar al navegador")
                
                try:
                    if warmup_type == 'advanced':
                        warmup_stats = warmer.warm_profile_advanced(
                            duration_minutes=warmup_duration,
                            include_searches=True,
                            include_social=True
                        )
                    else:
                        warmup_stats = warmer.warm_profile_basic(
                            duration_minutes=warmup_duration
                        )
                    
                    result['warmup_stats'] = warmup_stats
                    profile_data['warmup_completed'] = True
                    profile_data['warmup_stats'] = warmup_stats
                    
                    print_success("Precalentamiento completado")
                    
                finally:
                    warmer.disconnect(profile_id)
            else:
                print_info("Paso 4/4: Omitiendo precalentamiento")
            
            # Guardar datos completos
            save_profile_data(profile_id, profile_data)
            
            result['success'] = True
            
            # Resumen final
            logger.info("=" * 70)
            logger.info("✅ PERFIL CREADO EXITOSAMENTE")
            logger.info("=" * 70)
            logger.info(f"ID: {profile_id}")
            logger.info(f"Nombre: {profile_config.name}")
            logger.info(f"Ciudad: {city_display}")
            logger.info(f"Región: {region or 'N/A'}")
            logger.info(f"Tipo: {profile_config.device_type.upper()} ({proxy_type})")
            logger.info(f"Warmup: {'Sí' if warmup else 'No'}")
            if warmup and result['warmup_stats']:
                logger.info(f"Sitios visitados: {result['warmup_stats'].get('sites_visited', 0)}")
                logger.info(f"Tiempo total: {result['warmup_stats'].get('total_time', 0)}s")
            logger.info("=" * 70)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creando perfil: {e}")
            result['error'] = str(e)
            
            # Limpiar si hubo error
            if result['profile_id']:
                try:
                    logger.info("Limpiando perfil fallido...")
                    self.adspower.delete_profile([result['profile_id']])
                except:
                    pass
            
            return result
    
    def create_multiple_profiles(self,
                                 count: int,
                                 proxy_type: str = 'mobile',
                                 country: str = 'ec',
                                 warmup: bool = True,
                                 warmup_type: str = 'basic',
                                 warmup_duration: int = 20,
                                 delay_between: tuple = (60, 180)) -> Dict:
        """Crea múltiples perfiles"""
        logger.info("=" * 70)
        logger.info(f"CREACIÓN MASIVA DE PERFILES: {count} perfiles")
        logger.info("=" * 70)
        
        results = {
            'total': count,
            'successful': 0,
            'failed': 0,
            'profiles': [],
            'errors': []
        }
        
        start_time = time.time()
        
        for i in range(count):
            logger.info(f"\n>>> Creando perfil {i+1}/{count}...")
            
            result = self.create_single_profile(
                proxy_type=proxy_type,
                country=country,
                warmup=warmup,
                warmup_type=warmup_type,
                warmup_duration=warmup_duration
            )
            
            if result['success']:
                results['successful'] += 1
                results['profiles'].append({
                    'profile_id': result['profile_id'],
                    'name': result['profile_data']['profile_config']['name']
                })
            else:
                results['failed'] += 1
                results['errors'].append({
                    'index': i+1,
                    'error': result['error']
                })
            
            # Delay entre creaciones
            if i < count - 1:
                delay = random.randint(delay_between[0], delay_between[1])
                logger.info(f"⏱️  Esperando {delay}s antes del siguiente perfil...")
                time.sleep(delay)
        
        total_time = int(time.time() - start_time)
        results['total_time'] = total_time
        
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE CREACIÓN MASIVA")
        logger.info("=" * 70)
        logger.info(f"Total: {results['total']}")
        logger.info(f"Exitosos: {results['successful']}")
        logger.info(f"Fallidos: {results['failed']}")
        logger.info(f"Tiempo total: {total_time}s ({total_time//60}m {total_time%60}s)")
        logger.info("=" * 70)
        
        return results