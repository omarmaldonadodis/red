# humanizer.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BrowserHumanizer:
    """Humaniza el comportamiento del navegador para evitar detección"""
    
    def __init__(self, driver: webdriver.Chrome, device_type: str = 'desktop'):
        """
        Inicializa el humanizador
        
        Args:
            driver: Instancia de Selenium WebDriver
            device_type: 'desktop' o 'mobile'
        """
        self.driver = driver
        self.device_type = device_type
        self.actions = ActionChains(driver)
    
    def human_sleep(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Sleep con variación humana usando distribución normal"""
        # Usar distribución normal para comportamiento más humano
        mean = (min_seconds + max_seconds) / 2
        std = (max_seconds - min_seconds) / 6  # 99.7% dentro del rango
        sleep_time = np.random.normal(mean, std)
        sleep_time = max(min_seconds, min(max_seconds, sleep_time))  # Clamp al rango
        time.sleep(sleep_time)
    
    def human_type(self, element, text: str, mistake_probability: float = 0.05):
        """
        Escribe texto con velocidad y errores humanos
        
        Args:
            element: Elemento donde escribir
            text: Texto a escribir
            mistake_probability: Probabilidad de cometer un error (0-1)
        """
        for i, char in enumerate(text):
            # Simular error ocasional
            if random.random() < mistake_probability and i > 0:
                # Escribir carácter incorrecto
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                # Corregir con backspace
                element.send_keys(Keys.BACK_SPACE)
                time.sleep(random.uniform(0.1, 0.2))
            
            # Escribir carácter correcto
            element.send_keys(char)
            
            # Velocidad variable: 80-250ms por carácter
            base_speed = random.uniform(0.08, 0.25)
            
            # Pausas más largas después de palabras
            if char == ' ':
                base_speed *= random.uniform(1.5, 2.5)
            
            # Pausas ocasionales (como si pensara)
            if random.random() < 0.15:
                base_speed *= random.uniform(2, 4)
            
            time.sleep(base_speed)
    
    def move_mouse_naturally(self, steps: int = 10):
        """
        Mueve el mouse de forma natural con curva Bezier
        
        Args:
            steps: Número de pasos en el movimiento
        """
        try:
            # Obtener tamaño de la ventana
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            
            # Generar puntos de control para curva Bezier
            start_x = random.randint(0, width)
            start_y = random.randint(0, height)
            end_x = random.randint(0, width)
            end_y = random.randint(0, height)
            
            # Puntos de control intermedios
            ctrl1_x = random.randint(0, width)
            ctrl1_y = random.randint(0, height)
            ctrl2_x = random.randint(0, width)
            ctrl2_y = random.randint(0, height)
            
            # Calcular curva Bezier
            for step in range(steps):
                t = step / steps
                
                # Fórmula de curva Bezier cúbica
                x = (1-t)**3 * start_x + 3*(1-t)**2*t * ctrl1_x + 3*(1-t)*t**2 * ctrl2_x + t**3 * end_x
                y = (1-t)**3 * start_y + 3*(1-t)**2*t * ctrl1_y + 3*(1-t)*t**2 * ctrl2_y + t**3 * end_y
                
                # Ejecutar movimiento
                script = """
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': arguments[0],
                    'clientY': arguments[1]
                });
                document.dispatchEvent(event);
                """
                self.driver.execute_script(script, int(x), int(y))
                time.sleep(random.uniform(0.01, 0.03))
                
        except Exception as e:
            logger.warning(f"Error moviendo mouse: {e}")
    
    def random_scroll(self, num_scrolls: int = None):
        """
        Realiza scroll aleatorio en la página de forma natural
        
        Args:
            num_scrolls: Número de scrolls (None = aleatorio)
        """
        try:
            if num_scrolls is None:
                num_scrolls = random.randint(2, 6)
            
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            current_position = 0
            
            for _ in range(num_scrolls):
                # Decidir dirección (90% hacia abajo, 10% hacia arriba)
                scroll_down = random.random() < 0.9
                
                if scroll_down:
                    # Scroll hacia abajo en incrementos variables
                    scroll_amount = random.randint(viewport_height // 3, viewport_height)
                    current_position = min(current_position + scroll_amount, scroll_height - viewport_height)
                else:
                    # Ocasionalmente scroll hacia arriba
                    scroll_amount = random.randint(viewport_height // 4, viewport_height // 2)
                    current_position = max(current_position - scroll_amount, 0)
                
                # Ejecutar scroll suave
                self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
                
                # Pausa después del scroll (simular lectura)
                self.human_sleep(0.8, 2.5)
                
                # Movimiento de mouse ocasional durante el scroll
                if random.random() < 0.4:
                    self.move_mouse_naturally(steps=5)
                    
        except Exception as e:
            logger.warning(f"Error en scroll: {e}")
    
    def interact_with_page(self):
        """Interacciones aleatorias con la página para parecer humano"""
        interactions = []
        
        # Movimiento de mouse (alta probabilidad)
        if random.random() < 0.8:
            interactions.append(('mouse_move', 0.8))
        
        # Scroll (alta probabilidad)
        if random.random() < 0.9:
            interactions.append(('scroll', 0.9))
        
        # Click aleatorio en lugares seguros (baja probabilidad)
        if random.random() < 0.2:
            interactions.append(('safe_click', 0.2))
        
        # Hover sobre elementos (probabilidad media)
        if random.random() < 0.5:
            interactions.append(('hover', 0.5))
        
        # Ejecutar interacciones
        for interaction, _ in interactions:
            try:
                if interaction == 'mouse_move':
                    self.move_mouse_naturally(steps=random.randint(8, 15))
                    
                elif interaction == 'scroll':
                    self.random_scroll()
                    
                elif interaction == 'safe_click':
                    # Click en una posición aleatoria que no sea un link
                    script = """
                    var x = Math.random() * window.innerWidth;
                    var y = Math.random() * window.innerHeight;
                    var element = document.elementFromPoint(x, y);
                    if (element && element.tagName !== 'A' && element.tagName !== 'BUTTON') {
                        element.click();
                    }
                    """
                    self.driver.execute_script(script)
                    self.human_sleep(0.3, 0.8)
                    
                elif interaction == 'hover':
                    # Hover sobre un elemento aleatorio
                    elements = self.driver.find_elements(By.TAG_NAME, 'div')
                    if elements:
                        element = random.choice(elements[:20])  # Solo primeros 20
                        try:
                            self.actions.move_to_element(element).perform()
                            self.human_sleep(0.5, 1.5)
                        except:
                            pass
                            
            except Exception as e:
                logger.debug(f"Error en interacción {interaction}: {e}")
                continue
    
    def visit_site(self, url: str, stay_duration: tuple = (10, 30)) -> bool:
        """
        Visita un sitio web de forma natural
        
        Args:
            url: URL a visitar
            stay_duration: Tupla (min, max) segundos de permanencia
        
        Returns:
            bool: True si exitoso
        """
        try:
            # NUEVO: Bloquear imágenes y videos para ahorrar datos
            chrome_prefs = {
                "profile.managed_default_content_settings.images": 2,  # Bloquear imágenes
                "profile.managed_default_content_settings.media_stream": 2  # Bloquear video
            }

            # Asegurar que tenga protocolo
            if not url.startswith('http'):
                url = f'https://{url}'
            
            logger.info(f"Visitando: {url}")
            
            # Navegar al sitio
            self.driver.get(url)
            
            # Esperar carga inicial
            self.human_sleep(2, 4)
            
            # Verificar que la página cargó
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Interactuar con la página
            self.interact_with_page()
            
            # Tiempo de permanencia variable
            stay_time = random.uniform(stay_duration[0], stay_duration[1])
            
            # Durante la permanencia, hacer algunas interacciones adicionales
            num_interactions = random.randint(1, 3)
            time_per_interaction = stay_time / (num_interactions + 1)
            
            for _ in range(num_interactions):
                time.sleep(time_per_interaction)
                
                # Interacción aleatoria
                if random.random() < 0.7:
                    self.random_scroll(num_scrolls=random.randint(1, 3))
                else:
                    self.move_mouse_naturally()
            
            # Tiempo restante
            time.sleep(time_per_interaction)
            
            logger.info(f"✓ Sitio visitado exitosamente: {url}")
            return True
            
        except TimeoutException:
            logger.warning(f"Timeout visitando: {url}")
            return False
        except WebDriverException as e:
            logger.warning(f"Error visitando {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado visitando {url}: {e}")
            return False
    
    def build_browsing_history(self, sites: List[str], duration_minutes: int = 30) -> Dict:
        """
        Construye historial de navegación realista
        
        Args:
            sites: Lista de sitios a visitar
            duration_minutes: Duración total en minutos
        
        Returns:
            Dict con estadísticas de la sesión
        """
        logger.info(f"📚 Construyendo historial de navegación ({duration_minutes} minutos)")
        logger.info(f"   Sitios a visitar: {len(sites)}")
        
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        
        stats = {
            'sites_visited': 0,
            'sites_failed': 0,
            'total_time': 0,
            'sites_list': []
        }
        
        # Mezclar sitios para orden aleatorio
        sites_shuffled = sites.copy()
        random.shuffle(sites_shuffled)
        
        for site in sites_shuffled:
            # Verificar si se acabó el tiempo
            elapsed = time.time() - start_time
            if elapsed >= duration_seconds:
                logger.info("⏱️  Tiempo de warmup completado")
                break
            
            # Calcular tiempo restante y ajustar duración de visita
            time_remaining = duration_seconds - elapsed
            sites_remaining = len(sites_shuffled) - stats['sites_visited']
            
            if sites_remaining > 0:
                avg_time_per_site = time_remaining / sites_remaining
                max_stay = min(60, avg_time_per_site * 1.5)
                min_stay = min(10, max_stay / 3)
            else:
                min_stay, max_stay = 10, 30
            
            # Visitar sitio
            success = self.visit_site(site, stay_duration=(min_stay, max_stay))
            
            if success:
                stats['sites_visited'] += 1
                stats['sites_list'].append(site)
            else:
                stats['sites_failed'] += 1
            
            # Pausa entre sitios (simular búsqueda del siguiente sitio)
            if stats['sites_visited'] + stats['sites_failed'] < len(sites_shuffled):
                self.human_sleep(2, 5)
        
        stats['total_time'] = int(time.time() - start_time)
        
        logger.info("✅ Historial de navegación completado")
        logger.info(f"   Sitios visitados: {stats['sites_visited']}")
        logger.info(f"   Sitios fallidos: {stats['sites_failed']}")
        logger.info(f"   Tiempo total: {stats['total_time']}s")
        
        return stats
    
    def simulate_search(self, search_query: str):
        """
        Simula una búsqueda en Google
        
        Args:
            search_query: Término de búsqueda
        """
        try:
            logger.info(f"🔍 Buscando: {search_query}")
            
            # Ir a Google
            self.driver.get('https://www.google.com')
            self.human_sleep(1, 2)
            
            # Aceptar cookies si aparece el diálogo
            try:
                accept_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Acepto') or contains(., 'Accept')]"))
                )
                accept_button.click()
                self.human_sleep(0.5, 1)
            except:
                pass
            
            # Buscar el input de búsqueda
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # Escribir búsqueda de forma humana
            self.human_type(search_box, search_query)
            self.human_sleep(0.5, 1.5)
            
            # Enviar búsqueda
            search_box.send_keys(Keys.RETURN)
            self.human_sleep(2, 4)
            
            # Scroll por los resultados
            self.random_scroll(num_scrolls=random.randint(2, 4))
            
            # Ocasionalmente hacer click en un resultado
            if random.random() < 0.3:
                try:
                    results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g a')
                    if results and len(results) > 3:
                        # Click en uno de los primeros resultados
                        result_to_click = random.choice(results[1:5])
                        result_to_click.click()
                        self.human_sleep(3, 6)
                        
                        # Interactuar con la página
                        self.interact_with_page()
                        
                        # Volver atrás
                        self.driver.back()
                        self.human_sleep(1, 2)
                except:
                    pass
            
            logger.info(f"✓ Búsqueda completada: {search_query}")
            
        except Exception as e:
            logger.warning(f"Error en búsqueda: {e}")
    
    def clear_browser_data(self):
        """Limpia algunos datos del navegador para simular uso normal"""
        try:
            # Limpiar localStorage de algunos sitios aleatorios
            self.driver.execute_script("localStorage.clear();")
            
            # Limpiar sessionStorage
            self.driver.execute_script("sessionStorage.clear();")
            
            logger.info("🧹 Datos temporales del navegador limpiados")
        except Exception as e:
            logger.warning(f"Error limpiando datos: {e}")