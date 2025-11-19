# adspower_manager.py
import requests
import json
from typing import Optional, Dict, List
import time
import random

class AdsPowerManager:
    """Gestor completo de AdsPower API con autenticación correcta"""
    
    def __init__(self, api_url: str = "http://local.adspower.net:50325", api_key: str = None):
        """
        Inicializa el manager de AdsPower
        
        Args:
            api_url: URL de la API local de AdsPower
            api_key: API Key obtenida desde AdsPower Settings
        """
        self.api_url = api_url
        self.api_key = api_key
        
        if not api_key:
            raise ValueError(
                "❌ API Key es requerida.\n"
                "   Obtén tu API Key desde: AdsPower → Settings → API Settings"
            )
        
        # Verificar conexión
        self._test_connection()
    
    def _test_connection(self):
        """Verifica que la conexión con AdsPower sea válida"""
        try:
            response = self._make_request('GET', '/api/v1/user/list', params={'page': 1, 'page_size': 1})
            
            # Contar perfiles
            profiles = response.get('data', {}).get('list', [])
            total_profiles = len(profiles)
            
            print(f"✅ Conectado a AdsPower API")
            print(f"   Perfiles encontrados: {total_profiles}")
            
            if profiles:
                print(f"   Último perfil: {profiles[0].get('name', 'Sin nombre')}")
                
        except Exception as e:
            raise ConnectionError(
                f"❌ No se pudo conectar con AdsPower:\n"
                f"   {str(e)}\n\n"
                f"   Verifica que:\n"
                f"   1. AdsPower esté abierto y corriendo\n"
                f"   2. La API Key sea correcta (Settings → API Settings)\n"
                f"   3. El puerto {self.api_url.split(':')[-1]} esté disponible"
            )
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """
        Realiza peticiones a la API de AdsPower con API Key en el header
        
        FORMATO CORRECTO: Authorization: Bearer {api_key}
        
        Args:
            method: GET, POST, etc.
            endpoint: Endpoint de la API
            params: Query parameters
            json_data: JSON body para POST requests
        
        Returns:
            Dict con la respuesta de la API
        """
        url = f"{self.api_url}{endpoint}"
        
        # API Key va en el HEADER como Bearer token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # Params sin api_key
        if params is None:
            params = {}
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, params=params, json=json_data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            result = response.json()
            
            # Verificar código de respuesta de AdsPower
            if result.get('code') != 0:
                error_msg = result.get('msg', 'Unknown error')
                raise Exception(f"Error de AdsPower API: {error_msg}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en petición HTTP a AdsPower: {e}")
    
  # adspower_manager.py - MÉTODO create_profile CORREGIDO

    def create_profile(self, profile_config, proxy_config: Dict) -> str:
        """
        Crea un nuevo perfil en AdsPower con configuración completa
        """
        
        # Determinar configuraciones según tipo de dispositivo
        if profile_config.device_type == 'mobile':
            screen_resolutions = ["375_667", "414_896", "390_844", "393_851"]
            hardware_concurrency = random.choice([4, 6, 8])
            device_memory = random.choice([4, 6, 8])
        else:
            screen_resolutions = ["1920_1080", "1366_768", "1440_900", "1536_864", "2560_1440"]
            hardware_concurrency = random.choice([4, 8, 16])
            device_memory = random.choice([8, 16, 32])
        
        # Configuración del fingerprint
        fingerprint_data = {
            "name": f"{profile_config.name}_{profile_config.age}_{profile_config.proxy_type}",
            "group_id": "7937312",
            "domain_name": "",
            "open_urls": [],
            "repeat_config": ["0"],
            "username": "", 
            "password": "",
            "remark": json.dumps({
                'age': profile_config.age,
                'city': profile_config.city,
                'interests': profile_config.interests,
                'device_type': profile_config.device_type,
                'proxy_type': profile_config.proxy_type,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }),
            
            # Proxy configuration
            "user_proxy_config": {
                "proxy_soft": "other",
                "proxy_type": proxy_config.get('type', 'http'),
                "proxy_host": proxy_config['host'],
                "proxy_port": str(proxy_config['port']),
                "proxy_user": proxy_config['username'],
                "proxy_password": proxy_config['password']
            },
            
            # Fingerprint del navegador - CORREGIDO
            "fingerprint_config": {
                # Timezone y ubicación
                "automatic_timezone": "0",
                "timezone": profile_config.timezone,
                "webrtc": "proxy",
                "location": "ask",
                
                # Idiomas
                "language": [profile_config.language, "en-US"],
                "page_language": [profile_config.language, "en-US"],
                
                # User Agent
                "ua": profile_config.user_agent,
                
                # Resolución de pantalla
                "screen_resolution": random.choice(screen_resolutions),
                
                # Fonts
                "fonts": ["all"],
                
                # Canvas fingerprinting
                "canvas": "1",
                
                # WebGL fingerprinting
                "webgl_image": "1",
                "webgl": "1",
                
                # Audio fingerprinting
                "audio": "1",
                
                # Media devices
                "media_devices": "1",
                
                # Do Not Track
                "do_not_track": "default",
                
                # Hardware
                "hardware_concurrency": str(hardware_concurrency),
                "device_memory": str(device_memory),
                
                # Client Rects
                "client_rects": "1",
                
                # Speech Voices
                "speech_voices": "1",
                
                # Port Scan Protection
                "port_scan_protection": "1",
                
                # Platform
                "platform": "Win32" if profile_config.device_type == 'desktop' else "Linux armv81",
                
                # ELIMINADOS: random_ua (causa error)
            }
        }
        
        result = self._make_request('POST', '/api/v1/user/create', json_data=fingerprint_data)
        
        profile_id = result['data']['id']
        print(f"✅ Perfil creado exitosamente")
        print(f"   ID: {profile_id}")
        print(f"   Nombre: {fingerprint_data['name']}")
        print(f"   Tipo: {profile_config.device_type.upper()} ({profile_config.proxy_type})")
        
        return profile_id  
    def get_profile_list(self, page: int = 1, page_size: int = 100, group_id: Optional[str] = None) -> List[Dict]:
        """Obtiene lista de perfiles existentes"""
        params = {'page': page, 'page_size': page_size}
        if group_id:
            params['group_id'] = group_id
        
        result = self._make_request('GET', '/api/v1/user/list', params=params)
        return result['data']['list']
    
    def get_profile_detail(self, profile_id: str) -> Dict:
        """Obtiene detalles de un perfil específico"""
        result = self._make_request('GET', '/api/v1/user/detail', params={'user_id': profile_id})
        return result['data']
    
    def update_profile(self, profile_id: str, update_data: Dict) -> bool:
        """Actualiza un perfil existente"""
        update_data['user_id'] = profile_id
        result = self._make_request('POST', '/api/v1/user/update', json_data=update_data)
        print(f"✅ Perfil actualizado: {profile_id}")
        return True
    
    def delete_profile(self, profile_ids: List[str]) -> bool:
        """Elimina uno o más perfiles"""
        result = self._make_request('POST', '/api/v1/user/delete', json_data={'user_ids': profile_ids})
        print(f"✅ {len(profile_ids)} perfil(es) eliminado(s)")
        return True
    
    def open_browser(self, profile_id: str, headless: bool = False, disable_password_saving: bool = True) -> Dict:
        """Abre el navegador para un perfil"""
        launch_args = []
        
        if disable_password_saving:
            launch_args.append("--password-store=basic")
        
        params = {"user_id": profile_id, "headless": "1" if headless else "0"}
        
        if launch_args:
            params["launch_args"] = json.dumps(launch_args)
        
        result = self._make_request('GET', '/api/v1/browser/start', params=params)
        
        browser_data = {
            'ws_endpoint': result['data']['ws']['selenium'],
            'webdriver': result['data']['webdriver'],
            'debug_port': result['data']['debug_port'],
            'debugger_address': f"127.0.0.1:{result['data']['debug_port']}"
        }
        
        print(f"🌐 Navegador abierto")
        print(f"   Perfil ID: {profile_id}")
        print(f"   Debug Port: {browser_data['debug_port']}")
        
        return browser_data
    
    def close_browser(self, profile_id: str) -> bool:
        """Cierra el navegador de un perfil"""
        result = self._make_request('GET', '/api/v1/browser/stop', params={'user_id': profile_id})
        print(f"✅ Navegador cerrado: {profile_id}")
        return True
    
    def check_browser_status(self, profile_id: str) -> Dict:
        """Verifica el estado del navegador de un perfil"""
        result = self._make_request('GET', '/api/v1/browser/active', params={'user_id': profile_id})
        return result['data']
    
    def create_group(self, group_name: str) -> str:
        """Crea un nuevo grupo de perfiles"""
        result = self._make_request('POST', '/api/v1/group/create', json_data={'group_name': group_name})
        group_id = result['data']['group_id']
        print(f"✅ Grupo creado: {group_name} (ID: {group_id})")
        return group_id
    
    def get_groups(self) -> List[Dict]:
        """Obtiene lista de grupos"""
        result = self._make_request('GET', '/api/v1/group/list')
        return result['data']['list']