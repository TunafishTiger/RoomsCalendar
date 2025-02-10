import argparse
import os
from datetime import date, datetime, timedelta
import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.progress import track
from sh import lpr

study_room_mode = True

#  Define basic elements to construct our calendar.
STATUS_CLOSED = "4_Asset_ClosedToday.png"
#  Study Room assets
SR_WEEKDAY_HOURS = "SR_0_Asset_WeekdayHours.png"
SR_FRIDAY_HOURS = "SR_1_Asset_FridayHours.png"
SR_SATURDAY_HOURS = "SR_2_Asset_SaturdayHours.png"
SR_SUNDAY_HOURS = "SR_3_Asset_SundayHours.png"
#  Program Room assets
PR_WEEKDAY_HOURS = "PR_0_Asset_WeekdayHours.png"
PR_FRIDAY_HOURS = "PR_1_Asset_FridayHours.png"
PR_SATURDAY_HOURS = "PR_2_Asset_SaturdayHours.png"
PR_SUNDAY_HOURS = "PR_3_Asset_SundayHours.png"


#  Define our fonts and sizes.
DATE_STRING_FONT = ImageFont.truetype("SF-Pro-Text-Black.ttf", 80)

#  Define a dictionary of holidays and special dates, some of which we are closed on or imprint artwork for.

"""
    Holiday name or date; artwork location; whether closed or not.
    Reset dates each year as soon as the new calendar is available.
"""

mpm_holidays = {
    "New Year's Day": (None, True),
    "New Year's Day (Observed)": (None, True),
    "Martin Luther King Jr. Day": (None, True),
    "2023-02-14": (None, False),
    "Washington's Birthday": (None, True),
    "2023-04-07": (None, True),
    "2023-04-08": (None, True),
    "2023-04-09": (None, True),
    "2023-05-27": (None, True),
    "Memorial Day": (None, True),
    "2023-05-29": (None, True),
    "2023-06-19": (None, False),
    "Independence Day": (None, True),
    "Independence Day (Observed)": (None, True),
    "2023-09-02": (None, True),
    "2023-09-04": (None, True),
    "Labor Day": (None, True),
    "2023-10-09": (None, True),
    "2023-10-31": (None, False),
    "Veterans Day": (None, True),
    "Veterans Day (Observed)": (None, True),
    "Thanksgiving": (None, True),
    "Day After Thanksgiving": (None, True),
    "2023-11-24": (None, True),
    "2023-11-25": (None, True),
    "2023-12-23": (None, True),
    "Christmas Eve": (None, True),
    "Christmas Eve (Observed)": (None, True),
    "Christmas Day": (None, True),
    "2023-12-26": (None, True),
    "2023-12-29": (None, True),
    "2023-12-30": (None, True),
    "New Year's Eve": (None, True),
}

var_version = "version 2025: last revised Fri Feb 7"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a calendar for study room or program room usage.")
    parser.add_argument("month", type=str, nargs="?", default=(datetime.today().replace(day=28) + timedelta(days=4)).strftime("%B"),
                        help="Month to print (e.g., 'June'). Defaults to the next month if none is given.")
    parser.add_argument("--program-room", action="store_true", help="Run in program room mode instead of study room mode.")
    return parser.parse_args()


def year_to_print_for(answer_):
    if datetime.today().month >= 11 and answer_ <= 2:
        return datetime.today().year + 1
    return datetime.today().year


def printing_end_date(answer_, year_to_print_for_, answer_as_number_):
    if answer_ == "December":
        return date(year_to_print_for_ + 1, 1, 1)
    return date(year_to_print_for_, answer_as_number_ + 1, 1)


def overlays(calendar_sheet_, calendar_sheet_filename_, art_to_use_, building_closure_):
    """Imprint closure and/or holiday artwork."""
    if art_to_use_:
        calendar_sheet_.paste(
            Image.open(art_to_use_).convert("RGBA"),
            (0, 0),
            mask=Image.open(art_to_use_).convert("RGBA"),
        )
    if building_closure_:
        calendar_sheet_.paste(
            Image.open(STATUS_CLOSED).convert("RGBA"),
            (0, 0),
            mask=Image.open(STATUS_CLOSED).convert("RGBA"),
        )
    calendar_sheet_.save(calendar_sheet_filename_, format="png")


def daterange_to_print(first_date_, last_date_):
    for n in track(range(int((last_date_ - first_date_).days)), description="Generating calendar..."):
        yield first_date_ + timedelta(n)


