from datetime import datetime

from django.core.management.base import BaseCommand

from calendar_generator.models import Holiday


class Command(BaseCommand):
    help = 'Creates a holiday with a date range'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the holiday')
        parser.add_argument('start_date', type=str, help='Start date of the holiday (YYYY-MM-DD)')
        parser.add_argument('end_date', type=str, help='End date of the holiday (YYYY-MM-DD)')
        parser.add_argument('--closed', action='store_true', help='Whether the library is closed during this holiday')
        parser.add_argument('--artwork', type=str, help='Path to the artwork for this holiday', default=None)

    def handle(self, *args, **options):
        name = options['name']
        start_date_str = options['start_date']
        end_date_str = options['end_date']
        is_closed = options['closed']
        artwork_path = options['artwork']

        try:
            # Parse the dates
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # Validate that end_date is after start_date
            if end_date < start_date:
                self.stdout.write(self.style.ERROR("End date must be after start date"))
                return

            # Check if a holiday with this name and date range already exists
            if Holiday.objects.filter(name=name, date=start_date, end_date=end_date).exists():
                self.stdout.write(
                    self.style.WARNING(f"Holiday already exists: {name} from {start_date} to {end_date}, skipping..."))
                return

            # Create the holiday
            holiday = Holiday.objects.create(
                name=name,
                date=start_date,
                end_date=end_date,
                is_closed=is_closed,
                artwork_path=artwork_path
            )

            self.stdout.write(self.style.SUCCESS(f"Created holiday: {name} from {start_date} to {end_date}"))

            # Show how many days this holiday spans
            days = (end_date - start_date).days + 1
            self.stdout.write(self.style.SUCCESS(f"This holiday spans {days} days"))

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Error processing dates: {e}"))
