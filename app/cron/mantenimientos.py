from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.mantenimiento import Mantenimiento
from app.models.usuario import Usuario, Vehiculo
from app.services.notificacion_service import crear_y_enviar_notificacion
from datetime import datetime, date, timedelta

def notificar_mantenimientos_diarios():
    """
    Se ejecuta diariamente. Busca mantenimientos cuya fecha_proximo
    sea hoy o mañana, y notifica al usuario dueño del vehículo.
    """
    db: Session = SessionLocal()
    try:
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        
        # Filtrar mantenimientos activos que tocan hoy o mañana
        mantenimientos = db.query(Mantenimiento).filter(
            Mantenimiento.estado == 'Activo',
            # Asumimos que fecha_proximo es DateTime o Date
            # Castamos a Date o lo tratamos como Date si es posible
        ).all()
        
        for mant in mantenimientos:
            if mant.fecha_proximo and mant.fecha_proximo.date() in (hoy, manana):
                vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == mant.id_vehiculo).first()
                if not vehiculo:
                    continue
                
                usuario = db.query(Usuario).filter(Usuario.id_usuario == vehiculo.id_usuario).first()
                if not usuario or not usuario.push_token:
                    continue
                
                # Enviar notificacion push
                fecha_str = "hoy" if mant.fecha_proximo.date() == hoy else "mañana"
                titulo = "🔔 Recordatorio de Mantenimiento"
                mensaje = f"Tu vehículo {vehiculo.placa} tiene programado un {mant.tipo_mantenimiento} para {fecha_str}."
                
                # Evitar notificar dos veces el mismo día (opcional, pero con 1 trigger diario está bien)
                crear_y_enviar_notificacion(
                    db,
                    titulo=titulo,
                    mensaje=mensaje,
                    id_usuario=usuario.id_usuario,
                    push_token=usuario.push_token,
                    data={"tipo": "mantenimiento"}
                )
                
        db.commit()
    except Exception as e:
        print(f"Error en cron de mantenimientos: {e}")
    finally:
        db.close()
