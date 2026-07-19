#!/usr/bin/env bash
# Script de arranque para Render.
#
# Comportamiento:
#   - Si SEED_ON_STARTUP=true (default): crea las tablas si no existen,
#     trunca todo y siembra datos de prueba consistentes (todos los estados).
#   - Si SEED_ON_STARTUP=false: arranca directo sin tocar la base.
#
# Pensado para un proyecto universitario donde cada deploy debe partir
# de un estado conocido. Pon SEED_ON_STARTUP=false cuando quieras congelar.
set -e

# IMPORTANTE: crear el esquema completo desde los modelos (fuente de verdad).
# El baseline de Alembic (0001) esta VACIO: asume que las tablas base ya existen
# via create_all. Por eso en una BD nueva y vacia `alembic upgrade head` falla al
# crear tenant_user (FK a usuario) porque usuario aun no existe.
# Solucion: drop de todo si es SEED, luego create_all (idempotente) + stamp head.

if [ "${SEED_ON_STARTUP:-true}" = "true" ]; then
    echo "==> [start.sh] SEED_ON_STARTUP=true -> Limpiando el esquema anterior por completo"
    python -c "from app.db.session import engine; from sqlalchemy import text; 
with engine.begin() as conn:
    conn.execute(text('DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;'))"
fi

echo "==> [start.sh] Creando esquema desde los modelos (create_all, idempotente)"
python -c "import app.models; from app.db.session import Base, engine; Base.metadata.create_all(bind=engine)"

echo "==> [start.sh] Alembic stamp head (marca migraciones al dia sin re-ejecutarlas)"
alembic stamp head

if [ "${SEED_ON_STARTUP:-true}" = "true" ]; then
    echo "==> [start.sh] SEED_ON_STARTUP=true → corriendo SETT/run_all.py"
    python -m SETT.run_all
else
    echo "==> [start.sh] SEED_ON_STARTUP=$SEED_ON_STARTUP → no se siembra la base"
fi

echo "==> [start.sh] Levantando gunicorn (uvicorn worker)"
exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120
