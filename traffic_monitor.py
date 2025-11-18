# traffic_monitor.py
import json
import os
from typing import Dict, List
from datetime import datetime
from utils import load_profile_data, save_profile_data
import logging

logger = logging.getLogger(__name__)

class TrafficMonitor:
    """Monitor de tráfico de datos para perfiles con 3x-ui"""
    
    def __init__(self, threexui_manager):
        """
        Inicializa el monitor de tráfico
        
        Args:
            threexui_manager: Instancia de ThreeXUIManager
        """
        self.threexui = threexui_manager
    
    def get_profile_traffic(self, profile_id: str) -> Dict:
        """
        Obtiene estadísticas de tráfico de un perfil específico
        
        Args:
            profile_id: ID del perfil en AdsPower
        
        Returns:
            Dict con estadísticas de tráfico
        """
        # Cargar datos del perfil
        profile_data = load_profile_data(profile_id)
        
        if not profile_data:
            return {'error': 'Perfil no encontrado'}
        
        # Verificar si tiene cliente 3x-ui
        threexui_client = profile_data.get('threexui_client')
        
        if not threexui_client or 'error' in threexui_client:
            return {'error': 'Perfil sin cliente 3x-ui'}
        
        # Obtener tráfico desde 3x-ui
        client_email = threexui_client.get('email')
        traffic = self.threexui.get_client_traffic(client_email)
        
        if 'error' in traffic:
            return traffic
        
        # Agregar info del perfil
        traffic['profile_id'] = profile_id
        traffic['profile_name'] = profile_data['profile_config']['name']
        traffic['created_at'] = profile_data.get('created_at')
        
        # Guardar última consulta
        profile_data['last_traffic_check'] = {
            'timestamp': datetime.now().isoformat(),
            'usage_mb': traffic['total_used_mb'],
            'percentage': traffic['percentage_used']
        }
        save_profile_data(profile_id, profile_data)
        
        return traffic
    
    def get_all_profiles_traffic(self) -> List[Dict]:
        """
        Obtiene tráfico de todos los perfiles con 3x-ui
        
        Returns:
            Lista de dicts con estadísticas de cada perfil
        """
        profiles_dir = 'profiles/profile_data'
        
        if not os.path.exists(profiles_dir):
            return []
        
        all_traffic = []
        
        # Iterar sobre todos los archivos de perfil
        for filename in os.listdir(profiles_dir):
            if not filename.endswith('.json'):
                continue
            
            profile_id = filename.replace('.json', '')
            
            try:
                traffic = self.get_profile_traffic(profile_id)
                
                if 'error' not in traffic:
                    all_traffic.append(traffic)
                    
            except Exception as e:
                logger.warning(f"Error obteniendo tráfico de {profile_id}: {e}")
        
        # Ordenar por uso (mayor a menor)
        all_traffic.sort(key=lambda x: x.get('total_used_mb', 0), reverse=True)
        
        return all_traffic
    
    def get_top_consumers(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene los perfiles que más datos han consumido
        
        Args:
            limit: Número de perfiles a retornar
        
        Returns:
            Lista de perfiles ordenados por consumo
        """
        all_traffic = self.get_all_profiles_traffic()
        return all_traffic[:limit]
    
    def get_profiles_near_limit(self, threshold_percentage: float = 80.0) -> List[Dict]:
        """
        Obtiene perfiles que están cerca de su límite de datos
        
        Args:
            threshold_percentage: Porcentaje de uso para considerar "cerca del límite"
        
        Returns:
            Lista de perfiles cerca del límite
        """
        all_traffic = self.get_all_profiles_traffic()
        
        near_limit = [
            profile for profile in all_traffic
            if profile.get('percentage_used', 0) >= threshold_percentage
        ]
        
        return near_limit
    
    def reset_profile_traffic(self, profile_id: str) -> bool:
        """
        Resetea el tráfico de un perfil específico
        
        Args:
            profile_id: ID del perfil
        
        Returns:
            bool: True si exitoso
        """
        profile_data = load_profile_data(profile_id)
        
        if not profile_data:
            logger.error(f"Perfil {profile_id} no encontrado")
            return False
        
        threexui_client = profile_data.get('threexui_client')
        
        if not threexui_client or 'error' in threexui_client:
            logger.error(f"Perfil {profile_id} sin cliente 3x-ui")
            return False
        
        client_email = threexui_client.get('email')
        
        if self.threexui.reset_client_traffic(client_email):
            # Guardar evento de reset
            profile_data['traffic_resets'] = profile_data.get('traffic_resets', [])
            profile_data['traffic_resets'].append({
                'timestamp': datetime.now().isoformat(),
                'previous_usage_mb': profile_data.get('last_traffic_check', {}).get('usage_mb', 0)
            })
            save_profile_data(profile_id, profile_data)
            
            logger.info(f"✅ Tráfico reseteado para perfil {profile_id}")
            return True
        
        return False
    
    def update_profile_limit(self, profile_id: str, new_limit_gb: int) -> bool:
        """
        Actualiza el límite de datos de un perfil
        
        Args:
            profile_id: ID del perfil
            new_limit_gb: Nuevo límite en GB
        
        Returns:
            bool: True si exitoso
        """
        profile_data = load_profile_data(profile_id)
        
        if not profile_data:
            return False
        
        threexui_client = profile_data.get('threexui_client')
        
        if not threexui_client or 'error' in threexui_client:
            return False
        
        client_email = threexui_client.get('email')
        
        if self.threexui.update_client_limit(client_email, new_limit_gb):
            # Actualizar en datos guardados
            threexui_client['total_gb'] = new_limit_gb
            profile_data['threexui_client'] = threexui_client
            save_profile_data(profile_id, profile_data)
            
            logger.info(f"✅ Límite actualizado: {profile_id} → {new_limit_gb} GB")
            return True
        
        return False
    
    def print_traffic_report(self, profiles: List[Dict] = None):
        """
        Imprime reporte formateado de tráfico
        
        Args:
            profiles: Lista de perfiles (None = todos)
        """
        if profiles is None:
            profiles = self.get_all_profiles_traffic()
        
        if not profiles:
            print("📊 No hay datos de tráfico disponibles")
            return
        
        print("\n" + "=" * 90)
        print("📊 REPORTE DE TRÁFICO DE PERFILES".center(90))
        print("=" * 90)
        
        print(f"\n{'Perfil':<30} {'Usado':<15} {'Límite':<15} {'%':<10} {'Estado':<10}")
        print("-" * 90)
        
        for profile in profiles:
            name = profile.get('profile_name', 'N/A')[:28]
            used = f"{profile.get('total_used_mb', 0):.2f} MB"
            limit = f"{profile.get('total_limit_mb', 0):.2f} MB"
            percentage = profile.get('percentage_used', 0)
            
            # Determinar estado por color
            if percentage >= 90:
                status = "🔴 CRÍTICO"
            elif percentage >= 80:
                status = "🟡 ALTO"
            elif percentage >= 50:
                status = "🟢 MEDIO"
            else:
                status = "⚪ BAJO"
            
            print(f"{name:<30} {used:<15} {limit:<15} {percentage:<9.1f}% {status:<10}")
        
        print("-" * 90)
        
        # Estadísticas generales
        total_used = sum(p.get('total_used_mb', 0) for p in profiles)
        total_limit = sum(p.get('total_limit_mb', 0) for p in profiles)
        avg_percentage = sum(p.get('percentage_used', 0) for p in profiles) / len(profiles)
        
        print(f"\n📈 Estadísticas generales:")
        print(f"   Total perfiles: {len(profiles)}")
        print(f"   Consumo total: {total_used:.2f} MB")
        print(f"   Límite total: {total_limit:.2f} MB")
        print(f"   Uso promedio: {avg_percentage:.1f}%")
        print("=" * 90 + "\n")
    
    def export_traffic_report(self, filename: str = None) -> str:
        """
        Exporta reporte de tráfico a JSON
        
        Args:
            filename: Nombre del archivo (opcional)
        
        Returns:
            Path del archivo generado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"profiles/traffic_report_{timestamp}.json"
        
        all_traffic = self.get_all_profiles_traffic()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_profiles': len(all_traffic),
            'profiles': all_traffic,
            'summary': {
                'total_used_mb': sum(p.get('total_used_mb', 0) for p in all_traffic),
                'total_limit_mb': sum(p.get('total_limit_mb', 0) for p in all_traffic),
                'avg_percentage': sum(p.get('percentage_used', 0) for p in all_traffic) / len(all_traffic) if all_traffic else 0
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Reporte exportado: {filename}")
        
        return filename