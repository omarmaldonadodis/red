# advanced_account_creator.py - Sistema Avanzado con Control Total
import threading
import queue
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from account_creator import AccountCreator
from utils import print_success, print_error, print_info, print_warning
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProfileRequest:
    """Solicitud de creación de perfil con control total"""
    # Datos personales
    custom_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Ubicación
    country: str = 'ec'
    city: Optional[str] = None
    region: Optional[str] = None
    
    # Dispositivo
    proxy_type: str = 'mobile'
    device_id: Optional[str] = None  # ID específico del dispositivo
    
    # Intereses
    interests: Optional[List[str]] = None
    
    # Warmup
    do_warmup: bool = True
    warmup_sites: Optional[List[str]] = None  # Sitios específicos para warmup
    warmup_duration: int = 20
    accept_cookies_auto: bool = True
    
    # Reportes
    generate_reports: bool = True


class AdvancedAccountCreator:
    """Creador avanzado con control total y precalentamiento paralelo"""
    
    def __init__(self, base_creator: AccountCreator):
        self.creator = base_creator
        self.active_warmups = []
        self.warmup_reports = {}
        self.lock = threading.Lock()
    
    def create_profile_custom(self, request: ProfileRequest) -> Dict:
        """Crea un perfil con control total"""
        logger.info("="*70)
        logger.info("CREANDO PERFIL PERSONALIZADO")
        logger.info("="*70)
        
        result = {
            'success': False,
            'profile_id': None,
            'profile_data': None,
            'warmup_stats': None,
            'error': None,
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Paso 1: Generar configuración personalizada
            from config import ProfileGenerator
            from mobile_devices import get_device_by_id, get_random_mobile_device
            
            if request.device_id:
                device_data = get_device_by_id(request.device_id)
                if not device_data:
                    raise ValueError(f"Dispositivo '{request.device_id}' no encontrado")
                logger.info(f"📱 Dispositivo: {device_data['name']}")
            
            # Generar perfil
            profile_config = ProfileGenerator.generate_profile(
                proxy_type=request.proxy_type,
                specific_device=request.device_id
            )
            
            # Sobrescribir con datos personalizados
            if request.custom_name:
                profile_config.name = request.custom_name
            if request.age:
                profile_config.age = request.age
            if request.gender:
                profile_config.gender = request.gender
            if request.interests:
                profile_config.interests = request.interests
            if request.city:
                profile_config.city = request.city.title()
            
            logger.info(f"👤 Perfil: {profile_config.name}, {profile_config.age} años")
            logger.info(f"📍 Ubicación: {profile_config.city}, {request.country.upper()}")
            logger.info(f"❤️  Intereses: {', '.join(profile_config.interests[:5])}")
            
            # Paso 2: Configurar proxy
            proxy_config = self.creator.proxy_manager.get_proxy_config(
                proxy_type=request.proxy_type,
                country=request.country,
                city=request.city.lower() if request.city else None,
                region=request.region,
                sticky_session=True,
                session_lifetime=3600
            )
            
            # Probar proxy
            print_info("Probando proxy...")
            proxy_test = self.creator.proxy_manager.test_proxy(proxy_config, timeout=20)
            
            if not proxy_test['success']:
                raise Exception(f"Proxy no funciona: {proxy_test['error']}")
            
            logger.info(f"✅ Proxy {request.proxy_type.upper()} - IP: {proxy_test['ip']}")
            
            # Paso 3: Crear perfil en AdsPower
            print_info("Creando perfil en AdsPower...")
            
            profile_id = self.creator.adspower.create_profile(
                profile_config=profile_config,
                proxy_config=proxy_config
            )
            
            result['profile_id'] = profile_id
            
            # Guardar datos
            profile_data = {
                'profile_id': profile_id,
                'profile_config': profile_config.to_dict(),
                'proxy_config': {
                    'type': proxy_config['proxy_type'],
                    'session_id': proxy_config['session_id'],
                    'country': request.country,
                    'city': request.city,
                    'region': request.region
                },
                'proxy_test': proxy_test,
                'custom_request': {
                    'custom_name': request.custom_name,
                    'custom_interests': request.interests,
                    'custom_warmup_sites': request.warmup_sites
                },
                'created_at': datetime.now().isoformat(),
                'warmup_completed': False
            }
            
            result['profile_data'] = profile_data
            
            # Paso 4: Warmup (si se solicita)
            if request.do_warmup:
                print_info(f"Iniciando warmup ({request.warmup_duration} min)...")
                
                # Si se especificaron sitios custom, usarlos
                sites_to_visit = request.warmup_sites if request.warmup_sites else profile_config.browsing_history
                
                warmup_stats = self._warmup_profile(
                    profile_id=profile_id,
                    profile_config=profile_config,
                    sites=sites_to_visit,
                    duration_minutes=request.warmup_duration,
                    accept_cookies_auto=request.accept_cookies_auto,
                    generate_reports=request.generate_reports
                )
                
                result['warmup_stats'] = warmup_stats
                profile_data['warmup_completed'] = True
                profile_data['warmup_stats'] = warmup_stats
            
            # Guardar perfil
            from utils import save_profile_data
            save_profile_data(profile_id, profile_data)
            
            result['success'] = True
            result['end_time'] = datetime.now().isoformat()
            
            print_success(f"✨ Perfil creado: {profile_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            result['error'] = str(e)
            result['end_time'] = datetime.now().isoformat()
            
            # Limpiar si falló
            if result['profile_id']:
                try:
                    self.creator.adspower.delete_profile([result['profile_id']])
                except:
                    pass
            
            return result
    
    def create_multiple_parallel(self, requests: List[ProfileRequest], max_parallel: int = 3) -> Dict:
        """Crea múltiples perfiles con warmup en paralelo"""
        logger.info("="*70)
        logger.info(f"CREACIÓN PARALELA - {len(requests)} perfiles (max {max_parallel} paralelos)")
        logger.info("="*70)
        
        results = {
            'total': len(requests),
            'successful': 0,
            'failed': 0,
            'profiles': [],
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        # Cola de tareas
        task_queue = queue.Queue()
        for i, req in enumerate(requests):
            task_queue.put((i, req))
        
        # Cola de resultados
        result_queue = queue.Queue()
        
        # Worker thread
        def worker():
            while True:
                try:
                    index, request = task_queue.get(timeout=1)
                except queue.Empty:
                    break
                
                logger.info(f"\n>>> Thread: Creando perfil {index + 1}/{len(requests)}...")
                
                result = self.create_profile_custom(request)
                result_queue.put((index, result))
                
                task_queue.task_done()
        
        # Lanzar threads
        threads = []
        for i in range(min(max_parallel, len(requests))):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        # Esperar a que terminen
        task_queue.join()
        
        # Recopilar resultados
        while not result_queue.empty():
            index, result = result_queue.get()
            
            if result['success']:
                results['successful'] += 1
                results['profiles'].append({
                    'index': index + 1,
                    'profile_id': result['profile_id'],
                    'name': result['profile_data']['profile_config']['name']
                })
            else:
                results['failed'] += 1
                results['errors'].append({
                    'index': index + 1,
                    'error': result['error']
                })
        
        results['end_time'] = datetime.now().isoformat()
        
        # Resumen
        logger.info("\n" + "="*70)
        logger.info("RESUMEN CREACIÓN PARALELA")
        logger.info("="*70)
        logger.info(f"Total: {results['total']}")
        logger.info(f"Exitosos: {results['successful']}")
        logger.info(f"Fallidos: {results['failed']}")
        logger.info("="*70)
        
        return results
    
    def _warmup_profile(self, profile_id: str, profile_config, sites: List[str], 
                       duration_minutes: int, accept_cookies_auto: bool,
                       generate_reports: bool) -> Dict:
        """Ejecuta warmup de un perfil con reportes"""
        from profile_warmer import ProfileWarmer
        
        warmer = ProfileWarmer(self.creator.adspower, profile_config)
        
        if not warmer.connect_to_browser(profile_id):
            raise Exception("No se pudo conectar al navegador")
        
        # Tracking de velocidad
        speed_tracker = {
            'sites': [],
            'start_time': time.time()
        }
        
        try:
            # Inyectar auto-aceptar cookies si está habilitado
            if accept_cookies_auto:
                self._inject_cookie_acceptor(warmer.driver)
            
            # Ejecutar warmup con tracking
            stats = warmer.build_browsing_history(
                sites=sites,
                duration_minutes=duration_minutes
            )
            
            # Generar reporte si se solicita
            if generate_reports:
                report = self._generate_warmup_report(
                    profile_id=profile_id,
                    stats=stats,
                    speed_tracker=speed_tracker
                )
                stats['report'] = report
                
                # Guardar reporte
                report_file = f"profiles/warmup_reports/{profile_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import os
                os.makedirs('profiles/warmup_reports', exist_ok=True)
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                print_success(f"📊 Reporte guardado: {report_file}")
            
            return stats
            
        finally:
            warmer.disconnect(profile_id)
    
    def _inject_cookie_acceptor(self, driver):
        """Inyecta script para aceptar cookies automáticamente"""
        script = """
        // Auto-aceptar cookies
        (function() {
            const acceptPatterns = [
                'accept', 'aceptar', 'agree', 'allow', 'permitir',
                'continuar', 'continue', 'entiendo', 'ok', 'de acuerdo'
            ];
            
            setInterval(() => {
                // Buscar botones de cookies
                const buttons = document.querySelectorAll('button, a[role="button"]');
                buttons.forEach(btn => {
                    const text = btn.textContent.toLowerCase();
                    if (acceptPatterns.some(pattern => text.includes(pattern))) {
                        if (btn.offsetParent !== null) {  // visible
                            console.log('Auto-accepting cookies:', btn.textContent);
                            btn.click();
                        }
                    }
                });
            }, 2000);
        })();
        """
        
        try:
            driver.execute_script(script)
            logger.info("🍪 Auto-aceptador de cookies activado")
        except:
            logger.warning("No se pudo inyectar auto-aceptador de cookies")
    
    def _generate_warmup_report(self, profile_id: str, stats: Dict, speed_tracker: Dict) -> Dict:
        """Genera reporte detallado de warmup"""
        total_time = time.time() - speed_tracker['start_time']
        
        report = {
            'profile_id': profile_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'duration_seconds': int(total_time),
                'sites_visited': stats.get('sites_visited', 0),
                'sites_failed': stats.get('sites_failed', 0),
                'success_rate': f"{(stats.get('sites_visited', 0) / (stats.get('sites_visited', 0) + stats.get('sites_failed', 1)) * 100):.1f}%"
            },
            'speed_metrics': {
                'avg_time_per_site': f"{total_time / max(stats.get('sites_visited', 1), 1):.2f}s",
                'total_duration': f"{int(total_time // 60)}m {int(total_time % 60)}s"
            },
            'sites_detail': stats.get('sites_list', [])
        }
        
        return report


def get_interest_websites(interests: List[str], lightweight_only: bool = True) -> List[str]:
    """
    Retorna sitios web optimizados según intereses
    
    Args:
        interests: Lista de intereses
        lightweight_only: Solo sitios ligeros y rápidos
    """
    # Base de datos de sitios LIGEROS por interés
    LIGHTWEIGHT_SITES = {
        'news_apps': [
            'lite.cnn.com',
            'www.bbc.com/news',
            'news.google.com',
            'www.reuters.com'
        ],
        'social_media': [
            'mobile.twitter.com',
            'm.facebook.com',
            'www.reddit.com'
        ],
        'shopping': [
            'm.aliexpress.com',
            'm.amazon.com',
            'www.ebay.com/m'
        ],
        'banking': [
            'www.pichincha.com',
            'www.bancoguayaquil.com'
        ],
        'technology': [
            'news.ycombinator.com',
            'slashdot.org',
            'www.theverge.com'
        ],
        'sports': [
            'www.espn.com/mobile',
            'www.goal.com',
            'm.marca.com'
        ],
        'music_streaming': [
            'open.spotify.com',
            'music.youtube.com'
        ],
        'messaging': [
            'web.whatsapp.com',
            'web.telegram.org'
        ]
    }
    
    selected_sites = []
    
    for interest in interests:
        if interest in LIGHTWEIGHT_SITES:
            selected_sites.extend(LIGHTWEIGHT_SITES[interest])
    
    # Agregar sitios comunes ligeros
    common_light = [
        'www.google.com',
        'www.wikipedia.org',
        'www.youtube.com/feed/trending'
    ]
    
    selected_sites.extend(common_light)
    
    # Eliminar duplicados
    return list(dict.fromkeys(selected_sites))