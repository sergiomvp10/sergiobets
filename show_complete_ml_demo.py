"""
Complete ML Demo - Shows real matches with all three bet types (1X2, BTTS, O/U 2.5)
"""

from footystats_api import obtener_partidos_del_dia, obtener_estadisticas_equipo
from ml_model_service_complete import CompleteMLModelService
from datetime import datetime
import json

def calculate_ev(probability, odds):
    """Calculate Expected Value"""
    return (probability * odds) - 1

def get_team_name(team_id):
    """Get team name from API"""
    try:
        stats = obtener_estadisticas_equipo(team_id, use_cache=True)
        if stats:
            if isinstance(stats, list) and len(stats) > 0:
                return stats[0].get('name', f'Team {team_id}')
            elif isinstance(stats, dict):
                return stats.get('name', f'Team {team_id}')
    except:
        pass
    return f'Team {team_id}'

print("=" * 80)
print("DEMOSTRACIÓN COMPLETA DEL SISTEMA ML")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 80)
print()

# Get matches
print("📥 Obteniendo partidos de hoy...")
partidos = obtener_partidos_del_dia()
print(f"✅ {len(partidos)} partidos encontrados")
print()

# Initialize ML
print("🤖 Inicializando sistema ML...")
ml_service = CompleteMLModelService()
print()

# Process first 3 matches with complete data
count = 0
total_recommendations = {'1x2': 0, 'btts': 0, 'ou25': 0}

