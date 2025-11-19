
"""
Proxy contador simple que registra el tráfico de cada perfil
AdsPower → Este Proxy → SOAX → Internet
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict
import socket
import struct

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrafficCounter:
    """Contador de tráfico por perfil"""
    
    def __init__(self, data_file: str = 'traffic_data.json'):
        self.data_file = data_file
        self.data = self._load_data()
        self._save_interval = 10  # Guardar cada 10 segundos
        self._last_save = datetime.now()
    
    def _load_data(self) -> Dict:
        """Carga datos guardados"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'profiles': {},
            'total_upload': 0,
            'total_download': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Guarda datos"""
        self.data['last_updated'] = datetime.now().isoformat()
        
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_traffic(self, profile_id: str, upload_bytes: int, download_bytes: int):
        """Registra tráfico de un perfil"""
        
        if profile_id not in self.data['profiles']:
            self.data['profiles'][profile_id] = {
                'upload': 0,
                'download': 0,
                'created_at': datetime.now().isoformat(),
                'session_count': 0
            }
        
        self.data['profiles'][profile_id]['upload'] += upload_bytes
        self.data['profiles'][profile_id]['download'] += download_bytes
        self.data['profiles'][profile_id]['last_active'] = datetime.now().isoformat()
        
        self.data['total_upload'] += upload_bytes
        self.data['total_download'] += download_bytes
        
        # Guardar periódicamente
        if (datetime.now() - self._last_save).seconds >= self._save_interval:
            self._save_data()
            self._last_save = datetime.now()
    
    def get_profile_stats(self, profile_id: str) -> Dict:
        """Obtiene estadísticas de un perfil"""
        if profile_id not in self.data['profiles']:
            return {
                'upload_mb': 0,
                'download_mb': 0,
                'total_mb': 0
            }
        
        profile = self.data['profiles'][profile_id]
        
        return {
            'upload_bytes': profile['upload'],
            'download_bytes': profile['download'],
            'upload_mb': round(profile['upload'] / (1024 * 1024), 2),
            'download_mb': round(profile['download'] / (1024 * 1024), 2),
            'total_mb': round((profile['upload'] + profile['download']) / (1024 * 1024), 2),
            'created_at': profile.get('created_at'),
            'last_active': profile.get('last_active')
        }
    
    def get_all_stats(self) -> Dict:
        """Obtiene estadísticas de todos los perfiles"""
        return {
            profile_id: self.get_profile_stats(profile_id)
            for profile_id in self.data['profiles'].keys()
        }
    
    def reset_profile(self, profile_id: str):
        """Resetea contador de un perfil"""
        if profile_id in self.data['profiles']:
            self.data['profiles'][profile_id]['upload'] = 0
            self.data['profiles'][profile_id]['download'] = 0
            self._save_data()


class SOCKS5ProxyServer:
    """
    Servidor proxy SOCKS5 que cuenta tráfico
    Compatible con AdsPower
    """
    
    def __init__(self, 
                 host: str = '127.0.0.1',
                 port: int = 9050,
                 upstream_proxy: Dict = None,
                 traffic_counter: TrafficCounter = None):
        """
        Inicializa el servidor proxy
        
        Args:
            host: IP local donde escuchar
            port: Puerto local
            upstream_proxy: Configuración del proxy SOAX
            traffic_counter: Contador de tráfico
        """
        self.host = host
        self.port = port
        self.upstream_proxy = upstream_proxy
        self.counter = traffic_counter or TrafficCounter()
        self.server = None
    
    async def start(self):
        """Inicia el servidor"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        addr = self.server.sockets[0].getsockname()
        logger.info(f"🚀 Proxy contador iniciado en {addr[0]}:{addr[1]}")
        logger.info(f"   Upstream: {self.upstream_proxy['host']}:{self.upstream_proxy['port']}")
        logger.info(f"   Configurar AdsPower para usar: SOCKS5 - {addr[0]}:{addr[1]}")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Maneja conexión de cliente"""
        
        client_addr = writer.get_extra_info('peername')
        profile_id = f"unknown_{client_addr[1]}"  # Temporal
        
        try:
            # SOCKS5 handshake
            version = await reader.read(1)
            
            if version != b'\x05':
                logger.warning(f"Versión SOCKS incorrecta desde {client_addr}")
                writer.close()
                await writer.wait_closed()
                return
            
            # Leer métodos de autenticación
            nmethods = ord(await reader.read(1))
            methods = await reader.read(nmethods)
            
            # Responder sin autenticación
            writer.write(b'\x05\x00')
            await writer.drain()
            
            # Leer solicitud de conexión
            request = await reader.read(4)
            
            if len(request) < 4:
                writer.close()
                await writer.wait_closed()
                return
            
            version, cmd, _, atyp = struct.unpack('BBBB', request)
            
            if cmd != 1:  # Solo CONNECT
                writer.write(b'\x05\x07\x00\x01' + b'\x00' * 6)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return
            
            # Leer destino
            if atyp == 1:  # IPv4
                addr = socket.inet_ntoa(await reader.read(4))
            elif atyp == 3:  # Dominio
                addr_len = ord(await reader.read(1))
                addr = (await reader.read(addr_len)).decode()
            else:
                writer.write(b'\x05\x08\x00\x01' + b'\x00' * 6)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return
            
            port_data = await reader.read(2)
            port = struct.unpack('>H', port_data)[0]
            
            # Intentar extraer profile_id del destino o mantener unknown
            # AdsPower puede incluir info en el user-agent o headers HTTP
            # Por ahora usamos una aproximación simple
            
            logger.info(f"📡 Conexión a {addr}:{port} desde {client_addr}")
            
            # Conectar al proxy upstream (SOAX)
            try:
                upstream_reader, upstream_writer = await self._connect_upstream(addr, port)
                
                # Responder éxito al cliente
                writer.write(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + struct.pack('>H', 0))
                await writer.drain()
                
                # Iniciar túnel bidireccional contando datos
                await self._tunnel(reader, writer, upstream_reader, upstream_writer, profile_id)
                
            except Exception as e:
                logger.error(f"Error conectando upstream: {e}")
                writer.write(b'\x05\x05\x00\x01' + b'\x00' * 6)
                await writer.drain()
            
        except Exception as e:
            logger.error(f"Error manejando cliente: {e}")
        
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def _connect_upstream(self, target_addr: str, target_port: int):
        """Conecta al proxy upstream (SOAX)"""
        
        # Conectar a SOAX
        reader, writer = await asyncio.open_connection(
            self.upstream_proxy['host'],
            self.upstream_proxy['port']
        )
        
        # SOCKS5 handshake con SOAX
        writer.write(b'\x05\x02\x00\x02')  # Versión 5, 2 métodos, sin auth y user/pass
        await writer.drain()
        
        response = await reader.read(2)
        
        if response[1] == 2:  # Usuario/contraseña requerido
            # Autenticación SOCKS5
            username = self.upstream_proxy['username'].encode()
            password = self.upstream_proxy['password'].encode()
            
            auth_request = bytes([1, len(username)]) + username + bytes([len(password)]) + password
            writer.write(auth_request)
            await writer.drain()
            
            auth_response = await reader.read(2)
            
            if auth_response[1] != 0:
                raise Exception("Autenticación SOAX fallida")
        
        # Solicitar conexión al destino a través de SOAX
        request = b'\x05\x01\x00'
        
        # Agregar destino
        if target_addr.replace('.', '').isdigit():  # IP
            request += b'\x01' + socket.inet_aton(target_addr)
        else:  # Dominio
            request += b'\x03' + bytes([len(target_addr)]) + target_addr.encode()
        
        request += struct.pack('>H', target_port)
        
        writer.write(request)
        await writer.drain()
        
        response = await reader.read(10)
        
        if response[1] != 0:
            raise Exception(f"SOAX rechazó conexión: código {response[1]}")
        
        return reader, writer
    
    async def _tunnel(self, 
                     client_reader: asyncio.StreamReader,
                     client_writer: asyncio.StreamWriter,
                     upstream_reader: asyncio.StreamReader,
                     upstream_writer: asyncio.StreamWriter,
                     profile_id: str):
        """Túnel bidireccional contando datos"""
        
        async def forward(reader, writer, direction: str):
            """Forward de datos contando bytes"""
            total_bytes = 0
            
            try:
                while True:
                    data = await reader.read(8192)
                    
                    if not data:
                        break
                    
                    total_bytes += len(data)
                    writer.write(data)
                    await writer.drain()
                
            except Exception as e:
                logger.debug(f"Error en {direction}: {e}")
            
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass
            
            return total_bytes
        
        # Ejecutar ambas direcciones simultáneamente
        client_to_upstream_task = asyncio.create_task(
            forward(client_reader, upstream_writer, "cliente→upstream")
        )
        
        upstream_to_client_task = asyncio.create_task(
            forward(upstream_reader, client_writer, "upstream→cliente")
        )
        
        # Esperar a que ambas terminen
        upload_bytes, download_bytes = await asyncio.gather(
            client_to_upstream_task,
            upstream_to_client_task,
            return_exceptions=True
        )
        
        # Registrar tráfico
        upload_bytes = upload_bytes if isinstance(upload_bytes, int) else 0
        download_bytes = download_bytes if isinstance(download_bytes, int) else 0
        
        if upload_bytes > 0 or download_bytes > 0:
            self.counter.add_traffic(profile_id, upload_bytes, download_bytes)
            logger.info(f"📊 {profile_id}: ↑{upload_bytes/1024:.1f}KB ↓{download_bytes/1024:.1f}KB")


def load_soax_config():
    """Carga configuración de SOAX desde .env"""
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv('SOAX_USERNAME', '')
    password = os.getenv('SOAX_PASSWORD', '')
    host = os.getenv('SOAX_PROXY_HOST', 'proxy.soax.com')
    port = int(os.getenv('SOAX_PROXY_PORT', '5000'))
    
    # Formato correcto SOAX
    if username.startswith('package-'):
        parts = username.split('-')
        if len(parts) >= 2:
            package_id = f"{parts[0]}-{parts[1]}"
        else:
            package_id = username
    else:
        package_id = username
    
    return {
        'username': package_id,
        'password': password,
        'host': host,
        'port': port
    }


async def main():
    """Función principal"""
    
    # Cargar config SOAX
    soax_config = load_soax_config()
    
    print("="*80)
    print("🎯 PROXY CONTADOR DE TRÁFICO")
    print("="*80)
    print(f"\n📡 Configuración:")
    print(f"   SOAX: {soax_config['host']}:{soax_config['port']}")
    print(f"   Package: {soax_config['username']}")
    print(f"\n🚀 Iniciando servidor...")
    
    # Crear contador
    counter = TrafficCounter('traffic_data.json')
    
    # Crear servidor proxy
    proxy = SOCKS5ProxyServer(
        host='127.0.0.1',
        port=9050,
        upstream_proxy=soax_config,
        traffic_counter=counter
    )
    
    # Iniciar
    try:
        await proxy.start()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deteniendo servidor...")
        counter._save_data()
        print("✅ Datos guardados")


if __name__ == "__main__":
    asyncio.run(main())