#!/usr/bin/env python3
"""
Script to update existing corner bets in the track record with the corrected logic
Run this after updating track_record.py to re-evaluate corner bets that were previously marked incorrectly
"""

from track_record import TrackRecordManager
import json
import shutil
from datetime import datetime

def update_existing_corner_bets():
    """Update existing corner bets with corrected evaluation logic"""
    print("=== ACTUALIZANDO APUESTAS DE CORNERS EXISTENTES ===")
    
    backup_file = f"historial_predicciones_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy('historial_predicciones.json', backup_file)
    print(f"✅ Backup creado: {backup_file}")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        historial = json.load(f)
    
    corner_bets = [p for p in historial if 'corner' in p.get('prediccion', '').lower()]
    print(f"📊 Encontradas {len(corner_bets)} apuestas de corners en el historial")
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    print("\n🔄 Ejecutando actualización completa del track record...")
    try:
        result = tracker.actualizar_historial_con_resultados()
        print(f"✅ Actualización completada: {result}")
        
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            updated_historial = json.load(f)
        
        updated_corner_bets = [p for p in updated_historial if 'corner' in p.get('prediccion', '').lower()]
        
        print(f"\n📈 RESULTADOS DE LA ACTUALIZACIÓN:")
        print(f"   Total de apuestas de corners: {len(updated_corner_bets)}")
        
        won_corners = [p for p in updated_corner_bets if p.get('acierto') == True]
        lost_corners = [p for p in updated_corner_bets if p.get('acierto') == False]
        pending_corners = [p for p in updated_corner_bets if p.get('acierto') is None]
        
        print(f"   ✅ Ganadas: {len(won_corners)}")
        print(f"   ❌ Perdidas: {len(lost_corners)}")
        print(f"   ⏳ Pendientes: {len(pending_corners)}")
        
        print(f"\n🔍 EJEMPLOS DE APUESTAS ACTUALIZADAS:")
        for i, bet in enumerate(won_corners[:3]):
            if bet.get('resultado_real'):
                corners = bet['resultado_real'].get('total_corners', 'N/A')
                print(f"   {i+1}. {bet.get('prediccion')} - GANADA (Corners: {corners})")
        
        for i, bet in enumerate(lost_corners[:3]):
            if bet.get('resultado_real'):
                corners = bet['resultado_real'].get('total_corners', 'N/A')
                print(f"   {i+1}. {bet.get('prediccion')} - PERDIDA (Corners: {corners})")
        
        print(f"\n✅ Actualización completada exitosamente!")
        print(f"📁 Backup guardado en: {backup_file}")
        
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")
        print(f"🔄 Restaurando backup...")
        shutil.copy(backup_file, 'historial_predicciones.json')
        print(f"✅ Backup restaurado")
        raise

if __name__ == "__main__":
    update_existing_corner_bets()
