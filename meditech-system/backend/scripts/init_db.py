"""
Script de Inicialización - Crea usuario SUPER_ROOT y datos semilla
Autor: Christhz 3.0
Uso: python scripts/init_db.py
"""

import sys
import os
from getpass import getpass

# Agregar ruta al proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import (
    Base, Branch, Role, User, StudyCatalog, RoleType
)
from passlib.context import CryptContext
from datetime import datetime

# Configuración
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_input(prompt: str, required: bool = True, default: str = None):
    while True:
        value = input(prompt).strip()
        if not value and default:
            return default
        if not value and required:
            print("  ⚠️  Este campo es obligatorio")
            continue
        return value

def main():
    print("\n" + "="*60)
    print("  MediTech System v3.0 - Inicialización")
    print("  Autor: Christhz 3.0")
    print("="*60 + "\n")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL no configurada en .env")
        sys.exit(1)
    
    # Conectar a base de datos
    print("📦 Conectando a la base de datos...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe usuario ROOT
        existing_root = db.query(Role).filter(Role.name == "SUPER_ROOT").first()
        if existing_root:
            print("⚠️  ¡El sistema ya está inicializado!")
            print("   Si deseas reiniciar, elimina la base de datos primero.\n")
            response = input("¿Deseas continuar de todos modos? (s/N): ").strip().lower()
            if response != 's':
                print("Operación cancelada.")
                sys.exit(0)
        
        print("\n✅ Conexión exitosa\n")
        
        # ==================== CREAR SUCURSAL PRINCIPAL ====================
        print("-"*60)
        print("🏢 CONFIGURACIÓN DE SUCURSAL PRINCIPAL")
        print("-"*60)
        
        branch_code = get_input("Código de sucursal (ej. SUCURSAL01): ", default="MAIN01")
        branch_name = get_input("Nombre de la sucursal: ", default="Sucursal Principal")
        branch_address = get_input("Dirección: ", required=False)
        branch_phone = get_input("Teléfono: ", required=False)
        branch_email = get_input("Email: ", required=False)
        
        branch = Branch(
            code=branch_code.upper(),
            name=branch_name,
            address=branch_address,
            phone=branch_phone,
            email=branch_email,
            active=True
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        print(f"✅ Sucursal '{branch.name}' creada con ID: {branch.id}\n")
        
        # ==================== CREAR ROLES ====================
        print("-"*60)
        print("🔐 CREACIÓN DE ROLES")
        print("-"*60)
        
        roles_data = [
            ("SUPER_ROOT", "Acceso total al sistema, configuración inicial", None, '{"all": true}'),
            ("ADMIN", "Administrador de sucursal", branch.id, '{"users": true, "patients": true, "invoices": true, "reports": true, "settings": true}'),
            ("RECEPCION", "Recepcionista - registro y facturación", branch.id, '{"patients": true, "invoices": true, "search": true}'),
            ("DOCTOR", "Médico - ver resultados y diagnósticos", branch.id, '{"patients": true, "results": true, "diagnosis": true}'),
            ("LABORATORIO", "Técnico de laboratorio", branch.id, '{"orders": true, "results_lab": true}'),
            ("RADIOLOGO", "Radiólogo - imágenes e informes", branch.id, '{"images": true, "results_rad": true}'),
            ("CONTABILIDAD", "Departamento de billing", branch.id, '{"invoices": true, "payments": true, "reports": true}'),
        ]
        
        created_roles = {}
        for role_name, desc, role_branch_id, permissions in roles_data:
            role = Role(
                name=role_name,
                description=desc,
                branch_id=role_branch_id,
                permissions=permissions
            )
            db.add(role)
            created_roles[role_name] = role
        
        db.commit()
        print("✅ Roles creados exitosamente\n")
        
        # ==================== CREAR USUARIO SUPER_ROOT ====================
        print("-"*60)
        print("👤 CREACIÓN DE USUARIO SUPER_ROOT")
        print("-"*60)
        print("Este usuario tendrá acceso TOTAL al sistema.\n")
        
        root_username = get_input("Username para SUPER_ROOT: ", default="root")
        root_email = get_input("Email: ")
        
        while True:
            root_password = getpass("Contraseña: ")
            if len(root_password) < 6:
                print("  ⚠️  La contraseña debe tener al menos 6 caracteres")
                continue
            root_password_confirm = getpass("Confirmar contraseña: ")
            if root_password != root_password_confirm:
                print("  ⚠️  Las contraseñas no coinciden")
                continue
            break
        
        root_full_name = get_input("Nombre completo: ", default="Administrador ROOT")
        
        super_root = User(
            username=root_username,
            email=root_email,
            password_hash=hash_password(root_password),
            full_name=root_full_name,
            role_id=created_roles["SUPER_ROOT"].id,
            branch_id=branch.id,
            active=True
        )
        db.add(super_root)
        db.commit()
        
        print(f"\n✅ Usuario SUPER_ROOT '{root_username}' creado exitosamente\n")
        
        # ==================== ESTUDIOS DE EJEMPLO ====================
        print("-"*60)
        print("📋 CARGANDO CATÁLOGO DE ESTUDIOS DE EJEMPLO")
        print("-"*60)
        
        studies = [
            # Laboratorio
            ("LAB001", "Biometría Hemática Completa", "Análisis completo de sangre", 150.00, "laboratorio", True, False, 24),
            ("LAB002", "Examen General de Orina", "Análisis químico y microscópico de orina", 80.00, "laboratorio", True, False, 24),
            ("LAB003", "Coprológico", "Análisis de heces fecales", 90.00, "laboratorio", True, False, 48),
            ("LAB004", "Glucosa en Sangre", "Medición de glucosa", 50.00, "laboratorio", True, True, 12),
            ("LAB005", "Perfil de Lípidos", "Colesterol y triglicéridos", 180.00, "laboratorio", True, True, 24),
            ("LAB006", "Prueba de Embarazo", "Determinación de HCG", 120.00, "laboratorio", True, False, 12),
            # Radiología
            ("RAD001", "Radiografía de Tórax", "RX simple de tórax", 250.00, "radiologia", False, False, 48),
            ("RAD002", "Radiografía de Extremidades", "RX de brazo o pierna", 200.00, "radiologia", False, False, 48),
            ("RAD003", "Ultrasonido Abdominal", "USG de abdomen completo", 450.00, "radiologia", False, True, 72),
            ("RAD004", "Mamografía", "Estudio mamario", 500.00, "radiologia", False, False, 72),
            ("RAD005", "Tomografía Computarizada", "TC de cráneo o cuerpo", 1200.00, "radiologia", False, False, 96),
        ]
        
        for code, name, desc, price, category, requires_sample, requires_fasting, turnaround in studies:
            study = StudyCatalog(
                code=code,
                name=name,
                description=desc,
                price=price,
                category=category,
                requires_sample=requires_sample,
                requires_fasting=requires_fasting,
                turnaround_time_hours=turnaround,
                branch_id=branch.id,
                active=True
            )
            db.add(study)
        
        db.commit()
        print(f"✅ {len(studies)} estudios cargados exitosamente\n")
        
        # ==================== RESUMEN FINAL ====================
        print("\n" + "="*60)
        print("  🎉 ¡INICIALIZACIÓN COMPLETADA!")
        print("="*60)
        print(f"\n📊 RESUMEN:")
        print(f"   • Sucursal: {branch.name} ({branch.code})")
        print(f"   • Usuario ROOT: {root_username}")
        print(f"   • Roles creados: {len(roles_data)}")
        print(f"   • Estudios cargados: {len(studies)}")
        print(f"\n🌐 URLs de acceso:")
        print(f"   • Frontend: http://localhost")
        print(f"   • API Docs: http://localhost:8000/docs")
        print(f"   • Orthanc PACS: http://localhost:8042")
        print(f"\n🔐 Credenciales ROOT:")
        print(f"   • Username: {root_username}")
        print(f"   • Contraseña: {root_password}")
        print(f"\n⚠️  IMPORTANTE:")
        print(f"   • Guarda estas credenciales en un lugar seguro")
        print(f"   • Cambia la contraseña después del primer login")
        print(f"   • No compartas el usuario SUPER_ROOT")
        print(f"\n💡 Próximos pasos:")
        print(f"   1. Inicia sesión con el usuario ROOT")
        print(f"   2. Crea más sucursales si es necesario")
        print(f"   3. Configura usuarios por sucursal")
        print(f"   4. Personaliza logos y colores")
        print(f"   5. Comienza a operar\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
