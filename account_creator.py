# account_creator.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from adspower_manager import AdsPowerManager
from proxy_manager import SOAXProxyManager, ThreeXUIManager
from profile_warmer import ProfileWarmer
from config import ProfileGenerator, ProfileConfig
from typing import Dict, Optional
import time
import json
import logging
from datetime import datetime
from utils import save_profile_data, print_success, print_error, print_info

logger = logging.getLogger(__name__)

class AccountCreator:
    """Orquestador principal para crear y humanizar cuentas"""
    
    def __init__(self, 
                 adspower_manager: AdsPowerManager,
                 proxy_manager: SOAXProxyManager,
                 threexui_manager: Optional[ThreeXUIManager] = None):
        """
        Inicializa el creador de cuentas
        
        Args:
            adspower_manager: Gestor de AdsPower
            proxy_manager: Gestor de proxies SOAX
            threexui_manager: Gestor de 3x-ui (opcional)
        """
        self.adspower = adspower_manager
        self.proxy_manager = proxy_manager
        self.threexui = threexui_manager
    
    def create_single_profile(self,
                            proxy_type: str = 'residential',
                            country: str = 'ec',
                            city: Optional[str] = None,
                            region: Optional[str] = None,
                            warmup: bool = True,
                            warmup_type: str = 'basic',
                            warmup_duration: int = 30) -> Dict:
        """
        Crea un solo perfil completo y humanizado
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
            # PASO 0: NORMALIZAR CIUDAD Y REGIÓN PRIMERO
            # ==================================================
            
            # Mapeo de ciudad a región (Ecuador)
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
            
            # Si se especificó ciudad, normalizarla
            if city:
                city_normalized = city.lower().strip()
                # Mapear a región automáticamente si no se especificó
                if not region and city_normalized in city_to_region_map:
                    region = city_to_region_map[city_normalized]
            else:
                city_normalized = None
            
            # ==================================================
            # PASO 1: GENERAR PERFIL CON CIUDAD ESPECÍFICA
            # ==================================================
            print_info(f"Paso 1/4: Generando perfil ({proxy_type})...")
            
            # Generar perfil (se generará con ciudad aleatoria si no se especificó)
            profile_config = ProfileGenerator.generate_profile(proxy_type=proxy_type)
            
            # SOBRESCRIBIR la ciudad del perfil si se especificó una
            if city_normalized:
                # Capitalizar para el perfil (Loja, Quito, etc.)
                city_display = city.title()
                profile_config.city = city_display
                
                # Actualizar timezone si es necesario
                # ProfileGenerator ya está importado al inicio del archivo
                ecuadorian_cities = {
                    'Quito': {'timezone': 'America/Guayaquil', 'population': 0.35},
                    'Guayaquil': {'timezone': 'America/Guayaquil', 'population': 0.30},
                    'Cuenca': {'timezone': 'America/Guayaquil', 'population': 0.10},
                    'Santo Domingo': {'timezone': 'America/Guayaquil', 'population': 0.08},
                    'Machala': {'timezone': 'America/Guayaquil', 'population': 0.07},
                    'Ambato': {'timezone': 'America/Guayaquil', 'population': 0.05},
                    'Portoviejo': {'timezone': 'America/Guayaquil', 'population': 0.03},
                    'Loja': {'timezone': 'America/Guayaquil', 'population': 0.02}
                }
                
                if city_display in ecuadorian_cities:
                    profile_config.timezone = ecuadorian_cities[city_display]['timezone']
            else:
                # Usar la ciudad generada aleatoriamente
                city_normalized = profile_config.city.lower()
                city_display = profile_config.city
                
                # Mapear región automáticamente
                if not region and city_normalized in city_to_region_map:
                    region = city_to_region_map[city_normalized]
            
            logger.info(f"Perfil generado:")
            logger.info(f"  Nombre: {profile_config.name}")
            logger.info(f"  Edad: {profile_config.age}")
            logger.info(f"  Ciudad: {city_display}")
            logger.info(f"  Región: {region or 'No especificada'}")
            logger.info(f"  Dispositivo: {profile_config.device_type}")
            logger.info(f"  Intereses: {', '.join(profile_config.interests)}")
            
            # ==================================================
            # PASO 2: CONFIGURAR PROXY CON GEO-TARGETING
            # ==================================================
            print_info(f"Paso 2/4: Configurando proxy {proxy_type.upper()} para {city_display.upper()}, Ecuador...")
            
            proxy_config = self.proxy_manager.get_proxy_config(
                proxy_type=proxy_type,
                country=country,
                city=city_normalized,  # Usar ciudad normalizada (lowercase)
                region=region,
                sticky_session=True,
                session_lifetime=3600
            )
            
            # Probar proxy
            print_info("Probando conexión del proxy...")
            proxy_test = self.proxy_manager.test_proxy(proxy_config, timeout=20)
            
            if not proxy_test['success']:
                raise Exception(f"Proxy no funciona: {proxy_test['error']}")
            
            logger.info(f"✅ Proxy funcionando:")
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
            
            # Crear cliente 3x-ui si está habilitado
            threexui_client = None
            if self.threexui:
                try:
                    print_info("Creando cliente 3x-ui con monitoreo de tráfico...")
                    
                    # Email único para el cliente
                    client_email = f"{profile_config.name.replace(' ', '_')}_{profile_id[:8]}"
                    
                    # Crear cliente con límite de datos y vinculado al perfil
                    threexui_client = self.threexui.create_client(
                        email=client_email,
                        total_gb=50,  # 50 GB por defecto
                        expiry_days=30,
                        profile_id=profile_id  # ⭐ VINCULAR con perfil AdsPower
                    )
                    
                    logger.info(f"✅ Cliente 3x-ui vinculado al perfil")
                    logger.info(f"   Email: {client_email}")
                    logger.info(f"   UUID: {threexui_client['uuid']}")
                    logger.info(f"   Límite: {threexui_client['total_gb']} GB")
                    
                except Exception as e:
                    logger.warning(f"No se pudo crear cliente 3x-ui: {e}")
                    threexui_client = {'error': str(e)}
                        
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
                'threexui_client': threexui_client,
                'created_at': datetime.now().isoformat(),
                'warmup_completed': False
            }
            
            result['profile_data'] = profile_data
            
            # ==================================================
            # PASO 4: PRECALENTAR PERFIL
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
                                 proxy_type: str = 'residential',
                                 country: str = 'ec',
                                 warmup: bool = True,
                                 warmup_type: str = 'basic',
                                 warmup_duration: int = 30,
                                 delay_between: tuple = (60, 180)) -> Dict:
        """
        Crea múltiples perfiles
        
        Args:
            count: Número de perfiles a crear
            proxy_type: 'residential' o 'mobile'
            country: Código de país
            warmup: Si se debe precalentar
            warmup_type: Tipo de warmup
            warmup_duration: Duración del warmup
            delay_between: Tupla (min, max) segundos de delay entre creaciones
        
        Returns:
            Dict con resultados
        """
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
            
            # Crear perfil
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
            
            # Delay entre creaciones (excepto en el último)
            if i < count - 1:
                delay = random.randint(delay_between[0], delay_between[1])
                logger.info(f"⏱️  Esperando {delay}s antes del siguiente perfil...")
                time.sleep(delay)
        
        total_time = int(time.time() - start_time)
        results['total_time'] = total_time
        
        # Resumen final
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE CREACIÓN MASIVA")
        logger.info("=" * 70)
        logger.info(f"Total: {results['total']}")
        logger.info(f"Exitosos: {results['successful']}")
        logger.info(f"Fallidos: {results['failed']}")
        logger.info(f"Tiempo total: {total_time}s ({total_time//60}m {total_time%60}s)")
        logger.info("=" * 70)
        
        # Guardar resumen
        summary_file = f"profiles/batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Resumen guardado en: {summary_file}")
        
        return results
    
    def warm_existing_profile(self,
                             profile_id: str,
                             warmup_type: str = 'basic',
                             warmup_duration: int = 30) -> Dict:
        """
        Precalienta un perfil existente
        
        Args:
            profile_id: ID del perfil en AdsPower
            warmup_type: 'basic' o 'advanced'
            warmup_duration: Duración en minutos
        
        Returns:
            Dict con estadísticas del warmup
        """
        logger.info("=" * 70)
        logger.info(f"PRECALENTANDO PERFIL EXISTENTE: {profile_id}")
        logger.info("=" * 70)
        
        try:
            # Obtener datos del perfil
            profile_detail = self.adspower.get_profile_detail(profile_id)
            
            # Intentar cargar configuración guardada
            from utils import load_profile_data
            saved_data = load_profile_data(profile_id)
            
            if saved_data and 'profile_config' in saved_data:
                # Reconstruir ProfileConfig desde datos guardados
                config_dict = saved_data['profile_config']
                profile_config = ProfileConfig(**config_dict)
            else:
                # Generar configuración básica
                logger.warning("No se encontró configuración guardada, usando configuración genérica")
                profile_config = ProfileGenerator.generate_profile()
            
            # Crear warmer
            warmer = ProfileWarmer(self.adspower, profile_config)
            
            # Conectar al navegador
            if not warmer.connect_to_browser(profile_id):
                raise Exception("No se pudo conectar al navegador")
            
            try:
                # Ejecutar warmup
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
                
                # Actualizar datos guardados
                if saved_data:
                    saved_data['last_warmup'] = warmup_stats
                    saved_data['last_warmup_at'] = datetime.now().isoformat()
                    save_profile_data(profile_id, saved_data)
                
                print_success("Precalentamiento completado")
                
                return {
                    'success': True,
                    'profile_id': profile_id,
                    'warmup_stats': warmup_stats
                }
                
            finally:
                warmer.disconnect(profile_id)
                
        except Exception as e:
            logger.error(f"❌ Error precalentando perfil: {e}")
            return {
                'success': False,
                'profile_id': profile_id,
                'error': str(e)
            }