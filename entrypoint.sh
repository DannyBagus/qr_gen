#!/bin/sh

# Stoppt das Skript sofort, wenn ein Befehl fehlschlägt
set -e

echo "Wende Datenbank-Migrationen an..."
python manage.py migrate

echo "Sammle statische Dateien (CSS, Bilder, Logos)..."
# Das kopiert deine Assets in den STATIC_ROOT Ordner
python manage.py collectstatic --noinput

echo "Starte Gunicorn Server..."
# 4 Worker Prozesse, bindet an Port 8000
# qr_gen_project.wsgi verweist auf qr_gen_project/wsgi.py
exec gunicorn qr_gen_project.wsgi:application --bind 0.0.0.0:8000 --workers 3