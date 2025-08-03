import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

class OddsAPIManager:
    def __init__(self, the_odds_api_key: str, footystats_api_key: str):
        self.the_odds_api_key = the_odds_api_key
        self.footystats_api_key = footystats_api_key
        self.the_odds_base_url = "https://api.the-odds-api.com/v4"
        self.footystats_base_url = "https://api.football-data-api.com"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        self.league_mapping = {
            "Premier League": "soccer_epl",
            "La Liga": "soccer_spain_la_liga", 
            "Serie A": "soccer_italy_serie_a",
            "Bundesliga": "soccer_germany_bundesliga",
            "Ligue 1": "soccer_france_ligue_one",
            "Champions League": "soccer_uefa_champs_league",
            "Liga MX": "soccer_mexico_ligamx",
            "MLS": "soccer_usa_mls",
            "Brasileirão": "soccer_brazil_campeonato",
            "Liga Argentina": "soccer_argentina_primera_division"
        }
    
    def get_enhanced_odds(self, fecha: str) -> List[Dict[str, Any]]:
        """Get odds from multiple sources with fallback"""
        cache_key = f"enhanced_odds_{fecha}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            the_odds_data = self._get_the_odds_api_data(fecha)
            if the_odds_data:
                self._update_cache(cache_key, the_odds_data)
                return the_odds_data
        except Exception as e:
            print(f"Error with The Odds API: {e}")
        
        try:
            footystats_data = self._get_footystats_data(fecha)
            if footystats_data:
                self._update_cache(cache_key, footystats_data)
                return footystats_data
        except Exception as e:
            print(f"Error with FootyStats API: {e}")
        
        return []
    
    def _get_the_odds_api_data(self, fecha: str) -> List[Dict[str, Any]]:
        """Get odds from The Odds API for multiple soccer leagues"""
        all_matches = []
        
        for league_name, sport_key in self.league_mapping.items():
            try:
                url = f"{self.the_odds_base_url}/sports/{sport_key}/odds"
                params = {
                    "apiKey": self.the_odds_api_key,
                    "regions": "us,uk,eu",
                    "markets": "h2h,btts,totals",
                    "oddsFormat": "decimal",
                    "dateFormat": "iso"
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    matches = self._process_the_odds_api_response(data, league_name, fecha)
                    all_matches.extend(matches)
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching {league_name} from The Odds API: {e}")
                continue
        
        return all_matches
    
    def _process_the_odds_api_response(self, data: List[Dict], league_name: str, fecha: str) -> List[Dict[str, Any]]:
        """Process The Odds API response into SergioBets format"""
        matches = []
        target_date = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        for match in data:
            try:
                commence_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
                match_date = commence_time.date()
                
                if match_date != target_date:
                    continue
                
                best_odds = self._find_best_odds(match['bookmakers'])
                
                if best_odds:
                    processed_match = {
                        "hora": commence_time.strftime("%H:%M"),
                        "liga": league_name,
                        "local": match['home_team'],
                        "visitante": match['away_team'],
                        "cuotas": {
                            "casa": "Multi-Bookmaker",
                            "local": str(best_odds['h2h']['home']),
                            "empate": str(best_odds['h2h']['draw']),
                            "visitante": str(best_odds['h2h']['away']),
                            "btts_si": str(best_odds.get('btts', {}).get('yes', 'N/A')),
                            "btts_no": str(best_odds.get('btts', {}).get('no', 'N/A')),
                            "over_25": str(best_odds.get('totals', {}).get('over', 'N/A')),
                            "under_25": str(best_odds.get('totals', {}).get('under', 'N/A'))
                        },
                        "bookmakers": self._get_bookmaker_comparison(match['bookmakers'])
                    }
                    matches.append(processed_match)
                    
            except Exception as e:
                print(f"Error processing match: {e}")
                continue
        
        return matches
    
    def _find_best_odds(self, bookmakers: List[Dict]) -> Dict[str, Any]:
        """Find best odds across all bookmakers"""
        best_odds = {
            'h2h': {'home': 0, 'draw': 0, 'away': 0},
            'btts': {'yes': 0, 'no': 0},
            'totals': {'over': 0, 'under': 0}
        }
        
        for bookmaker in bookmakers:
            for market in bookmaker.get('markets', []):
                market_key = market['key']
                
                if market_key == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == bookmaker.get('home_team', ''):
                            best_odds['h2h']['home'] = max(best_odds['h2h']['home'], outcome['price'])
                        elif outcome['name'] == bookmaker.get('away_team', ''):
                            best_odds['h2h']['away'] = max(best_odds['h2h']['away'], outcome['price'])
                        elif 'draw' in outcome['name'].lower():
                            best_odds['h2h']['draw'] = max(best_odds['h2h']['draw'], outcome['price'])
                
                elif market_key == 'btts':
                    for outcome in market['outcomes']:
                        if 'yes' in outcome['name'].lower():
                            best_odds['btts']['yes'] = max(best_odds['btts']['yes'], outcome['price'])
                        elif 'no' in outcome['name'].lower():
                            best_odds['btts']['no'] = max(best_odds['btts']['no'], outcome['price'])
                
                elif market_key == 'totals':
                    for outcome in market['outcomes']:
                        if 'over' in outcome['name'].lower():
                            best_odds['totals']['over'] = max(best_odds['totals']['over'], outcome['price'])
                        elif 'under' in outcome['name'].lower():
                            best_odds['totals']['under'] = max(best_odds['totals']['under'], outcome['price'])
        
        return best_odds
    
    def _get_bookmaker_comparison(self, bookmakers: List[Dict]) -> List[Dict[str, Any]]:
        """Get comparison of odds across bookmakers"""
        comparison = []
        for bookmaker in bookmakers[:5]:  # Limit to top 5 bookmakers
            bm_data = {
                "name": bookmaker['title'],
                "last_update": bookmaker.get('last_update', ''),
                "odds": {}
            }
            
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        bm_data['odds'][outcome['name']] = outcome['price']
            
            comparison.append(bm_data)
        
        return comparison
    
    def _get_footystats_data(self, fecha: str) -> List[Dict[str, Any]]:
        """Fallback to FootyStats API"""
        from footystats_api import obtener_partidos_del_dia
        
        try:
            partidos_raw = obtener_partidos_del_dia(fecha)
            partidos = []
            
            for partido in partidos_raw:
                partidos.append({
                    "hora": partido.get("time", "15:00"),
                    "liga": partido.get("league_name", "Unknown League"),
                    "local": partido.get("home_name", "Home Team"),
                    "visitante": partido.get("away_name", "Away Team"),
                    "cuotas": {
                        "casa": "FootyStats",
                        "local": str(partido.get("odds_ft_1", "2.00")),
                        "empate": str(partido.get("odds_ft_x", "3.00")),
                        "visitante": str(partido.get("odds_ft_2", "4.00"))
                    }
                })
            
            return partidos
            
        except Exception as e:
            print(f"Error with FootyStats fallback: {e}")
            return []
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _update_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        """Update cache with new data"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
