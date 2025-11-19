# proxy_manager.py
import requests
import random
from typing import Dict, Optional, List
import time
import urllib3
import string
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

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
    """Gestor para 3x-ui VPN panel con autoconfiguración y monitoreo de tráfico"""
    
    def __init__(self, panel_url: str, username: str, password: str, inbound_id: int = None):
        """
        Inicializa el gestor de 3x-ui con autoconfiguración
        
        Args:
            panel_url: URL del panel 3x-ui
            username: Usuario del panel
            password: Contraseña del panel
            inbound_id: ID del inbound (None = auto-detectar)
        """
        self.panel_url = panel_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        # Login
        self._login()
        
        # Auto-configurar o validar inbound
        self.inbound_id = self._setup_inbound(inbound_id)
        
        logger.info(f"✅ 3x-ui inicializado - Usando Inbound ID: {self.inbound_id}")
    
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
                logger.info("✅ Sesión iniciada en 3x-ui")
            else:
                raise Exception(f"Error de login: HTTP {response.status_code}")
                
        except Exception as e:
            raise Exception(f"No se pudo conectar con 3x-ui: {e}")
    
    def _setup_inbound(self, requested_id: int = None) -> int:
        """
        Configura el inbound automáticamente
        
        Args:
            requested_id: ID solicitado (None = auto-detectar)
        
        Returns:
            int: ID del inbound a usar
        """
        logger.info("🔧 Configurando inbound para 3x-ui...")
        
        # Obtener lista de inbounds existentes
        existing_inbounds = self._get_inbound_list()
        
        if not existing_inbounds:
            logger.warning("⚠️  No hay inbounds existentes")
            
            # Crear inbound automáticamente
            logger.info("📦 Creando nuevo inbound para el sistema...")
            new_inbound_id = self._create_default_inbound()
            
            if new_inbound_id:
                logger.info(f"✅ Inbound creado exitosamente: ID {new_inbound_id}")
                return new_inbound_id
            else:
                raise Exception("No se pudo crear inbound automáticamente")
        
        # Si se especificó un ID, verificar que exista
        if requested_id is not None:
            exists = any(ib['id'] == requested_id for ib in existing_inbounds)
            
            if exists:
                logger.info(f"✅ Usando Inbound ID {requested_id} (especificado en .env)")
                return requested_id
            else:
                logger.warning(f"⚠️  Inbound ID {requested_id} no existe")
                logger.info(f"   Inbounds disponibles: {[ib['id'] for ib in existing_inbounds]}")
        
        # Auto-seleccionar el primer inbound disponible
        first_inbound = existing_inbounds[0]
        auto_id = first_inbound['id']
        
        logger.info(f"🔄 Auto-seleccionando Inbound ID {auto_id}")
        logger.info(f"   Puerto: {first_inbound.get('port')}")
        logger.info(f"   Protocolo: {first_inbound.get('protocol')}")
        
        return auto_id
    
    def _get_inbound_list(self) -> List[Dict]:
        """
        Obtiene lista de inbounds existentes
        
        Returns:
            Lista de inbounds
        """
        try:
            response = self.session.get(
                f"{self.panel_url}/panel/api/inbounds/list",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    return data.get('obj', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de inbounds: {e}")
            return []
    
    def _create_default_inbound(self) -> Optional[int]:
        """
        Crea un inbound por defecto para el sistema
        
        Returns:
            ID del inbound creado o None si falla
        """
        try:
            # Configuración por defecto
            inbound_config = {
                'enable': True,
                'port': 443,
                'protocol': 'vless',
                'settings': json.dumps({
                    'clients': [],
                    'decryption': 'none',
                    'fallbacks': []
                }),
                'streamSettings': json.dumps({
                    'network': 'tcp',
                    'security': 'none',
                    'tcpSettings': {
                        'header': {
                            'type': 'none'
                        }
                    }
                }),
                'remark': 'AdsPower Profiles System',
                'sniffing': json.dumps({
                    'enabled': True,
                    'destOverride': ['http', 'tls']
                })
            }
            
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/add",
                json=inbound_config,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    # Obtener el ID del inbound recién creado
                    inbounds = self._get_inbound_list()
                    
                    # Buscar el que tenga el remark que pusimos
                    for ib in inbounds:
                        if ib.get('remark') == 'AdsPower Profiles System':
                            return ib['id']
                    
                    # Si no lo encontramos, retornar el último
                    if inbounds:
                        return inbounds[-1]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error creando inbound: {e}")
            return None
    
    def create_client(self, 
                     email: str, 
                     total_gb: int = 50, 
                     expiry_days: int = 30,
                     profile_id: str = None) -> Dict:
        """
        Crea un nuevo cliente en el inbound con límite de datos
        
        Args:
            email: Email/identificador del cliente
            total_gb: GB totales permitidos
            expiry_days: Días hasta expiración
            profile_id: ID del perfil de AdsPower (para vincular)
        
        Returns:
            Dict con datos del cliente creado
        """
        client_uuid = str(uuid.uuid4())
        expiry_time = int(time.time() * 1000) + (expiry_days * 24 * 60 * 60 * 1000)
        total_bytes = total_gb * 1024 * 1024 * 1024
        
        client_data = {
            'id': client_uuid,
            'email': email,
            'enable': True,
            'expiryTime': expiry_time,
            'totalGB': total_bytes,
            'flow': '',
            'subId': profile_id or ''
        }
        
        try:
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/addClient",
                json={
                    'id': self.inbound_id,
                    'settings': json.dumps({
                        'clients': [client_data]
                    })
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logger.info(f"✅ Cliente 3x-ui creado: {email}")
                    logger.info(f"   UUID: {client_uuid}")
                    logger.info(f"   Límite: {total_gb} GB")
                    logger.info(f"   Expira: {expiry_days} días")
                    
                    return {
                        'uuid': client_uuid,
                        'email': email,
                        'total_gb': total_gb,
                        'expiry_days': expiry_days,
                        'expiry_time': expiry_time,
                        'profile_id': profile_id,
                        'inbound_id': self.inbound_id,
                        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    raise Exception(f"API error: {result.get('msg', 'Unknown')}")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error creando cliente: {e}")
            return {'error': str(e)}
    
    def get_client_traffic(self, client_email: str) -> Dict:
        """
        Obtiene estadísticas de tráfico de un cliente
        
        Args:
            client_email: Email del cliente
        
        Returns:
            Dict con estadísticas de tráfico
        """
        try:
            response = self.session.get(
                f"{self.panel_url}/panel/api/inbounds/get/{self.inbound_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                return {'error': f'HTTP {response.status_code}'}
            
            data = response.json()
            
            if not data.get('success'):
                return {'error': 'API returned success=false'}
            
            inbound = data.get('obj', {})
            
            if 'settings' in inbound:
                settings = json.loads(inbound['settings'])
                clients = settings.get('clients', [])
                
                for client in clients:
                    if client.get('email') == client_email:
                        up = client.get('up', 0)
                        down = client.get('down', 0)
                        total_used = up + down
                        total_limit = client.get('totalGB', 0)
                        
                        percentage_used = (total_used / total_limit * 100) if total_limit > 0 else 0
                        remaining = max(0, total_limit - total_used)
                        
                        return {
                            'email': client_email,
                            'upload_bytes': up,
                            'download_bytes': down,
                            'total_used_bytes': total_used,
                            'total_limit_bytes': total_limit,
                            'remaining_bytes': remaining,
                            'upload_mb': round(up / (1024 * 1024), 2),
                            'download_mb': round(down / (1024 * 1024), 2),
                            'total_used_mb': round(total_used / (1024 * 1024), 2),
                            'total_limit_mb': round(total_limit / (1024 * 1024), 2),
                            'remaining_mb': round(remaining / (1024 * 1024), 2),
                            'percentage_used': round(percentage_used, 2),
                            'enabled': client.get('enable', False),
                            'expiry_time': client.get('expiryTime', 0)
                        }
                
                return {'error': f'Cliente {client_email} no encontrado'}
            
            return {'error': 'Invalid response format'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def update_client_limit(self, client_email: str, new_limit_gb: int) -> bool:
        """Actualiza el límite de datos de un cliente"""
        try:
            response = self.session.get(
                f"{self.panel_url}/panel/api/inbounds/get/{self.inbound_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            if not data.get('success'):
                return False
            
            inbound = data.get('obj', {})
            settings = json.loads(inbound['settings'])
            clients = settings.get('clients', [])
            
            # Buscar y actualizar
            updated = False
            for client in clients:
                if client.get('email') == client_email:
                    client['totalGB'] = new_limit_gb * 1024 * 1024 * 1024
                    updated = True
                    break
            
            if not updated:
                return False
            
            # Actualizar en el servidor
            update_response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/update/{self.inbound_id}",
                json={
                    'settings': json.dumps(settings)
                },
                timeout=10
            )
            
            if update_response.status_code == 200:
                logger.info(f"✅ Límite actualizado: {client_email} → {new_limit_gb} GB")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando límite: {e}")
            return False
    
    def reset_client_traffic(self, client_email: str) -> bool:
        """Resetea las estadísticas de tráfico de un cliente"""
        try:
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/resetClientTraffic/{self.inbound_id}/{client_email}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logger.info(f"✅ Tráfico reseteado: {client_email}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error reseteando tráfico: {e}")
            return False
    
    def delete_client(self, client_uuid: str) -> bool:
        """Elimina un cliente"""
        try:
            response = self.session.post(
                f"{self.panel_url}/panel/api/inbounds/delClient/{self.inbound_id}/{client_uuid}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logger.info(f"✅ Cliente eliminado: {client_uuid}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando cliente: {e}")
            return False
    
    def get_inbound_info(self) -> Dict:
        """Obtiene información del inbound actual"""
        try:
            response = self.session.get(
                f"{self.panel_url}/panel/api/inbounds/get/{self.inbound_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    inbound = data.get('obj', {})
                    
                    # Contar clientes
                    client_count = 0
                    if 'settings' in inbound:
                        settings = json.loads(inbound['settings'])
                        client_count = len(settings.get('clients', []))
                    
                    return {
                        'id': inbound.get('id'),
                        'port': inbound.get('port'),
                        'protocol': inbound.get('protocol'),
                        'remark': inbound.get('remark', ''),
                        'enabled': inbound.get('enable', False),
                        'client_count': client_count,
                        'up': inbound.get('up', 0),
                        'down': inbound.get('down', 0)
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo info del inbound: {e}")
            return {}