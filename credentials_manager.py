# credentials_manager.py
from dotenv import load_dotenv
import os
from typing import Optional

class CredentialsManager:
    """Gestor de credenciales del sistema"""
    
    def __init__(self, env_file: str = '.env'):
        """
        Inicializa el gestor de credenciales
        
        Args:
            env_file: Ruta al archivo .env
        """
        load_dotenv(env_file)
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Valida que las credenciales necesarias existan"""
        required = {
            'ADSPOWER_API_KEY': 'API Key de AdsPower (Settings → API Settings)',
            'ADSPOWER_API_URL': 'URL de AdsPower API',
            'SOAX_USERNAME': 'Username de SOAX',
            'SOAX_PASSWORD': 'Password de SOAX'
        }
        
        missing = []
        for key, description in required.items():
            value = os.getenv(key)
            if not value or value.strip() == '':
                missing.append(f"  ❌ {key}: {description}")
        
        if missing:
            print("\n" + "=" * 70)
            print("⚠️  CREDENCIALES FALTANTES")
            print("=" * 70)
            print("\nLas siguientes credenciales son requeridas:\n")
            print("\n".join(missing))
            print("\n💡 Solución: Ejecuta el asistente de configuración:")
            print("   python setup_credentials.py")
            print("\n   O edita manualmente el archivo .env")
            print("=" * 70 + "\n")
            raise ValueError("Credenciales incompletas")
    
    # AdsPower
    @property
    def adspower_url(self) -> str:
        return os.getenv('ADSPOWER_API_URL', 'http://local.adspower.net:50325')
    
    @property
    def adspower_api_key(self) -> str:
        return os.getenv('ADSPOWER_API_KEY')
    
    # SOAX
    @property
    def soax_username(self) -> str:
        return os.getenv('SOAX_USERNAME')
    
    @property
    def soax_password(self) -> str:
        return os.getenv('SOAX_PASSWORD')
    
    @property
    def soax_host(self) -> str:
        return os.getenv('SOAX_PROXY_HOST', 'proxy.soax.com')
    
    @property
    def soax_port(self) -> int:
        return int(os.getenv('SOAX_PROXY_PORT', 9999))
    
    # 3X-UI
    @property
    def use_3xui(self) -> bool:
        return os.getenv('USE_3XUI', 'false').lower() == 'true'
    
    @property
    def threexui_panel_url(self) -> Optional[str]:
        return os.getenv('THREEXUI_PANEL_URL') if self.use_3xui else None
    
    @property
    def threexui_username(self) -> Optional[str]:
        return os.getenv('THREEXUI_USERNAME') if self.use_3xui else None
    
    @property
    def threexui_password(self) -> Optional[str]:
        return os.getenv('THREEXUI_PASSWORD') if self.use_3xui else None
    
    @property
    def threexui_inbound_id(self) -> Optional[int]:
        val = os.getenv('THREEXUI_INBOUND_ID')
        return int(val) if val and self.use_3xui else None
    
    # Configuración general
    @property
    def default_country(self) -> str:
        return os.getenv('DEFAULT_COUNTRY', 'ec')
    
    @property
    def default_timezone(self) -> str:
        return os.getenv('DEFAULT_TIMEZONE', 'America/Guayaquil')
    
    @property
    def default_language(self) -> str:
        return os.getenv('DEFAULT_LANGUAGE', 'es-EC')
    
    # Configuración de warmup
    @property
    def warmup_min_duration(self) -> int:
        return int(os.getenv('WARMUP_MIN_DURATION', 30))
    
    @property
    def warmup_max_duration(self) -> int:
        return int(os.getenv('WARMUP_MAX_DURATION', 60))
    
    @property
    def warmup_min_sites(self) -> int:
        return int(os.getenv('WARMUP_MIN_SITES', 8))
    
    @property
    def warmup_max_sites(self) -> int:
        return int(os.getenv('WARMUP_MAX_SITES', 15))
    
    def get_summary(self) -> dict:
        """Retorna un resumen de la configuración actual"""
        return {
            'adspower': {
                'url': self.adspower_url,
                'api_key_configured': bool(self.adspower_api_key)
            },
            'soax': {
                'username': self.soax_username,
                'host': self.soax_host,
                'port': self.soax_port
            },
            '3xui': {
                'enabled': self.use_3xui,
                'configured': bool(self.threexui_panel_url) if self.use_3xui else False
            },
            'defaults': {
                'country': self.default_country,
                'timezone': self.default_timezone,
                'language': self.default_language
            },
            'warmup': {
                'duration': f"{self.warmup_min_duration}-{self.warmup_max_duration} min",
                'sites': f"{self.warmup_min_sites}-{self.warmup_max_sites}"
            }
        }