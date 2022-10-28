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


def main():

    def overlays(_art_to_use, _closure):
        """ Imprint closure and/or holiday artwork. """
        if _art_to_use:
            calendarSheet.paste(
                Image.open(_art_to_use).convert("RGBA"),
                (0, 0),
                mask=Image.open(_art_to_use).convert("RGBA")
            )
        if _closure:
            calendarSheet.paste(
                Image.open(STATUS_CLOSED).convert("RGBA"),
                (0, 0),
                mask=Image.open(STATUS_CLOSED).convert("RGBA")
            )
        calendarSheet.save(calendarSheetFilename, format="png")

    #  Compute deltas. Wrap iteration in console UI output.
    def daterange_to_print(first_date, last_date):
        for n in track(
                range(int((last_date - first_date).days)),
                description="[i]Compiling calendar...[/]",
        ):
            yield first_date + timedelta(n)

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
            #  Establish what month we're actually in.
            current_month = datetime.today().month

            #  Require one question and map native language to month integers.
            answer = Prompt.ask("What month should be printed?")
            answer = answer.capitalize()
            answer_as_number = int(datetime.strptime(answer, "%B").month)

            #  If we're in December and ask for January, treat it as next year's January.
            #  Else, January of current year.
            if answer in "January" and str(current_month) in "December":
                year_we_want_to_print_for = datetime.today().year + 1
            else:
                year_we_want_to_print_for = datetime.today().year

            printing_start_date = date(year_we_want_to_print_for, answer_as_number, 0o1)

            #  Always compute December with a range ending on Jan. 1 of next year.
            if answer in "December":
                printing_end_date = date(
                    year_we_want_to_print_for + 1, 0o1, 0o1
                )
            else:
                printing_end_date = date(
                    year_we_want_to_print_for, answer_as_number + 1, 0o1
                )

            #  Initialize a list of major holidays specific to Michigan.
            michigan_holidays = holidays.US(
                subdiv="MI", years=year_we_want_to_print_for
            )

            #  Initialize PDF file merger.
            merger = PdfFileMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        else:
            for single_date in daterange_to_print(
                    printing_start_date, printing_end_date
            ):

                #  Define a filename scheme.
                calendar_sheet_filename = single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                #  Create a mutable calendar sheet by first
                #  recognizing the current day of the standard week.
                match single_date.weekday():
                    case 6:
                        calendar_sheet = SUNDAY_HOURS_EXTENDED.copy()
                        overlays(None, True)
                    case 5:
                        calendar_sheet = SATURDAY_HOURS_EXTENDED.copy()
                    case 4:
                        calendar_sheet = FRIDAY_HOURS.copy()
                    case _:
                        calendar_sheet = WEEKDAY_HOURS.copy()

                #  Draw correct dates as we compose the calendar page.
                draw_dates = ImageDraw.Draw(calendar_sheet)
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

                #  This section needs to be updated manually each year to align
                #  with what MPM decides for our calendar.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    case "2022-02-14":
                        overlays(VALENTINESDAY, False)
                    case "2022-04-16":
                        overlays(GOODFRIDAY, True)
                    case "2022-05-28":
                        overlays(None, True)
                    case "2022-09-03" | "2022-09-05":
                        overlays(None, True)
                    case "2022-10-31":
                        overlays(HALLOWEEN, False)
                    case "2022-11-25" | "2022-11-26":
                        overlays(None, True)
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":
                        overlays(None, True)

                #  This section is algorithmic and matches holidays specific to
                #  Michigan. These are standard dates we are always closed, or,
                #  acknowledge with artwork.

                match michigan_holidays.get(f"{single_date}"):
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

                #  Save our transformed calendar page onto the filesystem.
                calendar_sheet.save(calendar_sheet_filename, format="pdf")

                #  At the end of each loop:
                #  append the file we've just saved into a multipage PDF.
                merger.append(calendar_sheet_filename)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = f"{answer}_{year_we_want_to_print_for}"

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
                f"\nThe pages for [cyan]{answer} {year_we_want_to_print_for}[/] are"
                f" being sent to the Staff RICOH IM C4500.\n"
                f"You can close the window and go to collect the calendar.\n"
                f"\n",
            )

            break


if __name__ == "__main__":
    main()
