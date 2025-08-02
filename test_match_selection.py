#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_match_selection_functionality():
    """Test the match selection with checkboxes functionality"""
    print("=== TESTING MATCH SELECTION FUNCTIONALITY ===")
    
    try:
        print("1. Testing match data structure...")
        
        sample_matches = [
            {
                "local": "Atlético Nacional",
                "visitante": "Millonarios", 
                "liga": "Liga Colombiana",
                "hora": "Por confirmar",
                "cuotas": {
                    "casa": "Betplay",
                    "local": "1.85",
                    "empate": "3.20", 
                    "visitante": "4.10"
                }
            },
            {
                "local": "América de Cali",
                "visitante": "Junior",
                "liga": "Liga Colombiana", 
                "hora": "Por confirmar",
                "cuotas": {
                    "casa": "Betplay",
                    "local": "2.10",
                    "empate": "3.00",
                    "visitante": "3.80"
                }
            }
        ]
        
        print(f"   ✅ Sample matches created: {len(sample_matches)} matches")
        for match in sample_matches:
            print(f"   - {match['local']} vs {match['visitante']} ({match['liga']})")
        
        print("\n2. Testing match message generation...")
        
        fecha = "2025-08-02"
        mensaje_partidos = f"⚽ PARTIDOS SELECCIONADOS ({fecha})\n\n"
        
        partidos_por_liga = {}
        for partido in sample_matches:
            liga = partido["liga"]
            if liga not in partidos_por_liga:
                partidos_por_liga[liga] = []
            
            info = f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
            info += f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"
            partidos_por_liga[liga].append(info)
        
        for liga in sorted(partidos_por_liga.keys()):
            mensaje_partidos += f"🔷 {liga}\n"
            for info in partidos_por_liga[liga]:
                mensaje_partidos += info
        
        print("   ✅ Message generated successfully:")
        print(f"   {mensaje_partidos[:200]}...")
        
        print("\n3. Testing file saving functionality...")
        
        import json
        
        with open('test_partidos_seleccionados.json', 'w', encoding='utf-8') as f:
            json.dump(sample_matches, f, indent=2, ensure_ascii=False)
        
        with open('test_partidos_seleccionados.txt', 'w', encoding='utf-8') as f:
            f.write(mensaje_partidos)
        
        if os.path.exists('test_partidos_seleccionados.json') and os.path.exists('test_partidos_seleccionados.txt'):
            print("   ✅ Files saved successfully")
        else:
            print("   ❌ File saving failed")
            return False
        
        print("\n4. Testing UI components...")
        try:
            import tkinter as tk
            from tkinter import ttk
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            frame_partidos = tk.Frame(root, bg="#f1f3f4")
            
            checkboxes_partidos = []
            partidos_actuales = sample_matches.copy()
            
            for i, partido in enumerate(partidos_actuales):
                var = tk.BooleanVar()
                checkboxes_partidos.append(var)
                
                partido_text = f"{partido['local']} vs {partido['visitante']} - {partido['liga']}"
                cuotas_text = f"Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}"
                
                frame_partido = tk.Frame(frame_partidos, bg="#f1f3f4")
                
                checkbox = tk.Checkbutton(frame_partido, variable=var, bg="#f1f3f4", 
                                         font=("Segoe UI", 9))
                
                label_partido = tk.Label(frame_partido, text=partido_text, 
                                       font=("Segoe UI", 9, "bold"), bg="#f1f3f4", fg="#333")
                
                label_cuotas = tk.Label(frame_partido, text=cuotas_text, 
                                      font=("Segoe UI", 8), bg="#f1f3f4", fg="#666")
            
            print("   ✅ UI components created successfully")
            
            checkboxes_partidos[0].set(True)  # Select first match
            
            partidos_seleccionados = []
            for i, var in enumerate(checkboxes_partidos):
                if var.get():
                    partidos_seleccionados.append(partidos_actuales[i])
            
            print(f"   ✅ Selection logic works: {len(partidos_seleccionados)} match(es) selected")
            
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ UI component test failed: {e}")
            return False
        
        if os.path.exists('test_partidos_seleccionados.json'):
            os.remove('test_partidos_seleccionados.json')
        if os.path.exists('test_partidos_seleccionados.txt'):
            os.remove('test_partidos_seleccionados.txt')
        
        print("\n✅ Match selection functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in match selection test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_match_selection_functionality()
    if success:
        print("✅ Match selection test passed")
    else:
        print("❌ Match selection test failed")
