#  Copyright (c) 2022. Working branch for development.
#  Sean Gibson (SeanGibsonBooks@outlook.com)

#  RoomsCalendarPrinter
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

#  Define our fonts and sizes.
DATE_FONT: Final = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
YEAR_FONT: Final = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

#  Define basic elements to construct our calendar.
STATUS_CLOSED: Final = Image.open("4_Asset_ClosedToday.png").convert("RGBA")
WEEKDAY_HOURS: Final = Image.open("0_Asset_WeekdayHours.png").convert("RGB")
FRIDAY_HOURS: Final = Image.open("1_Asset_FridayHours.png").convert("RGB")
SATURDAY_HOURS: Final = Image.open("2_Asset_SaturdayHours.png").convert("RGB")
SATURDAY_HOURS_EXTENDED: Final = Image.open(
    "2_Asset_SaturdayHours_Extended.png"
).convert("RGB")
SUNDAY_HOURS: Final = Image.open("3_Asset_SundayHours.png").convert("RGB")
SUNDAY_HOURS_EXTENDED: Final = Image.open("3_Asset_SundayHours_Extended.png").convert(
    "RGB"
)

#  Define artwork that can be overlayed.
ART_NEW_YEARS_DAY: Final = Image.open("art/NewYearsDay.png").convert("RGBA")
ART_MLK_DAY: Final = Image.open("art/MLKDay.png").convert("RGBA")
ART_VALENTINES_DAY: Final = Image.open("art/ValentinesDay.png").convert("RGBA")
ART_GOODFRIDAY_DAY: Final = Image.open("art/GoodFriday.png").convert("RGBA")
ART_MEMORIALDAY_DAY: Final = Image.open("art/MemorialDay.png").convert("RGBA")
ART_JUNETEENTH: Final = Image.open("art/Juneteenth.png").convert("RGBA")
ART_INDEPENDENCEDAY_DAY: Final = Image.open("art/IndependenceDay.png").convert("RGBA")
ART_LABORDAY_DAY: Final = Image.open("art/LaborDay.png").convert("RGBA")
ART_VETERANSDAY_DAY: Final = Image.open("art/VeteransDay.png").convert("RGBA")
ART_HALLOWEEN_DAY: Final = Image.open("art/Halloween.png").convert("RGBA")
ART_THANKSGIVINGDAY_DAY: Final = Image.open("art/Thanksgiving.png").convert("RGBA")
ART_CHRISTMASEVE_DAY: Final = Image.open("art/ChristmasEve.png").convert("RGBA")
ART_CHRISTMASDAY_DAY: Final = Image.open("art/ChristmasDay.png").convert("RGBA")
ART_NEW_YEARS_EVE_DAY: Final = Image.open("art/NewYearsEve.png").convert("RGBA")


