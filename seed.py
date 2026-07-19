import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))

import random
from datetime import datetime, timedelta
from faker import Faker
from app.db.session import SessionLocal
from app.models.user_model import Usuario, Vehiculo
from app.models.taller import Taller, TallerServicio
from app.models.tenant import Tenant, Plan, Suscripcion
from app.models.catalogos import EstadoIncidente, CategoriaProblema
from app.models.incidente import Incidente, Asignacion, Evaluacion, HistorialEstadoIncidente
from app.core.security import hash_password
from sqlalchemy import text
from app.models.usuario_taller import UsuarioTaller

fake = Faker('es_MX')  # Usamos MX para nombres en español

ZONAS_SANTA_CRUZ = [
    "Equipetrol", "Urubó", "Plan 3000", "Villa 1ro de Mayo", "Los Lotes", 
    "Doble Vía a La Guardia", "Av. Banzer", "Av. Cristo Redentor", "Av. Santos Dumont",
    "Av. Mutualista", "Barrio Sirari", "Las Palmas", "Centro", "Av. Bush", "Av. Paragua"
]

MARCAS_AUTOS = ["Toyota", "Nissan", "Suzuki", "Honda", "Hyundai", "Kia", "Chevrolet", "Ford", "Volkswagen", "Mazda"]
MODELOS = ["Corolla", "Hilux", "Sentra", "Swift", "Civic", "Tucson", "Rio", "Tracker", "Ranger", "Gol", "CX-5"]

def get_random_location():
    # Coordenadas aproximadas de Santa Cruz de la Sierra (Centro: -17.7833, -63.1821)
    lat = random.uniform(-17.85, -17.70)
    lng = random.uniform(-63.22, -63.10)
    return lat, lng

