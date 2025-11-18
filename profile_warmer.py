# profile_warmer.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from humanizer import BrowserHumanizer
from typing import Dict, List
import time
import random
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ProfileWarmer:
    """Clase para precalentar perfiles de AdsPower"""
    
    def __init__(self, adspower_manager, profile_config):
        """
        Inicializa el warmer
        
        Args:
            adspower_manager: Instancia de AdsPowerManager
            profile_config: Configuración del perfil (ProfileConfig)
        """
        self.adspower = adspower_manager
        self.profile_config = profile_config
        self.driver = None
        self.humanizer = None
    
    def connect_to_browser(self, profile_id: str) -> bool:
        """
        Conecta Selenium al navegador de AdsPower
        
        Args:
            profile_id: ID del perfil en AdsPower
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            logger.info(f"🔌 Conectando al navegador del perfil: {profile_id}")
            
            # Abrir navegador en AdsPower
            browser_data = self.adspower.open_browser(profile_id)
            
            # Configurar opciones de Chrome para conectar al navegador existente
            chrome_options = Options()
            chrome_options.add_experimental_option(
                "debuggerAddress", 
                browser_data['debugger_address']
            )
            
            # Deshabilitar notificaciones y popups
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            
            # Conectar al navegador
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Maximizar ventana
            self.driver.maximize_window()
            
            # Inicializar humanizer
            self.humanizer = BrowserHumanizer(self.driver, self.profile_config.device_type)
            
            logger.info("✅ Conectado exitosamente al navegador")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando al navegador: {e}")
            return False
    
    def warm_profile_basic(self, duration_minutes: int = 30) -> Dict:
        """
        Precalentamiento básico del perfil
        
        Args:
            duration_minutes: Duración del precalentamiento en minutos
        
        Returns:
            Dict con estadísticas del warmup
        """
        logger.info("🔥 Iniciando precalentamiento básico del perfil")
        logger.info(f"   Duración: {duration_minutes} minutos")
        logger.info(f"   Tipo de dispositivo: {self.profile_config.device_type.upper()}")
        logger.info(f"   Tipo de proxy: {self.profile_config.proxy_type.upper()}")
        
        start_time = time.time()
        
        # Construir historial de navegación
        stats = self.humanizer.build_browsing_history(
            sites=self.profile_config.browsing_history,
            duration_minutes=duration_minutes
        )
        
        total_time = int(time.time() - start_time)
        stats['warmup_duration'] = total_time
        stats['warmup_type'] = 'basic'
        stats['completed_at'] = datetime.now().isoformat()
        
        logger.info("✅ Precalentamiento básico completado")
        
        return stats
    
    def warm_profile_advanced(self, 
                             duration_minutes: int = 60,
                             include_searches: bool = True,
                             include_social: bool = True) -> Dict:
        """
        Precalentamiento avanzado con búsquedas y redes sociales
        
        Args:
            duration_minutes: Duración total en minutos
            include_searches: Incluir búsquedas en Google
            include_social: Incluir visitas a redes sociales
        
        Returns:
            Dict con estadísticas del warmup
        """
        logger.info("🔥 Iniciando precalentamiento AVANZADO del perfil")
        logger.info(f"   Duración: {duration_minutes} minutos")
        logger.info(f"   Búsquedas: {'Sí' if include_searches else 'No'}")
        logger.info(f"   Redes sociales: {'Sí' if include_social else 'No'}")
        
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        
        stats = {
            'sites_visited': 0,
            'searches_performed': 0,
            'social_interactions': 0,
            'total_time': 0,
            'warmup_type': 'advanced'
        }
        
        # Fase 1: Búsquedas relacionadas con intereses (25% del tiempo)
        if include_searches:
            search_time = duration_seconds * 0.25
            searches = self._generate_searches_from_interests()
            
            logger.info(f"🔍 Fase 1: Realizando {len(searches)} búsquedas...")
            
            search_start = time.time()
            for search_query in searches:
                if time.time() - search_start >= search_time:
                    break
                
                self.humanizer.simulate_search(search_query)
                stats['searches_performed'] += 1
                
                # Pausa entre búsquedas
                self.humanizer.human_sleep(3, 8)
        
        # Fase 2: Navegación por sitios de interés (50% del tiempo)
        browsing_time = duration_seconds * 0.5
        sites_to_visit = self._prioritize_sites()
        
        logger.info(f"📚 Fase 2: Visitando {len(sites_to_visit)} sitios...")
        
        browsing_stats = self.humanizer.build_browsing_history(
            sites=sites_to_visit,
            duration_minutes=int(browsing_time / 60)
        )
        stats['sites_visited'] = browsing_stats['sites_visited']
        
        # Fase 3: Redes sociales y sitios populares (25% del tiempo restante)
        if include_social:
            elapsed = time.time() - start_time
            remaining_time = duration_seconds - elapsed
            
            if remaining_time > 0:
                logger.info("📱 Fase 3: Interacción con redes sociales...")
                
                social_stats = self._visit_social_media(int(remaining_time / 60))
                stats['social_interactions'] = social_stats.get('sites_visited', 0)
        
        # Fase 4: Limpieza y finalización
        logger.info("🧹 Fase 4: Limpieza y finalización...")
        
        # Ocasionalmente limpiar datos temporales
        if random.random() < 0.3:
            self.humanizer.clear_browser_data()
        
        # Cerrar algunas pestañas si hay muchas abiertas
        try:
            if len(self.driver.window_handles) > 1:
                for _ in range(len(self.driver.window_handles) - 1):
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            pass
        
        total_time = int(time.time() - start_time)
        stats['total_time'] = total_time
        stats['completed_at'] = datetime.now().isoformat()
        
        logger.info("✅ Precalentamiento avanzado completado")
        logger.info(f"   Búsquedas: {stats['searches_performed']}")
        logger.info(f"   Sitios: {stats['sites_visited']}")
        logger.info(f"   Redes sociales: {stats['social_interactions']}")
        logger.info(f"   Tiempo total: {total_time}s")
        
        return stats
    
    def _generate_searches_from_interests(self) -> List[str]:
        """Genera búsquedas basadas en los intereses del perfil"""
        search_templates = {
            'sports': [
                'resultados fútbol hoy',
                'tabla posiciones liga ecuatoriana',
                'noticias deportes',
                'calendario partidos'
            ],
            'gaming': [
                'mejores juegos 2024',
                'trucos {game}',
                'gameplay {game}',
                'pc gaming Ecuador'
            ],
            'news': [
                'noticias Ecuador hoy',
                'últimas noticias',
                'noticias internacionales',
                'el universo noticias'
            ],
            'technology': [
                'nuevas tecnologías 2024',
                'mejores smartphones',
                'tutoriales programación',
                'inteligencia artificial'
            ],
            'finance': [
                'precio dólar hoy',
                'inversiones Ecuador',
                'finanzas personales',
                'bolsa valores'
            ],
            'shopping': [
                'ofertas online Ecuador',
                'comprar {product}',
                'mejores tiendas online',
                'mercado libre Ecuador'
            ]
        }
        
        searches = []
        
        for interest in self.profile_config.interests:
            if interest in search_templates:
                # Seleccionar 1-2 búsquedas por interés
                num_searches = random.randint(1, 2)
                selected = random.sample(
                    search_templates[interest],
                    min(num_searches, len(search_templates[interest]))
                )
                searches.extend(selected)
        
        # Agregar búsquedas genéricas
        generic_searches = [
            'clima Ecuador',
            'google maps',
            'gmail',
            'youtube'
        ]
        searches.extend(random.sample(generic_searches, 2))
        
        random.shuffle(searches)
        return searches[:8]  # Máximo 8 búsquedas
    
    def _prioritize_sites(self) -> List[str]:
        """Prioriza sitios según el tipo de dispositivo y proxy"""
        sites = self.profile_config.browsing_history.copy()
        
        # Para móviles, priorizar sitios mobile-friendly
        if self.profile_config.device_type == 'mobile':
            mobile_priority_sites = [
                'youtube.com', 'facebook.com', 'instagram.com',
                'twitter.com', 'whatsapp.com', 'gmail.com'
            ]
            
            # Mover sitios prioritarios al inicio
            prioritized = []
            remaining = []
            
            for site in sites:
                domain = site.replace('m.', '').replace('mobile.', '')
                if any(priority in domain for priority in mobile_priority_sites):
                    prioritized.append(site)
                else:
                    remaining.append(site)
            
            sites = prioritized + remaining
        
        return sites
    
    def _visit_social_media(self, duration_minutes: int) -> Dict:
        """
        Visita redes sociales específicas con interacciones
        
        Args:
            duration_minutes: Tiempo a dedicar a redes sociales
        
        Returns:
            Dict con estadísticas
        """
        social_sites = {
            'desktop': [
                'facebook.com',
                'twitter.com',
                'linkedin.com',
                'instagram.com',
                'youtube.com'
            ],
            'mobile': [
                'm.facebook.com',
                'mobile.twitter.com',
                'instagram.com',
                'youtube.com'
            ]
        }
        
        sites = social_sites.get(
            self.profile_config.device_type,
            social_sites['desktop']
        )
        
        # Seleccionar 2-3 redes sociales
        selected_sites = random.sample(sites, min(3, len(sites)))
        
        return self.humanizer.build_browsing_history(
            sites=selected_sites,
            duration_minutes=duration_minutes
        )
    
    def disconnect(self, profile_id: str):
        """Desconecta y cierra el navegador"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🔌 Navegador cerrado")
            
            # Cerrar navegador en AdsPower
            self.adspower.close_browser(profile_id)
            
        except Exception as e:
            logger.warning(f"Error al desconectar: {e}")