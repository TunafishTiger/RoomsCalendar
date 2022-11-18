#  RoomsCalendar
#  main.py
#  Sean Gibson (c) 2022-2023

"""
   Software to programmatically create a calendared logbook for study room usage.
   Always applies dates correctly, and includes support for both standard and special
   library-defined holidays, as well as predefined building closure dates.

   Replaces a manually curated Word document that was abusing the mail-merge feature.
   Requested by Sheliah Snipes in order to greatly reduce her workload of tedious tasks.
"""

import os
from datetime import date, datetime, timedelta
from typing import Final

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfFileMerger
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
    Reset dates each year as soon as the new calendar is available for February.
"""
mpm_holidays = {
    "New Year's Day": ("art/NewYearsDay.png", True),
    "New Year's Day (Observed)": (None, True),
    "Martin Luther King Jr. Day": ("art/MLKDay.png", True),
    "2022-02-14": ("art/ValentinesDay.png", False),
    "Good Friday": ("art/GoodFriday.png", True),
    "2022-04-16": ("art/GoodFriday.png", True),
    "Memorial Day": ("art/MemorialDay.png", True),
    "2022-05-28": (None, True),
    "2022-06-19": ("art/Juneteenth.png", False),
    "Independence Day": ("art/IndependenceDay.png", True),
    "Independence Day (Observed)": (None, True),
    "Labor Day": ("art/LaborDay.png", True),
    "2022-09-03": (None, True),
    "2022-09-05": (None, True),
    "2022-10-31": ("art/Halloween.png", False),
    "Veterans Day": ("art/VeteransDay.png", True),
    "Veterans Day (Observed)": (None, True),
    "Thanksgiving": ("art/Thanksgiving.png", True),
    "Day After Thanksgiving": (None, True),
    "Christmas Eve": ("art/ChristmasEve.png", True),
    "Christmas Eve (Observed)": (None, True),
    "Christmas Day": ("art/ChristmasDay.png", True),
    "New Year's Eve": ("art/NewYearsEve.png", True),
}


def year_to_print_for(answer_):
    """Establish when we are, what we want printed."""

    #  If we're in November or later and ask for January, treat it as next year's January.
    #  Else, January of current year.
    if datetime.today().month >= 11 and answer_ <= 0o1:
        year_to_print_for_ = datetime.today().year + 1
    else:
        year_to_print_for_ = datetime.today().year
    return year_to_print_for_


def printing_end_date(answer_):
    """Derive an end date for our calendar."""
    #  Always compute December with a range ending on Jan. 1 of next year.
    if answer_ in "December":
        printingEndDate_ = date(yearToPrintFor + 1, 0o1, 0o1)
    else:
        printingEndDate_ = date(yearToPrintFor, answerAsNumber + 1, 0o1)
    return printingEndDate_


def overlays(art_to_use_, closure_):
    """Imprint closure and/or holiday artwork."""
    if art_to_use_:
        calendarSheet.paste(
            Image.open(art_to_use_).convert("RGBA"),
            (0, 0),
            mask=Image.open(art_to_use_).convert("RGBA"),
        )
    if closure_:
        calendarSheet.paste(
            Image.open(STATUS_CLOSED).convert("RGBA"),
            (0, 0),
            mask=Image.open(STATUS_CLOSED).convert("RGBA"),
        )
    calendarSheet.save(calendarSheetFilename, format="png")


def daterange_to_print(first_date, last_date):
    """Compute deltas. Wrap iteration in console UI output."""
    for n in track(
        range(int((last_date - first_date).days)),
        description="[i]Compiling calendar...[/]",
    ):
        yield first_date + timedelta(n)


def standard_week(single_date_):
    """Create a mutable calendar sheet by first recognizing the current day of the standard week."""
    match single_date_.weekday():
        case 6:
            calendarsheet_ = Image.open(SUNDAY_HOURS_EXTENDED).convert("RGB").copy()
            calendarsheet_.paste(
                Image.open(STATUS_CLOSED).convert("RGBA"),
                (0, 0),
                mask=Image.open(STATUS_CLOSED).convert("RGBA"),
            )
            calendarsheet_.save(calendarSheetFilename, format="png")
        case 5:
            calendarsheet_ = Image.open(SATURDAY_HOURS_EXTENDED).convert("RGB").copy()
        case 4:
            calendarsheet_ = Image.open(FRIDAY_HOURS).convert("RGB").copy()
        case _:
            calendarsheet_ = Image.open(WEEKDAY_HOURS).convert("RGB").copy()
    return calendarsheet_


def draw_dates(calendarsheet_):
    """Draw dates on each day of the calendar."""
    draw_dates_ = ImageDraw.Draw(calendarsheet_)
    draw_dates_.text(
        (5000, 460),
        single_date.strftime("%A"),
        (0, 0, 0),
        anchor="rs",
        font=WEEKDAYNAME_FONT,
    )
    draw_dates_.text(
        (5000, 650),
        single_date.strftime("%B, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATESTAMP_FONT,
    )


def main():

    console.print(
        "\n",
        Panel(
            " \nThis program creates the calendar sheets for our room schedule.\n"
            " (Just type the name of a month, like [cyan b]June[/], and [green bold]press enter[/].)\n",
            title="Caroline Kennedy Library",
            subtitle=" :books: :books: :books: :books: :books: :books: ",
        ),
        "\n",
        width=80,
    )


if __name__ == "__main__":

    #  Initialize console from RICH.
    console = Console()

    main()

    #  Begin 1 infinite loop.
    while True:
        try:
            #  Require one question and map native language to month integers.
            answer = Prompt.ask("What month should be printed?")
            answer = answer.capitalize()

            answerAsNumber = int(datetime.strptime(answer, "%B").month)
            yearToPrintFor = year_to_print_for(answerAsNumber)

            printingStartDate = date(yearToPrintFor, answerAsNumber, 0o1)
            printingEndDate = printing_end_date(answer)

            #  Initialize a list of major holidays specific to Michigan.
            michiganHolidays = holidays.US(subdiv="MI", years=yearToPrintFor)

            #  Initialize PDF file merger.
            merger = PdfFileMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        else:
            for single_date in daterange_to_print(printingStartDate, printingEndDate):

                #  Define a filename scheme.
                calendarSheetFilename = single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                #  Figure out which image should be the base of our calendar based on day of the week.
                calendarSheet = standard_week(single_date)

                #  Draw correct dates as we compose the calendar page.
                draw_dates(calendarSheet)

                #  Study.
                if sth := mpm_holidays.get(
                    michiganHolidays.get(single_date),
                    mpm_holidays.get(datetime.strftime(single_date, "%Y-%m-%d")),
                ):
                    overlays(*sth)

                #  Save our transformed calendar page onto the filesystem.
                calendarSheet.save(calendarSheetFilename, format="pdf")

                #  At the end of each loop:
                #  append the new file we've just saved into a multipage PDF.
                merger.append(calendarSheetFilename)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = f"{answer}_{yearToPrintFor}"

            #  Write multi-page PDF to filesystem.
            merger.write(f"months/{calendar_month_name}.pdf")
            merger.close()

            #  Tidy up.
            #  Delete sheet images from their holding directory.
            for file in os.scandir("pages"):
                os.remove(file.path)

            #  We use CUPS for printing, which should be available for all UNIX-type systems.
            #  Relies on configuring Windows Subsystem for Linux as a suitable environment in the office.
            #  Further configuration of the networked printer takes place there. Here we simply send
            #  our print job.
            lpr(
                [
                    "-o media=Custom.11x17in",
                    "-o sides=one-sided",
                    "-o print-quality=5",
                    "-# 1",
                    # "-r",
                    f"months/{calendar_month_name}.pdf",
                ]
            )

            #  Fin.
            console.print(
                f"\nThe pages for [cyan]{answer} {yearToPrintFor}[/] are"
                f" being sent to the Staff RICOH IM C4500.\n"
                f"You can close the window and go to collect the calendar.\n"
                f"\n",
            )

            break
