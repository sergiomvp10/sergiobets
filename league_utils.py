#!/usr/bin/env python3
import re

# Mapa de pais extraido de la ruta de imagen -> nombre de la liga domestica
_COUNTRY_TO_LEAGUE = {
    'colombia': "Liga Colombia",
    'chile': "Primera Division Chile",
    'spain': "La Liga",
    'england': "Premier League",
    'italy': "Serie A",
    'germany': "Bundesliga",
    'france': "Ligue 1",
    'brazil': "Brasileirao",
    'argentina': "Liga Argentina",
    'mexico': "Liga MX",
    'portugal': "Primeira Liga",
    'netherlands': "Eredivisie",
    'scotland': "Scottish Premiership",
    'usa': "MLS",
    'united-states': "MLS",
    'peru': "Liga Peruana",
    'ecuador': "Liga Ecuatoriana",
    'uruguay': "Liga Uruguaya",
    'bolivia': "Liga Boliviana",
    'paraguay': "Liga Paraguaya",
    'venezuela': "Liga Venezolana",
    'japan': "J-League",
    'south-korea': "K-League",
    'china': "Chinese Super League",
    'australia': "A-League",
}

# Paises europeos que no tienen liga mapeada arriba
_EUROPEAN_MINOR = [
    'austria', 'belgium', 'czech', 'denmark', 'finland', 'greece',
    'hungary', 'norway', 'poland', 'romania', 'serbia', 'slovakia',
    'slovenia', 'sweden', 'switzerland', 'turkey', 'ukraine', 'croatia',
    'bosnia', 'montenegro', 'albania', 'macedonia', 'moldova', 'estonia',
    'latvia', 'lithuania', 'belarus', 'georgia', 'armenia', 'azerbaijan',
    'cyprus', 'iceland', 'luxembourg', 'malta', 'kosovo',
]

# Paises europeos principales (con liga mapeada)
_EUROPEAN_MAJOR = ['england', 'spain', 'italy', 'germany', 'france', 'portugal',
                   'netherlands', 'scotland']

# Paises sudamericanos
_SOUTH_AMERICAN = ['argentina', 'brazil', 'colombia', 'chile', 'peru', 'ecuador',
                   'uruguay', 'bolivia', 'paraguay', 'venezuela']

# Regex para extraer el pais de la ruta de imagen (teams/{country}-...)
_COUNTRY_RE = re.compile(r'teams/([a-z-]+?)-')


def _extract_country(image_path):
    """Extrae el pais de la ruta de imagen del equipo."""
    if not image_path:
        return None
    m = _COUNTRY_RE.search(image_path.lower())
    if m:
        return m.group(1)
    return None


def detectar_liga_por_imagen(home_image, away_image, competition_id=None, match_url=None):
    """
    Detecta la liga/competicion de un partido.
    
    Prioridad:
    1. match_url (contiene /europe/, /south-america/, etc.)
    2. Comparar paises de ambos equipos (si son diferentes = competicion internacional)
    3. Fallback: liga domestica del equipo local
    """
    home_country = _extract_country(home_image)
    away_country = _extract_country(away_image)
    
    # --- PASO 1: Detectar por match_url (mas confiable) ---
    if match_url:
        url_lower = match_url.lower()
        if '/europe/' in url_lower:
            return "Champions League"
        if '/south-america/' in url_lower:
            # Diferenciar Libertadores vs Sudamericana si es posible
            return "Copa Libertadores"
    
    # --- PASO 2: Si los equipos son de paises diferentes = competicion internacional ---
    if home_country and away_country and home_country != away_country:
        home_is_european = home_country in _EUROPEAN_MAJOR or home_country in _EUROPEAN_MINOR
        away_is_european = away_country in _EUROPEAN_MAJOR or away_country in _EUROPEAN_MINOR
        home_is_south_am = home_country in _SOUTH_AMERICAN
        away_is_south_am = away_country in _SOUTH_AMERICAN
        
        if home_is_european and away_is_european:
            return "Champions League"
        elif home_is_south_am and away_is_south_am:
            return "Copa Libertadores"
        else:
            return "Copa Internacional"
    
    # --- PASO 3: Mismos paises o no se pudo determinar -> liga domestica ---
    country = home_country or away_country
    if country:
        league = _COUNTRY_TO_LEAGUE.get(country)
        if league:
            return league
        # Pais europeo menor sin liga mapeada
        if country in _EUROPEAN_MINOR:
            return f"Liga {country.replace('-', ' ').title()}"
    
    return "Liga Internacional"

def convertir_timestamp_unix(timestamp_unix):
    """
    Convierte timestamp unix a formato legible en zona horaria de Bogota, Colombia (UTC-5)
    """
    if timestamp_unix and timestamp_unix > 0:
        from datetime import datetime, timezone, timedelta
        try:
            TZ_BOGOTA = timezone(timedelta(hours=-5))
            dt_utc = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)
            dt_bogota = dt_utc.astimezone(TZ_BOGOTA)
            return dt_bogota.strftime("%I:%M %p")
        except Exception as e:
            print(f"Error convirtiendo timestamp {timestamp_unix}: {e}")
            return "Por confirmar"
    return "Por confirmar"
