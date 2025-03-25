import typer
import os
from datetime import date, datetime, timedelta
import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.progress import track
import shutil
from sh import lpr

app = typer.Typer()

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

#  Holiday name or date; artwork location; whether closed or not.
#  Reset dates each year as soon as the new calendar is available.

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

var_version = "2025"


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
    for n in track(
        range(int((last_date_ - first_date_).days)), description="Creating calendar..."
    ):
        yield first_date_ + timedelta(n)


def standard_week(single_date_, study_room_mode):
    """Create a mutable calendar sheet based on the mode and current day of the week."""
    if study_room_mode:
        match single_date_.weekday():
            case 6:
                calendar_sheet_ = Image.open(SR_SUNDAY_HOURS).convert("RGB").copy()
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


def check_image_exists(image_path):
    if not os.path.exists(image_path):
        print(f"Error: Missing required image: {image_path}")
        exit(1)


def sendprintjob(calendar_month_name_):
    if not shutil.which("lpr"):
        print(
            "[bold red]Warning: lpr command not found. Print job not sent.[/bold red]"
        )
    else:
        lpr(
            [
                "-o media=A4",
                "-o sides=one-sided",
                "-o print-quality=5",
                "-# 1",
                f"months/{calendar_month_name_}.pdf",
            ]
        )


@app.command()
def main(
    month: str = typer.Argument(
        (datetime.today().replace(day=28) + timedelta(days=4)).strftime("%B"),
        help="Enter name of month to print (e.g., 'June'). Defaults to the next month if none is given.",
    ),
    study_room_mode: bool = typer.Option(
        True, "--study-room", "-sr", help="Run in study room mode."
    ),
    program_room_mode: bool = typer.Option(
        False, "--program-room", "-pr", help="Run in program room mode."
    ),
):

    console = Console()
    month_name = month.capitalize()

    if program_room_mode:
        study_room_mode = False

    mode_label = "Program Room" if not study_room_mode else "Study Room"

    console.print(
        f"\n" f"Running version {var_version} in [italic]{mode_label}[/italic] mode.\n"
    )

    try:
        var_answer_as_number = datetime.strptime(month_name, "%B").month
        var_year_to_print_for = year_to_print_for(var_answer_as_number)
        var_printing_start_date = date(var_year_to_print_for, var_answer_as_number, 1)
        var_printing_end_date = printing_end_date(
            month_name, var_year_to_print_for, var_answer_as_number
        )
    except ValueError:
        console.print(
            "[bold red]Invalid month name. Please enter a valid month.[/bold red]"
        )
        return

    merger = PdfMerger()
    var_michigan_holidays = holidays.US(subdiv="MI", years=var_year_to_print_for)

    if not os.path.exists("SF-Pro-Text-Black.ttf"):
        raise FileNotFoundError(
            "[bold red]SF-Pro-Text-Black.ttf not found. Please ensure the font is in the working directory.[/bold red]"
        )

    # Check if assets are available.
    check_image_exists(STATUS_CLOSED)

    check_image_exists(SR_WEEKDAY_HOURS)
    check_image_exists(SR_FRIDAY_HOURS)
    check_image_exists(SR_SATURDAY_HOURS)
    check_image_exists(SR_SUNDAY_HOURS)

    check_image_exists(PR_WEEKDAY_HOURS)
    check_image_exists(PR_FRIDAY_HOURS)
    check_image_exists(PR_SATURDAY_HOURS)
    check_image_exists(PR_SUNDAY_HOURS)

    for var_single_date in daterange_to_print(
        var_printing_start_date, var_printing_end_date
    ):
        var_calendar_sheet_filename = var_single_date.strftime(
            "pages/Calendar %A %b %d %Y.pdf"
        )

        #  Figure out which image should be the basis for our calendar page, based on day of the week.
        var_calendar_sheet = standard_week(var_single_date, var_calendar_sheet_filename)

        #  Draw correct dates as we compose the calendar page.
        draw_dates(var_calendar_sheet, var_single_date)

        #  Assignment operator.
        holiday_name = var_michigan_holidays.get(var_single_date)
        formatted_date = var_single_date.strftime("%Y-%m-%d")

        sth = mpm_holidays.get(holiday_name) or mpm_holidays.get(formatted_date)
        if sth:
            overlays(var_calendar_sheet, var_calendar_sheet_filename, *sth)

        #  Save our transformed calendar page onto the filesystem.
        os.makedirs("pages", exist_ok=True)
        var_calendar_sheet.save(var_calendar_sheet_filename, format="pdf")

        merger.append(var_calendar_sheet_filename)

    var_calendar_month_name = f"{mode_label}_{month_name}_{var_year_to_print_for}"
    os.makedirs("months", exist_ok=True)
    merger.write(f"months/{var_calendar_month_name}.pdf")
    merger.close()

    for file in os.scandir("pages"):
        os.remove(file.path)

    sendprintjob(var_calendar_month_name)
    console.print(
        f"\n[bold green]Successfully created {mode_label} calendar for {month_name} {var_year_to_print_for}[/bold green]"
    )
    console.print(
        "Now sending to Office Ricoh C4500. Please find your prints there.\n"
    )


if __name__ == "__main__":
    app()
