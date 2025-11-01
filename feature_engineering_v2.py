"""
Feature Engineering Pipeline V2 - Complete
Incluye: rolling form, rest days, Elo
Sin data leakage
"""

import os
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

class FeatureEngineerV2:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def load_historical_matches(self):
        """Cargar todos los partidos históricos ordenados por fecha"""
        query = """
            SELECT 
                match_id, date_utc, season, league_name,
                home_id, away_id, home_name, away_name,
                result, goals_home, goals_away,
                odds_ft_1, odds_ft_x, odds_ft_2,
                odds_btts_yes, odds_btts_no,
                odds_over25, odds_under25
            FROM historical_matches
            WHERE result IS NOT NULL
            ORDER BY date_utc ASC
        """
        
        df = pd.read_sql(query, self.conn)
        print(f"✅ Loaded {len(df)} historical matches")
        return df
    
    def calculate_market_probabilities(self, df):
        """Calcular probabilidades implícitas del mercado"""
        df['market_prob_home'] = np.nan
        df['market_prob_draw'] = np.nan
        df['market_prob_away'] = np.nan
        
        mask = (df['odds_ft_1'] > 1) & (df['odds_ft_x'] > 1) & (df['odds_ft_2'] > 1)
        
        if mask.sum() > 0:
            prob_1 = 1 / df.loc[mask, 'odds_ft_1']
            prob_x = 1 / df.loc[mask, 'odds_ft_x']
            prob_2 = 1 / df.loc[mask, 'odds_ft_2']
            
            total = prob_1 + prob_x + prob_2
            df.loc[mask, 'market_prob_home'] = prob_1 / total
            df.loc[mask, 'market_prob_draw'] = prob_x / total
            df.loc[mask, 'market_prob_away'] = prob_2 / total
        
        return df
    
    def calculate_elo_ratings(self, df, k_factor=20):
        """Calcular Elo ratings"""
        elo_ratings = {}
        df = df.copy()
        df['home_score'] = df['result'].map({'home': 1.0, 'draw': 0.5, 'away': 0.0})
        
        df['elo_home_pre'] = np.nan
        df['elo_away_pre'] = np.nan
        df['elo_diff'] = np.nan
        
        for idx, row in df.iterrows():
            home_id = row['home_id']
            away_id = row['away_id']
            
            if home_id not in elo_ratings:
                elo_ratings[home_id] = 1500
            if away_id not in elo_ratings:
                elo_ratings[away_id] = 1500
            
            df.at[idx, 'elo_home_pre'] = elo_ratings[home_id]
            df.at[idx, 'elo_away_pre'] = elo_ratings[away_id]
            df.at[idx, 'elo_diff'] = elo_ratings[home_id] - elo_ratings[away_id]
            
            expected_home = 1 / (1 + 10 ** ((elo_ratings[away_id] - elo_ratings[home_id]) / 400))
            actual_home = row['home_score']
            
            elo_ratings[home_id] += k_factor * (actual_home - expected_home)
            elo_ratings[away_id] += k_factor * ((1 - actual_home) - (1 - expected_home))
        
        return df
    
    def calculate_rolling_stats(self, df):
        """Calcular rolling stats L5 y L10"""
        print("   Calculando rolling stats...")
        
        for window in [5, 10]:
            for prefix in ['home', 'away']:
                df[f'{prefix}_L{window}_wins'] = 0.0
                df[f'{prefix}_L{window}_gf'] = 0.0
                df[f'{prefix}_L{window}_ga'] = 0.0
                df[f'{prefix}_L{window}_gd'] = 0.0
        
        all_teams = set(df['home_id'].unique()) | set(df['away_id'].unique())
        
        for team_id in all_teams:
            team_matches = df[(df['home_id'] == team_id) | (df['away_id'] == team_id)].copy()
            team_matches = team_matches.sort_values('date_utc')
            
            team_matches['team_win'] = 0
            team_matches['team_gf'] = 0
            team_matches['team_ga'] = 0
            
            home_mask = team_matches['home_id'] == team_id
            team_matches.loc[home_mask, 'team_win'] = (team_matches.loc[home_mask, 'result'] == 'home').astype(int)
            team_matches.loc[home_mask, 'team_gf'] = team_matches.loc[home_mask, 'goals_home']
            team_matches.loc[home_mask, 'team_ga'] = team_matches.loc[home_mask, 'goals_away']
            
            away_mask = team_matches['away_id'] == team_id
            team_matches.loc[away_mask, 'team_win'] = (team_matches.loc[away_mask, 'result'] == 'away').astype(int)
            team_matches.loc[away_mask, 'team_gf'] = team_matches.loc[away_mask, 'goals_away']
            team_matches.loc[away_mask, 'team_ga'] = team_matches.loc[away_mask, 'goals_home']
            
            for window in [5, 10]:
                team_matches[f'L{window}_wins'] = team_matches['team_win'].rolling(window, min_periods=1).sum().shift(1).fillna(0)
                team_matches[f'L{window}_gf'] = team_matches['team_gf'].rolling(window, min_periods=1).mean().shift(1).fillna(0)
                team_matches[f'L{window}_ga'] = team_matches['team_ga'].rolling(window, min_periods=1).mean().shift(1).fillna(0)
                team_matches[f'L{window}_gd'] = team_matches[f'L{window}_gf'] - team_matches[f'L{window}_ga']
            
            for window in [5, 10]:
                home_indices = team_matches[home_mask].index
                for col in [f'L{window}_wins', f'L{window}_gf', f'L{window}_ga', f'L{window}_gd']:
                    if len(home_indices) > 0:
                        df.loc[home_indices, f'home_{col}'] = team_matches.loc[home_indices, col].values
                
                away_indices = team_matches[away_mask].index
                for col in [f'L{window}_wins', f'L{window}_gf', f'L{window}_ga', f'L{window}_gd']:
                    if len(away_indices) > 0:
                        df.loc[away_indices, f'away_{col}'] = team_matches.loc[away_indices, col].values
        
        return df
    
    def calculate_rest_days(self, df):
        """Calcular rest days"""
        print("   Calculando rest days...")
        
        df['home_rest_days'] = 7.0
        df['away_rest_days'] = 7.0
        
        all_teams = set(df['home_id'].unique()) | set(df['away_id'].unique())
        
        for team_id in all_teams:
            team_matches = df[(df['home_id'] == team_id) | (df['away_id'] == team_id)].copy()
            team_matches = team_matches.sort_values('date_utc')
            
            team_matches['rest_days'] = team_matches['date_utc'].diff().dt.total_seconds() / 86400
            team_matches['rest_days'] = team_matches['rest_days'].shift(1).fillna(7)
            
            home_indices = team_matches[team_matches['home_id'] == team_id].index
            if len(home_indices) > 0:
                df.loc[home_indices, 'home_rest_days'] = team_matches.loc[home_indices, 'rest_days'].values
            
            away_indices = team_matches[team_matches['away_id'] == team_id].index
            if len(away_indices) > 0:
                df.loc[away_indices, 'away_rest_days'] = team_matches.loc[away_indices, 'rest_days'].values
        
        return df
    
    def generate_features(self):
        """Generar todas las features"""
        print("=" * 80)
        print("FEATURE ENGINEERING V2")
        print("=" * 80)
        print()
        
        print("1. Cargando datos...")
        df = self.load_historical_matches()
        print()
        
        print("2. Market probabilities...")
        df = self.calculate_market_probabilities(df)
        print(f"   ✅ {df['market_prob_home'].notna().sum()} partidos")
        print()
        
        print("3. Elo ratings...")
        df = self.calculate_elo_ratings(df)
        print("   ✅ Done")
        print()
        
        print("4. Rolling stats...")
        df = self.calculate_rolling_stats(df)
        print("   ✅ Done")
        print()
        
        print("5. Rest days...")
        df = self.calculate_rest_days(df)
        print("   ✅ Done")
        print()
        
        print("6. League dummies...")
        df = pd.get_dummies(df, columns=['league_name'], prefix='league', drop_first=False)
        print("   ✅ Done")
        print()
        
        df['is_home'] = 1
        
        print("=" * 80)
        print(f"Total: {len(df)} partidos, {len(df.columns)} features")
        print("=" * 80)
        
        return df

def main():
    engineer = FeatureEngineerV2()
    df = engineer.generate_features()
    
    output_file = 'historical_matches_features_v2.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Guardado: {output_file} ({df.shape})")

if __name__ == '__main__':
    main()
