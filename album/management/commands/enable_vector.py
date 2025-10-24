from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Enables the vector extension in the database.'

    def handle(self, *args, **options):
        self.stdout.write('Enabling the vector extension...')
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        self.stdout.write(self.style.SUCCESS('Vector extension enabled.'))
