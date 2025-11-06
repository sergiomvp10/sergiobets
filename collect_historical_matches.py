"""
Script para recolectar partidos históricos de FootyStats API
Con rate limiting (1800 requests/hora = 30/minuto)
"""

import os
import time
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv('FOOTYSTATS_API_KEY')
BASE_URL = 'https://api.football-data-api.com'
DATABASE_URL = os.getenv('DATABASE_URL')

REQUEST_DELAY = 2.0  # segundos entre requests

PRIORITY_LEAGUES = {
    'England Premier League': {
        'seasons': [
            {'id': 12325, 'year': '2024/2025'},
            {'id': 9660, 'year': '2023/2024'},
            {'id': 7704, 'year': '2022/2023'},
        ]
    },
    'Spain La Liga': {
        'seasons': [
            {'id': 12316, 'year': '2024/2025'},
            {'id': 9665, 'year': '2023/2024'},
            {'id': 7705, 'year': '2022/2023'},
        ]
    },
    'Germany Bundesliga': {
        'seasons': [
            {'id': 12529, 'year': '2024/2025'},
            {'id': 9655, 'year': '2023/2024'},
            {'id': 7706, 'year': '2022/2023'},
        ]
    },
    'Italy Serie A': {
        'seasons': [
            {'id': 12530, 'year': '2024/2025'},
            {'id': 9697, 'year': '2023/2024'},
            {'id': 7707, 'year': '2022/2023'},
        ]
    },
    'France Ligue 1': {
        'seasons': [
            {'id': 12337, 'year': '2024/2025'},
            {'id': 9674, 'year': '2023/2024'},
            {'id': 7708, 'year': '2022/2023'},
        ]
    },
    'Colombia Categoria Primera A': {
        'seasons': [
            {'id': 14086, 'year': '2025'},
            {'id': 10997, 'year': '2024'},
            {'id': 8936, 'year': '2023'},
        ]
    },
    'Argentina Primera División': {
        'seasons': [
            {'id': 5220, 'year': '2020/2021'},
            {'id': 2366, 'year': '2019/2020'},
            {'id': 1712, 'year': '2018/2019'},
        ]
    },
    'South America Copa Libertadores': {
        'seasons': [
            {'id': 10971, 'year': '2024'},
            {'id': 8781, 'year': '2023'},
            {'id': 7354, 'year': '2022'},
        ]
    },
    'South America Copa Sudamericana': {
        'seasons': [
            {'id': 10972, 'year': '2024'},
            {'id': 8782, 'year': '2023'},
            {'id': 7355, 'year': '2022'},
        ]
    },
}

