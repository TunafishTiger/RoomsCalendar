#  RoomsCalendar
#  main.py

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

"""
#  Define artwork that can be overlayed.
NEWYEARSDAY: Final = "art/NewYearsDay.png"
MLKDAY: Final = "art/MLKDay.png"
VALENTINESDAY: Final = "art/ValentinesDay.png"
GOODFRIDAY: Final = "art/GoodFriday.png"
MEMORIALDAY: Final = "art/MemorialDay.png"
JUNETEENTH: Final = "art/Juneteenth.png"
INDEPENDENCEDAY: Final = "art/IndependenceDay.png"
LABORDAY: Final = "art/LaborDay.png"
VETERANSDAY: Final = "art/VeteransDay.png"
HALLOWEEN: Final = "art/Halloween.png"
THANKSGIVING: Final = "art/Thanksgiving.png"
CHRISTMASEVE: Final = "art/ChristmasEve.png"
CHRISTMASDAY: Final = "art/ChristmasDay.png"
NEWYEARSEVE: Final = "art/NewYearsEve.png"
"""

mpm_holidays = {
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
    "Veterans Day": ("art/VeteransDay.png", True),
    "Veterans Day (Observed)": (None, True),
    "2022-10-31": ("art/Halloween.png", False),
    "Thanksgiving": ("art/Thanksgiving.png", True),
    "Day After Thanksgiving": (None, True),
    "Christmas Eve": ("art/ChristmasEve.png", True),
    "Christmas Eve (Observed)": (None, True),
    "Christmas Day": ("art/ChristmasDay.png", True),
    "New Year's Eve": ("art/NewYearsEve.png", True)
}


def year_we_want_to_print_for(answer_):
    """ Declare helper function to establish when we are, what we want printed. """
    current_month = datetime.today().month
    #  If we're in December and ask for January, treat it as next year's January.
    #  Else, January of current year.
    if answer_ in "January" and str(current_month) in "December":
        year_we_want_to_print_for_ = datetime.today().year + 1
    else:
        year_we_want_to_print_for_ = datetime.today().year
    return year_we_want_to_print_for_


def printing_end_date(answer_):
    """ Declare helper function to derive an end date for our calendar. """
    #  Always compute December with a range ending on Jan. 1 of next year.
    if answer_ in "December":
        printingEndDate_ = date(
            yearWeWantToPrintFor + 1, 0o1, 0o1
        )
    else:
        printingEndDate_ = date(
            yearWeWantToPrintFor, answerAsNumber + 1, 0o1
        )
    return printingEndDate_


def overlays(art_to_use_, closure_):
    """ Imprint closure and/or holiday artwork. """
    if art_to_use_:
        calendarSheet.paste(
            Image.open(art_to_use_).convert("RGBA"),
            (0, 0),
            mask=Image.open(art_to_use_).convert("RGBA")
        )
    if closure_:
        calendarSheet.paste(
            Image.open(STATUS_CLOSED).convert("RGBA"),
            (0, 0),
            mask=Image.open(STATUS_CLOSED).convert("RGBA")
        )
    calendarSheet.save(calendarSheetFilename, format="png")


def daterange_to_print(first_date, last_date):
    """ Compute deltas. Wrap iteration in console UI output. """
    for n in track(
            range(int((last_date - first_date).days)),
            description="[i]Compiling calendar...[/]",
    ):
        yield first_date + timedelta(n)


def standard_week(single_date_):
    """ Create a mutable calendar sheet by first recognizing the current day of the standard week. """
    match single_date_.weekday():
        case 6:
            calendarSheet_ = Image.open(SUNDAY_HOURS_EXTENDED).convert("RGB").copy()
            calendarSheet_.paste(
                Image.open(STATUS_CLOSED).convert("RGBA"),
                (0, 0),
                mask=Image.open(STATUS_CLOSED).convert("RGBA"))
            calendarSheet_.save(calendarSheetFilename, format="png")
        case 5:
            calendarSheet_ = Image.open(SATURDAY_HOURS_EXTENDED).convert("RGB").copy()
        case 4:
            calendarSheet_ = Image.open(FRIDAY_HOURS).convert("RGB").copy()
        case _:
            calendarSheet_ = Image.open(WEEKDAY_HOURS).convert("RGB").copy()
    return calendarSheet_


