"""
Datos estaticos para el seed: credenciales, catalogos, talleres, tecnicos,
clientes y la definicion declarativa de los 15 escenarios.
"""
from __future__ import annotations
import random

# Fijamos seed para reproducibilidad
rnd = random.Random(42)

# ── Catalogos ────────────────────────────────────────────────────────────────
ROLES = ["cliente", "taller", "tecnico", "admin"]
ESTADOS_INCIDENTE = [
    ("borrador", "Borrador: el cliente aun no confirmo el taller"),
    ("pendiente", "Reportado, sin asignar"),
    ("en_proceso", "Taller asignado, en atencion"),
    ("atendido", "Resuelto"),
    ("cancelado", "Cancelado por el usuario"),
]
ESTADOS_ASIGNACION = [
    "pendiente", "aceptada", "rechazada", "en_camino", "llegado", "completada", "cancelada"
]
ESTADOS_PAGO = ["pendiente", "procesando", "completado", "fallido", "reembolsado"]
ESTADOS_COTIZACION = ["pendiente", "enviada", "aceptada", "rechazada", "expirada"]
CATEGORIAS = [
    ("bateria",          "bateria",              "Problemas de bateria",              False),
    ("llanta_pinchada",  "llanta",               "Llanta desinflada o reventada",     False),
    ("choque",           "choque",               "Colision o accidente",              False),
    ("motor",            "motor",                "Fallas del motor",                  False),
    ("llaves",           "llaves",               "Llaves perdidas o bloqueadas",      False),
    ("otros",            "otros",                "Otros problemas",                   False),
    ("incierto",         "incierto",             "Sin clasificar",                    False),
    ("llantas",          "Servicio de llantas",  "Cambio / reparacion de llantas",    False),
    ("mecanica_general", "Mecanica general",     "Diagnostico y mecanica de taller",  True),
    ("electrico",        "Servicio electrico",   "Sistema electrico del vehiculo",    True),
    ("electronico",      "Servicio electronico", "Computadora y electronica",         True),
    ("chaperia_pintura", "Chaperia y pintura",   "Carroceria y pintura",              True),
    ("grua_auxilio",     "Grua / Auxilio vial",  "Traslado del vehiculo",             False),
    ("rutinario",        "Servicio rutinario",   "Mantenimiento programado",          False),
]
PRIORIDADES = [("baja", 1), ("media", 2), ("alta", 3), ("critica", 4)]
TIPOS_EVIDENCIA = ["imagen", "audio", "texto"]
METODOS_PAGO = ["tarjeta", "transferencia", "efectivo", "qr"]

# ── Planes SaaS ──────────────────────────────────────────────────────────────
PLANES = [
    {"codigo": "free", "nombre": "Free", "descripcion": "Plan gratuito", "precio_mensual": 0, "max_talleres": 1, "max_tecnicos": 5, "max_incidentes_mes": 50, "feature_websockets": False, "feature_kpis_avanzados": False, "feature_reportes_ia": False},
    {"codigo": "pro", "nombre": "Pro", "descripcion": "Plan Pro", "precio_mensual": 49, "max_talleres": 3, "max_tecnicos": 20, "max_incidentes_mes": 500, "feature_websockets": True, "feature_kpis_avanzados": True, "feature_reportes_ia": False},
    {"codigo": "enterprise", "nombre": "Enterprise", "descripcion": "Plan Enterprise", "precio_mensual": 199, "max_talleres": 999, "max_tecnicos": 999, "max_incidentes_mes": None, "feature_websockets": True, "feature_kpis_avanzados": True, "feature_reportes_ia": True},
]

ADMIN = {
    "nombre": "Administrador Plataforma",
    "email": "admin.plataforma@gmail.com",
    "password": "12345678",
    "telefono": "+591 70000000",
}

# ── Generacion de Talleres (20) ────────────────────────────────────────────────────
NOMBRES_TALLERES = ["Taller Los Andes", "Mecanica Rapida SRL", "Chaperia Express", "Llantas 24/7", "Auto Center", "Garage Pro", "Mecanica El Buen Pastor", "Servicios Integrales", "Diagnostico Inteligente", "Motor Master", "Taller El Tuerca", "Clinica del Automovil", "Mecanica Los Hermanos", "Reparaciones Santa Cruz", "Llanteria El Cruce", "Taller El Chaperio", "Mecanica Central", "Taller y Grúas del Sur", "Taller El Especialista", "Mecanica del Norte"]
TALLERES = []
for i, nombre in enumerate(NOMBRES_TALLERES):
    lat = -17.78 - rnd.random() * 0.06
    lng = -63.16 - rnd.random() * 0.06
    TALLERES.append({
        "slug": f"taller-{i+1}",
        "tenant_nombre": f"{nombre} Org",
        "plan": rnd.choice(["free", "pro", "enterprise"]),
        "nombre": nombre,
        "email": f"taller{i+1}@gmail.com",
        "password": "12345678",
        "telefono": f"+591 7000{i:04d}",
        "direccion": f"Zona {rnd.choice(['Norte', 'Sur', 'Este', 'Oeste', 'Equipetrol', 'Urubo'])} # {rnd.randint(10, 999)}",
        "latitud": lat,
        "longitud": lng,
        "capacidad_max": rnd.randint(3, 10),
        "categorias": ["bateria", "llanta", "motor", "choque", "llaves", "otros", "incierto", "Mecanica general", "Servicio electrico", "Grua / Auxilio vial", "Chaperia y pintura", "Servicio de llantas", "Servicio rutinario"],
    })

