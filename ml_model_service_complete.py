"""
Complete ML Model Service - handles 1X2, BTTS, and Over/Under 2.5 predictions
"""

import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta

class CompleteMLModelService:
    """ML Model Service for all bet types"""
    
    def __init__(self):
        """Initialize all ML models"""
        print("🤖 Loading ML models...")
        
        # Load 1X2 model
        self.model_1x2 = joblib.load('ml_model_v2.pkl')
        self.scaler_1x2 = joblib.load('ml_scaler_v2.pkl')
        with open('ml_features_v2.json', 'r') as f:
            self.features_1x2 = json.load(f)
        
        # Load BTTS model
        self.model_btts = joblib.load('ml_model_btts.pkl')
        self.scaler_btts = joblib.load('ml_scaler_btts.pkl')
        
        # Load O/U 2.5 model
        self.model_ou25 = joblib.load('ml_model_ou25.pkl')
        self.scaler_ou25 = joblib.load('ml_scaler_ou25.pkl')
        
        with open('ml_features_btts_ou.json', 'r') as f:
            self.features_btts_ou = json.load(f)
        
        # Load historical data
        self.historical_df = pd.read_csv('historical_matches_features_v2.csv')
        self.historical_df['date_utc'] = pd.to_datetime(self.historical_df['date_utc'])
        
        print(f"   ✅ 1X2 Model loaded ({len(self.features_1x2)} features)")
        print(f"   ✅ BTTS Model loaded ({len(self.features_btts_ou)} features)")
        print(f"   ✅ O/U 2.5 Model loaded ({len(self.features_btts_ou)} features)")
        print(f"   ✅ Historical data: {len(self.historical_df)} matches")
    
    def get_team_stats(self, team_id):
        """Get latest stats for a team from historical data"""
        team_matches = self.historical_df[
            (self.historical_df['home_id'] == team_id) | 
            (self.historical_df['away_id'] == team_id)
        ].sort_values('date_utc', ascending=False)
        
        if len(team_matches) == 0:
            # Return defaults
            return {
                'elo': 1500,
                'L5_wins': 0, 'L5_gf': 0, 'L5_ga': 0, 'L5_gd': 0,
                'L10_wins': 0, 'L10_gf': 0, 'L10_ga': 0, 'L10_gd': 0,
                'rest_days': 7
            }
        
        latest = team_matches.iloc[0]
        is_home = latest['home_id'] == team_id
        
        if is_home:
            return {
                'elo': latest.get('elo_home_pre', 1500),
                'L5_wins': latest.get('home_L5_wins', 0),
                'L5_gf': latest.get('home_L5_gf', 0),
                'L5_ga': latest.get('home_L5_ga', 0),
                'L5_gd': latest.get('home_L5_gd', 0),
                'L10_wins': latest.get('home_L10_wins', 0),
                'L10_gf': latest.get('home_L10_gf', 0),
                'L10_ga': latest.get('home_L10_ga', 0),
                'L10_gd': latest.get('home_L10_gd', 0),
                'rest_days': latest.get('home_rest_days', 7)
            }
        else:
            return {
                'elo': latest.get('elo_away_pre', 1500),
                'L5_wins': latest.get('away_L5_wins', 0),
                'L5_gf': latest.get('away_L5_gf', 0),
                'L5_ga': latest.get('away_L5_ga', 0),
                'L5_gd': latest.get('away_L5_gd', 0),
                'L10_wins': latest.get('away_L10_wins', 0),
                'L10_gf': latest.get('away_L10_gf', 0),
                'L10_ga': latest.get('away_L10_ga', 0),
                'L10_gd': latest.get('away_L10_gd', 0),
                'rest_days': latest.get('away_rest_days', 7)
            }
    
    def prepare_features(self, home_id, away_id, league_name, market_odds):
        """Prepare features for prediction"""
        # Get team stats
        home_stats = self.get_team_stats(home_id)
        away_stats = self.get_team_stats(away_id)
        
        # De-juice market odds
        total_prob = (1/market_odds['home'] + 1/market_odds['draw'] + 1/market_odds['away'])
        market_prob_home = (1/market_odds['home']) / total_prob
        market_prob_draw = (1/market_odds['draw']) / total_prob
        market_prob_away = (1/market_odds['away']) / total_prob
        
        # Base features
        features = {
            'market_prob_home': market_prob_home,
            'market_prob_draw': market_prob_draw,
            'market_prob_away': market_prob_away,
            'elo_home_pre': home_stats['elo'],
            'elo_away_pre': away_stats['elo'],
            'elo_diff': home_stats['elo'] - away_stats['elo'],
            'home_L5_wins': home_stats['L5_wins'],
            'home_L5_gf': home_stats['L5_gf'],
            'home_L5_ga': home_stats['L5_ga'],
            'home_L5_gd': home_stats['L5_gd'],
            'away_L5_wins': away_stats['L5_wins'],
            'away_L5_gf': away_stats['L5_gf'],
            'away_L5_ga': away_stats['L5_ga'],
            'away_L5_gd': away_stats['L5_gd'],
            'home_L10_wins': home_stats['L10_wins'],
            'home_L10_gf': home_stats['L10_gf'],
            'home_L10_ga': home_stats['L10_ga'],
            'home_L10_gd': home_stats['L10_gd'],
            'away_L10_wins': away_stats['L10_wins'],
            'away_L10_gf': away_stats['L10_gf'],
            'away_L10_ga': away_stats['L10_ga'],
            'away_L10_gd': away_stats['L10_gd'],
            'home_rest_days': home_stats['rest_days'],
            'away_rest_days': away_stats['rest_days'],
            'is_home': 1
        }
        
        # League dummies
        leagues = [
            'England Premier League', 'Spain La Liga', 'Germany Bundesliga',
            'Italy Serie A', 'France Ligue 1', 'Colombia Categoria Primera A',
            'Argentina Primera División', 'South America Copa Libertadores',
            'South America Copa Sudamericana'
        ]
        
        for league in leagues:
            col_name = f'league_{league.replace(" ", "_")}'
            features[col_name] = 1 if league_name == league else 0
        
        return features
    
    def predict_all_markets(self, home_id, away_id, league_name, market_odds):
        """Generate predictions for all markets (1X2, BTTS, O/U 2.5)"""
        
        # Prepare features
        features = self.prepare_features(home_id, away_id, league_name, market_odds)
        
        # 1X2 prediction - use all features including wins
        try:
            X_1x2 = np.array([[features[f] for f in self.features_1x2]])
            X_1x2_scaled = self.scaler_1x2.transform(X_1x2)
            probs_1x2 = self.model_1x2.predict_proba(X_1x2_scaled)[0]
            pred_1x2 = ['home', 'draw', 'away'][np.argmax(probs_1x2)]
        except KeyError as e:
            print(f"Warning: Missing feature for 1X2: {e}")
            # Use default probabilities based on market odds
            total = 1/market_odds['home'] + 1/market_odds['draw'] + 1/market_odds['away']
            probs_1x2 = np.array([
                (1/market_odds['home'])/total,
                (1/market_odds['draw'])/total,
                (1/market_odds['away'])/total
            ])
            pred_1x2 = ['home', 'draw', 'away'][np.argmax(probs_1x2)]
        
        # BTTS prediction - use features without wins
        try:
            X_btts = np.array([[features[f] for f in self.features_btts_ou]])
            X_btts_scaled = self.scaler_btts.transform(X_btts)
            probs_btts = self.model_btts.predict_proba(X_btts_scaled)[0]
        except KeyError as e:
            print(f"Warning: Missing feature for BTTS: {e}")
            probs_btts = np.array([0.5, 0.5])
        
        # O/U 2.5 prediction - use features without wins
        try:
            X_ou = np.array([[features[f] for f in self.features_btts_ou]])
            X_ou_scaled = self.scaler_ou25.transform(X_ou)
            probs_ou = self.model_ou25.predict_proba(X_ou_scaled)[0]
        except KeyError as e:
            print(f"Warning: Missing feature for O/U: {e}")
            probs_ou = np.array([0.5, 0.5])
        
        return {
            '1x2': {
                'prediction': pred_1x2,
                'confidence': float(max(probs_1x2)),
                'probabilities': {
                    'home': float(probs_1x2[0]),
                    'draw': float(probs_1x2[1]),
                    'away': float(probs_1x2[2])
                }
            },
            'btts': {
                'prediction': 'yes' if probs_btts[1] > 0.5 else 'no',
                'confidence': float(max(probs_btts)),
                'probabilities': {
                    'no': float(probs_btts[0]),
                    'yes': float(probs_btts[1])
                }
            },
            'over_under_25': {
                'prediction': 'over' if probs_ou[1] > 0.5 else 'under',
                'confidence': float(max(probs_ou)),
                'probabilities': {
                    'under': float(probs_ou[0]),
                    'over': float(probs_ou[1])
                }
            }
        }

if __name__ == '__main__':
    # Test
    service = CompleteMLModelService()
    
    # Test with sample match
    result = service.predict_all_markets(
        home_id=76,
        away_id=291,
        league_name='Spain La Liga',
        market_odds={'home': 1.71, 'draw': 3.87, 'away': 4.90}
    )
    
    print()
    print("Test prediction:")
    print(json.dumps(result, indent=2))
