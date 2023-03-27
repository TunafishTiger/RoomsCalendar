#  RoomsCalendar
#  main.py
#  Sean Gibson (c) 2022-2023

"""
    A tiny Python program to create a calendared logbook for study room usage.
    Always applies dates correctly; includes support for both standard and special
    library-defined holidays, as well as predefined building closure dates.

    Replaces a manually curated Word document that was abusing the mail-merge feature.
    Requested by Sheliah S. in order to greatly reduce her workload.
"""

import os
from datetime import date, datetime, timedelta
from typing import Final

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
from sh import lpr

#  Define basic elements to construct our calendar.
STATUS_CLOSED: Final = "4_Asset_ClosedToday.png"
WEEKDAY_HOURS: Final = "0_Asset_WeekdayHours.png"
FRIDAY_HOURS: Final = "1_Asset_FridayHours.png"
SATURDAY_HOURS: Final = "2_Asset_SaturdayHours.png"
SATURDAY_HOURS_EXTENDED: Final = "2_Asset_SaturdayHours_Extended.png"
SUNDAY_HOURS: Final = "3_Asset_SundayHours.png"
SUNDAY_HOURS_EXTENDED: Final = "3_Asset_SundayHours_Extended.png"

#  Define our fonts and sizes.
WEEKDAYNAME_FONT: Final = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
DATESTAMP_FONT: Final = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

#  Define a dictionary of holidays and special dates, some of which we are closed on or imprint artwork for.

"""
    Holiday name or date; artwork location; whether closed or not.
    Reset dates each year as soon as the new calendar is available.
"""

mpm_holidays = {
    "New Year's Day": ("art/NewYearsDay.png", True),
    "New Year's Day (Observed)": (None, True),
    "Martin Luther King Jr. Day": ("art/MLKDay.png", True),
    "2023-02-14": ("art/ValentinesDay.png", False),
    "Washington's Birthday": (None, True),
    "2023-04-07": (None, True),
    "2023-04-08": (None, True),
    "2023-04-09": ("art/EasterSunday.png", True),
    "2023-05-27": (None, True),
    "Memorial Day": ("art/MemorialDay.png", True),
    "2023-05-29": (None, True),
    "2023-06-19": ("art/Juneteenth.png", False),
    "Independence Day": ("art/IndependenceDay.png", True),
    "Independence Day (Observed)": (None, True),
    "2023-09-02": (None, True),
    "2023-09-04": (None, True),
    "Labor Day": ("art/LaborDay.png", True),
    "2023-10-09": ("art/IndigenousPeoplesDay.png", True),
    "2023-10-31": ("art/Halloween.png", False),
    "Veterans Day": ("art/VeteransDay.png", True),
    "Veterans Day (Observed)": (None, True),
    "Thanksgiving": ("art/Thanksgiving.png", True),
    "Day After Thanksgiving": ("art/Thanksgiving.png", True),
    "2023-11-24": ("art/Thanksgiving.png", True),
    "2023-11-25": ("art/Thanksgiving.png", True),
    "2023-12-23": (None, True),
    "Christmas Eve": ("art/ChristmasEve.png", True),
    "Christmas Eve (Observed)": (None, True),
    "Christmas Day": ("art/ChristmasDay.png", True),
    "2023-12-26": (None, True),
    "2023-12-29": (None, True),
    "2023-12-30": (None, True),
    "New Year's Eve": ("art/NewYearsEve.png", True),
}


var_version = "version 2023: last revised Wed Mar 22"


def year_to_print_for(answer_):
    """Establish when we are, what we want printed."""

    #  If we're in November or later and ask for January, treat it as next year's January.
    #  Else, January of current year.
    if datetime.today().month >= 11 and answer_ <= 0o2:
        year_to_print_for_ = datetime.today().year + 1
    else:
        year_to_print_for_ = datetime.today().year
    return year_to_print_for_


def printing_end_date(answer_, year_to_print_for_, answer_as_number_):
    """Derive an end date for our calendar."""
    #  Always compute December with a range ending on Jan. 1 of next year.
    if answer_ in "December":
        var_printing_end_date = date(year_to_print_for_ + 1, 0o1, 0o1)
    else:
        var_printing_end_date = date(year_to_print_for_, answer_as_number_ + 1, 0o1)
    return var_printing_end_date


def overlays(calendar_sheet_, calendar_sheet_filename_, art_to_use_, closure_):
    """Imprint closure and/or holiday artwork."""
    if art_to_use_:
        calendar_sheet_.paste(
            Image.open(art_to_use_).convert("RGBA"),
            (0, 0),
            mask=Image.open(art_to_use_).convert("RGBA"),
        )
    if closure_:
        calendar_sheet_.paste(
            Image.open(STATUS_CLOSED).convert("RGBA"),
            (0, 0),
            mask=Image.open(STATUS_CLOSED).convert("RGBA"),
        )
    calendar_sheet_.save(calendar_sheet_filename_, format="png")


