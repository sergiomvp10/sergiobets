#!/usr/bin/env python3
"""
Clean Old Bot Users Script
Removes all users from the old bot system and prepares for new bot @BetGeniuXbot
"""

import json
import os
from datetime import datetime
from access_manager import access_manager

def migrate_existing_users_to_new_bot():
    """Migrate existing users without bot_username to new bot"""
    users = access_manager._load_users()
    migrated_count = 0
    
    for user in users:
        if "bot_username" not in user:
            user["bot_username"] = "BetGeniuXbot"
            migrated_count += 1
    
    if migrated_count > 0:
        access_manager._save_users(users)
        print(f"✅ {migrated_count} usuarios migrados al nuevo bot @BetGeniuXbot")
    
    return migrated_count

def main():
    """Clean old bot users and prepare for new bot"""
    print("🧹 LIMPIANDO USUARIOS DEL BOT ANTERIOR")
    print("=" * 50)
    print("🎯 Preparando para nuevo bot: @BetGeniuXbot")
    print()
    
    migrated = migrate_existing_users_to_new_bot()
    
    cleaned = access_manager.limpiar_usuarios_bot_anterior("BetGeniuXbot")
    
    usuarios_actuales = access_manager.contar_usuarios_por_bot("BetGeniuXbot")
    
    print()
    print("🎉 LIMPIEZA COMPLETADA!")
    print("=" * 40)
    print(f"✅ Usuarios migrados: {migrated}")
    print(f"🧹 Usuarios del bot anterior limpiados: {cleaned}")
    print(f"📱 Usuarios del nuevo bot @BetGeniuXbot: {usuarios_actuales}")
    print()
    print("🔍 Próximos pasos:")
    print("   1. Iniciar nuevo bot: python3 run_telegram_bot.py")
    print("   2. Probar comando /start con @BetGeniuXbot")
    print("   3. Verificar que el registro de usuarios funciona correctamente")

if __name__ == "__main__":
    main()
