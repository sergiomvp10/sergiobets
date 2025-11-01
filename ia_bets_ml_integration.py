"""
Integration of ML Model into ia_bets prediction system
This adds ML predictions alongside existing heuristic predictions
"""

import os
import sys

# Add ML model service
try:
    from ml_model_service_simple import MLModelService
    ML_AVAILABLE = True
    print("✅ ML Model loaded successfully")
except Exception as e:
    ML_AVAILABLE = False
    print(f"⚠️ ML Model not available: {e}")

# Initialize ML service globally
_ml_service = None

def get_ml_service():
    """Get or initialize ML service"""
    global _ml_service
    if _ml_service is None and ML_AVAILABLE:
        try:
            _ml_service = MLModelService()
        except Exception as e:
            print(f"❌ Error initializing ML service: {e}")
    return _ml_service

def generar_prediccion_ml(partido: dict, home_id: int = None, away_id: int = None) -> dict:
    """
    Generate ML prediction for a match
    
    Args:
        partido: Match data with cuotas, local, visitante, liga
        home_id: Home team ID from FootyStats
        away_id: Away team ID from FootyStats
    
    Returns:
        dict with ML prediction or None if ML not available
    """
    ml_service = get_ml_service()
    
    if not ml_service or not home_id or not away_id:
        return None
    
    try:
        # Prepare market odds
        cuotas = partido.get('cuotas', {})
        market_odds = {
            'home': float(cuotas.get('local', 2.0)),
            'draw': float(cuotas.get('empate', 3.0)),
            'away': float(cuotas.get('visitante', 3.0))
        }
        
        # Get league name
        liga = partido.get('liga', 'Unknown')
        
        # Map league names to match training data
        league_mapping = {
            'Premier League': 'England Premier League',
            'La Liga': 'Spain La Liga',
            'Serie A': 'Italy Serie A',
            'Bundesliga': 'Germany Bundesliga',
            'Ligue 1': 'France Ligue 1',
            'Liga Colombiana': 'Colombia Categoria Primera A',
            'Liga Argentina': 'Argentina Primera División',
            'Copa Libertadores': 'South America Copa Libertadores',
            'Copa Sudamericana': 'South America Copa Sudamericana'
        }
        
        league_name = league_mapping.get(liga, liga)
        
        # Get ML prediction
        ml_pred = ml_service.predict(home_id, away_id, league_name, market_odds)
        
        if ml_pred:
            return {
                'prediction': ml_pred['prediction'],
                'confidence': ml_pred['confidence'],
                'probabilities': ml_pred['probabilities'],
                'source': 'ml_model_v2'
            }
        
    except Exception as e:
        print(f"❌ Error in ML prediction: {e}")
    
    return None

def combinar_predicciones_ml_heuristica(ml_pred: dict, heuristic_pred: dict, alpha: float = 0.3) -> dict:
    """
    Combine ML and heuristic predictions
    
    Args:
        ml_pred: ML prediction with probabilities
        heuristic_pred: Heuristic prediction with probabilities
        alpha: Weight for ML model (0-1), 1-alpha for heuristic
    
    Returns:
        Combined prediction
    """
    if not ml_pred:
        return heuristic_pred
    
    if not heuristic_pred:
        return ml_pred
    
    # Combine probabilities
    ml_probs = ml_pred['probabilities']
    heur_probs = heuristic_pred.get('probabilities', {
        'home': 0.33,
        'draw': 0.33,
        'away': 0.34
    })
    
    combined_probs = {
        'home': alpha * ml_probs['home'] + (1 - alpha) * heur_probs.get('home', 0.33),
        'draw': alpha * ml_probs['draw'] + (1 - alpha) * heur_probs.get('draw', 0.33),
        'away': alpha * ml_probs['away'] + (1 - alpha) * heur_probs.get('away', 0.34)
    }
    
    # Select best prediction
    best_outcome = max(combined_probs.items(), key=lambda x: x[1])
    
    return {
        'prediction': best_outcome[0],
        'confidence': best_outcome[1],
        'probabilities': combined_probs,
        'source': 'ml_heuristic_combined',
        'ml_weight': alpha
    }

