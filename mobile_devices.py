# mobile_devices.py - CORREGIDO CON VALORES COMPATIBLES ADSPOWER
"""
Base de datos de dispositivos móviles reales con fingerprints ultrarrealistas
IMPORTANTE: hardware_concurrency solo acepta: 2,3,4,6,8,10,12,16,20,24,32,64
IMPORTANTE: device_memory solo acepta: 2,4,6,8,16,32,64,128
"""

MOBILE_DEVICES = {
    # ==========================================
    # SAMSUNG GALAXY (ANDROID)
    # ==========================================
    'samsung_s24_ultra': {
        'name': 'Samsung Galaxy S24 Ultra',
        'screen_size': '6.8"',
        'resolution': '1440x3120',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 750',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '120.0.6099.230',
    },
    
    'samsung_s23_ultra': {
        'name': 'Samsung Galaxy S23 Ultra',
        'screen_size': '6.8"',
        'resolution': '1440x3088',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.194 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 740',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '119.0.6045.194',
    },
    
    'samsung_s24_plus': {
        'name': 'Samsung Galaxy S24+',
        'screen_size': '6.7"',
        'resolution': '1440x3120',
        'viewport': '412x914',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 750',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '120.0.6099.144',
    },
    
    'samsung_a54': {
        'name': 'Samsung Galaxy A54 5G',
        'screen_size': '6.4"',
        'resolution': '1080x2340',
        'viewport': '412x915',
        'pixel_ratio': 2.625,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 8,  # ✅ Compatible
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Mali-G68',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '119.0.6045.193',
    },
    
    # ==========================================
    # APPLE IPHONE (iOS)
    # ==========================================
    'iphone_15_pro_max': {
        'name': 'iPhone 15 Pro Max',
        'screen_size': '6.7"',
        'resolution': '1290x2796',
        'viewport': '430x932',
        'pixel_ratio': 3.0,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        'platform': 'iPhone',
        'hardware_concurrency': 6,  # ✅ Compatible
        'device_memory': 8,  # ✅ Compatible
        'max_touch_points': 5,
        'vendor': 'Apple Computer, Inc.',
        'renderer': 'Apple GPU',
        'languages': ['es-EC', 'es-US', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '605.1.15',
        'safari_version': '17.5',
    },
    
    'iphone_15_plus': {
        'name': 'iPhone 15 Plus',
        'screen_size': '6.7"',
        'resolution': '1290x2796',
        'viewport': '430x932',
        'pixel_ratio': 3.0,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        'platform': 'iPhone',
        'hardware_concurrency': 6,  # ✅ Compatible
        'device_memory': 6,  # ✅ Compatible (redondeado de 6GB)
        'max_touch_points': 5,
        'vendor': 'Apple Computer, Inc.',
        'renderer': 'Apple GPU',
        'languages': ['es-EC', 'es-US', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '605.1.15',
        'safari_version': '17.4',
    },
    
    'iphone_14_pro_max': {
        'name': 'iPhone 14 Pro Max',
        'screen_size': '6.7"',
        'resolution': '1290x2796',
        'viewport': '430x932',
        'pixel_ratio': 3.0,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
        'platform': 'iPhone',
        'hardware_concurrency': 6,  # ✅ Compatible
        'device_memory': 6,  # ✅ Compatible
        'max_touch_points': 5,
        'vendor': 'Apple Computer, Inc.',
        'renderer': 'Apple GPU',
        'languages': ['es-EC', 'es-US', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '605.1.15',
        'safari_version': '17.3',
    },
    
    # ==========================================
    # GOOGLE PIXEL (ANDROID)
    # ==========================================
    'pixel_8_pro': {
        'name': 'Google Pixel 8 Pro',
        'screen_size': '6.7"',
        'resolution': '1344x2992',
        'viewport': '448x998',
        'pixel_ratio': 3.0,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 10,  # ✅ Compatible (era 9, ahora 10)
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Mali-G715',
        'languages': ['es-EC', 'es-419', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '120.0.6099.230',
    },
    
    'pixel_7_pro': {
        'name': 'Google Pixel 7 Pro',
        'screen_size': '6.7"',
        'resolution': '1440x3120',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.194 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 5,
        'vendor': 'Google Inc.',
        'renderer': 'Mali-G710',
        'languages': ['es-EC', 'es-419', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '119.0.6045.194',
    },
    
    # ==========================================
    # XIAOMI (ANDROID)
    # ==========================================
    'xiaomi_14_ultra': {
        'name': 'Xiaomi 14 Ultra',
        'screen_size': '6.73"',
        'resolution': '1440x3200',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; 2405CPH3DC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible
        'max_touch_points': 10,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 750',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '120.0.6099.144',
    },
    
    'xiaomi_13_pro': {
        'name': 'Xiaomi 13 Pro',
        'screen_size': '6.73"',
        'resolution': '1440x3200',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; 2210132C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible (era 12, ahora 16)
        'max_touch_points': 10,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 740',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '119.0.6045.193',
    },
    
    # ==========================================
    # ONEPLUS (ANDROID)
    # ==========================================
    'oneplus_12': {
        'name': 'OnePlus 12',
        'screen_size': '6.82"',
        'resolution': '1440x3168',
        'viewport': '412x915',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; CPH2583) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible
        'max_touch_points': 10,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 750',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '120.0.6099.230',
    },
    
    'oneplus_11': {
        'name': 'OnePlus 11',
        'screen_size': '6.7"',
        'resolution': '1440x3216',
        'viewport': '412x918',
        'pixel_ratio': 3.5,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14; CPH2449) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.194 Mobile Safari/537.36',
        'platform': 'Linux armv81',
        'hardware_concurrency': 8,  # ✅ Compatible
        'device_memory': 16,  # ✅ Compatible
        'max_touch_points': 10,
        'vendor': 'Google Inc.',
        'renderer': 'Adreno (TM) 740',
        'languages': ['es-EC', 'es', 'en-US', 'en'],
        'timezone_offset': -300,
        'color_depth': 32,
        'webkit_version': '537.36',
        'chrome_version': '119.0.6045.194',
    },
}


def get_random_mobile_device():
    """Retorna un dispositivo móvil aleatorio"""
    import random
    device_id = random.choice(list(MOBILE_DEVICES.keys()))
    return device_id, MOBILE_DEVICES[device_id]


def get_device_by_id(device_id: str):
    """Retorna un dispositivo específico por ID"""
    return MOBILE_DEVICES.get(device_id)


def get_all_device_ids():
    """Retorna lista de todos los IDs de dispositivos"""
    return list(MOBILE_DEVICES.keys())


def get_devices_by_brand(brand: str):
    """Retorna dispositivos de una marca específica"""
    brand = brand.lower()
    return {k: v for k, v in MOBILE_DEVICES.items() if k.startswith(brand)}


def list_devices_menu():
    """Muestra menú interactivo de dispositivos"""
    brands = {}
    for device_id, device in MOBILE_DEVICES.items():
        brand = device_id.split('_')[0].title()
        if brand not in brands:
            brands[brand] = []
        brands[brand].append((device_id, device))
    
    print("\n" + "="*70)
    print("DISPOSITIVOS MÓVILES DISPONIBLES".center(70))
    print("="*70)
    
    for brand, devices in sorted(brands.items()):
        print(f"\n📱 {brand}:")
        for device_id, device in devices:
            print(f"   • {device['name']:<30} ({device['screen_size']}, {device['hardware_concurrency']} cores)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    list_devices_menu()