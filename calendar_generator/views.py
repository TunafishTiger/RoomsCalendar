import os
from datetime import date, datetime, timedelta

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect

from .forms import CalendarGenerationForm
from .models import CalendarGeneration

# Define constants for assets
STATUS_CLOSED = "images/4_Asset_ClosedToday.png"
# Study Room assets
SR_WEEKDAY_HOURS = "images/SR_0_Asset_WeekdayHours.png"
SR_FRIDAY_HOURS = "images/SR_1_Asset_FridayHours.png"
SR_SATURDAY_HOURS = "images/SR_2_Asset_SaturdayHours.png"
SR_SUNDAY_HOURS = "images/SR_3_Asset_SundayHours.png"
# Program Room assets
PR_WEEKDAY_HOURS = "images/PR_0_Asset_WeekdayHours.png"
PR_FRIDAY_HOURS = "images/PR_1_Asset_FridayHours.png"
PR_SATURDAY_HOURS = "images/PR_2_Asset_SaturdayHours.png"
PR_SUNDAY_HOURS = "images/PR_3_Asset_SundayHours.png"

# Define font
DATE_STRING_FONT_PATH = os.path.join(settings.STATIC_ROOT, 'fonts', 'SF-Pro-Text-Black.ttf')

# Define holidays dictionary
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


def home(request):
    """Home page view with calendar generation form."""
    form = CalendarGenerationForm()

    if request.method == 'POST':
        form = CalendarGenerationForm(request.POST)
        if form.is_valid():
            calendar = form.save(commit=False)

            # Create directories if they don't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'pages'), exist_ok=True)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'calendars'), exist_ok=True)

            # Generate the calendar
            try:
                pdf_path = generate_calendar(
                    calendar.room_type,
                    calendar.month,
                    calendar.year
                )

                # Save the PDF path to the model
                calendar.pdf_file = pdf_path.replace(str(settings.MEDIA_ROOT) + '/', '')
                calendar.save()

                # Redirect to the success page
                return redirect('calendar_success', calendar_id=calendar.id)
            except Exception as e:
                messages.error(request, f"Error generating calendar: {str(e)}")

    return render(request, 'calendar_generator/home.html', {'form': form})


def calendar_success(request, calendar_id):
    """Success page after calendar generation."""
    try:
        calendar = CalendarGeneration.objects.get(id=calendar_id)
        return render(request, 'calendar_generator/success.html', {'calendar': calendar})
    except CalendarGeneration.DoesNotExist:
        messages.error(request, "Calendar not found.")
        return redirect('home')


def download_calendar(request, calendar_id):
    """Download the generated calendar."""
    try:
        calendar = CalendarGeneration.objects.get(id=calendar_id)
        file_path = calendar.pdf_file.path

        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        else:
            messages.error(request, "Calendar file not found.")
            return redirect('home')
    except CalendarGeneration.DoesNotExist:
        messages.error(request, "Calendar not found.")
        return redirect('home')


# Helper functions for calendar generation
def year_to_print_for(month):
    if datetime.today().month >= 11 and month <= 2:
        return datetime.today().year + 1
    return datetime.today().year


def get_printing_end_date(month_name, year, month_number):
    if month_name == "December":
        return date(year + 1, 1, 1)
    return date(year, month_number + 1, 1)


def daterange_to_print(first_date, last_date):
    for n in range(int((last_date - first_date).days)):
        yield first_date + timedelta(n)