# ── Generacion de Tecnicos (2 por taller) ──────────────────────────────────────────────────
TECNICOS = []
NOMBRES_TEC = ["Roberto", "Andrea", "Marcelo", "Gabriela", "Fernando", "Patricia", "Juan", "Maria", "Carlos", "Ana", "Luis", "Laura", "Pedro", "Sofia", "Jorge", "Carmen", "Miguel", "Lucia", "Jose", "Marta"]
APELLIDOS = ["Fuentes", "Salinas", "Vaca", "Ortiz", "Rojas", "Cruz", "Perez", "Gomez", "Lopez", "Diaz", "Martinez", "Gonzalez", "Rodriguez", "Fernandez", "Garcia", "Sanchez", "Romero", "Sosa", "Torres", "Ramirez"]
for i in range(len(TALLERES)):
    for j in range(2):
        TECNICOS.append({
            "nombre": f"{rnd.choice(NOMBRES_TEC)} {rnd.choice(APELLIDOS)}",
            "email": f"tecnico.t{i+1}_{j+1}@gmail.com",
            "password": "12345678",
            "telefono": f"+591 7100{i:02d}{j:02d}",
            "taller_idx": i
        })

# ── Generacion de Clientes (45) ─────────────────────────────────────────────────────────────────
CLIENTES = []
MARCAS_MODELOS = [("Toyota", "Corolla", 2021, "Blanco"), ("Nissan", "Sentra", 2020, "Rojo"), ("Suzuki", "Swift", 2022, "Azul"), ("Kia", "Picanto", 2023, "Negro"), ("Chevrolet", "Spark", 2019, "Gris"), ("Honda", "Civic", 2018, "Plateado"), ("Hyundai", "Accent", 2017, "Verde"), ("Mazda", "3", 2020, "Azul"), ("Volkswagen", "Gol", 2019, "Blanco"), ("Ford", "Fiesta", 2021, "Rojo")]

for i in range(1, 46):
    key = f"cli_{i}"
    if i == 1: key = "cli_pendiente"
    if i == 2: key = "cli_aceptada"
    if i == 3: key = "cli_rechazada"
    if i == 4: key = "cli_en_camino"
    if i == 5: key = "cli_llegado"
    if i == 6: key = "cli_atendido"
    if i == 7: key = "cli_cancelado"
    if i == 8: key = "cli_cot_pendiente"
    if i == 9: key = "cli_cot_enviada"
    if i == 10: key = "cli_cot_aceptada"
    if i == 11: key = "cli_cot_rechazada"
    if i == 12: key = "cli_cot_expirada"
    if i == 13: key = "cli_pago_procesando"
    if i == 14: key = "cli_pago_fallido"
    if i == 15: key = "cli_pago_reembolso"
    if i == 16: key = "cli_pago_pendiente"

    marca, modelo, anio, color = rnd.choice(MARCAS_MODELOS)
    CLIENTES.append({
        "key": key,
        "nombre": f"{rnd.choice(NOMBRES_TEC)} {rnd.choice(APELLIDOS)}",
        "email": f"cliente{i}@gmail.com",
        "password": "12345678",
        "telefono": f"+591 7011{i:04d}",
        "vehiculo": {"placa": f"SCZ-{i:03d}", "marca": marca, "modelo": modelo, "anio": anio, "color": color}
    })

COORDS_SCZ = [(-17.802625, -63.200045), (-17.781230, -63.181450), (-17.815320, -63.188120), (-17.795020, -63.190100), (-17.808120, -63.196250), (-17.787500, -63.175800), (-17.823100, -63.205400), (-17.793800, -63.192100), (-17.811200, -63.179600), (-17.776900, -63.166400)]

TABLAS_A_LIMPIAR = [
    "taller_favorito", "ubicacion_tecnico", "historial_estado_asignacion", "historial_estado_incidente",
    "candidato_asignacion", "evaluacion", "asignacion", "cotizacion", "evidencia",
    "metrica", "notificacion", "mensaje", "pago", "mantenimiento", "incidente", "vehiculo",
    "usuario_taller", "taller_servicio", "taller", "tenant_user", "suscripcion",
    "tenant", "plan", "usuario", "rol", "estado_incidente", "estado_asignacion",
    "estado_cotizacion", "estado_pago", "categoria_problema", "prioridad",
    "tipo_evidencia", "metodo_pago"
]