class HistoricalDataCollector:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor()
        self.request_count = 0
        self.start_time = time.time()
        self.matches_inserted = 0
        self.matches_skipped = 0
        
    def __del__(self):
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def rate_limit(self):
        """Esperar para respetar rate limit"""
        time.sleep(REQUEST_DELAY)
        self.request_count += 1
        
        if self.request_count % 10 == 0:
            elapsed = time.time() - self.start_time
            rate = self.request_count / (elapsed / 60)  # requests por minuto
            print(f"  📊 Requests: {self.request_count} | Rate: {rate:.1f}/min | Insertados: {self.matches_inserted} | Skipped: {self.matches_skipped}")
    
    def fetch_season_matches(self, season_id, league_name, season_year):
        """Obtener partidos de una temporada específica"""
        endpoint = f"{BASE_URL}/league-matches"
        params = {
            'key': API_KEY,
            'season_id': season_id
        }
        
        try:
            self.rate_limit()
            response = requests.get(endpoint, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('data', [])
                print(f"  ✅ {league_name} {season_year}: {len(matches)} partidos")
                return matches
            elif response.status_code == 429:
                print(f"  ⚠️ Rate limit alcanzado, esperando 60 segundos...")
                time.sleep(60)
                return self.fetch_season_matches(season_id, league_name, season_year)
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:200]}")
                return []
        except Exception as e:
            print(f"  ❌ Excepción: {e}")
            return []
    
    def parse_match_result(self, match):
        """Determinar resultado del partido"""
        status = match.get('status')
        if status != 'complete':
            return None
        
        home_goals = match.get('homeGoalCount')
        away_goals = match.get('awayGoalCount')
        
        if home_goals is None or away_goals is None:
            return None
        
        if home_goals > away_goals:
            return 'home'
        elif away_goals > home_goals:
            return 'away'
        else:
            return 'draw'
    
    def insert_match(self, match, league_name, season_year):
        """Insertar partido en la base de datos"""
        try:
            match_id = match.get('id')
            if not match_id:
                return False
            
            self.cur.execute("SELECT id FROM historical_matches WHERE match_id = %s", (match_id,))
            if self.cur.fetchone():
                self.matches_skipped += 1
                return False
            
            result = self.parse_match_result(match)
            if not result:
                self.matches_skipped += 1
                return False
            
            date_unix = match.get('date_unix')
            if date_unix:
                date_utc = datetime.fromtimestamp(date_unix)
            else:
                self.matches_skipped += 1
                return False
            
            home_id = match.get('homeID') or match.get('home_id')
            away_id = match.get('awayID') or match.get('away_id')
            home_name = match.get('home_name', 'Unknown')
            away_name = match.get('away_name', 'Unknown')
            home_goals = match.get('homeGoalCount', 0)
            away_goals = match.get('awayGoalCount', 0)
            competition_id = match.get('competition_id')
            
            odds_ft_1 = match.get('odds_ft_1')
            odds_ft_x = match.get('odds_ft_x')
            odds_ft_2 = match.get('odds_ft_2')
            odds_btts_yes = match.get('odds_btts_yes')
            odds_btts_no = match.get('odds_btts_no')
            odds_over25 = match.get('odds_over_25')
            odds_under25 = match.get('odds_under_25')
            
            self.cur.execute("""
                INSERT INTO historical_matches (
                    match_id, date_utc, season, league_name, competition_id,
                    home_id, away_id, home_name, away_name,
                    result, goals_home, goals_away,
                    odds_ft_1, odds_ft_x, odds_ft_2,
                    odds_btts_yes, odds_btts_no,
                    odds_over25, odds_under25
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s
                )
            """, (
                match_id, date_utc, season_year, league_name, competition_id,
                home_id, away_id, home_name, away_name,
                result, home_goals, away_goals,
                odds_ft_1, odds_ft_x, odds_ft_2,
                odds_btts_yes, odds_btts_no,
                odds_over25, odds_under25
            ))
            
            self.conn.commit()
            self.matches_inserted += 1
            return True
            
        except Exception as e:
            print(f"  ❌ Error insertando partido {match.get('id')}: {e}")
            self.conn.rollback()
            return False
    
    def collect_all(self, leagues=None):
        """Recolectar datos de todas las ligas"""
        if leagues is None:
            leagues = PRIORITY_LEAGUES
        
        print('=' * 80)
        print('RECOLECCIÓN DE DATOS HISTÓRICOS')
        print('=' * 80)
        print()
        print(f"Ligas a procesar: {len(leagues)}")
        print(f"Rate limit: {REQUEST_DELAY}s entre requests (30/min)")
        print()
        
        for league_name, league_data in leagues.items():
            print(f"\n📊 {league_name}")
            print('-' * 80)
            
            for season in league_data['seasons']:
                season_id = season['id']
                season_year = season['year']
                
                matches = self.fetch_season_matches(season_id, league_name, season_year)
                
                for match in matches:
                    self.insert_match(match, league_name, season_year)
        
        print()
        print('=' * 80)
        print('RESUMEN DE RECOLECCIÓN')
        print('=' * 80)
        print(f"Total requests: {self.request_count}")
        print(f"Partidos insertados: {self.matches_inserted}")
        print(f"Partidos omitidos: {self.matches_skipped}")
        print(f"Tiempo total: {(time.time() - self.start_time) / 60:.1f} minutos")
        print()
        
        self.cur.execute("SELECT COUNT(*) FROM historical_matches")
        total = self.cur.fetchone()[0]
        print(f"Total en base de datos: {total} partidos")
        print('=' * 80)

def main():
    """Función principal"""
    collector = HistoricalDataCollector()
    
    collector.collect_all(PRIORITY_LEAGUES)
    

if __name__ == '__main__':
    main()
