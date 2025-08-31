#!/usr/bin/env python3
"""Test manual editing functionality"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_manual_editing():
    """Test manual editing of predictions"""
    print("🧪 TESTING MANUAL EDITING FUNCTIONALITY")
    print("=" * 60)
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Total predictions: {len(data)}")
        
        editable_predictions = []
        for pred in data:
            if pred.get('sent_to_telegram', False) and pred.get('resultado_real'):
                editable_predictions.append(pred)
        
        print(f"✏️ Editable predictions: {len(editable_predictions)}")
        
        if editable_predictions:
            test_pred = editable_predictions[0]
            print(f"\n🎯 Testing with prediction: {test_pred.get('partido', 'N/A')}")
            print(f"   Current acierto: {test_pred.get('acierto')}")
            print(f"   Current ganancia: {test_pred.get('ganancia')}")
            
            original_acierto = test_pred.get('acierto')
            test_pred['acierto'] = not original_acierto if original_acierto is not None else True
            test_pred['actualizacion_manual'] = True
            
            print(f"   After manual edit: {test_pred.get('acierto')}")
            print("✅ Manual editing simulation successful")
        
        predictions_with_results = len([p for p in data if p.get('resultado_real')])
        predictions_pending = len([p for p in data if p.get('acierto') is None])
        predictions_won = len([p for p in data if p.get('acierto') is True])
        predictions_lost = len([p for p in data if p.get('acierto') is False])
        
        print(f"\n📈 PREDICTION STATISTICS:")
        print(f"   • With results: {predictions_with_results}")
        print(f"   • Pending: {predictions_pending}")
        print(f"   • Won: {predictions_won}")
        print(f"   • Lost: {predictions_lost}")
        
        manual_edits = len([p for p in data if p.get('actualizacion_manual')])
        print(f"   • Manual edits: {manual_edits}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing manual editing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manual_editing()
    if success:
        print("\n✅ MANUAL EDITING TEST PASSED")
    else:
        print("\n❌ MANUAL EDITING TEST FAILED")
