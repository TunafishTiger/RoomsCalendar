#  Copyright (c) 2022. Working branch for development.
#  Sean Gibson (SeanGibsonBooks@outlook.com)

#  RoomsCalendarPrinter
#  main.py

import os
from datetime import date, datetime, timedelta

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfFileMerger
from dateutil.easter import easter
from dateutil.relativedelta import FR, SA, relativedelta as rd
from holidays.constants import (DEC, JUN, MAY, NOV, OCT, SEP)
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
from sh import lpr

#  CONSTANTS:

#  Define our fonts and sizes.
DATE_FONT = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
YEAR_FONT = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

#  Define basic elements to construct our calendar.
STATUS_CLOSED = Image.open("4_Asset_ClosedToday.png").convert("RGBA")
WEEKDAY_HOURS = Image.open("0_Asset_WeekdayHours.png").convert("RGB")
FRIDAY_HOURS = Image.open("1_Asset_FridayHours.png").convert("RGB")
SATURDAY_HOURS = Image.open("2_Asset_SaturdayHours.png").convert("RGB")
SUNDAY_HOURS = Image.open("3_Asset_SundayHours.png").convert("RGB")

#  Define artwork that can be overlayed.
ART_NEW_YEARS_DAY = Image.open("art/NewYearsDay.png").convert("RGBA")
ART_MLK_DAY = Image.open("art/MLKDay.png").convert("RGBA")
ART_VALENTINES_DAY = Image.open("art/ValentinesDay.png").convert("RGBA")
ART_GOODFRIDAY = Image.open("art/GoodFriday.png").convert("RGBA")
ART_MEMORIALDAY_DAY = Image.open("art/MemorialDay.png").convert("RGBA")
ART_JUNETEENTH = Image.open("art/Juneteenth.png").convert("RGBA")
ART_INDEPENDENCEDAY_DAY = Image.open("art/IndependenceDay.png").convert("RGBA")
ART_LABORDAY_DAY = Image.open("art/LaborDay.png").convert("RGBA")
ART_VETERANSDAY_DAY = Image.open("art/VeteransDay.png").convert("RGBA")
ART_HALLOWEEN_DAY = Image.open("art/Halloween.png").convert("RGBA")
ART_THANKSGIVINGDAY_DAY = Image.open("art/Thanksgiving.png").convert("RGBA")
ART_CHRISTMASEVE_DAY = Image.open("art/ChristmasEve.png").convert("RGBA")
ART_CHRISTMASDAY_DAY = Image.open("art/ChristmasDay.png").convert("RGBA")
ART_NEW_YEARS_EVE_DAY = Image.open("art/NewYearsEve.png").convert("RGBA")


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

    console.print("\n")
    console.print(
        Panel(
            " \n This program creates the calendar sheets for our room schedule. \n"
            " (Just type the name of a month, like [cyan b]June[/], and [green bold]press enter[/].)",
            title="Caroline Kennedy Library",
            subtitle=" :books: :books: :books: :books: :books:" " :books: ",
        ),
        width=80,
    )
    console.print("\n")

    #  Begin 1 infinite loop.
    while True:
        try:

            #  Establish our location within real time.
            current_month = datetime.today().month

            #  Require one question and map native language to month integers.
            month_the_user_requested_to_print = Prompt.ask(
                "What month should be printed?"
            )

            month_the_user_requested_to_print = (
                month_the_user_requested_to_print.capitalize()
            )

            mturtp_as_number = int(
                datetime.strptime(month_the_user_requested_to_print, "%B").month
            )

            #  If we're in December and ask for January, treat it as next year's January.
            if month_the_user_requested_to_print in "January" and str(current_month) in "December":
                year_we_want_to_print_for = datetime.today().year + 1
            else:
                # year_we_want_to_print_for = 2021  # Test flag
                year_we_want_to_print_for = datetime.today().year

            printing_start_date = date(year_we_want_to_print_for, mturtp_as_number, 0o1)

            #  Always compute December with a range ending on Jan. 1 of next year.
            if month_the_user_requested_to_print in "December":
                printing_end_date = date(year_we_want_to_print_for + 1, 0o1, 0o1)
            else:
                printing_end_date = date(
                    year_we_want_to_print_for, mturtp_as_number + 1, 0o1
                )

            #  HOLIDAYS
            #  Initialize a list of US federal holidays specific to Michigan.
            michigan_holidays = holidays.US(
                subdiv="MI", years=year_we_want_to_print_for
            )

            #  Create our own algorithmic class specific to dates important to
            #  Caroline Kennedy Library. Includes concept of holiday weekends.
            class CarolineKennedyHolidays(holidays.HolidayBase):
                def _populate(self, year):
                    self[date(year, 2, 14)] = "Valentine's Day"
                    self[easter(year) + rd(weekday=SA(-1))] = "Good Friday Weekend"
                    self[date(year, MAY, 31) + rd(weekday=SA(-1))] = "Memorial Day Weekend"
                    self[date(year, JUN, 19)] = "Juneteenth"
                    self[date(year, SEP, 1) + rd(weekday=SA(+1))] = "Labor Day Weekend"  # huh
                    self[date(year, OCT, 31)] = "Halloween"
                    self[date(year, NOV, 1) + rd(weekday=FR(+4))] = "Thanksgiving Friday"
                    self[date(year, NOV, 1) + rd(weekday=SA(+4))] = "Thanksgiving Saturday"
                    self[date(year, DEC, 1) + rd(weekday=FR(+4))] = "Christmas Friday"
                    self[date(year, DEC, 1) + rd(weekday=SA(+4))] = "Christmas Saturday"
                    self[date(year, DEC, 26)] = "Day After Christmas"
                    self[date(year, DEC, 1) + rd(weekday=FR(+5))] = "New Year\'s Eve Friday"
                    self[date(year, DEC, 1) + rd(weekday=SA(+5))] = "New Year\'s Eve Saturday"

            ck_holidays = CarolineKennedyHolidays()

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
                        mutable_calendar_img = SUNDAY_HOURS.copy()
                        overlay_closed_status()
                    case 5:
                        mutable_calendar_img = SATURDAY_HOURS.copy()
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
                        overlay_artwork(ART_GOODFRIDAY)
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

                match ck_holidays.get(f"{single_date}"):
                    case "Valentine's Day":
                        overlay_artwork(ART_VALENTINES_DAY)
                    case "Good Friday Weekend":
                        overlay_closed_status()
                    case "Memorial Day Weekend":
                        overlay_closed_status()
                    case "Juneteenth":
                        overlay_artwork(ART_JUNETEENTH)
                    case "Labor Day Weekend":
                        overlay_closed_status()
                    case "Halloween":
                        overlay_artwork(ART_HALLOWEEN_DAY)
                    case "Thanksgiving Friday" | \
                         "Thanksgiving Saturday":
                        overlay_closed_status()
                    case "Christmas Friday" | \
                         "Christmas Saturday" | \
                         "Day After Christmas":
                        overlay_closed_status()
                    case "New Year\'s Eve Friday" | \
                         "New Year\'s Eve Saturday":
                        overlay_closed_status()

                #  Save our transformed calendar page onto the filesystem.
                mutable_calendar_img.save(calendar_page_name, format="pdf")

                #  At the end of each loop:
                #  append the file we've just saved into a multi-page PDF.
                merger.append(calendar_page_name)

            #  Derive a filename for our new multi-page PDF file.
            calendar_month_name = (
                f"{month_the_user_requested_to_print}_{year_we_want_to_print_for}"
            )

            #  Write multi-page PDF to filesystem.
            merger.write(f"months/{calendar_month_name}.pdf")
            merger.close()

            #  We use CUPS for printing, which should be available for all UNIX-type systems.
            #  Rely on configuring Windows Subsystem for Linux as a suitable environment in the office.
            #  Further configuration of the networked printer takes place there. Here we simply send to
            #  our print job to it.
            lpr(
                [
                    "-o media=Custom.11x17in",
                    "-o sides=one-sided",
                    "-o print-quality=5",
                    "-# 1",
                    # "-r",
                    f"months/{calendar_month_name}.pdf"
                ]
            )

            #  Delete page images from their holding directory.
            for file in os.scandir('pages'):
                os.remove(file.path)

            #  Fin.
            console.print(
                f"\nThe pages for [cyan]{month_the_user_requested_to_print.upper()} {year_we_want_to_print_for}[/] are"
                f" being sent to the Staff RICOH IM C4500.\nYou can close the window and go to collect the calendar.\n"
                f"\n"
            )
            break


if __name__ == "__main__":
    main()