def standard_week(single_date, study_room_mode):
    """Create a mutable calendar sheet based on the mode and current day of the week."""
    static_dir = os.path.join(settings.STATIC_ROOT)

    if study_room_mode == 'study':
        match single_date.weekday():
            case 6:
                calendar_sheet = Image.open(os.path.join(static_dir, SR_SUNDAY_HOURS)).convert("RGB").copy()
            case 5:
                calendar_sheet = Image.open(os.path.join(static_dir, SR_SATURDAY_HOURS)).convert("RGB").copy()
            case 4:
                calendar_sheet = Image.open(os.path.join(static_dir, SR_FRIDAY_HOURS)).convert("RGB").copy()
            case _:
                calendar_sheet = Image.open(os.path.join(static_dir, SR_WEEKDAY_HOURS)).convert("RGB").copy()
    else:
        match single_date.weekday():
            case 6:
                calendar_sheet = Image.open(os.path.join(static_dir, PR_SUNDAY_HOURS)).convert("RGB").copy()
            case 5:
                calendar_sheet = Image.open(os.path.join(static_dir, PR_SATURDAY_HOURS)).convert("RGB").copy()
            case 4:
                calendar_sheet = Image.open(os.path.join(static_dir, PR_FRIDAY_HOURS)).convert("RGB").copy()
            case _:
                calendar_sheet = Image.open(os.path.join(static_dir, PR_WEEKDAY_HOURS)).convert("RGB").copy()
    return calendar_sheet


def draw_dates(calendarsheet, single_date):
    """Draw dates on each day of the calendar."""
    draw_dates_ = ImageDraw.Draw(calendarsheet)
    font = ImageFont.truetype(DATE_STRING_FONT_PATH, 80)
    draw_dates_.text(
        (3274, 114),
        single_date.strftime("%A — %b, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=font,
    )


def overlays(calendar_sheet, calendar_sheet_filename, art_to_use, building_closure):
    """Imprint closure and/or holiday artwork."""
    static_dir = os.path.join(settings.STATIC_ROOT)

    if art_to_use:
        calendar_sheet.paste(
            Image.open(os.path.join(static_dir, art_to_use)).convert("RGBA"),
            (0, 0),
            mask=Image.open(os.path.join(static_dir, art_to_use)).convert("RGBA"),
        )
    if building_closure:
        calendar_sheet.paste(
            Image.open(os.path.join(static_dir, STATUS_CLOSED)).convert("RGBA"),
            (0, 0),
            mask=Image.open(os.path.join(static_dir, STATUS_CLOSED)).convert("RGBA"),
        )
    calendar_sheet.save(calendar_sheet_filename, format="png")


def generate_calendar(room_type, month, year):
    """Generate a calendar for the specified month, year, and room type."""
    # Get month name
    month_name = dict(CalendarGeneration.MONTH_CHOICES)[month]

    # Set up dates
    printing_start_date = date(year, month, 1)
    printing_end_date = get_printing_end_date(month_name, year, month)

    # Set up directories
    pages_dir = os.path.join(settings.MEDIA_ROOT, 'pages')
    calendars_dir = os.path.join(settings.MEDIA_ROOT, 'calendars')
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(calendars_dir, exist_ok=True)

    # Initialize PDF merger
    merger = PdfMerger()
    michigan_holidays = holidays.US(subdiv="MI", years=year)

    # Generate calendar pages
    for single_date in daterange_to_print(printing_start_date, printing_end_date):
        calendar_sheet_filename = os.path.join(
            pages_dir,
            single_date.strftime("Calendar %A %b %d %Y.pdf")
        )

        # Figure out which image should be the basis for our calendar page
        calendar_sheet = standard_week(single_date, room_type)

        # Draw correct dates
        draw_dates(calendar_sheet, single_date)

        # Check for holidays
        holiday_name = michigan_holidays.get(single_date)
        formatted_date = single_date.strftime("%Y-%m-%d")

        sth = mpm_holidays.get(holiday_name) or mpm_holidays.get(formatted_date)
        if sth:
            overlays(calendar_sheet, calendar_sheet_filename, *sth)

        # Save the calendar page
        calendar_sheet.save(calendar_sheet_filename, format="pdf")

        # Add to merger
        merger.append(calendar_sheet_filename)

    # Save the merged PDF
    room_type_label = "Study Room" if room_type == 'study' else "Program Room"
    calendar_name = f"{room_type_label}_{month_name}_{year}.pdf"
    output_path = os.path.join(calendars_dir, calendar_name)
    merger.write(output_path)
    merger.close()

    # Clean up temporary files
    for file in os.scandir(pages_dir):
        os.remove(file.path)

    return output_path
