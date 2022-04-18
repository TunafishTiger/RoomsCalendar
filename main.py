#  Copyright (c) 2022. Working branch for development.
#  Sean Gibson (SeanGibsonBooks@outlook.com)

#  RoomsCalendarPrinter
#  main.py

import subprocess
from datetime import date, datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from holidays import country_holidays
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt


def main():
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

    #  Declare helper function to imprint closure.
    def overlay_closed_status(base_image):
        base_image = base_image
        base_image.paste(status_closed, (0, 0), mask=status_closed)
        base_image.save(calendar_page_name, format="png")

    #  Declare helper function to imprint holiday inserts.
    def overlay_artwork(base_image, art_to_use):
        base_image = base_image
        art_to_use = art_to_use
        base_image.paste(art_to_use, (0, 0), mask=art_to_use)
        base_image.save(calendar_page_name, format="png")

    #  Define an elegant way to compute deltas. Wrap iteration in console UI output.
    def daterange_to_print(first_date, last_date):
        for n in track(
            range(int((last_date - first_date).days)),
            description="[i]Compiling calendar...[/]",
        ):
            yield first_date + timedelta(n)

    #  Begin 1 infinite loop.
    while True:
        try:

            #  When are we in real time?
            current_month = datetime.today().month

            #  Require one question and map native language to month integers.
            month_the_user_requested_to_print = Prompt.ask(
                "What month should be printed?"
            )
            mturtp_as_number = int(
                datetime.strptime(month_the_user_requested_to_print, "%B").month
            )

            #  If we're in December and ask for January, treat it as next year's January.
            if month_the_user_requested_to_print in (
                "January",
                "january",
            ) and current_month in (
                "December",
                "december",
            ):
                year_we_want_to_print_for = datetime.today().year + 1
            else:
                year_we_want_to_print_for = datetime.today().year

            printing_start_date = date(year_we_want_to_print_for, mturtp_as_number, 0o1)

            #  Always compute December with a range ending on Jan. 1 of next year.
            if month_the_user_requested_to_print in ("December", "december"):
                printing_end_date = date(year_we_want_to_print_for + 1, 0o1, 0o1)
            else:
                printing_end_date = date(
                    year_we_want_to_print_for, mturtp_as_number + 1, 0o1
                )

            #  Initialize a list of US federal holidays specific to Michigan.
            us_holidays = country_holidays(
                "US", subdiv="MI", years=year_we_want_to_print_for
            )

            #  Debug holidays
            #    for day in us_holidays.items():
            #    console.print(day)

            #  Debug variables
            #  console.print(f'{month_the_user_requested_to_print} : {mturtp_as_number} :
            #  {printing_start_date}, {printing_end_date}')
            #  console.print(type(month_the_user_requested_to_print), type(mturtp_as_number),
            #  type(printing_start_date), type(printing_end_date))

            #  Define our fonts and sizes.
            date_font = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            year_font = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            #  Define basic elements to construct our calendar.
            status_closed = Image.open("4_Asset_ClosedToday.png").convert("RGBA")
            weekday_hours = Image.open("0_Asset_WeekdayHours.png").convert("RGB")
            friday_hours = Image.open("1_Asset_FridayHours.png").convert("RGB")
            saturday_hours = Image.open("2_Asset_SaturdayHours.png").convert("RGB")
            sunday_hours = Image.open("3_Asset_SundayHours.png").convert("RGB")

            #  Define constants for artwork to be overlayed.
            art_new_years_day = Image.open("art/NewYearsDay.png").convert("RGBA")
            art_mlk_day = Image.open("art/MLKDay.png").convert("RGBA")
            art_valentines_day = Image.open("art/ValentinesDay.png").convert("RGBA")
            art_goodfriday_day = Image.open("art/GoodFriday.png").convert("RGBA")
            art_memorialday_day = Image.open("art/MemorialDay.png").convert("RGBA")
            art_independenceday_day = Image.open("art/IndependenceDay.png").convert(
                "RGBA"
            )
            art_laborday_day = Image.open("art/LaborDay.png").convert("RGBA")
            art_veteransday_day = Image.open("art/VeteransDay.png").convert("RGBA")
            art_halloween_day = Image.open("art/Halloween.png").convert("RGBA")
            art_thanksgivingday_day = Image.open("art/Thanksgiving.png").convert("RGBA")
            art_christmas_eve_day = Image.open("art/ChristmasEve.png").convert("RGBA")
            art_christmasday_day = Image.open("art/ChristmasDay.png").convert("RGBA")
            art_new_years_eve_day = Image.open("art/NewYearsEve.png").convert("RGBA")

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
                    "pages/Calendar %A %b %d %Y.png"
                )

                #  Create a mutable calendar image by first
                #  recognizing correct day of the standard week.
                match single_date.weekday():
                    case 6:
                        mutable_calendar_img = sunday_hours.copy()
                        overlay_closed_status(mutable_calendar_img)
                    case 5:
                        mutable_calendar_img = saturday_hours.copy()
                    case 4:
                        mutable_calendar_img = friday_hours.copy()
                    case _:
                        mutable_calendar_img = weekday_hours.copy()

                #  Draw correct dates as we compose the calendar page.
                draw_dates = ImageDraw.Draw(mutable_calendar_img)
                draw_dates.text(
                    (5000, 460),
                    single_date.strftime("%A"),
                    (0, 0, 0),
                    anchor="rs",
                    font=date_font,
                )
                draw_dates.text(
                    (5000, 650),
                    single_date.strftime("%B, %d, %Y"),
                    (0, 0, 0),
                    anchor="rs",
                    font=year_font,
                )

                #
                #  These next two sections determine which special days during
                #  the year are labeled with artwork and/or marked as closed.
                #

                #  This section needs its dates verified by hand each year based on
                #  the list we are given by the City for when we will be closed.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    # Valentine's Day.
                    case "2022-02-14":
                        overlay_artwork(mutable_calendar_img, art_valentines_day)
                    # Good Friday weekend.
                    case "2022-04-16":
                        overlay_artwork(mutable_calendar_img, art_goodfriday_day)
                        overlay_closed_status(mutable_calendar_img)
                    # Memorial Day weekend.
                    case "2022-05-28":
                        overlay_closed_status(mutable_calendar_img)
                    # Labor Day weekend.
                    case "2022-09-03" | "2022-09-05":
                        overlay_closed_status(mutable_calendar_img)
                    # Halloween.
                    case "2022-10-31":
                        overlay_artwork(mutable_calendar_img, art_halloween_day)
                    # Thanksgiving Day weekend.
                    case "2022-11-25" | "2022-11-26":
                        overlay_closed_status(mutable_calendar_img)
                    # Christmas weekend.
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":
                        overlay_closed_status(mutable_calendar_img)

                #  This section is based on algorithms for major federal holidays.
                #  It is meant to never need updating.
                match us_holidays.get(f"{single_date}"):
                    case "New Year's Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_new_years_day)
                    case "New Year's Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Martin Luther King Jr. Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_mlk_day)
                    case "Good Friday":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_goodfriday_day)
                    case "Memorial Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_memorialday_day)
                    case "Independence Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_independenceday_day)
                    case "Independence Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Labor Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_laborday_day)
                    case "Veterans Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_veteransday_day)
                    case "Veterans Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Thanksgiving":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_thanksgivingday_day)
                    case "Christmas Eve":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_christmas_eve_day)
                    case "Christmas Eve (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Christmas Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_christmasday_day)
                    case "New Year's Eve":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_new_years_eve_day)

                #  Save our transformed calendar page onto the filesystem.
                #  Mostly for debugging purposes.
                mutable_calendar_img.save(calendar_page_name, format="png")

                # We use CUPS for printing, which should be available for all UNIX-type systems.
                # Rely on configuring Windows Subsystem for Linux as a suitable environment in the office.
                # Further configuration of the networked printer takes place there. Here we simply use it.
                subprocess.call(
                    [
                        "lpr",
                        "-o media=Custom.11x17in",
                        "-o print-quality=5",
                        "-# 1",
                        #"-r",  # The -r switch deletes the file after creating its print job.
                        calendar_page_name,
                    ]
                )

            # Fin.
            console.print(
                f"\nThe pages for [cyan]{month_the_user_requested_to_print.upper()} {year_we_want_to_print_for}[/] are"
                f" being sent to the Staff RICOH IM C4500.\nYou can close the window and go to collect the calendar.\n"
                f"\n"
            )
            break


if __name__ == "__main__":
    main()