def daterange_to_print(first_date_, last_date_):
    """Compute deltas. Wrap iteration in console UI output."""
    for n in track(
        range(int((last_date_ - first_date_).days)),
        description="[i].. Compiling calendar...[/]",
    ):
        yield first_date_ + timedelta(n)


def standard_week(single_date_, calendar_sheet_filename_):
    """Create a mutable calendar sheet by first recognizing the current day of the standard week."""
    match single_date_.weekday():
        case 6:
            calendar_sheet_ = Image.open(SUNDAY_HOURS_EXTENDED).convert("RGB").copy()
            calendar_sheet_.paste(
                Image.open(STATUS_CLOSED).convert("RGBA"),
                (0, 0),
                mask=Image.open(STATUS_CLOSED).convert("RGBA"),
            )
            calendar_sheet_.save(calendar_sheet_filename_, format="png")
        case 5:
            calendar_sheet_ = Image.open(SATURDAY_HOURS_EXTENDED).convert("RGB").copy()
        case 4:
            calendar_sheet_ = Image.open(FRIDAY_HOURS).convert("RGB").copy()
        case _:
            calendar_sheet_ = Image.open(WEEKDAY_HOURS).convert("RGB").copy()
    return calendar_sheet_


def draw_dates(calendarsheet_, single_date_):
    """Draw dates on each day of the calendar."""
    draw_dates_ = ImageDraw.Draw(calendarsheet_)
    draw_dates_.text(
        (5000, 460),
        single_date_.strftime("%A"),
        (0, 0, 0),
        anchor="rs",
        font=WEEKDAYNAME_FONT,
    )
    draw_dates_.text(
        (5000, 650),
        single_date_.strftime("%B, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATESTAMP_FONT,
    )


def sendprintjob(calendar_month_name_):
    """
    We use CUPS for printing, which should be available for all UNIX-type systems.
    Relies on configuring Windows Subsystem for Linux as a suitable environment in the office.
    Further configuration of the networked printer takes place there. Here we simply send
    our print job.
    """
    lpr(
        [
            "-o media=Custom.11x17in",
            "-o sides=one-sided",
            "-o print-quality=5",
            "-# 1",
            # "-r",
            f"months/{calendar_month_name_}.pdf",
        ]
    )


def main():

    #  Initialize console from RICH.
    console = Console()

    console.print(
        '\n',
        Panel(
            f'\n'
            f'A Python program to create a calendared logbook for study room usage. '
            f'Always applies dates correctly; includes support for both standard and special '
            f'library-defined holidays, as well as predefined building closure dates.\n\n'
            f'(Just type the name of a month, like [cyan b]"June"[/], and [green bold]press enter[/].)\n',
            title='CAROLINE KENNEDY LIBRARY',
            subtitle=f' :books: :books: :books: [i]{var_version}[/i] :books: :books: :books: ',
        ),
        '\n',
        width=80,
    )

    #  Begin loop.
    while True:
        try:
            #  Require one question, map language to month integer, derive start and end dates.
            var_answer = Prompt.ask("What month should be printed?")
            var_answer = var_answer.capitalize()

            var_answer_as_number = int(datetime.strptime(var_answer, "%B").month)
            var_year_to_print_for = year_to_print_for(var_answer_as_number)

            var_printing_start_date = date(var_year_to_print_for, var_answer_as_number, 0o1)
            var_printing_end_date = printing_end_date(var_answer, var_year_to_print_for, var_answer_as_number)

            #  Initialize a list of major holidays specific to Michigan.
            var_michigan_holidays = holidays.US(subdiv="MI", years=var_year_to_print_for)

            #  Initialize PDF file merger.
            merger = PdfMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        else:
            for var_single_date in daterange_to_print(var_printing_start_date, var_printing_end_date):

                #  Define a filename scheme.
                var_calendar_sheet_filename = var_single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

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

                #  At the end of each loop:
                #  append the new file we've just saved into a multi-page PDF.
                merger.append(var_calendar_sheet_filename)

            #  Derive a filename for our new multi-page PDF file.
            var_calendar_month_name = f"{var_answer}_{var_year_to_print_for}"

            #  Write multi-page PDF to filesystem.
            try:
                merger.write(f"months/{var_calendar_month_name}.pdf")
            finally:
                merger.close()

            #  Tidy up.
            #  Delete sheet images from their holding directory.
            for file in os.scandir("pages"):
                os.remove(file.path)

            sendprintjob(var_calendar_month_name)

            #  Fin.
            console.print(
                f'\n'
                f'The pages for [cyan]{var_answer} {var_year_to_print_for}[/] are '
                f'being sent to the Staff [i]RICOH IM C4500.[/i]\n'
                f'You can close the window and go to collect the calendar.'
                f'\n\n'
            )

            break


if __name__ == "__main__":
    main()
