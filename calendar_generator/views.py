import os
from datetime import date, datetime, timedelta

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect

# Try to import sh module, provide fallback if not available.
try:
    import sh
    from sh import lpr, ErrorReturnCode
except ImportError:
    # Define fallback for sh module
    sh = None

    # Define fallback for lpr function
    def lpr(*args, **kwargs):
        raise Exception("The 'sh' module is not installed. Please install it using 'pip install sh'.")

    # Define fallback for ErrorReturnCode
    class ErrorReturnCode(Exception):
        pass

from .forms import CalendarGenerationForm
from .models import CalendarGeneration, Holiday

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


# Function to get holiday information from the database
def get_holiday_info(holiday_name=None, date_str=None):
    """
    Get holiday information from the database.

    Args:
        holiday_name (str, optional): The name of the holiday.
        date_str (str, optional): The date string in YYYY-MM-DD format.

    Returns:
        tuple: A tuple containing (artwork_path, is_closed) or None if no holiday is found.
    """
    try:
        # Try to find by name first
        if holiday_name:
            holiday = Holiday.objects.filter(name=holiday_name).first()
            if holiday:
                # Check if holiday has an uploaded artwork
                if holiday.artwork and holiday.artwork.image:
                    return (holiday.artwork.image.path, holiday.is_closed)
                # Fall back to artwork_path if no uploaded artwork
                return (holiday.artwork_path, holiday.is_closed)

        # Then try to find by date
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Check for exact date match
                holiday = Holiday.objects.filter(date=date_obj).first()
                if holiday:
                    # Check if holiday has an uploaded artwork
                    if holiday.artwork and holiday.artwork.image:
                        return (holiday.artwork.image.path, holiday.is_closed)
                    # Fall back to artwork_path if no uploaded artwork
                    return (holiday.artwork_path, holiday.is_closed)

                # Check if date falls within a date range
                range_holiday = Holiday.objects.filter(
                    date__lte=date_obj,
                    end_date__gte=date_obj
                ).first()
                if range_holiday:
                    # Check if holiday has an uploaded artwork
                    if range_holiday.artwork and range_holiday.artwork.image:
                        return (range_holiday.artwork.image.path, range_holiday.is_closed)
                    # Fall back to artwork_path if no uploaded artwork
                    return (range_holiday.artwork_path, range_holiday.is_closed)

            except ValueError:
                pass

        return None
    except Exception as e:
        print(f"Error getting holiday info: {e}")
        return None


def home(request):
    """Home page view with calendar generation form."""
    form = CalendarGenerationForm()

    if request.method == 'POST':
        form = CalendarGenerationForm(request.POST)
        if form.is_valid():
            calendar = form.save(commit=False)

            # Set the year internally based on the selected month
            calendar.year = year_to_print_for(calendar.month)

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

                # Add success message
                messages.success(request,
                                 f"Your calendar for {calendar.get_month_display()} {calendar.year} has been generated successfully.")

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


def print_calendar(request, calendar_id):
    """Send the generated calendar to the printer."""
    try:
        calendar = CalendarGeneration.objects.get(id=calendar_id)
        file_path = calendar.pdf_file.path

        if os.path.exists(file_path):
            # Check if sh module is available
            if sh is None:
                messages.error(request, "The 'sh' module is not installed. Please install it using 'pip install sh'.")
                return redirect('calendar_success', calendar_id=calendar.id)

            try:
                # Get the network printer name from settings
                network_printer = getattr(settings, 'NETWORK_PRINTER_NAME', None)

                # Send the PDF to the printer using lpr command
                if network_printer:
                    # If network printer is configured, specify it with -P option
                    lpr("-P", network_printer,
                        "-o", "media=Letter",
                        "-o", "sides=one-sided",
                        "-o", "print-quality=5",
                        "-#", "1",
                        file_path)
                else:
                    # Fall back to default printer if no network printer is configured
                    lpr("-o", "media=Letter",
                        "-o", "sides=one-sided",
                        "-o", "print-quality=5",
                        "-#", "1",
                        file_path)

                if network_printer:
                    messages.success(request, f"Calendar sent to {network_printer} printer successfully. Please find your prints there.")
                else:
                    messages.success(request, "Calendar sent to default printer successfully.")
                return redirect('calendar_success', calendar_id=calendar.id)
            except ErrorReturnCode as e:
                messages.error(request, f"Error sending to printer: {str(e)}")
                return redirect('calendar_success', calendar_id=calendar.id)
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect('calendar_success', calendar_id=calendar.id)
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
    """
    Imprint closure and/or holiday artwork.

    Returns:
        PIL.Image: The modified calendar sheet with overlays applied
    """
    static_dir = os.path.join(settings.STATIC_ROOT)

    # Convert calendar_sheet to RGBA mode to properly handle alpha channels
    if calendar_sheet.mode != "RGBA":
        calendar_sheet = calendar_sheet.convert("RGBA")

    # Handle cases where one or both overlays are present
    if art_to_use:
        # Determine the artwork path
        if os.path.isabs(art_to_use):
            art_path = art_to_use
        else:
            art_path = os.path.join(static_dir, art_to_use)

        artwork_image = Image.open(art_path).convert("RGBA")
        calendar_sheet = Image.alpha_composite(calendar_sheet, artwork_image)

    if building_closure:
        # Determine the closure image path
        if os.path.isabs(STATUS_CLOSED):
            closure_path = STATUS_CLOSED
        else:
            closure_path = os.path.join(static_dir, STATUS_CLOSED)

        closure_image = Image.open(closure_path).convert("RGBA")
        calendar_sheet = Image.alpha_composite(calendar_sheet, closure_image)

    # Save a PNG version for reference
    calendar_sheet.save(calendar_sheet_filename, format="png")

    # Return the modified calendar sheet
    return calendar_sheet


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
        
        # Get holiday artwork and closure status
        holiday_info = get_holiday_info(holiday_name, formatted_date)
        
        # Determine if building should be marked as closed
        is_sunday = single_date.weekday() == 6
        should_show_closed = is_sunday or (holiday_info and holiday_info[1])
        
        # Get holiday artwork if it exists
        holiday_artwork = holiday_info[0] if holiday_info else None
        
        # Apply overlays with both holiday artwork and closure status when applicable
        calendar_sheet = overlays(
            calendar_sheet,
            calendar_sheet_filename,
            holiday_artwork,
            should_show_closed
        )

        # Convert back to RGB for PDF saving if needed
        if calendar_sheet.mode == "RGBA":
            calendar_sheet = calendar_sheet.convert("RGB")

        # Save the calendar page with overlays
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