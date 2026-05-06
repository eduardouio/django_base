#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
DB_ENV="${1:-DEVELOPMENT}"

if [ ! -d "$SRC_DIR" ]; then
	echo "No se encontró el directorio src en: $SRC_DIR"
	exit 1
fi

if command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
	PYTHON_BIN="python"
else
	echo "No se encontró Python en el sistema."
	exit 1
fi

echo "Buscando y eliminando archivos de migrations y base sqlite..."

mapfile -t deleted_py < <(find "$SRC_DIR" -type f -path "*/migrations/*.py" ! -name "__init__.py" -print -delete)
mapfile -t deleted_pyc < <(find "$SRC_DIR" -type f -path "*/migrations/*.pyc" -print -delete)
mapfile -t deleted_db < <(find "$SRC_DIR" -type f -name "db.sqlite3" -print -delete)

total=$(( ${#deleted_py[@]} + ${#deleted_pyc[@]} + ${#deleted_db[@]} ))

if [ "$total" -eq 0 ]; then
	echo "No se encontraron archivos para eliminar."
else
	if [ ${#deleted_py[@]} -gt 0 ]; then
		echo
		echo "Archivos .py eliminados:"
		for f in "${deleted_py[@]}"; do echo " - $f"; done
	fi
	if [ ${#deleted_pyc[@]} -gt 0 ]; then
		echo
		echo "Archivos .pyc eliminados:"
		for f in "${deleted_pyc[@]}"; do echo " - $f"; done
	fi
	if [ ${#deleted_db[@]} -gt 0 ]; then
		echo
		echo "Bases sqlite eliminadas:"
		for f in "${deleted_db[@]}"; do echo " - $f"; done
	fi
	echo
	echo "Resumen: se eliminaron $total archivos."
fi

echo
echo "Leyendo configuración de base de datos '$DB_ENV' desde config/secrets.py..."

readarray -t db_conf < <(
	cd "$SRC_DIR"
	"$PYTHON_BIN" - <<PY
import sys
sys.path.insert(0, '.')
from config.secrets import DATABASES

env = "$DB_ENV"
if env not in DATABASES:
    valid = list(DATABASES.keys())
    print(f"Entorno '{env}' no encontrado. Opciones validas: {valid}", file=sys.stderr)
    sys.exit(1)

db = DATABASES[env]
print(db['NAME'])
print(db['HOST'])
print(db['PORT'])
print(db['USER'])
print(db.get('PASSWORD', ''))
PY
)

DB_NAME="${db_conf[0]:-}"
DB_HOST="${db_conf[1]:-}"
DB_PORT="${db_conf[2]:-}"
DB_USER="${db_conf[3]:-}"
DB_PASSWD="${db_conf[4]:-}"

if [ -z "$DB_NAME" ] || [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_USER" ]; then
	echo "No se pudo obtener la configuración de base de datos desde config/secrets.py"
	exit 1
fi

echo "Entorno  : $DB_ENV"
echo "Base de datos: $DB_NAME @ $DB_HOST:$DB_PORT (usuario: $DB_USER)"

echo
echo "ATENCION: esta operación eliminará y recreará '$DB_NAME' y regenerará migraciones."
read -r -p "Escribe 'calamardo' para confirmar: " user_confirmation

if [ "$user_confirmation" != "calamardo" ]; then
	echo "Operación cancelada por el usuario."
	exit 0
fi

if ! command -v psql >/dev/null 2>&1; then
	echo "No se encontró psql. Instala postgresql-client para continuar."
	exit 1
fi

echo
echo "Eliminando y recreando la base de datos '$DB_NAME'..."

PGPASSWORD="$DB_PASSWD" psql \
	-h "$DB_HOST" \
	-p "$DB_PORT" \
	-U "$DB_USER" \
	-d postgres \
	-c "DROP DATABASE IF EXISTS \"$DB_NAME\";"

PGPASSWORD="$DB_PASSWD" psql \
	-h "$DB_HOST" \
	-p "$DB_PORT" \
	-U "$DB_USER" \
	-d postgres \
	-c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\" ENCODING 'UTF8';"

echo "Base de datos recreada correctamente."

echo
echo "Generando migraciones..."
(
	cd "$SRC_DIR"
	"$PYTHON_BIN" manage.py makemigrations
)

echo
echo "Aplicando migraciones..."
(
	cd "$SRC_DIR"
	"$PYTHON_BIN" manage.py migrate
)

echo
echo "Operación completada."
