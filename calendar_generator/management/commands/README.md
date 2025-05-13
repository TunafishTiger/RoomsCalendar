# Holiday Management Commands

This directory contains management commands for managing holidays in the RoomsCalendar application.

## Available Commands

### populate_holidays

Populates the Holiday model with initial data from the hardcoded mpm_holidays dictionary.

```bash
python manage.py populate_holidays
```

### create_holiday_range

Creates a holiday with a date range. This is useful for holidays that span multiple days.

```bash
python manage.py create_holiday_range "Holiday Name" "2025-01-01" "2025-01-03" --closed --artwork="path/to/artwork.png"
```

#### Arguments:

- `name`: Name of the holiday
- `start_date`: Start date of the holiday (YYYY-MM-DD)
- `end_date`: End date of the holiday (YYYY-MM-DD)
- `--closed`: (Optional) Whether the library is closed during this holiday
- `--artwork`: (Optional) Path to the artwork for this holiday

## Using Date Ranges in the Admin Interface

The Holiday model now supports date ranges. When adding or editing a holiday in the admin interface:

1. Navigate to the admin interface at `/admin/calendar_generator/holiday/`
2. Click "Add Holiday" or select an existing holiday to edit
3. Enter the holiday name
4. Select the start date in the "Date" field
5. (Optional) Select the end date in the "End date" field if the holiday spans multiple days
6. Check "Is closed" if the library is closed during this holiday
7. (Optional) Enter the path to the artwork for this holiday
8. Click "Save"

When a holiday has a date range, the calendar generator will apply the holiday settings to all days within that range.

## Examples

### Creating a Single-Day Holiday

```bash
python manage.py create_holiday_range "New Year's Day" "2025-01-01" "2025-01-01" --closed
```

### Creating a Multi-Day Holiday

```bash
python manage.py create_holiday_range "Spring Break" "2025-03-15" "2025-03-22" --closed
```

### Creating a Holiday with Custom Artwork

```bash
python manage.py create_holiday_range "Christmas Week" "2025-12-24" "2025-12-26" --closed --artwork="images/christmas.png"
```