def seleccionar_mejor_tipo_apuesta(partido: dict, ml_pred: dict = None) -> dict:
    """
    Select best bet type for a match based on ML predictions and market odds
    
    Args:
        partido: Match data
        ml_pred: ML prediction (optional)
    
    Returns:
        dict with best bet type, market, odds, EV
    """
    cuotas = partido.get('cuotas', {})
    
    # Calculate EV for different bet types
    bet_options = []
    
    # 1X2 Market
    if ml_pred:
        ml_probs = ml_pred['probabilities']
        
        # Home
        odds_home = float(cuotas.get('local', 2.0))
        ev_home = (ml_probs['home'] * odds_home) - 1
        bet_options.append({
            'tipo': '1X2',
            'mercado': 'Local',
            'cuota': odds_home,
            'probabilidad': ml_probs['home'],
            'ev': ev_home
        })
        
        # Draw
        odds_draw = float(cuotas.get('empate', 3.0))
        ev_draw = (ml_probs['draw'] * odds_draw) - 1
        bet_options.append({
            'tipo': '1X2',
            'mercado': 'Empate',
            'cuota': odds_draw,
            'probabilidad': ml_probs['draw'],
            'ev': ev_draw
        })
        
        # Away
        odds_away = float(cuotas.get('visitante', 3.0))
        ev_away = (ml_probs['away'] * odds_away) - 1
        bet_options.append({
            'tipo': '1X2',
            'mercado': 'Visitante',
            'cuota': odds_away,
            'probabilidad': ml_probs['away'],
            'ev': ev_away
        })
    
    # BTTS (if available)
    if 'btts_si' in cuotas and 'btts_no' in cuotas:
        # Use heuristic for BTTS (no ML model yet)
        pass
    
    # Over/Under 2.5 (if available)
    if 'over_25' in cuotas and 'under_25' in cuotas:
        # Use heuristic for O/U (no ML model yet)
        pass
    
    # Select bet with highest EV
    if bet_options:
        best_bet = max(bet_options, key=lambda x: x['ev'])
        return best_bet
    
    return None

# Test function
def test_ml_integration():
    """Test ML integration with sample match"""
    print("=" * 80)
    print("TESTING ML INTEGRATION")
    print("=" * 80)
    print()
    
    # Sample match
    partido = {
        'local': 'Arsenal',
        'visitante': 'Chelsea',
        'liga': 'Premier League',
        'cuotas': {
            'local': '2.10',
            'empate': '3.40',
            'visitante': '3.50'
        }
    }
    
    home_id = 42
    away_id = 44
    
    print(f"Match: {partido['local']} vs {partido['visitante']}")
    print(f"League: {partido['liga']}")
    print(f"Odds: {partido['cuotas']}")
    print()
    
    # Get ML prediction
    ml_pred = generar_prediccion_ml(partido, home_id, away_id)
    
    if ml_pred:
        print("✅ ML Prediction:")
        print(f"   Prediction: {ml_pred['prediction']}")
        print(f"   Confidence: {ml_pred['confidence']:.2%}")
        print(f"   Probabilities:")
        print(f"     Home: {ml_pred['probabilities']['home']:.2%}")
        print(f"     Draw: {ml_pred['probabilities']['draw']:.2%}")
        print(f"     Away: {ml_pred['probabilities']['away']:.2%}")
        print()
        
        # Select best bet type
        best_bet = seleccionar_mejor_tipo_apuesta(partido, ml_pred)
        
        if best_bet:
            print("✅ Best Bet:")
            print(f"   Type: {best_bet['tipo']}")
            print(f"   Market: {best_bet['mercado']}")
            print(f"   Odds: {best_bet['cuota']:.2f}")
            print(f"   Probability: {best_bet['probabilidad']:.2%}")
            print(f"   EV: {best_bet['ev']:.2%}")
    else:
        print("❌ ML prediction failed")
    
    print("=" * 80)

if __name__ == '__main__':
    test_ml_integration()
