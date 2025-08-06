#!/usr/bin/env python3

def detectar_liga_por_imagen(home_image, away_image):
    """
    Detecta la liga basándose en las rutas de imágenes de los equipos
    """
    if home_image and 'colombia' in home_image.lower():
        return "Liga Colombiana"
    elif home_image and 'chile' in home_image.lower():
        return "Primera División Chile"
    elif home_image and 'spain' in home_image.lower():
        return "La Liga"
    elif home_image and 'england' in home_image.lower():
        return "Premier League"
    elif home_image and 'italy' in home_image.lower():
        return "Serie A"
    elif home_image and 'germany' in home_image.lower():
        return "Bundesliga"
    elif home_image and 'france' in home_image.lower():
        return "Ligue 1"
    elif home_image and 'brazil' in home_image.lower():
        return "Brasileirão"
    elif home_image and 'argentina' in home_image.lower():
        return "Liga Argentina"
    elif home_image and 'mexico' in home_image.lower():
        return "Liga MX"
    elif home_image and 'portugal' in home_image.lower():
        return "Primeira Liga"
    elif home_image and 'netherlands' in home_image.lower():
        return "Eredivisie"
    elif home_image and 'scotland' in home_image.lower():
        return "Scottish Premiership"
    elif home_image and 'usa' in home_image.lower() or home_image and 'united-states' in home_image.lower():
        return "MLS"
    elif home_image and 'peru' in home_image.lower():
        return "Liga Peruana"
    elif home_image and 'ecuador' in home_image.lower():
        return "Liga Ecuatoriana"
    elif home_image and 'uruguay' in home_image.lower():
        return "Liga Uruguaya"
    elif home_image and 'bolivia' in home_image.lower():
        return "Liga Boliviana"
    
    european_countries = ['austria', 'belgium', 'czech', 'denmark', 'finland', 'greece', 
                         'hungary', 'norway', 'poland', 'romania', 'serbia', 'slovakia', 
                         'slovenia', 'sweden', 'switzerland', 'turkey', 'ukraine', 'croatia',
                         'bosnia', 'montenegro', 'albania', 'macedonia', 'moldova', 'estonia',
                         'latvia', 'lithuania', 'belarus', 'georgia', 'armenia', 'azerbaijan']
    
    home_european = any(country in home_image.lower() for country in european_countries) if home_image else False
    away_european = any(country in away_image.lower() for country in european_countries) if away_image else False
    
    if home_european and away_european:
        return "Champions League"
    
    elif home_european or away_european:
        return "Champions League"
    
    else:
        return "Liga Internacional"

def convertir_timestamp_unix(timestamp_unix):
    """
    Convierte timestamp unix a formato legible en zona horaria de Arizona
    """
    if timestamp_unix and timestamp_unix > 0:
        from datetime import datetime
        import pytz
        try:
            dt_utc = datetime.fromtimestamp(timestamp_unix, tz=pytz.UTC)
            arizona_tz = pytz.timezone('US/Arizona')
            dt_arizona = dt_utc.astimezone(arizona_tz)
            return dt_arizona.strftime("%H:%M")
        except Exception as e:
            print(f"Error convirtiendo timestamp {timestamp_unix}: {e}")
            return "Por confirmar"
    return "Por confirmar"
