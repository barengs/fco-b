#!/bin/bash
cd /Users/ROFI/Develop/proyek/fco_project
source venv/bin/activate
echo "Removing existing database..."
rm -f db.sqlite3
echo "Creating new database with migrations..."
python manage.py migrate
echo "Creating superuser..."
python manage.py createsuperuser --username admin --email admin@example.com
echo "Done!"