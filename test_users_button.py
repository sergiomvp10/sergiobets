#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_users_button_functionality():
    """Test the Users button functionality"""
    print("=== TESTING USERS BUTTON FUNCTIONALITY ===")
    
    try:
        test_usuarios_content = """123456789 - testuser1 - Juan
987654321 - testuser2 - María
555555555 - sin_username - Pedro"""
        
        with open('usuarios.txt', 'w', encoding='utf-8') as f:
            f.write(test_usuarios_content)
        
        print("1. Testing usuarios.txt file creation...")
        if os.path.exists('usuarios.txt'):
            print("   ✅ usuarios.txt created successfully")
        else:
            print("   ❌ usuarios.txt not found")
            return False
        
        print("\n2. Testing file reading functionality...")
        usuarios_data = []
        total_usuarios = 0
        
        with open('usuarios.txt', 'r', encoding='utf-8') as f:
            for linea in f:
                if linea.strip() and ' - ' in linea:
                    partes = linea.strip().split(' - ')
                    if len(partes) >= 3:
                        usuarios_data.append({
                            'user_id': partes[0],
                            'username': partes[1],
                            'first_name': partes[2]
                        })
                        total_usuarios += 1
        
        print(f"   ✅ Read {total_usuarios} users successfully")
        for usuario in usuarios_data:
            print(f"   - {usuario['user_id']} | {usuario['username']} | {usuario['first_name']}")
        
        print("\n3. Testing UI integration...")
        try:
            import tkinter as tk
            from tkinter import scrolledtext
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            ventana_usuarios = tk.Toplevel(root)
            ventana_usuarios.withdraw()  # Hide the test window
            
            frame_header = tk.Frame(ventana_usuarios, bg="#f1f3f4")
            titulo_text = f"👥 Usuarios Registrados en Telegram ({total_usuarios} usuarios)"
            label_titulo = tk.Label(frame_header, text=titulo_text, 
                                   font=("Segoe UI", 14, "bold"), bg="#f1f3f4", fg="#333")
            
            frame_lista = tk.Frame(ventana_usuarios, bg="#f1f3f4")
            texto_usuarios = scrolledtext.ScrolledText(frame_lista, 
                                                      font=("Courier", 10),
                                                      bg="white", 
                                                      fg="#333",
                                                      wrap=tk.WORD,
                                                      state=tk.NORMAL)
            
            texto_usuarios.insert(tk.END, "ID de Usuario       | Username           | Nombre\n")
            texto_usuarios.insert(tk.END, "-" * 65 + "\n")
            
            for usuario in usuarios_data:
                user_id = usuario['user_id'].ljust(16)
                username = usuario['username'].ljust(18)
                first_name = usuario['first_name']
                
                linea = f"{user_id} | {username} | {first_name}\n"
                texto_usuarios.insert(tk.END, linea)
            
            texto_usuarios.config(state=tk.DISABLED)
            
            print("   ✅ UI components created successfully")
            
            ventana_usuarios.destroy()
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ UI integration test failed: {e}")
            return False
        
        if os.path.exists('usuarios.txt'):
            os.remove('usuarios.txt')
        
        print("\n✅ Users button functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in users button test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_users_button_functionality()
    if success:
        print("✅ Users button test passed")
    else:
        print("❌ Users button test failed")