if __name__ == "__main__":

    #  Initialize console from RICH.
    console = Console()

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

    #  Begin 1 infinite loop.
    while True:
        try:
            #  Require one question and map native language to month integers.
            answer = Prompt.ask("What month should be printed?")
            answer = answer.capitalize()
            answerAsNumber = int(datetime.strptime(answer, "%B").month)

            yearWeWantToPrintFor = year_we_want_to_print_for(answer)
            printingStartDate = date(yearWeWantToPrintFor, answerAsNumber, 0o1)
            printingEndDate = printing_end_date(answer)

            #  Initialize a list of major holidays specific to Michigan.
            michiganHolidays = holidays.US(
                subdiv="MI", years=yearWeWantToPrintFor
            )

            #  Initialize PDF file merger.
            merger = PdfFileMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        else:
            for single_date in daterange_to_print(
                printingStartDate, printingEndDate
            ):

                #  Define a filename scheme.
                calendarSheetFilename = single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                calendarSheet = standard_week(single_date)

                #  Draw correct dates as we compose the calendar page.
                draw_dates = ImageDraw.Draw(calendarSheet)
                draw_dates.text(
                    (5000, 460),
                    single_date.strftime("%A"),
                    (0, 0, 0),
                    anchor="rs",
                    font=WEEKDAYNAME_FONT,
                )
                draw_dates.text(
                    (5000, 650),
                    single_date.strftime("%B, %d, %Y"),
                    (0, 0, 0),
                    anchor="rs",
                    font=DATESTAMP_FONT,
                )

                """
                #  This section needs to be updated manually each year to align
                #  with what MPM decides for our calendar.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    # Valentine's Day.
                    case "2022-02-14":
                        overlays(VALENTINESDAY, False)
                    # Good Friday weekend.mc
                    case "2022-04-16":
                        overlays(GOODFRIDAY, True)
                    # Memorial Day weekend.
                    case "2022-05-28":
                        overlays(None, True)
                    # Labor Day weekend.
                    case "2022-09-03" | "2022-09-05":
                        overlays(None, True)
                    # Halloween.
                    case "2022-10-31":
                        overlays(HALLOWEEN, False)
                    # Thanksgiving Day weekend.
                    case "2022-11-25" | "2022-11-26":
                        overlays(None, True)
                    # Christmas weekend.
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":
                        overlays(None, True)

                #  This section is algorithmic and matches holidays specific to
                #  Michigan. These are standard dates we are always closed, or,
                #  acknowledge with artwork.

                match michiganHolidays.get(f"{single_date}"):
                    case "New Year's Day":
                        overlays(NEWYEARSDAY, True)
                    case "New Year's Day (Observed)":
                        overlays(None, True)
                    case "Martin Luther King Jr. Day":
                        overlays(MLKDAY, True)
                    case "Good Friday":
                        overlays(GOODFRIDAY, True)
                    case "Memorial Day":
                        overlays(MEMORIALDAY, True)
                    case "Independence Day":
                        overlays(INDEPENDENCEDAY, True)
                    case "Independence Day (Observed)":
                        overlays(None, True)
                    case "Labor Day":
                        overlays(LABORDAY, True)
                    case "Veterans Day":
                        overlays(VETERANSDAY, True)
                    case "Veterans Day (Observed)":
                        overlays(None, True)
                    case "Thanksgiving":
                        overlays(THANKSGIVING, True)
                    case "Day After Thanksgiving":
                        overlays(None, True)
                    case "Christmas Eve":
                        overlays(CHRISTMASEVE, True)
                    case "Christmas Eve (Observed)":
                        overlays(None, True)
                    case "Christmas Day":
                        overlays(CHRISTMASDAY, True)
                    case "New Year's Eve":
                        overlays(NEWYEARSEVE, True)
                """

                sth = mpm_holidays.get(holiday_name, None) or mpm_holidays.get(date_str, None)
                if sth:
                    overlays(*sth)

                #  Save our transformed calendar page onto the filesystem.
                calendarSheet.save(calendarSheetFilename, format="pdf")

                #  At the end of each loop:
                #  append the file we've just saved into a new multipage PDF.
                merger.append(calendarSheetFilename)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = f"{answer}_{yearWeWantToPrintFor}"

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
                f"\nThe pages for [cyan]{answer} {yearWeWantToPrintFor}[/] are"
                f" being sent to the Staff RICOH IM C4500.\n"
                f"You can close the window and go to collect the calendar.\n"
                f"\n",
            )

            break
