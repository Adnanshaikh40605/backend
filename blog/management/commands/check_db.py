from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    help = 'Check database connection and report status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retry',
            action='store_true',
            help='Retry connection if it fails',
        )
        parser.add_argument(
            '--retry-count',
            type=int,
            default=5,
            help='Number of retry attempts',
        )
        parser.add_argument(
            '--retry-delay',
            type=int,
            default=2,
            help='Delay between retries in seconds',
        )

    def handle(self, *args, **options):
        retry = options['retry']
        retry_count = options['retry_count']
        retry_delay = options['retry_delay']
        
        attempt = 0
        
        while True:
            attempt += 1
            try:
                # Try to get a cursor to test the connection
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS(f'Database connection successful! (Attempt {attempt})'))
                
                # Print database info
                db_settings = connections.databases['default']
                self.stdout.write(f"Database engine: {db_settings['ENGINE']}")
                self.stdout.write(f"Database name: {db_settings['NAME']}")
                if 'HOST' in db_settings and db_settings['HOST']:
                    self.stdout.write(f"Database host: {db_settings['HOST']}")
                if 'PORT' in db_settings and db_settings['PORT']:
                    self.stdout.write(f"Database port: {db_settings['PORT']}")
                
                return
            except OperationalError as e:
                self.stdout.write(self.style.ERROR(f'Database connection failed! (Attempt {attempt})'))
                self.stdout.write(self.style.ERROR(f'Error: {e}'))
                
                if retry and attempt < retry_count:
                    self.stdout.write(f'Retrying in {retry_delay} seconds...')
                    time.sleep(retry_delay)
                    continue
                else:
                    self.stdout.write(self.style.ERROR('Max retries reached or retry disabled. Exiting.'))
                    return 