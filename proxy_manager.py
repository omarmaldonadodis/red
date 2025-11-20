# proxy_manager.py - SOLO SOAX
import requests
import random
from typing import Dict, Optional
import string
import logging
import urllib3
import time


logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SOAXProxyManager:
    """Gestor de proxies SOAX - Soporte completo Mobile + Residential"""
    
    def __init__(self, username: str, password: str, host: str = "proxy.soax.com", port: int = 5000):
        """
        Inicializa el gestor de proxies SOAX
        
        Args:
            username: Package ID de SOAX (ej: package-325126-ses)
            password: Password de SOAX
            host: Host del proxy SOAX
            port: Puerto del proxy SOAX (5000 por defecto)
        """
        # Extraer solo el package number del username
        if username.startswith('package-'):
            parts = username.split('-')
            if len(parts) >= 2:
                self.package_id = f"{parts[0]}-{parts[1]}"
            else:
                self.package_id = username
        else:
            self.package_id = username
        
        self.password = password
        self.host = host
        self.port = port
        self._active_sessions = {}
        
        print(f"✅ SOAX inicializado - Package ID: {self.package_id}")
    
    def get_proxy_config(self, 
                        proxy_type: str = 'mobile',
                        country: str = 'ec',
                        city: Optional[str] = None,
                        region: Optional[str] = None,
                        session_id: Optional[str] = None,
                        sticky_session: bool = True,
                        session_lifetime: int = 300) -> Dict:
        """
        Genera configuración de proxy SOAX con geo-targeting
        
        FORMATO CORRECTO SOAX:
        package-XXXXX-country-ec-region-pichincha-city-quito-sessionid-YYYY-sessionlength-300
        
        Args:
            proxy_type: 'mobile' o 'residential'
            country: Código de país (ISO 2 letras) - 'ec' para Ecuador
            city: Ciudad específica - 'quito', 'guayaquil', etc
            region: Región específica - 'pichincha', 'guayas', etc
            session_id: ID de sesión personalizado (opcional)
            sticky_session: Mantener la misma IP durante la sesión
            session_lifetime: Tiempo de vida de la sesión en segundos (max 3600)
        
        Returns:
            Dict con configuración de proxy
        """
        # Generar session ID si no existe
        if not session_id:
            session_id = self._generate_session_id()
        
        # FORMATO CORRECTO SOAX 2024 CON GEO-TARGETING:
        username_parts = [self.package_id]
        
        # Agregar tipo de proxy (mobile o residential)
        # SOAX usa 'type-mobile' o 'type-residential' como parámetro
        
        # Agregar país
        if country:
            username_parts.append(f"country-{country.lower()}")
        
        # Agregar región (si se especifica)
        if region:
            username_parts.append(f"region-{region.lower()}")
        
        # Agregar ciudad (si se especifica)
        if city:
            username_parts.append(f"city-{city.lower()}")
        
        # Agregar sesión sticky
        if sticky_session:
            username_parts.append(f"sessionid-{session_id}")
            username_parts.append(f"sessionlength-{session_lifetime}")
        
        # Agregar siempre el string "opt-lookalike" al final
        username_final = "-".join(username_parts) + "-opt-lookalike"
        
        proxy_config = {
            'type': 'http',
            'host': self.host,
            'port': self.port,
            'username': username_final,
            'password': self.password,
            'session_id': session_id,
            'proxy_type': proxy_type,
            'session_lifetime': session_lifetime,
            'country': country,
            'city': city,
            'region': region,
        }
        
        # Guardar sesión activa
        if sticky_session:
            self._active_sessions[session_id] = {
                'config': proxy_config,
                'created_at': time.time(),
                'proxy_type': proxy_type,
                'expires_at': time.time() + session_lifetime
            }
        
        return proxy_config
    
    def test_proxy(self, proxy_config: Dict, timeout: int = 60) -> Dict:
        """Prueba si el proxy funciona correctamente"""
        proxy_url = self.get_proxy_url(proxy_config)
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        result = {
            'success': False,
            'ip': None,
            'country': None,
            'city': None,
            'isp': None,
            'connection_type': proxy_config['proxy_type'],
            'error': None
        }
        
        try:
            print(f"   Probando proxy SOAX {proxy_config['proxy_type'].upper()}...")
            print(f"   Username: {proxy_config['username'][:500]}...")
            
            # Test usando el endpoint de SOAX
            response = requests.get(
                'http://checker.soax.com/api/ipinfo',
                proxies=proxies,
                timeout=timeout,
                verify=False
            )
            
            # Intentar parsear como JSON
            try:
                data = response.json()
            except:
                data = {'text': response.text}
            
            # Extraer IP
            result['ip'] = data.get('ip') or data.get('query') or data.get('ipAddress')
            result['country'] = data.get('country') or data.get('countryCode')
            result['city'] = data.get('city') or data.get('regionName')
            result['isp'] = data.get('isp') or data.get('org') or data.get('as')
            
            # Si no obtuvimos IP, intentar con ipify
            if not result['ip']:
                print(f"   Probando con ipify...")
                response2 = requests.get(
                    'https://api.ipify.org?format=json',
                    proxies=proxies,
                    timeout=timeout,
                    verify=False
                )
                result['ip'] = response2.json().get('ip')
            
            if result['ip']:
                result['success'] = True
            else:
                result['error'] = 'No se pudo obtener IP del proxy'
            
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout al conectar con el proxy (>25s)'
        except requests.exceptions.ProxyError as e:
            error_str = str(e)
            if '407' in error_str:
                result['error'] = 'Error 407: Autenticación fallida'
            else:
                result['error'] = f'Error de proxy: {error_str[:100]}'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Error de conexión: Verifica saldo en SOAX'
        except Exception as e:
            result['error'] = f'Error: {str(e)[:100]}'
        
        return result
    
    def get_proxy_url(self, proxy_config: Dict) -> str:
        """Convierte configuración de proxy a URL"""
        return (f"{proxy_config['type']}://"
                f"{proxy_config['username']}:{proxy_config['password']}@"
                f"{proxy_config['host']}:{proxy_config['port']}")
    
    def _generate_session_id(self) -> str:
        """Genera un ID de sesión único en formato SOAX (16 chars alfanuméricos)"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(16))
    
    def get_active_sessions(self) -> Dict:
        """Retorna sesiones activas"""
        import time
        current_time = time.time()
        expired = [sid for sid, data in self._active_sessions.items() 
                  if current_time > data.get('expires_at', 0)]
        
        for sid in expired:
            del self._active_sessions[sid]
        
        return self._active_sessions
    
    def clear_session(self, session_id: str):
        """Elimina una sesión del registro"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]