for partido in partidos:
    if count >= 3:
        break
    
    # Get IDs
    home_id = partido.get('homeID') or partido.get('home_id')
    away_id = partido.get('awayID') or partido.get('away_id')
    
    if not home_id or not away_id:
        continue
    
    # Get odds
    odds_1 = partido.get('odds_ft_1')
    odds_x = partido.get('odds_ft_x')
    odds_2 = partido.get('odds_ft_2')
    odds_btts_yes = partido.get('odds_btts_yes')
    odds_btts_no = partido.get('odds_btts_no')
    odds_over25 = partido.get('odds_ft_over25')
    odds_under25 = partido.get('odds_ft_under25')
    
    if not all([odds_1, odds_x, odds_2, odds_btts_yes, odds_btts_no, odds_over25, odds_under25]):
        continue
    
    count += 1
    
    # Get team names
    home_name = get_team_name(home_id)
    away_name = get_team_name(away_id)
    
    print("=" * 80)
    print(f"PARTIDO {count}")
    print("=" * 80)
    print(f"🏟️  {home_name} vs {away_name}")
    print(f"🏆 Liga: {partido.get('competition_name', 'N/A')}")
    print()
    
    # Show market odds
    print("💰 CUOTAS DEL MERCADO:")
    print(f"   1X2: Local {odds_1:.2f} | Empate {odds_x:.2f} | Visitante {odds_2:.2f}")
    print(f"   BTTS: Sí {odds_btts_yes:.2f} | No {odds_btts_no:.2f}")
    print(f"   O/U 2.5: Over {odds_over25:.2f} | Under {odds_under25:.2f}")
    print()
    
    # Get ML predictions for all markets
    league_name = partido.get('competition_name', 'Unknown')
    market_odds = {'home': odds_1, 'draw': odds_x, 'away': odds_2}
    
    predictions = ml_service.predict_all_markets(home_id, away_id, league_name, market_odds)
    
    # Show 1X2 analysis
    print("🤖 ANÁLISIS ML - 1X2:")
    print(f"   Predicción: {predictions['1x2']['prediction'].upper()}")
    print(f"   Probabilidades:")
    print(f"     • Local:     {predictions['1x2']['probabilities']['home']:.1%}")
    print(f"     • Empate:    {predictions['1x2']['probabilities']['draw']:.1%}")
    print(f"     • Visitante: {predictions['1x2']['probabilities']['away']:.1%}")
    
    # Calculate EV for each 1X2 option
    ev_home = calculate_ev(predictions['1x2']['probabilities']['home'], odds_1)
    ev_draw = calculate_ev(predictions['1x2']['probabilities']['draw'], odds_x)
    ev_away = calculate_ev(predictions['1x2']['probabilities']['away'], odds_2)
    
    print(f"   Valor Esperado:")
    print(f"     • Local:     {ev_home:+.2%}")
    print(f"     • Empate:    {ev_draw:+.2%}")
    print(f"     • Visitante: {ev_away:+.2%}")
    
    best_1x2_ev = max(ev_home, ev_draw, ev_away)
    if best_1x2_ev > 0:
        if best_1x2_ev == ev_home:
            print(f"   ✅ RECOMIENDA: Local @ {odds_1:.2f} (EV: {ev_home:+.2%})")
            total_recommendations['1x2'] += 1
        elif best_1x2_ev == ev_draw:
            print(f"   ✅ RECOMIENDA: Empate @ {odds_x:.2f} (EV: {ev_draw:+.2%})")
            total_recommendations['1x2'] += 1
        else:
            print(f"   ✅ RECOMIENDA: Visitante @ {odds_2:.2f} (EV: {ev_away:+.2%})")
            total_recommendations['1x2'] += 1
    else:
        print(f"   ❌ NO RECOMIENDA (todos EV negativos)")
    print()
    
    # Show BTTS analysis
    print("🤖 ANÁLISIS ML - BTTS:")
    print(f"   Predicción: {predictions['btts']['prediction'].upper()}")
    print(f"   Probabilidades:")
    print(f"     • Sí:  {predictions['btts']['probabilities']['yes']:.1%}")
    print(f"     • No:  {predictions['btts']['probabilities']['no']:.1%}")
    
    ev_btts_yes = calculate_ev(predictions['btts']['probabilities']['yes'], odds_btts_yes)
    ev_btts_no = calculate_ev(predictions['btts']['probabilities']['no'], odds_btts_no)
    
    print(f"   Valor Esperado:")
    print(f"     • Sí:  {ev_btts_yes:+.2%}")
    print(f"     • No:  {ev_btts_no:+.2%}")
    
    best_btts_ev = max(ev_btts_yes, ev_btts_no)
    if best_btts_ev > 0:
        if best_btts_ev == ev_btts_yes:
            print(f"   ✅ RECOMIENDA: BTTS Sí @ {odds_btts_yes:.2f} (EV: {ev_btts_yes:+.2%})")
            total_recommendations['btts'] += 1
        else:
            print(f"   ✅ RECOMIENDA: BTTS No @ {odds_btts_no:.2f} (EV: {ev_btts_no:+.2%})")
            total_recommendations['btts'] += 1
    else:
        print(f"   ❌ NO RECOMIENDA (todos EV negativos)")
    print()
    
    # Show O/U 2.5 analysis
    print("🤖 ANÁLISIS ML - OVER/UNDER 2.5:")
    print(f"   Predicción: {predictions['over_under_25']['prediction'].upper()}")
    print(f"   Probabilidades:")
    print(f"     • Over:  {predictions['over_under_25']['probabilities']['over']:.1%}")
    print(f"     • Under: {predictions['over_under_25']['probabilities']['under']:.1%}")
    
    ev_over = calculate_ev(predictions['over_under_25']['probabilities']['over'], odds_over25)
    ev_under = calculate_ev(predictions['over_under_25']['probabilities']['under'], odds_under25)
    
    print(f"   Valor Esperado:")
    print(f"     • Over:  {ev_over:+.2%}")
    print(f"     • Under: {ev_under:+.2%}")
    
    best_ou_ev = max(ev_over, ev_under)
    if best_ou_ev > 0:
        if best_ou_ev == ev_over:
            print(f"   ✅ RECOMIENDA: Over 2.5 @ {odds_over25:.2f} (EV: {ev_over:+.2%})")
            total_recommendations['ou25'] += 1
        else:
            print(f"   ✅ RECOMIENDA: Under 2.5 @ {odds_under25:.2f} (EV: {ev_under:+.2%})")
            total_recommendations['ou25'] += 1
    else:
        print(f"   ❌ NO RECOMIENDA (todos EV negativos)")
    print()
    
    # Show best overall bet
    all_evs = [
        ('1X2 Local', ev_home, odds_1),
        ('1X2 Empate', ev_draw, odds_x),
        ('1X2 Visitante', ev_away, odds_2),
        ('BTTS Sí', ev_btts_yes, odds_btts_yes),
        ('BTTS No', ev_btts_no, odds_btts_no),
        ('Over 2.5', ev_over, odds_over25),
        ('Under 2.5', ev_under, odds_under25)
    ]
    
    best_bet = max(all_evs, key=lambda x: x[1])
    
    print("💡 MEJOR APUESTA GENERAL:")
    if best_bet[1] > 0:
        print(f"   {best_bet[0]} @ {best_bet[2]:.2f}")
        print(f"   EV: {best_bet[1]:+.2%} ✅")
    else:
        print(f"   Ninguna (mejor EV: {best_bet[1]:+.2%}) ❌")
    print()

print("=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)
print()
print(f"✅ Partidos analizados: {count}")
print(f"✅ Recomendaciones por mercado:")
print(f"   • 1X2: {total_recommendations['1x2']} de {count}")
print(f"   • BTTS: {total_recommendations['btts']} de {count}")
print(f"   • O/U 2.5: {total_recommendations['ou25']} de {count}")
print()
print("🎯 CAPACIDADES DEL SISTEMA ML:")
print("   ✅ Analiza 3 mercados: 1X2, BTTS, Over/Under 2.5")
print("   ✅ Usa datos reales de equipos (Elo, forma, descanso)")
print("   ✅ Calcula probabilidades para cada opción")
print("   ✅ Compara con cuotas del mercado")
print("   ✅ Identifica apuestas con valor esperado positivo")
print("   ✅ Selecciona la mejor apuesta entre todos los mercados")
print()
print("⚠️  LIMITACIONES:")
print(f"   • Accuracy 1X2: 51.49% (por debajo del mercado 52.33%)")
print(f"   • Accuracy BTTS: 53.15%")
print(f"   • Accuracy O/U 2.5: 58.34% ✅ (mejor que el mercado)")
print()
print("💡 RECOMENDACIÓN:")
print("   Usar como FILTRO, no como sistema principal")
print("   Solo publicar apuestas con EV > 2%")
print("=" * 80)
