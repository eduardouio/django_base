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

if ! command -v psql >/dev/null 2>&1; then
	echo "No se encontró psql. Instala postgresql-client para continuar."
	exit 1
fi

delete_migrations() {
	echo "Buscando y eliminando archivos de migrations y base sqlite..."
	mapfile -t deleted_py < <(find "$SRC_DIR" -type f -path "*/migrations/*.py" ! -name "__init__.py" -print -delete)
	mapfile -t deleted_pyc < <(find "$SRC_DIR" -type f -path "*/migrations/*.pyc" -print -delete)
	mapfile -t deleted_db < <(find "$SRC_DIR" -type f -name "db.sqlite3" -print -delete)

	local total=$(( ${#deleted_py[@]} + ${#deleted_pyc[@]} + ${#deleted_db[@]} ))

	if [ "$total" -eq 0 ]; then
		echo "No se encontraron archivos para eliminar."
	else
		echo "Resumen: se eliminaron $total archivos de migración/sqlite."
	fi
}

drop_database() {
	echo "Eliminando la base de datos '$DB_NAME'..."
	PGPASSWORD="$DB_PASSWD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
}

create_database() {
	echo "Creando la base de datos '$DB_NAME'..."
	PGPASSWORD="$DB_PASSWD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tnc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
		PGPASSWORD="$DB_PASSWD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\" ENCODING 'UTF8';"
}

run_migrations() {
	echo "Generando migraciones..."
	( cd "$SRC_DIR" && "$PYTHON_BIN" manage.py makemigrations )
	echo "Aplicando migraciones..."
	( cd "$SRC_DIR" && "$PYTHON_BIN" manage.py migrate )
}

test_connection() {
	echo "Probando conexión a la base de datos '$DB_NAME'..."
	# Intentar conectar a la BD y listar tablas (\dt)
	if PGPASSWORD="$DB_PASSWD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt"; then
		echo "Conexión exitosa y tablas mostradas."
	else
		echo "Ocurrió un error al intentar conectar a la base de datos (o la BD no existe)."
	fi
}

confirm_action() {
	echo "ATENCIÓN: Se requiere confirmación para esta operación destructiva."
	read -r -p "Escribe 'calamardo' para confirmar: " user_confirmation
	if [ "$user_confirmation" != "calamardo" ]; then
		echo "Operación cancelada por el usuario."
		exit 0
	fi
}

echo "=== MENÚ DE OPCIONES ==="
echo "1. Crear base de datos (en blanco)"
echo "2. Eliminar migraciones (archivos locales)"
echo "3. Eliminar base de datos (DROP DATABASE)"
echo "4. Destrucción total (Eliminar db, eliminar migraciones, recrear db en blanco)"
echo "5. Probar conexión y listar tablas de la base de datos"
echo "0. Salir"
read -r -p "Selecciona una opción [0-5]: " option

case "$option" in
	1)
		create_database
		;;
	2)
		confirm_action
		delete_migrations
		;;
	3)
		confirm_action
		drop_database
		;;
	4)
		confirm_action
		drop_database
		delete_migrations
		create_database
		;;
	5)
		test_connection
		;;
	0)
		echo "Saliendo sin hacer cambios."
		exit 0
		;;
	*)
		echo "Opción no válida."
		exit 1
		;;
esac

echo
echo "Operación completada."
