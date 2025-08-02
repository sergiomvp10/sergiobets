#!/usr/bin/env python3

import pygame
import os

def test_audio_only():
    """Test only the audio functionality without GUI dependencies"""
    print("=== TESTING AUDIO FUNCTIONALITY (NO GUI) ===")
    
    try:
        print("1. Testing pygame installation...")
        pygame.mixer.init()
        print("   ✅ pygame.mixer initialized successfully")
        
        print("\n2. Testing audio file search...")
        archivos_sonido = ['sonido_exito.mp3', 'success.mp3', 'notification.mp3', 'alert.mp3']
        archivos_encontrados = []
        
        for archivo in archivos_sonido:
            if os.path.exists(archivo):
                archivos_encontrados.append(archivo)
                print(f"   ✅ Found: {archivo}")
            else:
                print(f"   ❌ Not found: {archivo}")
        
        if not archivos_encontrados:
            print("   ⚠️  No MP3 files found - this is expected for testing")
            print("   📝 User should place their MP3 file as one of:", archivos_sonido)
        
        print("\n3. Testing pygame cleanup...")
        pygame.mixer.quit()
        print("   ✅ pygame.mixer cleaned up successfully")
        
        print("\n✅ Audio functionality test completed successfully")
        print("\n📋 Instructions for user:")
        print("   1. Place your MP3 file in the SergioBets directory")
        print("   2. Name it one of: sonido_exito.mp3, success.mp3, notification.mp3, or alert.mp3")
        print("   3. The sound will play automatically when 'Enviar pronóstico seleccionado' succeeds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in audio functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audio_only()
    if success:
        print("✅ Audio functionality test passed")
    else:
        print("❌ Audio functionality test failed")