def standard_week(single_date_, calendar_sheet_filename_):
    """Create a mutable calendar sheet by first recognizing the current day of the standard week."""
    if study_room_mode:
        match single_date_.weekday():
            case 6:
                calendar_sheet_ = Image.open(SR_SUNDAY_HOURS).convert("RGB").copy()
                calendar_sheet_.paste(
                    Image.open(STATUS_CLOSED).convert("RGBA"),
                    (0, 0),
                    mask=Image.open(STATUS_CLOSED).convert("RGBA"),
                )
                calendar_sheet_.save(calendar_sheet_filename_, format="png")
            case 5:
                calendar_sheet_ = Image.open(SR_SATURDAY_HOURS).convert("RGB").copy()
            case 4:
                calendar_sheet_ = Image.open(SR_FRIDAY_HOURS).convert("RGB").copy()
            case _:
                calendar_sheet_ = Image.open(SR_WEEKDAY_HOURS).convert("RGB").copy()
    else:
        match single_date_.weekday():
            case 6:
                calendar_sheet_ = Image.open(PR_SUNDAY_HOURS).convert("RGB").copy()
                calendar_sheet_.paste(
                    Image.open(STATUS_CLOSED).convert("RGBA"),
                    (0, 0),
                    mask=Image.open(STATUS_CLOSED).convert("RGBA"),
                )
                calendar_sheet_.save(calendar_sheet_filename_, format="png")
            case 5:
                calendar_sheet_ = Image.open(PR_SATURDAY_HOURS).convert("RGB").copy()
            case 4:
                calendar_sheet_ = Image.open(PR_FRIDAY_HOURS).convert("RGB").copy()
            case _:
                calendar_sheet_ = Image.open(PR_WEEKDAY_HOURS).convert("RGB").copy()
    return calendar_sheet_


def draw_dates(calendarsheet_, single_date_):
    """Draw dates on each day of the calendar."""
    draw_dates_ = ImageDraw.Draw(calendarsheet_)
    draw_dates_.text(
        (3274, 114),
        single_date_.strftime("%A — %b, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATE_STRING_FONT,
    )

def sendprintjob(calendar_month_name_):
    lpr(["-o media=A4", "-o sides=one-sided", "-o print-quality=5", "-# 1", f"months/{calendar_month_name_}.pdf"])


def main():
    global study_room_mode
    args = parse_arguments()
    console = Console()
    month_name = args.month.capitalize()

    if args.program_room:
        study_room_mode = False

    try:
        var_answer_as_number = datetime.strptime(month_name, "%B").month
        var_year_to_print_for = year_to_print_for(var_answer_as_number)
        var_printing_start_date = date(var_year_to_print_for, var_answer_as_number, 1)
        var_printing_end_date = printing_end_date(month_name, var_year_to_print_for, var_answer_as_number)
    except ValueError:
        console.print("Invalid month name. Please enter a valid month.")
        return

    merger = PdfMerger()
    var_michigan_holidays = holidays.US(subdiv="MI", years=var_year_to_print_for)

    for var_single_date in daterange_to_print(var_printing_start_date, var_printing_end_date):
        var_calendar_sheet_filename = var_single_date.strftime("pages/Calendar %A %b %d %Y.pdf")

        #  Figure out which image should be the basis for our calendar page, based on day of the week.
        var_calendar_sheet = standard_week(var_single_date, var_calendar_sheet_filename)

        #  Draw correct dates as we compose the calendar page.
        draw_dates(var_calendar_sheet, var_single_date)

        #  Assignment operator.
        if sth := mpm_holidays.get(
                var_michigan_holidays.get(var_single_date),
                mpm_holidays.get(datetime.strftime(var_single_date, "%Y-%m-%d")),
        ):
            overlays(var_calendar_sheet, var_calendar_sheet_filename, *sth)

        #  Save our transformed calendar page onto the filesystem.
        var_calendar_sheet.save(var_calendar_sheet_filename, format="pdf")

        merger.append(var_calendar_sheet_filename)

    var_calendar_month_name = f"{month_name}_{var_year_to_print_for}"
    mode_label = "ProgramRoom" if not study_room_mode else "StudyRoom"
    var_calendar_month_name = f"{mode_label}_{month_name}_{var_year_to_print_for}"
    merger.close()


    for file in os.scandir("pages"):
        os.remove(file.path)

    sendprintjob(var_calendar_month_name)
    console.print(f"Calendar for {month_name} {var_year_to_print_for} is being sent to the printer.")


if __name__ == "__main__":
    main()
