# RoomsCalendar

A Django web application for generating calendars for library study rooms and program rooms.

## Description

This application allows users to generate calendars for library study rooms and program rooms. It creates PDF calendars
for a specified month and year, with different layouts based on the day of the week and room type. The application also
handles holidays and special dates.

## Features

- Generate calendars for study rooms or program rooms
- Select month and year for calendar generation
- Download generated calendars as PDF files
- Print calendars directly to a printer
- View calendar generation history
- Handle holidays and special dates
- Support for multi-day holiday ranges

## Holiday Management

The application supports managing holidays through the admin interface. Holidays can be single-day or span multiple
days.

### Managing Holidays in Admin

Navigate to `/admin/calendar_generator/holiday/` to manage holidays.

### Available Management Commands

- `populate_holidays`: Populates the database with initial holiday data
  ```
  python manage.py populate_holidays
  ```

- `create_holiday_range`: Creates a holiday with a date range
  ```
  python manage.py create_holiday_range "Holiday Name" "YYYY-MM-DD" "YYYY-MM-DD" --closed --artwork="path/to/artwork.png"
  ```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd RoomsCalendar
   ```

2. Install dependencies:
   ```
   pip install django holidays pillow pypdf2
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Collect static files:
   ```
   python manage.py collectstatic
   ```

5. Run the development server:
   ```
   # Option 1: Using the manage.py script
   python manage.py runserver

   # Option 2: Using the provided shell script
   ./start_django_server.sh
   ```

6. Access the application at http://127.0.0.1:8000/

## Usage

1. Select the room type (Study Room or Program Room)
2. Select the month and year for the calendar
3. Click "Generate & Download Calendar"
4. The calendar will be generated and you'll be redirected to a success page
5. Click "Download Calendar" to download the PDF
6. Click "Print Calendar" to send the calendar directly to the printer
   - The application is configured to print to a networked printer named 'Office-Ricoh-C4500'
   - You can change the printer name in the settings.py file by modifying the NETWORK_PRINTER_NAME setting

## Project Structure

- `calendar_generator/`: Django app for calendar generation
    - `models.py`: Database models for holidays and calendar generation
    - `forms.py`: Form for calendar generation
    - `views.py`: Views for handling web requests and calendar generation
    - `urls.py`: URL routing for the app
- `roomscalendar/`: Django project settings
- `static/`: Static files (images, fonts)
- `templates/`: HTML templates
- `media/`: User-uploaded and generated files

## Transformation from Textual to Django

This project was transformed from a Textual TUI (Terminal User Interface) application to a Django web application. The
transformation involved:

1. Creating a Django project and app structure
2. Migrating the calendar generation logic from the Textual app to Django views
3. Creating models to store calendar generation data
4. Creating forms for user input
5. Creating templates for the web interface
6. Setting up URL routing
7. Configuring static files and media handling

The core calendar generation functionality remains the same, but the user interface has been transformed from a
terminal-based UI to a web-based UI.

## Troubleshooting

### OperationalError when accessing the admin interface

If you encounter an `OperationalError` when accessing the admin interface, it might be due to pending migrations. Run:

```
python manage.py migrate
```

To check the status of migrations, you can use the custom management command:

```
python manage.py check_migrations
```

This will show which migrations have been applied and which are pending.

### Printing Issues

If you encounter issues with printing to the networked printer:

1. Verify that the printer name in settings.py (NETWORK_PRINTER_NAME) matches the actual printer name on your network
2. Ensure that the printer is turned on and connected to the network
3. Check that the user running the Django application has permission to print to the networked printer
4. If using Linux, make sure CUPS is properly configured with the networked printer
5. Check the printer queue for any stuck jobs that might be blocking new print jobs

You can test the printer connection from the command line using:

```
lpr -P Office-Ricoh-C4500 -o media=Letter test_file.pdf
```

Replace 'Office-Ricoh-C4500' with your actual printer name and 'test_file.pdf' with a test PDF file.
