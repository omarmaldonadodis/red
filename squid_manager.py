# squid_manager.py
"""
Gestor de Squid Proxy para monitoreo de tráfico SOAX
"""

import subprocess
import os
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class SquidManager:
    """
    Gestor completo de Squid para Mac INTEL
    
    Rutas adaptadas a:
    /usr/local/etc/squid/
    /usr/local/var/logs/
    /usr/local/var/cache/squid/
    """
    
    def __init__(self, 
                 config_path: str = "/usr/local/etc/squid/squid.conf",
                 log_path: str = "/usr/local/var/logs/squid_access.log"):
        """
        Inicializa el gestor de Squid
        
        Args:
            config_path: Ruta al archivo squid.conf
            log_path: Ruta al archivo de log de acceso
        """
        self.config_path = config_path
        self.log_path = log_path
        self.cache_log_path = "/usr/local/var/logs/squid_cache.log"
        
        # Verificar que Squid esté instalado
        if not self._is_squid_installed():
            raise Exception(
                "Squid no está instalado.\n"
                "Instala con: brew install squid"
            )
        
        logger.info("✅ Squid Manager inicializado")
    
    def _is_squid_installed(self) -> bool:
        """Verifica si Squid está instalado"""
        try:
            result = subprocess.run(
                ['which', 'squid'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def is_running(self) -> bool:
        """Verifica si Squid está corriendo"""
        try:
            result = subprocess.run(
                ['brew', 'services', 'list'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'squid' in line.lower():
                    return 'started' in line.lower()
            
            return False
        except:
            return False
    
    def start(self) -> bool:
        """Inicia Squid"""
        try:
            logger.info("🚀 Iniciando Squid...")
            
            result = subprocess.run(
                ['brew', 'services', 'start', 'squid'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Squid iniciado")
                return True
            else:
                logger.error(f"❌ Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Error iniciando Squid: {e}")
            return False
    
    def stop(self) -> bool:
        """Detiene Squid"""
        try:
            logger.info("🛑 Deteniendo Squid...")
            
            result = subprocess.run(
                ['brew', 'services', 'stop', 'squid'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Squid detenido")
                return True
            else:
                logger.error(f"❌ Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deteniendo Squid: {e}")
            return False
    
    def restart(self) -> bool:
        """Reinicia Squid"""
        try:
            logger.info("🔄 Reiniciando Squid...")
            
            result = subprocess.run(
                ['brew', 'services', 'restart', 'squid'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Squid reiniciado")
                return True
            else:
                logger.error(f"❌ Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Error reiniciando Squid: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Obtiene estado completo de Squid"""
        return {
            'running': self.is_running(),
            'config_exists': os.path.exists(self.config_path),
            'log_exists': os.path.exists(self.log_path),
            'log_size_mb': self._get_log_size_mb()
        }
    
    def _get_log_size_mb(self) -> float:
        """Obtiene tamaño del log en MB"""
        try:
            if os.path.exists(self.log_path):
                size_bytes = os.path.getsize(self.log_path)
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except:
            return 0.0
    
    def update_soax_credentials(self, username: str, password: str) -> bool:
        """
        Actualiza credenciales SOAX en squid.conf
        """
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
                return False
            
            # Leer configuración actual
            with open(self.config_path, 'r') as f:
                config = f.read()
            
            pattern = r'cache_peer proxy\.soax\.com parent \d+ \d+ no-query no-digest login=([^:]+):(.+)'
            new_line = f'cache_peer proxy.soax.com parent 5000 0 no-query no-digest login={username}:{password}'
            
            if re.search(pattern, config):
                config = re.sub(pattern, new_line, config)
            else:
                config = config.replace(
                    'http_port 3128',
                    f'http_port 3128\n\n# SOAX Parent Proxy\n{new_line}\nnever_direct allow all'
                )
            
            with open(self.config_path, 'w') as f:
                f.write(config)
            
            logger.info("✅ Credenciales SOAX actualizadas en squid.conf")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando credenciales: {e}")
            return False

    # --- EL RESTO DEL ARCHIVO SIGUE IGUAL ---
    # NO TOCO NINGUNA LÓGICA DE PARSEO NI ESTADÍSTICAS
    # SOLO CAMBIAMOS RUTAS ARRIBA


    
    def parse_logs(self, 
                   lines: int = None,
                   profile_id: str = None) -> Dict:
        """
        Parsea logs de Squid para obtener estadísticas
        
        Args:
            lines: Número de líneas a parsear (None = todas)
            profile_id: Filtrar por perfil específico
        
        Returns:
            Dict con estadísticas
        """
        if not os.path.exists(self.log_path):
            logger.error(f"Log no encontrado: {self.log_path}")
            return {}
        
        stats = defaultdict(lambda: {
            'total_bytes': 0,
            'upload_bytes': 0,
            'download_bytes': 0,
            'requests': 0,
            'urls': [],
            'last_access': None,
            'first_access': None
        })
        
        try:
            with open(self.log_path, 'r') as f:
                log_lines = f.readlines()
            
            # Limitar líneas si se especificó
            if lines:
                log_lines = log_lines[-lines:]
            
            # Formato del log Squid:
            # timestamp duration client code/status bytes method URL rfc931 peerstatus/peerhost type
            
            for line in log_lines:
                parts = line.split()
                
                if len(parts) < 10:
                    continue
                
                try:
                    timestamp = float(parts[0])
                    duration = int(parts[1])
                    client = parts[2]
                    status = parts[3]
                    bytes_transferred = int(parts[4])
                    method = parts[5]
                    url = parts[6]
                    
                    # Filtrar por perfil si se especificó
                    if profile_id and profile_id not in url:
                        continue
                    
                    # Acumular estadísticas
                    stats[client]['total_bytes'] += bytes_transferred
                    stats[client]['requests'] += 1
                    
                    # Diferenciar upload vs download por método
                    if method in ['POST', 'PUT', 'PATCH']:
                        stats[client]['upload_bytes'] += bytes_transferred
                    else:
                        stats[client]['download_bytes'] += bytes_transferred
                    
                    # Guardar URL (máximo 100)
                    if len(stats[client]['urls']) < 100:
                        stats[client]['urls'].append(url)
                    
                    # Timestamps
                    access_time = datetime.fromtimestamp(timestamp)
                    if not stats[client]['first_access']:
                        stats[client]['first_access'] = access_time.isoformat()
                    stats[client]['last_access'] = access_time.isoformat()
                    
                except (ValueError, IndexError) as e:
                    continue
            
            # Convertir a MB y agregar más info
            for client in stats:
                stats[client]['total_mb'] = round(stats[client]['total_bytes'] / (1024 * 1024), 2)
                stats[client]['upload_mb'] = round(stats[client]['upload_bytes'] / (1024 * 1024), 2)
                stats[client]['download_mb'] = round(stats[client]['download_bytes'] / (1024 * 1024), 2)
            
            return dict(stats)
            
        except Exception as e:
            logger.error(f"❌ Error parseando logs: {e}")
            return {}
    
    def get_profile_stats(self, profile_id: str) -> Dict:
        """
        Obtiene estadísticas de un perfil específico
        
        Args:
            profile_id: ID del perfil
        
        Returns:
            Dict con estadísticas del perfil
        """
        all_stats = self.parse_logs(profile_id=profile_id)
        
        # Sumar estadísticas de todos los clientes relacionados al perfil
        total_stats = {
            'profile_id': profile_id,
            'total_mb': 0,
            'upload_mb': 0,
            'download_mb': 0,
            'requests': 0,
            'clients': []
        }
        
        for client, stats in all_stats.items():
            total_stats['total_mb'] += stats['total_mb']
            total_stats['upload_mb'] += stats['upload_mb']
            total_stats['download_mb'] += stats['download_mb']
            total_stats['requests'] += stats['requests']
            total_stats['clients'].append({
                'ip': client,
                'stats': stats
            })
        
        return total_stats
    
    def get_total_usage(self) -> Dict:
        """Obtiene uso total de todos los perfiles"""
        all_stats = self.parse_logs()
        
        total = {
            'total_mb': 0,
            'upload_mb': 0,
            'download_mb': 0,
            'requests': 0,
            'unique_clients': len(all_stats)
        }
        
        for client, stats in all_stats.items():
            total['total_mb'] += stats['total_mb']
            total['upload_mb'] += stats['upload_mb']
            total['download_mb'] += stats['download_mb']
            total['requests'] += stats['requests']
        
        return total
    
    def clear_logs(self) -> bool:
        """Limpia los logs de Squid"""
        try:
            # Rotar logs
            if os.path.exists(self.log_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.log_path}.{timestamp}"
                os.rename(self.log_path, backup_path)
                logger.info(f"✅ Log respaldado en: {backup_path}")
            
            # Crear nuevo log vacío
            open(self.log_path, 'w').close()
            
            # Reiniciar Squid para que use el nuevo log
            self.restart()
            
            logger.info("✅ Logs limpiados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error limpiando logs: {e}")
            return False
    
    def test_proxy(self, timeout: int = 10) -> Dict:
        """
        Prueba el proxy Squid
        
        Returns:
            Dict con resultado del test
        """
        import requests
        
        result = {
            'success': False,
            'ip': None,
            'response_time': None,
            'error': None
        }
        
        proxy_url = "http://127.0.0.1:3128"
        
        try:
            import time
            start = time.time()
            
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                },
                timeout=timeout
            )
            
            end = time.time()
            
            result['success'] = True
            result['ip'] = response.json().get('ip')
            result['response_time'] = round(end - start, 2)
            
            logger.info(f"✅ Proxy funcionando - IP: {result['ip']}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ Error probando proxy: {e}")
        
        return result
    
    def print_status_report(self):
        """Imprime reporte de estado de Squid"""
        status = self.get_status()
        
        print("\n" + "=" * 70)
        print("📊 ESTADO DE SQUID")
        print("=" * 70)
        
        print(f"\n🔧 Servicio:")
        print(f"   Estado: {'🟢 CORRIENDO' if status['running'] else '🔴 DETENIDO'}")
        
        print(f"\n📁 Archivos:")
        print(f"   Config: {'✅' if status['config_exists'] else '❌'} {self.config_path}")
        print(f"   Log: {'✅' if status['log_exists'] else '❌'} {self.log_path}")
        print(f"   Tamaño log: {status['log_size_mb']} MB")
        
        if status['running']:
            # Test de conectividad
            test = self.test_proxy()
            print(f"\n🌐 Conectividad:")
            print(f"   Proxy: {'✅ OK' if test['success'] else '❌ FALLO'}")
            if test['success']:
                print(f"   IP SOAX: {test['ip']}")
                print(f"   Tiempo: {test['response_time']}s")
            else:
                print(f"   Error: {test['error']}")
            
            # Estadísticas de uso
            usage = self.get_total_usage()
            print(f"\n📈 Uso Total:")
            print(f"   Datos: {usage['total_mb']:.2f} MB")
            print(f"   Upload: {usage['upload_mb']:.2f} MB")
            print(f"   Download: {usage['download_mb']:.2f} MB")
            print(f"   Requests: {usage['requests']}")
            print(f"   Clientes únicos: {usage['unique_clients']}")
        
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    # Test rápido
    try:
        squid = SquidManager()
        squid.print_status_report()
    except Exception as e:
        print(f"Error: {e}")