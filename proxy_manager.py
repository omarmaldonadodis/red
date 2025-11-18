# proxy_manager.py
import requests
import random
from typing import Dict, Optional, List
import time
import urllib3
import string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SOAXProxyManager:
    """Gestor de proxies SOAX con formato correcto 2024"""
    
    def __init__(self, username: str, password: str, host: str = "proxy.soax.com", port: int = 5000):
        """
        Inicializa el gestor de proxies SOAX
        
        Args:
            username: Package ID de SOAX (ej: package-325126)
            password: Password de SOAX
            host: Host del proxy SOAX
            port: Puerto del proxy SOAX (5000 por defecto)
        """
        # Extraer solo el package number del username
        if username.startswith('package-'):
            # Si viene como "package-325126-ses", extraer solo "package-325126"
            parts = username.split('-')
            if len(parts) >= 2:
                self.package_id = f"{parts[0]}-{parts[1]}"  # package-325126
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
                        proxy_type: str = 'residential',
                        country: str = 'ec',
                        city: Optional[str] = None,
                        region: Optional[str] = None,
                        session_id: Optional[str] = None,
                        sticky_session: bool = True,
                        session_lifetime: int = 300) -> Dict:
        """
        Genera configuración de proxy SOAX con geo-targeting
        
        FORMATO CORRECTO SOAX CON GEO-TARGETING:
        package-XXXXX-country-ec-region-pichincha-city-quito-sessionid-YYYY-sessionlength-300
        
        Args:
            proxy_type: 'residential' o 'mobile'
            country: Código de país (ISO 2 letras) - 'ec' para Ecuador
            city: Ciudad específica - 'quito', 'guayaquil', etc
            region: Región específica - 'pichincha', 'guayas', etc
            session_id: ID de sesión personalizado (opcional)
            sticky_session: Mantener la misma IP durante la sesión
            session_lifetime: Tiempo de vida de la sesión en segundos (max 3600 = 60 min)
        
        Returns:
            Dict con configuración de proxy
        """
        # Generar session ID si no existe
        if not session_id:
            session_id = self._generate_session_id()
        
        # FORMATO CORRECTO SOAX 2024 CON GEO-TARGETING:
        username_parts = [self.package_id]
        
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
        
        username_final = "-".join(username_parts)
        
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
            'region': region
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
    def get_proxy_url(self, proxy_config: Dict) -> str:
        """Convierte configuración de proxy a URL"""
        return (f"{proxy_config['type']}://"
                f"{proxy_config['username']}:{proxy_config['password']}@"
                f"{proxy_config['host']}:{proxy_config['port']}")
    
    def get_proxy_string_for_adspower(self, proxy_config: Dict) -> Dict:
        """
        Retorna configuración formateada para AdsPower
        
        Returns:
            Dict con formato esperado por AdsPower
        """
        return {
            'proxy_soft': 'other',
            'proxy_type': proxy_config['type'],  # http
            'proxy_host': proxy_config['host'],
            'proxy_port': str(proxy_config['port']),
            'proxy_user': proxy_config['username'],
            'proxy_password': proxy_config['password']
        }
    
    def test_proxy(self, proxy_config: Dict, timeout: int = 25) -> Dict:
        """
        Prueba si el proxy funciona correctamente
        
        Args:
            proxy_config: Configuración del proxy
            timeout: Timeout en segundos
        
        Returns:
            Dict con resultado del test
        """
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
            'connection_type': None,
            'error': None
        }
        
        try:
            print(f"   Probando proxy SOAX...")
            print(f"   Username: {proxy_config['username'][:60]}...")
            
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
                # Si no es JSON, crear data vacía
                data = {'text': response.text}
            
            # Extraer IP de diferentes formatos posibles
            result['ip'] = data.get('ip') or data.get('query') or data.get('ipAddress')
            result['country'] = data.get('country') or data.get('countryCode') or data.get('country_code')
            result['city'] = data.get('city') or data.get('regionName')
            result['isp'] = data.get('isp') or data.get('org') or data.get('as') or data.get('asname')
            
            # Si no obtuvimos IP, intentar con api.ipify.org
            if not result['ip']:
                print(f"   Probando con ipify...")
                response2 = requests.get(
                    'https://api.ipify.org?format=json',
                    proxies=proxies,
                    timeout=timeout,
                    verify=False
                )
                result['ip'] = response2.json().get('ip')
            
            # Si obtuvimos IP, considerar exitoso
            if result['ip']:
                result['success'] = True
                
                # Detectar tipo de conexión
                if result['isp']:
                    mobile_indicators = ['mobile', 'cellular', 'wireless', 'lte', '4g', '5g', 'telefonica', 'claro', 'movistar']
                    isp_lower = result['isp'].lower()
                    result['connection_type'] = 'mobile' if any(ind in isp_lower for ind in mobile_indicators) else 'residential'
                else:
                    result['connection_type'] = 'residential'
            else:
                result['error'] = 'No se pudo obtener IP del proxy'
            
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout al conectar con el proxy (>25s)'
        except requests.exceptions.ProxyError as e:
            error_str = str(e)
            if '407' in error_str:
                result['error'] = 'Error 407: Autenticación fallida - verifica credenciales SOAX'
            else:
                result['error'] = f'Error de proxy: {error_str[:100]}'
        except requests.exceptions.ConnectionError as e:
            result['error'] = f'Error de conexión: Verifica saldo en SOAX'
        except Exception as e:
            result['error'] = f'Error: {str(e)[:100]}'
        
        return result  
    def _generate_session_id(self) -> str:
        """
        Genera un ID de sesión único en formato SOAX
        Formato: 16 caracteres alfanuméricos (mayúsculas y minúsculas)
        Ejemplo: 0lVgdzCHC2e9LAOW
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(16))
    
    def get_active_sessions(self) -> Dict:
        """Retorna sesiones activas"""
        # Limpiar sesiones expiradas
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


class ThreeXUIManager:
    """Gestor para 3x-ui VPN panel"""
    
    def __init__(self, panel_url: str, username: str, password: str, inbound_id: int):
        """
        Inicializa el gestor de 3x-ui
        
        Args:
            panel_url: URL del panel 3x-ui
            username: Usuario del panel
            password: Contraseña del panel
            inbound_id: ID del inbound a usar
        """
        self.panel_url = panel_url.rstrip('/')
        self.username = username
        self.password = password
        self.inbound_id = inbound_id
        self.session = requests.Session()
        self._login()
    
    def _login(self):
        """Inicia sesión en el panel 3x-ui"""
        try:
            response = self.session.post(
                f"{self.panel_url}/login",
                data={
                    'username': self.username,
                    'password': self.password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Sesión iniciada en 3x-ui")
            else:
                raise Exception(f"Error de login: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"No se pudo conectar con 3x-ui: {e}")
    
    def create_client(self, email: str, total_gb: int = 50, expiry_days: int = 30) -> Dict:
        """
        Crea un nuevo cliente en el inbound
        
        Args:
            email: Email/identificador del cliente
            total_gb: GB totales permitidos
            expiry_days: Días hasta expiración
        
        Returns:
            Dict con datos del cliente creado
        """
        import uuid
        
        client_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'enable': True,
            'expiryTime': int(time.time() * 1000) + (expiry_days * 24 * 60 * 60 * 1000),
            'totalGB': total_gb * 1024 * 1024 * 1024,
            'flow': ''
        }
        
        try:
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/addClient",
                json={
                    'id': self.inbound_id,
                    'settings': {
                        'clients': [client_data]
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Cliente 3x-ui creado: {email}")
                return client_data
            else:
                raise Exception(f"Error creando cliente: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Error en 3x-ui: {e}")
    
    def get_client_link(self, client_id: str) -> str:
        """Obtiene el link de conexión del cliente"""
        return f"vless://{client_id}@{self.panel_url.replace('http://', '')}:443"
    
    def delete_client(self, client_id: str) -> bool:
        """Elimina un cliente"""
        try:
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/delClient/{self.inbound_id}/{client_id}",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False