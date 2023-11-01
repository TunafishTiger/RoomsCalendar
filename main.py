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


version = "version 2023: last revised Wed Mar 29"


def figure_year_to_print_for(month_name):
    """Establish when we are, what we want printed."""

    #  If we're in November or later and ask for January, treat it as next year's January.
    #  Else, January of current year.
    if datetime.today().month >= 11 and month_name <= 0o2:
        year_to_print_for = datetime.today().year + 1
    else:
        year_to_print_for = datetime.today().year
    return year_to_print_for


def figure_printing_end_date(month_name, year, month_as_int):
    """Derive an end date for our calendar."""
    #  Always compute December with a range ending on Jan. 1 of next year.
    if month_name in "December":
        printing_end_date = date(year + 1, 0o1, 0o1)
    else:
        printing_end_date = date(year, month_as_int + 1, 0o1)
    return printing_end_date


def overlays(calendar_sheet, calendar_sheet_filename, art, building_closure):
    """Imprint closure and/or holiday artwork."""
    if art:
        calendar_sheet.paste(
            Image.open(art).convert("RGBA"),
            (0, 0),
            mask=Image.open(art).convert("RGBA"),
        )
    if building_closure:
        calendar_sheet.paste(
            Image.open(STATUS_CLOSED).convert("RGBA"),
            (0, 0),
            mask=Image.open(STATUS_CLOSED).convert("RGBA"),
        )
    calendar_sheet.save(calendar_sheet_filename, format="png")


def daterange_to_print(first_date, last_date):
    """Compute deltas. Wrap iteration in console UI output."""
    for n in track(
        range(int((last_date - first_date).days)),
        description="[i].. Compiling calendar...[/]",
    ):
        yield first_date + timedelta(n)


def standard_week(single_date, calendar_sheet_filename):
    """Create a mutable calendar sheet by first recognizing the current day of the standard week."""
    match single_date.weekday():
        case 6:
            calendar_sheet = Image.open(SUNDAY_HOURS_EXTENDED).convert("RGB").copy()
            calendar_sheet.paste(
                Image.open(STATUS_CLOSED).convert("RGBA"),
                (0, 0),
                mask=Image.open(STATUS_CLOSED).convert("RGBA"),
            )
            calendar_sheet.save(calendar_sheet_filename, format="png")
        case 5:
            calendar_sheet = Image.open(SATURDAY_HOURS_EXTENDED).convert("RGB").copy()
        case 4:
            calendar_sheet = Image.open(FRIDAY_HOURS).convert("RGB").copy()
        case _:
            calendar_sheet = Image.open(WEEKDAY_HOURS).convert("RGB").copy()
    return calendar_sheet


def draw_dates(calendarsheet, single_date):
    """Draw dates on each day of the calendar."""
    drawn_dates = ImageDraw.Draw(calendarsheet)
    drawn_dates.text(
        (5000, 460),
        single_date.strftime("%A"),
        (0, 0, 0),
        anchor="rs",
        font=WEEKDAYNAME_FONT,
    )
    drawn_dates.text(
        (5000, 650),
        single_date.strftime("%B, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATESTAMP_FONT,
    )


def sendprintjob(calendar_month_name):
    """
    We use CUPS for printing, which should be available for all UNIX-like systems.
    Relies on configuring Windows Subsystem for Linux as a suitable environment in the office.
    Further configuration of the networked printer takes place there. Here, we simply send
    our print job.
    """
    lpr(
        [
            "-o media=Custom.11x17in",
            "-o sides=one-sided",
            "-o print-quality=5",
            "-# 1",
            # "-r", recursive delete flag
            f"months/{calendar_month_name}.pdf",
        ]
    )


def main():

    #  Initialize console from RICH.
    console = Console()

    console.print(
        f'\n',
        Panel(
            f'\n'
            f'A Python :snake: program to create a calendared logbook for tracking study room usage. '
            f'It always applies dates correctly, and it includes support for both standard and special '
            f'library-defined holidays, as well as predefined building closure dates.\n\n'
            f'(Just type the name of a month, like [cyan b]"June"[/], and [green bold]press enter[/].)\n',
            title='CAROLINE KENNEDY LIBRARY',
            subtitle=f' :books: :books: :books: [i]{version}[/i] :books: :books: :books: ',
        ),
        f'\n',
        width=80,
    )

    #  Begin loop.
    while True:
        try:
            #  Require one question, map language to month integer, derive start and end dates.
            answer = Prompt.ask("What month should be printed?")
            answer = answer.capitalize()

            answer_as_int = int(datetime.strptime(answer, "%B").month)
            year_to_print_for = figure_year_to_print_for(answer_as_int)

            printing_start_date = date(year_to_print_for, answer_as_int, 0o1)
            printing_end_date = figure_printing_end_date(answer, year_to_print_for, answer_as_int)

            #  Initialize a list of major holidays specific to Michigan.
            michigan_holidays = holidays.US(subdiv="MI", years=year_to_print_for)

            #  Initialize PDF file merger.
            merger = PdfMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        else:
            for single_date in daterange_to_print(printing_start_date, printing_end_date):

                #  Define a filename scheme.
                calendar_sheet_filename = single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                #  Figure out which image should be the basis for our calendar page, based on day of the week.
                calendar_sheet = standard_week(single_date, calendar_sheet_filename)

                #  Draw correct dates as we compose the calendar page.
                draw_dates(calendar_sheet, single_date)

                #  Assignment operator.
                if sth := mpm_holidays.get(
                    michigan_holidays.get(single_date),
                    mpm_holidays.get(datetime.strftime(single_date, "%Y-%m-%d")),
                ):
                    overlays(calendar_sheet, calendar_sheet_filename, *sth)

                #  Save our transformed calendar page onto the filesystem.
                calendar_sheet.save(calendar_sheet_filename, format="pdf")

                #  At the end of each loop:
                #  append the new file we've just saved into a multi-page PDF.
                merger.append(calendar_sheet_filename)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = f"{answer}_{year_to_print_for}"

            #  Write multi-page PDF to filesystem.
            try:
                merger.write(f"months/{calendar_month_name}.pdf")
            finally:
                merger.close()

            #  Tidy up.
            #  Delete sheet images from their holding directory.
            for file in os.scandir("pages"):
                os.remove(file.path)

            sendprintjob(calendar_month_name)

            #  Fin.
            console.print(
                f'\n'
                f'The pages for [cyan]{answer} {year_to_print_for}[/] are '
                f'being sent to the Staff [i]RICOH IM C4500.[/i]\n'
                f'You can close the window and go to collect the calendar.'
                f'\n\n'
            )

            break


if __name__ == "__main__":
    main()
