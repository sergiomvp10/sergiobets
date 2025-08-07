
import tkinter as tk
from tkinter import scrolledtext
import time

class TestUserDuplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Test User Duplication')
        self.root.geometry('800x600')
        
        # Create text area similar to the real one
        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=80, 
            height=30,
            font=('Courier', 10)
        )
        self.text_area.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        # Create refresh button
        self.refresh_btn = tk.Button(
            button_frame, 
            text='🔄 Refrescar', 
            command=self.refrescar_usuarios,
            bg='#3498db', 
            fg='white',
            font=('Segoe UI', 10, 'bold')
        )
        self.refresh_btn.pack(side='left', padx=5)
        
        # Counter for debugging
        self.call_count = 0
        self.executing = False
        
        # Initial load
        self.refrescar_usuarios()
    
    def refrescar_usuarios(self):
        self.call_count += 1
        print(f'🔄 LLAMADA #{self.call_count} a refrescar_usuarios()')
        
        # Check if already executing (race condition detection)
        if self.executing:
            print(f'⚠️  DETECTADA EJECUCIÓN SIMULTÁNEA - LLAMADA #{self.call_count}')
            return
        
        self.executing = True
        
        try:
            # Clear and populate (simulating the real function)
            self.text_area.delete('1.0', tk.END)
            self.text_area.config(state='normal')
            
            # Simulate user data
            users = [
                {'user_id': '7659029315', 'username': 'nJutro6', 'first_name': 'Mo', 'premium': True},
                {'user_id': '6286055084', 'username': 'Sie7e0', 'first_name': 'Left', 'premium': True},
                {'user_id': '6937898258', 'username': 'N/A', 'first_name': 'Juli', 'premium': True},
            ]
            
            # Add header
            self.text_area.insert(tk.END, f"{'ID':<12} {'Usuario':<20} {'Nombre':<20} {'Premium':<8} {'Expira':<20}
")
            self.text_area.insert(tk.END, "="*90 + "
")
            
            # Add users
            for user in users:
                premium = "✅ SÍ" if user.get('premium', False) else "❌ NO"
                linea = f"{user['user_id']:<12} {user['username']:<20} {user['first_name']:<20} {premium:<8} {'2025-08-12 20:47':<20}
"
                self.text_area.insert(tk.END, linea)
            
            self.text_area.config(state='disabled')
            print(f'✅ COMPLETADA LLAMADA #{self.call_count}')
            
        except Exception as e:
            print(f'❌ ERROR EN LLAMADA #{self.call_count}: {e}')
        finally:
            self.executing = False
    
    def run(self):
        print('🎯 Iniciando test de duplicación...')
        print('Haz clic en Refrescar varias veces rápidamente para probar')
        self.root.mainloop()

if __name__ == '__main__':
    test = TestUserDuplication()
    test.run()
