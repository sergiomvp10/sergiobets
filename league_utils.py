#!/usr/bin/env python3

def detectar_liga_por_imagen(home_image, away_image):
    """
    Detecta la liga basándose en las rutas de imágenes de los equipos
    """
    if home_image and 'colombia' in home_image.lower():
        return "Liga Colombiana"
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
    else:
        return "Liga Internacional"

def convertir_timestamp_unix(timestamp_unix):
    """
    Convierte timestamp unix a formato legible
    """
    if timestamp_unix and timestamp_unix > 0:
        from datetime import datetime
        try:
            dt = datetime.fromtimestamp(timestamp_unix)
            return dt.strftime("%H:%M")
        except:
            return "Por confirmar"
    return "Por confirmar"
