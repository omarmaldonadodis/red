# utils.py
import os
import json
import time
from datetime import datetime
from typing import Dict, Any
import logging

def setup_directories():
    """Crea las carpetas necesarias si no existen"""
    directories = [
        'profiles',
        'profiles/profile_data',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def setup_logging():
    """Configura el sistema de logging"""
    log_filename = f"logs/account_creator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def save_profile_data(profile_id: str, data: Dict[str, Any]):
    """Guarda datos de un perfil en JSON"""
    filename = f"profiles/profile_data/{profile_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Datos del perfil guardados: {filename}")

def load_profile_data(profile_id: str) -> Dict[str, Any]:
    """Carga datos de un perfil desde JSON"""
    filename = f"profiles/profile_data/{profile_id}.json"
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_duration(seconds: int) -> str:
    """Formatea segundos a formato legible"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def print_header(title: str, width: int = 70):
    """Imprime un header formateado"""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")

def print_section(title: str, width: int = 70):
    """Imprime una sección formateada"""
    print("\n" + "-" * width)
    print(f"  {title}")
    print("-" * width)

def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Imprime mensaje de advertencia"""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")

def wait_with_progress(seconds: int, message: str = "Esperando"):
    """Espera con barra de progreso"""
    from tqdm import tqdm
    
    for _ in tqdm(range(seconds), desc=message, unit="s"):
        time.sleep(1)

def get_user_input(prompt: str, default: Any = None, input_type: type = str) -> Any:
    """Obtiene input del usuario con validación"""
    while True:
        if default is not None:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
            if not user_input:
                print_warning("Input no puede estar vacío")
                continue
        
        try:
            return input_type(user_input)
        except ValueError:
            print_error(f"Input debe ser de tipo {input_type.__name__}")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Obtiene respuesta sí/no del usuario"""
    default_str = "S/n" if default else "s/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['s', 'si', 'sí', 'y', 'yes']

def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

class ProgressTracker:
    """Tracker de progreso para operaciones largas"""
    
    def __init__(self, total: int, description: str = "Progreso"):
        from tqdm import tqdm
        self.pbar = tqdm(total=total, desc=description, unit="perfil")
        self.completed = 0
        self.failed = 0
    
    def update(self, success: bool = True):
        """Actualiza el progreso"""
        self.pbar.update(1)
        if success:
            self.completed += 1
        else:
            self.failed += 1
    
    def close(self):
        """Cierra la barra de progreso"""
        self.pbar.close()
    
    def get_summary(self) -> str:
        """Retorna resumen del progreso"""
        total = self.completed + self.failed
        return f"Completados: {self.completed}/{total} | Fallidos: {self.failed}/{total}"