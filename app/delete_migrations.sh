#!/bin/bash

BASE_DIR=$(pwd)

find "$BASE_DIR" -path "*/migrations/*.py" ! -name "__init__.py" -delete
find "$BASE_DIR" -path "*/migrations/*.pyc" -delete
find "$BASE_DIR" -path "*/db.sqlite3" -delete

echo "Carpetas de migrations y base sqlite eliminadas."