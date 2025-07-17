from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Tests database connection'

    def handle(self, *args, **options):
        self.stdout.write('Testing database connection...')
        
        try:
            db_conn = connections['default']
            db_conn.cursor()
            self.stdout.write(self.style.SUCCESS('Database connection successful!'))
            
            # Print connection info
            db_settings = db_conn.settings_dict
            self.stdout.write(f"\nConnection Details:")
            self.stdout.write(f"Database: {db_settings['NAME']}")
            self.stdout.write(f"Host: {db_settings['HOST']}")
            self.stdout.write(f"Port: {db_settings['PORT']}")
            self.stdout.write(f"User: {db_settings['USER']}")
            
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed! Error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}')) 