def main():

    #  Declare helper function to imprint closure.
    def overlay_closed_status():
        mutable_calendar_img.paste(STATUS_CLOSED, (0, 0), mask=STATUS_CLOSED)
        mutable_calendar_img.save(calendar_page_name, format="png")

    #  Declare helper function to imprint holiday inserts.
    def overlay_artwork(art_to_use):
        mutable_calendar_img.paste(art_to_use, (0, 0), mask=art_to_use)
        mutable_calendar_img.save(calendar_page_name, format="png")

    #  Define an elegant way to compute deltas. Wrap iteration in console UI output.
    def daterange_to_print(first_date, last_date):
        for n in track(
            range(int((last_date - first_date).days)),
            description="[i]Compiling calendar...[/]",
        ):
            yield first_date + timedelta(n)

    #  Say hello and request communication.
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

            #  Establish our location within real time.
            current_month = datetime.today().month

            #  Require one question and map native language to month integers.
            answer = Prompt.ask("What month should be printed?")

            answer = answer.capitalize()

            answer_as_number = int(datetime.strptime(answer, "%B").month)

            #  If we're in December and ask for January, treat it as next year's January.
            if answer in "January" and str(current_month) in "December":
                year_we_want_to_print_for = datetime.today().year + 1
            else:
                # year_we_want_to_print_for = 2021  # Test flag
                year_we_want_to_print_for = datetime.today().year

            printing_start_date = date(year_we_want_to_print_for, answer_as_number, 0o1)

            #  Always compute December with a range ending on Jan. 1 of next year.
            if answer in "December":
                printing_end_date = date(year_we_want_to_print_for + 1, 0o1, 0o1)
            else:
                printing_end_date = date(
                    year_we_want_to_print_for, answer_as_number + 1, 0o1
                )

            #  Initialize a list of major holidays specific to Michigan.
            michigan_holidays = holidays.US(
                subdiv="MI", years=year_we_want_to_print_for
            )

            #  Open PDF file merger.
            merger = PdfFileMerger()

        #  Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        #  Iterate through our given month one day at a time until finished.
        else:
            for single_date in daterange_to_print(
                printing_start_date, printing_end_date
            ):

                #  Define a filename scheme.
                calendar_page_name = single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                #  Create a mutable calendar image by first
                #  recognizing correct day of the standard week.
                match single_date.weekday():
                    case 6:
                        mutable_calendar_img = SUNDAY_HOURS_EXTENDED.copy()
                        overlay_closed_status()
                    case 5:
                        mutable_calendar_img = SATURDAY_HOURS_EXTENDED.copy()
                    case 4:
                        mutable_calendar_img = FRIDAY_HOURS.copy()
                    case _:
                        mutable_calendar_img = WEEKDAY_HOURS.copy()

                #  Draw correct dates as we compose the calendar page.
                draw_dates = ImageDraw.Draw(mutable_calendar_img)
                draw_dates.text(
                    (5000, 460),
                    single_date.strftime("%A"),
                    (0, 0, 0),
                    anchor="rs",
                    font=DATE_FONT,
                )
                draw_dates.text(
                    (5000, 650),
                    single_date.strftime("%B, %d, %Y"),
                    (0, 0, 0),
                    anchor="rs",
                    font=YEAR_FONT,
                )

                #  This section is meant to pull from SQL.

                #  This section needs to be updated manually each year to align
                #  with what MPM decides for our calendar.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    # Valentine's Day.
                    case "2022-02-14":
                        overlay_artwork(ART_VALENTINES_DAY)
                    # Good Friday weekend.
                    case "2022-04-16":
                        overlay_artwork(ART_GOODFRIDAY_DAY)
                        overlay_closed_status()
                    # Memorial Day weekend.
                    case "2022-05-28":
                        overlay_closed_status()
                    # Labor Day weekend.
                    case "2022-09-03" | "2022-09-05":
                        overlay_closed_status()
                    # Halloween.
                    case "2022-10-31":
                        overlay_artwork(ART_HALLOWEEN_DAY)
                    # Thanksgiving Day weekend.
                    case "2022-11-25" | "2022-11-26":
                        overlay_closed_status()
                    # Christmas weekend.
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":
                        overlay_closed_status()

                #  This section is algorithmic and matches holidays specific to
                #  Michigan. These are standard dates we are always closed on.

                match michigan_holidays.get(f"{single_date}"):
                    case "New Year's Day":
                        overlay_closed_status()
                        overlay_artwork(ART_NEW_YEARS_DAY)
                    case "New Year's Day (Observed)":
                        overlay_closed_status()
                    case "Martin Luther King Jr. Day":
                        overlay_closed_status()
                        overlay_artwork(ART_MLK_DAY)
                    case "Good Friday":
                        overlay_closed_status()
                        overlay_artwork(ART_GOODFRIDAY_DAY)
                    case "Memorial Day":
                        overlay_closed_status()
                        overlay_artwork(ART_MEMORIALDAY_DAY)
                    case "Independence Day":
                        overlay_closed_status()
                        overlay_artwork(ART_INDEPENDENCEDAY_DAY)
                    case "Independence Day (Observed)":
                        overlay_closed_status()
                    case "Labor Day":
                        overlay_closed_status()
                        overlay_artwork(ART_LABORDAY_DAY)
                    case "Veterans Day":
                        overlay_closed_status()
                        overlay_artwork(ART_VETERANSDAY_DAY)
                    case "Veterans Day (Observed)":
                        overlay_closed_status()
                    case "Thanksgiving":
                        overlay_closed_status()
                        overlay_artwork(ART_THANKSGIVINGDAY_DAY)
                    case "Day After Thanksgiving":
                        overlay_closed_status()
                    case "Christmas Eve":
                        overlay_closed_status()
                        overlay_artwork(ART_CHRISTMASEVE_DAY)
                    case "Christmas Eve (Observed)":
                        overlay_closed_status()
                    case "Christmas Day":
                        overlay_closed_status()
                        overlay_artwork(ART_CHRISTMASDAY_DAY)
                    case "New Year's Eve":
                        overlay_closed_status()
                        overlay_artwork(ART_NEW_YEARS_EVE_DAY)

                #  Save our transformed calendar page onto the filesystem.
                mutable_calendar_img.save(calendar_page_name, format="pdf")

                #  At the end of each loop:
                #  append the file we've just saved into a multi-page PDF.
                merger.append(calendar_page_name)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = f"{answer}_{year_we_want_to_print_for}"

            #  Write multi-page PDF to filesystem.
            merger.write(f"months/{calendar_month_name}.pdf")
            merger.close()

            #  Delete page images from their holding directory.
            for file in os.scandir("pages"):
                os.remove(file.path)

            #  We use CUPS for printing, which should be available for all UNIX-type systems.
            #  Relies on configuring Windows Subsystem for Linux as a suitable environment in the office.
            #  Further configuration of the networked printer takes place there. Here we simply send to
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
