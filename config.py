# config.py
from dataclasses import dataclass, asdict
from typing import List, Dict
import random
from faker import Faker

@dataclass
class ProfileConfig:
    """Configuración de un perfil de usuario"""
    name: str
    age: int
    gender: str
    country: str
    city: str
    language: str
    timezone: str
    user_agent: str
    interests: List[str]
    browsing_history: List[str]
    proxy_type: str  # 'residential' o 'mobile'
    device_type: str  # 'desktop' o 'mobile'
    
    def to_dict(self):
        return asdict(self)

class ProfileGenerator:
    """Genera perfiles realistas con historiales coherentes"""
    
    # Datos específicos de Ecuador
    ECUADORIAN_CITIES = {
        'Quito': {'timezone': 'America/Guayaquil', 'population': 0.35},
        'Guayaquil': {'timezone': 'America/Guayaquil', 'population': 0.30},
        'Cuenca': {'timezone': 'America/Guayaquil', 'population': 0.10},
        'Santo Domingo': {'timezone': 'America/Guayaquil', 'population': 0.08},
        'Machala': {'timezone': 'America/Guayaquil', 'population': 0.07},
        'Ambato': {'timezone': 'America/Guayaquil', 'population': 0.05},
        'Portoviejo': {'timezone': 'America/Guayaquil', 'population': 0.03},
        'Loja': {'timezone': 'America/Guayaquil', 'population': 0.02}
    }
    
    ECUADORIAN_NAMES = {
        'male': [
            'José', 'Carlos', 'Luis', 'Miguel', 'Juan', 'Diego', 'Andrés',
            'Fernando', 'Jorge', 'Mario', 'Pablo', 'Daniel', 'Javier',
            'Alejandro', 'Ricardo', 'Mauricio', 'Sebastián', 'Gabriel'
        ],
        'female': [
            'María', 'Ana', 'Carmen', 'Rosa', 'Patricia', 'Diana', 'Sofía',
            'Gabriela', 'Andrea', 'Daniela', 'Carolina', 'Mónica', 'Isabel',
            'Fernanda', 'Valeria', 'Camila', 'Natalia', 'Jessica'
        ]
    }
    
    # Intereses por edad y tipo de dispositivo
    INTERESTS_BY_AGE_DESKTOP = {
        '18-25': [
            'gaming', 'social_media', 'streaming', 'music', 'sports',
            'technology', 'youtube', 'twitch', 'instagram', 'tiktok'
        ],
        '26-35': [
            'sports', 'news', 'finance', 'travel', 'technology',
            'business', 'investment', 'real_estate', 'cars', 'fitness'
        ],
        '36-50': [
            'news', 'business', 'real_estate', 'cooking', 'family',
            'health', 'politics', 'religion', 'gardening', 'diy'
        ],
        '50+': [
            'news', 'health', 'family', 'religion', 'gardening',
            'cooking', 'history', 'travel', 'retirement', 'grandchildren'
        ]
    }
    
    INTERESTS_BY_AGE_MOBILE = {
        '18-25': [
            'social_media', 'mobile_gaming', 'messaging', 'photos',
            'tiktok', 'instagram', 'snapchat', 'music_streaming'
        ],
        '26-35': [
            'messaging', 'social_media', 'news_apps', 'banking',
            'shopping', 'food_delivery', 'ride_sharing', 'fitness_apps'
        ],
        '36-50': [
            'messaging', 'email', 'news_apps', 'social_media',
            'banking', 'shopping', 'family_apps', 'health_apps'
        ],
        '50+': [
            'messaging', 'email', 'news_apps', 'weather',
            'family_apps', 'health_apps', 'religion_apps'
        ]
    }
    
    # Sitios web por interés (Desktop)
    SITES_BY_INTEREST_DESKTOP = {
        'gaming': [
            'steampowered.com', 'epicgames.com', 'twitch.tv',
            'ign.com', 'gamespot.com', 'kotaku.com', 'pcgamer.com'
        ],
        'sports': [
            'espn.com', 'goal.com', 'marca.com', 'as.com',
            'eluniverso.com/deportes', 'foxsports.com'
        ],
        'social_media': [
            'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'reddit.com', 'pinterest.com'
        ],
        'streaming': [
            'youtube.com', 'netflix.com', 'primevideo.com',
            'disneyplus.com', 'hbomax.com', 'twitch.tv'
        ],
        'music': [
            'spotify.com', 'youtube.com/music', 'soundcloud.com',
            'deezer.com', 'tidal.com', 'pandora.com'
        ],
        'news': [
            'eluniverso.com', 'elcomercio.com', 'bbc.com/mundo',
            'cnn.com/espanol', 'elpais.com', 'lavanguardia.com'
        ],
        'finance': [
            'bloomberg.com', 'investing.com', 'finance.yahoo.com',
            'marketwatch.com', 'cnbc.com', 'forbes.com'
        ],
        'technology': [
            'techcrunch.com', 'theverge.com', 'wired.com',
            'arstechnica.com', 'engadget.com', 'zdnet.com'
        ],
        'business': [
            'linkedin.com', 'forbes.com', 'bloomberg.com',
            'businessinsider.com', 'entrepreneur.com'
        ],
        'shopping': [
            'amazon.com', 'mercadolibre.com.ec', 'aliexpress.com',
            'ebay.com', 'walmart.com'
        ],
        'travel': [
            'booking.com', 'airbnb.com', 'tripadvisor.com',
            'expedia.com', 'kayak.com', 'skyscanner.com'
        ],
        'cooking': [
            'allrecipes.com', 'foodnetwork.com', 'tasty.co',
            'seriouseats.com', 'bonappetit.com'
        ],
        'health': [
            'webmd.com', 'healthline.com', 'mayoclinic.org',
            'medicalnewstoday.com', 'nih.gov'
        ]
    }
    
    # Sitios móviles (versiones mobile-optimized)
    SITES_BY_INTEREST_MOBILE = {
        'social_media': [
            'm.facebook.com', 'mobile.twitter.com', 'instagram.com',
            'reddit.com', 'pinterest.com'
        ],
        'mobile_gaming': [
            'play.google.com', 'apps.apple.com', 'mobilegamer.com'
        ],
        'messaging': [
            'web.whatsapp.com', 'telegram.org', 'discord.com',
            'messenger.com'
        ],
        'news_apps': [
            'm.eluniverso.com', 'm.elcomercio.com', 'flipboard.com',
            'news.google.com'
        ],
        'banking': [
            'pichincha.com', 'bancoguayaquil.com', 'produbanco.com'
        ],
        'shopping': [
            'm.mercadolibre.com.ec', 'm.amazon.com', 'wish.com'
        ],
        'music_streaming': [
            'open.spotify.com', 'music.youtube.com', 'soundcloud.com'
        ]
    }
    
    # User agents realistas
    DESKTOP_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    ]
    
    MOBILE_USER_AGENTS = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    ]
    
    @classmethod
    def generate_profile(cls, proxy_type: str = 'residential') -> ProfileConfig:
        """
        Genera un perfil realista basado en el tipo de proxy
        
        Args:
            proxy_type: 'residential' (desktop) o 'mobile'
        """
        # Determinar tipo de dispositivo según proxy
        device_type = 'mobile' if proxy_type == 'mobile' else 'desktop'
        
        # Generar datos básicos
        gender = random.choice(['male', 'female'])
        age = cls._generate_realistic_age(device_type)
        age_range = cls._get_age_range(age)
        
        # Seleccionar ciudad con distribución realista
        city = random.choices(
            list(cls.ECUADORIAN_CITIES.keys()),
            weights=[data['population'] for data in cls.ECUADORIAN_CITIES.values()]
        )[0]
        
        # Seleccionar nombre
        faker_ec = Faker('es_ES')
        first_name = random.choice(cls.ECUADORIAN_NAMES[gender])
        last_name = faker_ec.last_name()
        full_name = f"{first_name} {last_name}"
        
        # Seleccionar intereses según edad y dispositivo
        if device_type == 'mobile':
            available_interests = cls.INTERESTS_BY_AGE_MOBILE[age_range]
            num_interests = random.randint(3, 5)
        else:
            available_interests = cls.INTERESTS_BY_AGE_DESKTOP[age_range]
            num_interests = random.randint(4, 7)
        
        interests = random.sample(available_interests, min(num_interests, len(available_interests)))
        
        # Generar historial de navegación
        browsing_history = cls._generate_browsing_history(interests, device_type)
        
        # User agent según dispositivo
        user_agent = random.choice(
            cls.MOBILE_USER_AGENTS if device_type == 'mobile' else cls.DESKTOP_USER_AGENTS
        )
        
        return ProfileConfig(
            name=full_name,
            age=age,
            gender=gender,
            country='EC',
            city=city,
            language='es-EC',
            timezone=cls.ECUADORIAN_CITIES[city]['timezone'],
            user_agent=user_agent,
            interests=interests,
            browsing_history=browsing_history,
            proxy_type=proxy_type,
            device_type=device_type
        )
    
    @staticmethod
    def _generate_realistic_age(device_type: str) -> int:
        """Genera edad con distribución realista según tipo de dispositivo"""
        if device_type == 'mobile':
            # Móviles: más jóvenes
            weights = [0.35, 0.40, 0.20, 0.05]  # 18-25, 26-35, 36-50, 50+
            age_ranges = [(18, 25), (26, 35), (36, 50), (51, 65)]
        else:
            # Desktop: distribución más equilibrada
            weights = [0.25, 0.35, 0.30, 0.10]
            age_ranges = [(18, 25), (26, 35), (36, 50), (51, 65)]
        
        selected_range = random.choices(age_ranges, weights=weights)[0]
        return random.randint(selected_range[0], selected_range[1])
    
    @staticmethod
    def _get_age_range(age: int) -> str:
        """Determina el rango de edad"""
        if age <= 25:
            return '18-25'
        elif age <= 35:
            return '26-35'
        elif age <= 50:
            return '36-50'
        else:
            return '50+'
    
    @classmethod
    def _generate_browsing_history(cls, interests: List[str], device_type: str) -> List[str]:
        """Genera historial de navegación basado en intereses"""
        sites = []
        
        # Sitios comunes para todos
        common_sites = [
            'google.com',
            'youtube.com',
            'gmail.com' if device_type == 'desktop' else 'm.gmail.com',
            'facebook.com' if device_type == 'desktop' else 'm.facebook.com'
        ]
        sites.extend(common_sites)
        
        # Sitios según intereses
        sites_dict = cls.SITES_BY_INTEREST_MOBILE if device_type == 'mobile' else cls.SITES_BY_INTEREST_DESKTOP
        
        for interest in interests:
            if interest in sites_dict:
                interest_sites = sites_dict[interest]
                # Agregar 1-3 sitios por interés
                num_sites = random.randint(1, min(3, len(interest_sites)))
                sites.extend(random.sample(interest_sites, num_sites))
        
        # Sitios locales ecuatorianos (siempre agregar algunos)
        ecuadorian_sites = [
            'eluniverso.com' if device_type == 'desktop' else 'm.eluniverso.com',
            'elcomercio.com' if device_type == 'desktop' else 'm.elcomercio.com',
            'pichincha.com',
            'mercadolibre.com.ec'
        ]
        sites.extend(random.sample(ecuadorian_sites, 2))
        
        # Eliminar duplicados y mezclar
        sites = list(set(sites))
        random.shuffle(sites)
        
        return sites[:20]  # Limitar a 20 sitios