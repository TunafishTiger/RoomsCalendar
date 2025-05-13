from datetime import datetime

from django.core.management.base import BaseCommand

from calendar_generator.models import Holiday


class Command(BaseCommand):
    help = 'Populates the Holiday model with initial data from the hardcoded mpm_holidays dictionary'

    def handle(self, *args, **options):
        # Define the original hardcoded holidays
        mpm_holidays = {
            "New Year's Day": (None, True),
            "New Year's Day (Observed)": (None, True),
            "Martin Luther King Jr. Day": (None, True),
            "2025-02-14": (None, False),
            "2025-02-17": (None, True),
            "Washington's Birthday": (None, False),
            "2025-04-18": (None, True),
            "2025-04-19": (None, True),
            "2025-05-24": (None, True),
            "Memorial Day": (None, True),
            "2025-06-07": (None, True),
            "2025-06-19": (None, True),
            "Independence Day": (None, True),
            "2025-07-05": (None, True),
            "2025-08-30": (None, True),
            "Labor Day": (None, True),
            "2025-10-13": (None, True),
            "Veterans Day": (None, True),
            "Veterans Day (Observed)": (None, True),
            "2025-11-27": (None, True),
            "Thanksgiving": (None, True),
            "Day After Thanksgiving": (None, True),
            "2025-11-29": (None, True),
            "Christmas Eve": (None, True),
            "Christmas Eve (Observed)": (None, True),
            "Christmas Day": (None, True),
            "2025-12-26": (None, True),
            "2025-12-27": (None, True),
            "New Year's Eve": (None, True),
        }

        # Dictionary mapping holiday names to their dates in 2025
        holiday_dates_2025 = {
            "New Year's Day": "2025-01-01",
            "New Year's Day (Observed)": "2025-01-01",  # Assuming it's the same day in 2025
            "Martin Luther King Jr. Day": "2025-01-20",  # Third Monday in January
            "Washington's Birthday": "2025-02-17",  # Third Monday in February
            "Memorial Day": "2025-05-26",  # Last Monday in May
            "Independence Day": "2025-07-04",
            "Labor Day": "2025-09-01",  # First Monday in September
            "Veterans Day": "2025-11-11",
            "Veterans Day (Observed)": "2025-11-11",  # Assuming it's the same day in 2025
            "Thanksgiving": "2025-11-27",  # Fourth Thursday in November
            "Day After Thanksgiving": "2025-11-28",
            "Christmas Eve": "2025-12-24",
            "Christmas Eve (Observed)": "2025-12-24",  # Assuming it's the same day in 2025
            "Christmas Day": "2025-12-25",
            "New Year's Eve": "2025-12-31",
        }

        # Counter for created and skipped holidays
        created_count = 0
        skipped_count = 0

        # Process each holiday
        for key, value in mpm_holidays.items():
            artwork_path, is_closed = value

            # Check if the key is a date string (YYYY-MM-DD)
            try:
                if '-' in key:
                    # It's a date string
                    date_obj = datetime.strptime(key, "%Y-%m-%d").date()
                    name = f"Holiday on {date_obj.strftime('%B %d, %Y')}"
                else:
                    # It's a named holiday
                    name = key
                    if key in holiday_dates_2025:
                        date_obj = datetime.strptime(holiday_dates_2025[key], "%Y-%m-%d").date()
                    else:
                        self.stdout.write(self.style.WARNING(f"No date found for {key}, skipping..."))
                        skipped_count += 1
                        continue

                # Check if holiday already exists
                if not Holiday.objects.filter(name=name, date=date_obj).exists():
                    # Create the holiday
                    Holiday.objects.create(
                        name=name,
                        date=date_obj,
                        is_closed=is_closed,
                        artwork_path=artwork_path
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created holiday: {name} on {date_obj}"))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f"Holiday already exists: {name} on {date_obj}, skipping..."))

            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"Error processing {key}: {e}"))
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Finished! Created {created_count} holidays, skipped {skipped_count} holidays."))
