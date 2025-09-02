from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Ensure CustomUser model is migrated first before other migrations'

    def handle(self, *args, **options):
        self.stdout.write('Checking CustomUser migration status...')
        
        # Check if the CustomUser table exists
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='owners_customuser'")
            result = c.fetchone()
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS('CustomUser table already exists')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('CustomUser table does not exist, applying migrations...')
                )
                # Apply owners app migrations first
                call_command('migrate', 'owners', verbosity=2)
                
                # Then apply all other migrations
                call_command('migrate', verbosity=2)
                
                self.stdout.write(
                    self.style.SUCCESS('All migrations applied successfully')
                )
                
        except OperationalError:
            self.stdout.write(
                self.style.ERROR('Database not accessible')
            )