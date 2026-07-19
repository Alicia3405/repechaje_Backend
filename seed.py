import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))

from app.db.session import SessionLocal
from app.models.user_model import Usuario
from app.models.taller import Taller
from app.models.tenant import Tenant, Plan, Suscripcion
from app.core.security import hash_password
from sqlalchemy import text

def seed():
    db = SessionLocal()
    try:
        # 1. Insertar roles base si no existen
        db.execute(text("INSERT INTO rol (id_rol, nombre) VALUES (1, 'cliente'), (2, 'taller'), (3, 'tecnico'), (4, 'admin') ON CONFLICT DO NOTHING;"))
        
        # 2. Crear Cuenta de Super Administrador (rol=4)
        admin = db.query(Usuario).filter_by(email='admin@admin.com').first()
        if not admin:
            admin = Usuario(id_rol=4, nombre='Super Admin', email='admin@admin.com', password_hash=hash_password('admin123'), activo=True)
            db.add(admin)

        # 3. Crear un Tenant (necesario por ser arquitectura Multi-Tenant)
        tenant = db.query(Tenant).filter_by(slug='taller-central').first()
        if not tenant:
            tenant = Tenant(slug='taller-central', nombre='Taller Central', email_contacto='contacto@taller.com', activo=True)
            db.add(tenant)
            db.flush()
            
            # Asignar suscripción gratuita
            plan_free = db.query(Plan).filter_by(codigo='free').first()
            if plan_free:
                sub = Suscripcion(id_tenant=tenant.id_tenant, id_plan=plan_free.id_plan, estado='activa')
                db.add(sub)

        # 4. Crear Cuenta de Taller vinculada al Tenant
        taller = db.query(Taller).filter_by(email='taller@taller.com').first()
        if not taller:
            taller = Taller(id_tenant=tenant.id_tenant, nombre='Taller Central', email='taller@taller.com', password_hash=hash_password('taller123'), activo=True, disponible=True, verificado=True)
            db.add(taller)

        db.commit()
        print("CREDENCIALES CREADAS EXITOSAMENTE")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
