"""
Database operations for predictions storage
Shared between scheduler and bot services
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def save_prediction(prediction: Dict[str, Any], event_date: str) -> bool:
    """
    Save a prediction to the database
    Uses ON CONFLICT to handle duplicates (idempotent)
    """
    try:
        # Parse prediction data
        partido = prediction.get('partido', '')
        teams = partido.split(' vs ')
        home_team = teams[0].strip() if len(teams) > 0 else 'Unknown'
        away_team = teams[1].strip() if len(teams) > 1 else 'Unknown'
        
        # Extract market code and selection from prediccion
        prediccion = prediction.get('prediccion', '')
        market_code, selection = parse_market_selection(prediccion)
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO predicciones_historicas (
                        event_date, match_id, league_name, home_team, away_team,
                        market_code, selection, odds, stake, confidence,
                        expected_value, reason, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendiente'
                    )
                    ON CONFLICT (match_id, market_code, selection, event_date)
                    DO UPDATE SET
                        odds = EXCLUDED.odds,
                        confidence = EXCLUDED.confidence,
                        expected_value = EXCLUDED.expected_value,
                        updated_at = NOW()
                """, (
                    event_date,
                    prediction.get('id', ''),
                    prediction.get('liga', 'Unknown'),
                    home_team,
                    away_team,
                    market_code,
                    selection,
                    prediction.get('cuota', 0),
                    prediction.get('stake_recomendado', 1),
                    prediction.get('confianza', 0),
                    prediction.get('valor_esperado', 0),
                    prediction.get('razon', ''),
                ))
        return True
    except Exception as e:
        print(f"Error saving prediction to DB: {e}")
        return False

def parse_market_selection(prediccion: str) -> tuple:
    """Parse market code and selection from prediccion string"""
    prediccion_lower = prediccion.lower()
    
    # BTTS
    if 'ambos equipos marcan' in prediccion_lower:
        if 'sí' in prediccion_lower or 'si' in prediccion_lower:
            return ('btts', 'Sí')
        else:
            return ('btts', 'No')
    
    # Over/Under goals
    if 'más de' in prediccion_lower or 'over' in prediccion_lower:
        if '0.5' in prediccion:
            return ('over_05', 'Over')
        elif '1.5' in prediccion:
            return ('over_15', 'Over')
        elif '2.5' in prediccion:
            return ('over_25', 'Over')
        elif '3.5' in prediccion:
            return ('over_35', 'Over')
        elif '4.5' in prediccion:
            return ('over_45', 'Over')
    
    if 'menos de' in prediccion_lower or 'under' in prediccion_lower:
        if '0.5' in prediccion:
            return ('under_05', 'Under')
        elif '1.5' in prediccion:
            return ('under_15', 'Under')
        elif '2.5' in prediccion:
            return ('under_25', 'Under')
        elif '3.5' in prediccion:
            return ('under_35', 'Under')
        elif '4.5' in prediccion:
            return ('under_45', 'Under')
    
    # Corners
    if 'corner' in prediccion_lower:
        if 'más' in prediccion_lower or 'over' in prediccion_lower:
            if '8.5' in prediccion:
                return ('corners_over_85', 'Over')
            elif '9.5' in prediccion:
                return ('corners_over_95', 'Over')
            elif '10.5' in prediccion:
                return ('corners_over_105', 'Over')
        elif 'menos' in prediccion_lower or 'under' in prediccion_lower:
            if '8.5' in prediccion:
                return ('corners_under_85', 'Under')
            elif '9.5' in prediccion:
                return ('corners_under_95', 'Under')
            elif '10.5' in prediccion:
                return ('corners_under_105', 'Under')
    
    # Cards
    if 'tarjeta' in prediccion_lower or 'card' in prediccion_lower:
        if 'más' in prediccion_lower or 'over' in prediccion_lower:
            if '3.5' in prediccion:
                return ('cards_over_35', 'Over')
            elif '4.5' in prediccion:
                return ('cards_over_45', 'Over')
        elif 'menos' in prediccion_lower or 'under' in prediccion_lower:
            if '3.5' in prediccion:
                return ('cards_under_35', 'Under')
            elif '4.5' in prediccion:
                return ('cards_under_45', 'Under')
    
    # Default
    return ('other', prediccion[:50])

def get_pending_predictions(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all pending predictions"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM predicciones_historicas
                    WHERE status = 'pendiente'
                    ORDER BY event_date DESC, created_at DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"Error getting pending predictions: {e}")
        return []

def get_statistics(days: int = None) -> Dict[str, Any]:
    """Get prediction statistics (all-time if days=None)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get counts
                if days is None:
                    cur.execute("""
                        SELECT
                            COUNT(*) FILTER (WHERE status = 'pendiente') as pendientes,
                            COUNT(*) FILTER (WHERE status = 'acierto') as aciertos,
                            COUNT(*) FILTER (WHERE status = 'fallo') as fallos,
                            COUNT(*) as total
                        FROM predicciones_historicas
                    """)
                else:
                    cur.execute("""
                        SELECT
                            COUNT(*) FILTER (WHERE status = 'pendiente') as pendientes,
                            COUNT(*) FILTER (WHERE status = 'acierto') as aciertos,
                            COUNT(*) FILTER (WHERE status = 'fallo') as fallos,
                            COUNT(*) as total
                        FROM predicciones_historicas
                        WHERE event_date >= CURRENT_DATE - INTERVAL '%s days'
                    """, (days,))
                stats = dict(cur.fetchone())
                
                # Calculate win rate
                resueltos = stats['aciertos'] + stats['fallos']
                if resueltos > 0:
                    stats['win_rate'] = round((stats['aciertos'] / resueltos) * 100, 1)
                else:
                    stats['win_rate'] = 0.0
                
                return stats
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {'pendientes': 0, 'aciertos': 0, 'fallos': 0, 'total': 0, 'win_rate': 0.0}

def update_prediction_result(match_id: str, market_code: str, selection: str, 
                            event_date: str, is_win: bool) -> bool:
    """Update prediction result"""
    try:
        status = 'acierto' if is_win else 'fallo'
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE predicciones_historicas
                    SET status = %s, resolved_at = NOW()
                    WHERE match_id = %s AND market_code = %s 
                    AND selection = %s AND event_date = %s
                    AND status = 'pendiente'
                """, (status, match_id, market_code, selection, event_date))
                return cur.rowcount > 0
    except Exception as e:
        print(f"Error updating prediction result: {e}")
        return False

def migrate_json_to_db(json_file: str = 'historial_predicciones.json') -> int:
    """Migrate predictions from JSON file to database (one-time migration)"""
    try:
        from json_storage import cargar_json
        
        historial = cargar_json(json_file) or []
        migrated = 0
        
        for pred in historial:
            if save_prediction(pred, pred.get('fecha', datetime.now().strftime('%Y-%m-%d'))):
                migrated += 1
        
        print(f"✅ Migrated {migrated}/{len(historial)} predictions to database")
        return migrated
    except Exception as e:
        print(f"Error migrating JSON to DB: {e}")
        return 0
