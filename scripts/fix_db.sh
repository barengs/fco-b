#!/bin/bash
cd /Users/ROFI/Develop/proyek/fco_project
source venv/bin/activate
echo "Removing existing database..."
rm -f db.sqlite3
echo "Creating new database with migrations..."
python manage.py migrate
echo "Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
echo "Done!"