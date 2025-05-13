from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = 'Checks the status of migrations in the database'

    def handle(self, *args, **options):
        # Get all applied migrations
        recorder = MigrationRecorder(connection)
        applied_migrations = recorder.applied_migrations()

        # Check if our migration is applied
        if ('calendar_generator', '0002_holiday_end_date') in applied_migrations:
            self.stdout.write(self.style.SUCCESS('Migration 0002_holiday_end_date has been applied'))
        else:
            self.stdout.write(self.style.ERROR('Migration 0002_holiday_end_date has NOT been applied'))

        # List all applied migrations for the calendar_generator app
        self.stdout.write(self.style.NOTICE('Applied migrations for calendar_generator:'))
        for app, name in applied_migrations:
            if app == 'calendar_generator':
                self.stdout.write(f'  - {name}')