def seed():
    db = SessionLocal()
    try:
        # 1. Insertar roles base
        db.execute(text("INSERT INTO rol (id_rol, nombre) VALUES (1, 'cliente'), (2, 'taller'), (3, 'tecnico'), (4, 'admin') ON CONFLICT DO NOTHING;"))
        db.commit()

        # 2. Super Admin
        admin = db.query(Usuario).filter_by(email='admin@admin.com').first()
        if not admin:
            admin = Usuario(id_rol=4, nombre='Super Admin', email='admin@admin.com', password_hash=hash_password('admin123'), activo=True)
            db.add(admin)

        # 3. Tenant Base y Plan
        plan = db.query(Plan).filter_by(id_plan=1).first()
        if not plan:
            plan = Plan(id_plan=1, codigo='free', nombre='Gratuito', precio_mensual=0, moneda='USD', max_talleres=1, max_tecnicos=3)
            db.add(plan)
            db.flush()
        tenant = db.query(Tenant).filter_by(slug='scz-network').first()
        if not tenant:
            tenant = Tenant(slug='scz-network', nombre='Red Talleres SCZ', email_contacto='red@scz.com', activo=True)
            db.add(tenant)
            db.flush()
            sub = Suscripcion(id_tenant=tenant.id_tenant, id_plan=1, estado='activa')
            db.add(sub)
        else:
            sub = db.query(Suscripcion).filter_by(id_tenant=tenant.id_tenant).first()

        db.commit()

        # 4. Crear 20 Talleres
        talleres_creados = []
        for i in range(20):
            email = f"taller{i+1}@scz.com"
            taller = db.query(Taller).filter_by(email=email).first()
            if not taller:
                lat, lng = get_random_location()
                zona = random.choice(ZONAS_SANTA_CRUZ)
                taller = Taller(
                    id_tenant=tenant.id_tenant,
                    nombre=f"Taller Mecánico {fake.company_suffix()} - {zona}",
                    email=email,
                    telefono=fake.phone_number()[:20],
                    password_hash=hash_password('taller123'),
                    activo=True,
                    verificado=True,
                    disponible=True,
                    latitud=lat,
                    longitud=lng,
                    direccion=f"Av. Principal {random.randint(10, 999)}, {zona}"
                )
                db.add(taller)
                talleres_creados.append(taller)
        db.commit()
        
        talleres = db.query(Taller).all()

        # Asegurar Categorías
        categorias_nombres = ["Mecánica", "Eléctrico", "Llantas", "Grúa", "Batería"]
        for i, nombre in enumerate(categorias_nombres, start=1):
            cat = db.query(CategoriaProblema).filter_by(id_categoria=i).first()
            if not cat:
                cat = CategoriaProblema(id_categoria=i, nombre=nombre, requiere_cotizacion=False, activo=True)
                db.add(cat)
        db.commit()

        for t in talleres:
            if not db.query(TallerServicio).filter_by(id_taller=t.id_taller).first():
                for cat_id in random.sample([1, 2, 3, 4, 5], k=random.randint(2, 4)):
                    ts = TallerServicio(id_taller=t.id_taller, id_categoria=cat_id, servicio_movil=True, tarifa_base=random.randint(50, 150))
                    db.add(ts)
        db.commit()

        # 5. Crear 45 Usuarios (10 Mecánicos, 35 Clientes)
        usuarios_clientes = []
        usuarios_mecanicos = []
        for i in range(45):
            is_cliente = i < 35
            rol_id = 1 if is_cliente else 3
            email = f"cliente{i}@mail.com" if is_cliente else f"tecnico{i}@mail.com"
            user = db.query(Usuario).filter_by(email=email).first()
            if not user:
                user = Usuario(
                    id_rol=rol_id,
                    nombre=fake.name(),
                    email=email,
                    password_hash=hash_password('123456'),
                    telefono=fake.phone_number()[:15],
                    activo=True
                )
                db.add(user)
                db.flush()
                
                if is_cliente:
                    # Asignar de 1 a 3 vehículos
                    for _ in range(random.randint(1, 3)):
                        veh = Vehiculo(
                            id_usuario=user.id_usuario,
                            marca=random.choice(MARCAS_AUTOS),
                            modelo=random.choice(MODELOS),
                            placa=f"{random.randint(1000,9999)}{random.choice(['ABC', 'XYZ', 'HJK', 'LMN'])}",
                            color=fake.color_name()
                        )
                        db.add(veh)
                    usuarios_clientes.append(user)
                else:
                    usuarios_mecanicos.append(user)
                    # Vincular al técnico con un taller al azar
                    taller_rand = random.choice(talleres)
                    ut = UsuarioTaller(id_usuario=user.id_usuario, id_taller=taller_rand.id_taller)
                    db.add(ut)
            else:
                if is_cliente: usuarios_clientes.append(user)
                else: usuarios_mecanicos.append(user)
        db.commit()

        # 6. Crear 150 Emergencias (Incidentes)
        # Asegurar Estados
        db.execute(text("INSERT INTO estado_incidente (id_estado, nombre) VALUES (1, 'pendiente'), (2, 'asignando'), (3, 'en_camino'), (4, 'atendido'), (5, 'cancelado') ON CONFLICT DO NOTHING;"))
        db.execute(text("INSERT INTO prioridad (id_prioridad, nivel, orden) VALUES (1, 'Baja', 1), (2, 'Media', 2), (3, 'Alta', 3), (4, 'Crítica', 4) ON CONFLICT DO NOTHING;"))
        db.execute(text("INSERT INTO estado_asignacion (id_estado_asignacion, nombre) VALUES (1, 'pendiente'), (2, 'aceptada'), (3, 'en_progreso'), (4, 'completada'), (5, 'rechazada') ON CONFLICT DO NOTHING;"))
        db.commit()

        clientes_con_auto = db.query(Usuario).filter(Usuario.id_rol == 1).all()
        for i in range(150):
            cliente = random.choice(clientes_con_auto)
            vehiculo = db.query(Vehiculo).filter_by(id_usuario=cliente.id_usuario).first()
            if not vehiculo: continue
            
            lat, lng = get_random_location()
            dias_atras = random.randint(1, 365)
            fecha_creacion = datetime.now() - timedelta(days=dias_atras, hours=random.randint(0,23))
            
            incidente = Incidente(
                id_tenant=tenant.id_tenant,
                id_usuario=cliente.id_usuario,
                id_vehiculo=vehiculo.id_vehiculo,
                id_estado=4,  # atendido (completado)
                id_categoria=random.randint(1, 5),
                id_prioridad=random.randint(1, 4),
                latitud=lat,
                longitud=lng,
                descripcion_usuario=fake.sentence(),
                resumen_ia="Problema mecánico detectado: " + fake.sentence(),
                created_at=fecha_creacion,
                updated_at=fecha_creacion + timedelta(hours=2)
            )
            db.add(incidente)
            db.flush()

            # Historial estado incidente
            historial = HistorialEstadoIncidente(id_incidente=incidente.id_incidente, id_estado_nuevo=4, created_at=fecha_creacion + timedelta(hours=2))
            db.add(historial)

            # Asignación
            taller = random.choice(talleres)
            tecnicos_del_taller = db.query(UsuarioTaller).filter_by(id_taller=taller.id_taller).all()
            id_tecnico = random.choice(tecnicos_del_taller).id_usuario if tecnicos_del_taller else None

            asignacion = Asignacion(
                id_incidente=incidente.id_incidente,
                id_taller=taller.id_taller,
                id_usuario=id_tecnico,
                id_estado_asignacion=4, # completada
                created_at=fecha_creacion + timedelta(minutes=10)
            )
            db.add(asignacion)
            db.flush()

            # Calificaciones Opcionales (Mutuas)
            if random.random() > 0.3: # 70% de probabilidad de que haya calificación
                evaluacion = Evaluacion(
                    id_incidente=incidente.id_incidente,
                    id_usuario=cliente.id_usuario,
                    id_taller=taller.id_taller,
                    estrellas=random.randint(3, 5) if random.random() > 0.2 else None, # Cliente califica
                    comentario=fake.sentence() if random.random() > 0.5 else None,
                    estrellas_taller=random.randint(4, 5) if random.random() > 0.4 else None, # Taller califica
                    comentario_taller=fake.sentence() if random.random() > 0.5 else None,
                    created_at=fecha_creacion + timedelta(hours=3)
                )
                db.add(evaluacion)

        db.commit()
        print("POBLACION MASIVA COMPLETADA EXITOSAMENTE")
        print("- 20 Talleres creados")
        print("- 45 Usuarios (Clientes y Mecanicos) con multiples vehiculos creados")
        print("- 150 Incidentes/Emergencias con historial y calificaciones opcionales generados")

    except Exception as e:
        db.rollback()
        print(f"Error durante el seeder: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
