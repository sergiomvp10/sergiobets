"""
Simplified ML Model Service - Uses CSV data instead of DB queries
"""

import joblib
import json
import numpy as np
import pandas as pd

class MLModelService:
    def __init__(self):
        """Initialize ML model service"""
        self.model = joblib.load('ml_model_v2.pkl')
        self.scaler = joblib.load('ml_scaler_v2.pkl')
        
        with open('ml_features_v2.json', 'r') as f:
            self.feature_names = json.load(f)
        
        # Load historical data for lookups
        self.historical_df = pd.read_csv('historical_matches_features_v2.csv')
        
        print("✅ ML Model Service initialized")
        print(f"   Features: {len(self.feature_names)}")
    
    def get_team_stats(self, team_id):
        """Get latest stats for a team from historical data"""
        team_matches = self.historical_df[
            (self.historical_df['home_id'] == team_id) | 
            (self.historical_df['away_id'] == team_id)
        ].sort_values('date_utc', ascending=False)
        
        if len(team_matches) == 0:
            return {
                'elo': 1500,
                'L5_wins': 0, 'L5_gf': 0, 'L5_ga': 0, 'L5_gd': 0,
                'L10_wins': 0, 'L10_gf': 0, 'L10_ga': 0, 'L10_gd': 0,
                'rest_days': 7
            }
        
        latest = team_matches.iloc[0]
        
        # Get Elo
        if latest['home_id'] == team_id:
            elo = latest.get('elo_home_pre', 1500)
            l5_wins = latest.get('home_L5_wins', 0)
            l5_gf = latest.get('home_L5_gf', 0)
            l5_ga = latest.get('home_L5_ga', 0)
            l5_gd = latest.get('home_L5_gd', 0)
            l10_wins = latest.get('home_L10_wins', 0)
            l10_gf = latest.get('home_L10_gf', 0)
            l10_ga = latest.get('home_L10_ga', 0)
            l10_gd = latest.get('home_L10_gd', 0)
            rest_days = latest.get('home_rest_days', 7)
        else:
            elo = latest.get('elo_away_pre', 1500)
            l5_wins = latest.get('away_L5_wins', 0)
            l5_gf = latest.get('away_L5_gf', 0)
            l5_ga = latest.get('away_L5_ga', 0)
            l5_gd = latest.get('away_L5_gd', 0)
            l10_wins = latest.get('away_L10_wins', 0)
            l10_gf = latest.get('away_L10_gf', 0)
            l10_ga = latest.get('away_L10_ga', 0)
            l10_gd = latest.get('away_L10_gd', 0)
            rest_days = latest.get('away_rest_days', 7)
        
        return {
            'elo': elo,
            'L5_wins': l5_wins, 'L5_gf': l5_gf, 'L5_ga': l5_ga, 'L5_gd': l5_gd,
            'L10_wins': l10_wins, 'L10_gf': l10_gf, 'L10_ga': l10_ga, 'L10_gd': l10_gd,
            'rest_days': rest_days
        }
    
    def prepare_features(self, home_id, away_id, league_name, market_odds):
        """Prepare features for prediction"""
        features = {}
        
        # Market probabilities
        prob_1 = 1 / market_odds['home']
        prob_x = 1 / market_odds['draw']
        prob_2 = 1 / market_odds['away']
        total = prob_1 + prob_x + prob_2
        
        features['market_prob_home'] = prob_1 / total
        features['market_prob_draw'] = prob_x / total
        features['market_prob_away'] = prob_2 / total
        
        # Get team stats
        home_stats = self.get_team_stats(home_id)
        away_stats = self.get_team_stats(away_id)
        
        # Elo
        features['elo_home_pre'] = home_stats['elo']
        features['elo_away_pre'] = away_stats['elo']
        features['elo_diff'] = home_stats['elo'] - away_stats['elo']
        
        # L5 stats
        features['home_L5_wins'] = home_stats['L5_wins']
        features['home_L5_gf'] = home_stats['L5_gf']
        features['home_L5_ga'] = home_stats['L5_ga']
        features['home_L5_gd'] = home_stats['L5_gd']
        
        features['away_L5_wins'] = away_stats['L5_wins']
        features['away_L5_gf'] = away_stats['L5_gf']
        features['away_L5_ga'] = away_stats['L5_ga']
        features['away_L5_gd'] = away_stats['L5_gd']
        
        # L10 stats
        features['home_L10_wins'] = home_stats['L10_wins']
        features['home_L10_gf'] = home_stats['L10_gf']
        features['home_L10_ga'] = home_stats['L10_ga']
        features['home_L10_gd'] = home_stats['L10_gd']
        
        features['away_L10_wins'] = away_stats['L10_wins']
        features['away_L10_gf'] = away_stats['L10_gf']
        features['away_L10_ga'] = away_stats['L10_ga']
        features['away_L10_gd'] = away_stats['L10_gd']
        
        # Rest days
        features['home_rest_days'] = home_stats['rest_days']
        features['away_rest_days'] = away_stats['rest_days']
        
        # Home advantage
        features['is_home'] = 1
        
        # League dummies
        all_leagues = [
            'Argentina Primera División',
            'Colombia Categoria Primera A',
            'England Premier League',
            'France Ligue 1',
            'Germany Bundesliga',
            'Italy Serie A',
            'South America Copa Libertadores',
            'South America Copa Sudamericana',
            'Spain La Liga'
        ]
        
        for league in all_leagues:
            features[f'league_{league}'] = 1 if league == league_name else 0
        
        # Convert to array
        feature_array = []
        for fname in self.feature_names:
            feature_array.append(features.get(fname, 0))
        
        return np.array(feature_array).reshape(1, -1)
    
    def predict(self, home_id, away_id, league_name, market_odds):
        """Generate ML prediction"""
        try:
            X = self.prepare_features(home_id, away_id, league_name, market_odds)
            X_scaled = self.scaler.transform(X)
            
            proba = self.model.predict_proba(X_scaled)[0]
            pred_class = self.model.predict(X_scaled)[0]
            
            pred_label = ['home', 'draw', 'away'][pred_class]
            confidence = proba[pred_class]
            
            return {
                'probabilities': {
                    'home': float(proba[0]),
                    'draw': float(proba[1]),
                    'away': float(proba[2])
                },
                'prediction': pred_label,
                'confidence': float(confidence)
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

# Test
if __name__ == '__main__':
    print("=" * 80)
    print("TESTING ML MODEL SERVICE")
    print("=" * 80)
    print()
    
    service = MLModelService()
    
    # Test with Arsenal vs Chelsea
    result = service.predict(
        home_id=42,
        away_id=44,
        league_name='England Premier League',
        market_odds={'home': 2.10, 'draw': 3.40, 'away': 3.50}
    )
    
    if result:
        print("✅ ML Prediction:")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Probabilities: H={result['probabilities']['home']:.2%}, D={result['probabilities']['draw']:.2%}, A={result['probabilities']['away']:.2%}")
    
    print("=" * 80)
