#!/usr/bin/env python3
"""
Access Manager for SergioBets VIP System
Manages premium user access, expiration dates, and user permissions
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AccessManager:
    def __init__(self, users_file: str = "usuarios.json"):
        self.users_file = users_file
        self.legacy_file = "usuarios.txt"
        self._migrate_from_legacy_if_needed()
    
    def _migrate_from_legacy_if_needed(self):
        """Migrate from usuarios.txt to usuarios.json if needed"""
        if os.path.exists(self.legacy_file) and not os.path.exists(self.users_file):
            print("🔄 Migrando usuarios de formato texto a JSON...")
            legacy_users = self._load_legacy_users()
            migrated_users = []
            
            for user_line in legacy_users:
                if " - " in user_line:
                    parts = user_line.strip().split(" - ")
                    if len(parts) >= 3:
                        user_id, username, first_name = parts[0], parts[1], parts[2]
                        migrated_users.append({
                            "user_id": user_id,
                            "username": username,
                            "first_name": first_name,
                            "premium": False,
                            "fecha_expiracion": None,
                            "fecha_registro": datetime.now().isoformat()
                        })
            
            self._save_users(migrated_users)
            
            backup_file = f"usuarios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.rename(self.legacy_file, backup_file)
            print(f"✅ Migración completada. Backup creado: {backup_file}")
    
    def _load_legacy_users(self) -> List[str]:
        """Load users from legacy usuarios.txt format"""
        try:
            with open(self.legacy_file, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            return []
    
    def _load_users(self) -> List[Dict]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"⚠️ Error leyendo {self.users_file}, creando archivo nuevo")
            return []
    
    def _save_users(self, users: List[Dict]):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando usuarios: {e}")
    
    def _find_user_index(self, user_id: str) -> Tuple[Optional[int], List[Dict]]:
        """Find user index in users list"""
        users = self._load_users()
        for i, user in enumerate(users):
            if str(user.get("user_id")) == str(user_id):
                return i, users
        return None, users
    
    def registrar_usuario(self, user_id: str, username: str, first_name: str) -> bool:
        """Register a new user or update existing user info"""
        user_index, users = self._find_user_index(user_id)
        
        if user_index is not None:
            users[user_index].update({
                "username": username,
                "first_name": first_name
            })
        else:
            users.append({
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "premium": False,
                "fecha_expiracion": None,
                "fecha_registro": datetime.now().isoformat()
            })
        
        self._save_users(users)
        return True
    
    def otorgar_acceso(self, user_id: str, dias: int) -> bool:
        """Grant premium access to user for X days"""
        user_index, users = self._find_user_index(user_id)
        
        if user_index is None:
            print(f"❌ Usuario {user_id} no encontrado")
            return False
        
        fecha_expiracion = datetime.now() + timedelta(days=dias)
        users[user_index].update({
            "premium": True,
            "fecha_expiracion": fecha_expiracion.isoformat()
        })
        
        self._save_users(users)
        print(f"✅ Acceso premium otorgado a {users[user_index]['username']} por {dias} días")
        return True
    
    def banear_usuario(self, user_id: str) -> bool:
        """Remove premium access immediately"""
        user_index, users = self._find_user_index(user_id)
        
        if user_index is None:
            print(f"❌ Usuario {user_id} no encontrado")
            return False
        
        users[user_index].update({
            "premium": False,
            "fecha_expiracion": None
        })
        
        self._save_users(users)
        print(f"✅ Usuario {users[user_index]['username']} baneado (acceso premium removido)")
        return True
    
    def verificar_acceso(self, user_id: str) -> bool:
        """Check if user has valid premium access"""
        user_index, users = self._find_user_index(user_id)
        
        if user_index is None:
            return False
        
        user = users[user_index]
        
        if not user.get("premium", False):
            return False
        
        fecha_expiracion_str = user.get("fecha_expiracion")
        if not fecha_expiracion_str:
            return False
        
        try:
            fecha_expiracion = datetime.fromisoformat(fecha_expiracion_str)
            return fecha_expiracion > datetime.now()
        except (ValueError, TypeError):
            return False
    
    def limpiar_usuarios_expirados(self) -> int:
        """Clean expired premium users and return count of cleaned users"""
        users = self._load_users()
        cleaned_count = 0
        
        for user in users:
            if user.get("premium", False) and user.get("fecha_expiracion"):
                try:
                    fecha_expiracion = datetime.fromisoformat(user["fecha_expiracion"])
                    if fecha_expiracion <= datetime.now():
                        user["premium"] = False
                        user["fecha_expiracion"] = None
                        cleaned_count += 1
                except (ValueError, TypeError):
                    user["premium"] = False
                    user["fecha_expiracion"] = None
                    cleaned_count += 1
        
        if cleaned_count > 0:
            self._save_users(users)
            print(f"🧹 {cleaned_count} usuarios con acceso expirado limpiados")
        
        return cleaned_count
    
    def obtener_usuario(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        user_index, users = self._find_user_index(user_id)
        return users[user_index] if user_index is not None else None
    
    def listar_usuarios(self) -> List[Dict]:
        """List all users"""
        return self._load_users()
    
    def listar_usuarios_premium(self) -> List[Dict]:
        """List only premium users with valid access"""
        users = self._load_users()
        premium_users = []
        
        for user in users:
            if self.verificar_acceso(user["user_id"]):
                premium_users.append(user)
        
        return premium_users
    
    def contar_usuarios_registrados(self) -> int:
        """Count total registered users"""
        return len(self._load_users())
    
    def contar_usuarios_premium(self) -> int:
        """Count users with valid premium access"""
        return len(self.listar_usuarios_premium())
    
    def obtener_estadisticas(self) -> Dict:
        """Get user statistics"""
        users = self._load_users()
        premium_users = self.listar_usuarios_premium()
        
        return {
            "total_usuarios": len(users),
            "usuarios_premium": len(premium_users),
            "usuarios_gratuitos": len(users) - len(premium_users),
            "porcentaje_premium": (len(premium_users) / len(users) * 100) if users else 0
        }

access_manager = AccessManager()

def registrar_usuario(user_id: str, username: str, first_name: str) -> bool:
    return access_manager.registrar_usuario(user_id, username, first_name)

def otorgar_acceso(user_id: str, dias: int) -> bool:
    return access_manager.otorgar_acceso(user_id, dias)

def banear_usuario(user_id: str) -> bool:
    return access_manager.banear_usuario(user_id)

def verificar_acceso(user_id: str) -> bool:
    return access_manager.verificar_acceso(user_id)

def cargar_usuarios_registrados() -> List[str]:
    """Backward compatibility: return users in old format"""
    users = access_manager.listar_usuarios()
    return [f"{user['user_id']} - {user['username']} - {user['first_name']}" for user in users]

def contar_usuarios_registrados() -> int:
    return access_manager.contar_usuarios_registrados()
