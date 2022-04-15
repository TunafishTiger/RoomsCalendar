#  Copyright (c) 2022.
#  Sean Gibson (SeanGibsonBooks@outlook.com)

#  RoomsCalendarPrinter
#  main.py

import subprocess
from datetime import date, datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt

from holidays import country_holidays


def main():
    # Say hello and request communication.
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

    # Declare helper function to imprint closure.
    def overlay_closed_status(base_image):
        base_image = base_image
        base_image.paste(status_img_closed, (0, 0), mask=status_img_closed)
        base_image.save(calendar_page_name, format="png")

    # Declare helper function to imprint holiday inserts.
    def overlay_artwork(base_image, art_to_use):
        base_image = base_image
        art_to_use = art_to_use
        base_image.paste(art_to_use, (0, 0), mask=art_to_use)
        base_image.save(calendar_page_name, format="png")

    # Define an elegant way to compute deltas. Wrap iteration in console UI output.
    def daterange_to_print(first_date, last_date):
        for n in track(
            range(int((last_date - first_date).days)),
            description="[i]Compiling calendar...[/]",
        ):
            yield first_date + timedelta(n)

    # Begin 1 infinite loop.
    while True:
        try:

            # When are we in real time?
            current_month = datetime.today().month

            # Require one question and map native language to month integers.
            month_the_user_requested_to_print = Prompt.ask(
                "What month should be printed?"
            )
            mturtp_as_number = int(
                datetime.strptime(month_the_user_requested_to_print, "%B").month
            )

            # If we're in December and ask for January, treat it as next year's January.
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

            # Always compute December with a range ending on Jan. 1 of next year.
            if month_the_user_requested_to_print in ("December", "december"):
                printing_end_date = date(year_we_want_to_print_for + 1, 0o1, 0o1)
            else:
                printing_end_date = date(
                    year_we_want_to_print_for, mturtp_as_number + 1, 0o1
                )

            # Initialize a list of US federal holidays specific to Michigan.
            us_holidays = country_holidays(
                "US", subdiv="MI", years=year_we_want_to_print_for
            )

            # Debug holidays
            #   for day in us_holidays.items():
            #   console.print(day)

            # Debug variables
            # console.print(f'{month_the_user_requested_to_print} : {mturtp_as_number} : {days_in_month} ::
            # {printing_start_date}, {printing_end_date}')
            # console.print(type(month_the_user_requested_to_print), type(mturtp_as_number), type(days_in_month),
            # type(printing_start_date), type(printing_end_date))

            # Define our fonts and sizes.
            date_font = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            year_font = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            # Initialize variables for the standard week, reading into memory only once.
            status_img_closed = Image.open(
                "4_RoomSchedule_Template_Closed_Overlay.png"
            ).convert("RGBA")
            base_img_weekday = Image.open(
                "0_RoomSchedule_Template_Weekdays.png"
            ).convert("RGB")
            base_img_fri = Image.open("1_RoomSchedule_Template_Fridays.png").convert(
                "RGB"
            )
            base_img_sat = Image.open("2_RoomSchedule_Template_Saturdays.png").convert(
                "RGB"
            )
            base_img_sun = Image.open("3_RoomSchedule_Template_Sundays.png").convert(
                "RGB"
            )

            # Define artwork for all of our observed holidays and special closures.
            art_new_years_day = Image.open("holidays/NewYearsDay.png").convert("RGBA")
            art_mlk_day = Image.open("holidays/MLKDay.png").convert("RGBA")
            art_valentines_day = Image.open("holidays/ValentinesDay.png").convert(
                "RGBA"
            )
            art_goodfriday_day = Image.open("holidays/GoodFriday.png").convert("RGBA")
            art_memorialday_day = Image.open("holidays/MemorialDay.png").convert("RGBA")
            art_independenceday_day = Image.open(
                "holidays/IndependenceDay.png"
            ).convert("RGBA")
            art_laborday_day = Image.open("holidays/LaborDay.png").convert("RGBA")
            art_veteransday_day = Image.open("holidays/VeteransDay.png").convert("RGBA")
            art_halloween_day = Image.open("holidays/Halloween.png").convert("RGBA")
            art_thanksgivingday_day = Image.open("holidays/Thanksgiving.png").convert(
                "RGBA"
            )
            art_christmas_eve_day = Image.open("holidays/ChristmasEve.png").convert(
                "RGBA"
            )
            art_christmasday_day = Image.open("holidays/ChristmasDay.png").convert(
                "RGBA"
            )
            art_new_years_eve_day = Image.open("holidays/NewYearsEve.png").convert(
                "RGBA"
            )

        # Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        # Iterate through our given month...
        else:
            for single_date in daterange_to_print(
                printing_start_date, printing_end_date
            ):

                # Define a filename scheme.
                calendar_page_name = single_date.strftime(
                    "pages/X_RoomSchedule_%a-%B-%d-%Y.png"
                )

                # Create a mutable calendar image by first
                # recognizing correct day of the standard week.
                match single_date.weekday():
                    case 6:
                        mutable_calendar_img = base_img_sun.copy()
                        overlay_closed_status(mutable_calendar_img)
                    case 5:
                        mutable_calendar_img = base_img_sat.copy()
                    case 4:
                        mutable_calendar_img = base_img_fri.copy()
                    case _:
                        mutable_calendar_img = base_img_weekday.copy()

                # Place correct dates onto the calendar image.
                draw = ImageDraw.Draw(mutable_calendar_img)
                draw.text(
                    (5000, 460),
                    single_date.strftime("%A"),
                    (0, 0, 0),
                    anchor="rs",
                    font=date_font,
                )
                draw.text(
                    (5000, 650),
                    single_date.strftime("%B, %d, %Y"),
                    (0, 0, 0),
                    anchor="rs",
                    font=year_font,
                )

                # Here we account manually each year for long weekends around holidays
                # or for in-staff days.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    case "2022-02-14":  # Valentine's Day.
                        overlay_artwork(mutable_calendar_img, art_valentines_day.copy())
                    case "2022-04-16":  # Good Friday weekend.
                        overlay_closed_status(mutable_calendar_img)
                    case "2022-05-28":  # Memorial Day weekend.
                        overlay_closed_status(mutable_calendar_img)
                    case "2022-09-03" | "2022-09-05":  # Labor Day weekend.
                        overlay_closed_status(mutable_calendar_img)
                    case "2022-10-31":  # Halloween.
                        overlay_artwork(mutable_calendar_img, art_halloween_day.copy())
                    case "2022-11-25" | "2022-11-26":  # Thanksgiving Day weekend.
                        overlay_closed_status(mutable_calendar_img)
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":  # Christmas weekend.
                        overlay_closed_status(mutable_calendar_img)

                # Account for holidays based on algorithm, never needing updating.
                # 'Observed' days do not get holiday inserts, only closure status.
                match us_holidays.get(f"{single_date}"):
                    case "New Year's Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_new_years_day.copy())
                    case "New Year's Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Martin Luther King Jr. Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_mlk_day.copy())
                    case "Good Friday":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_goodfriday_day.copy())
                    case "Memorial Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_memorialday_day.copy()
                        )
                    case "Independence Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_independenceday_day.copy()
                        )
                    case "Independence Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Labor Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(mutable_calendar_img, art_laborday_day.copy())
                    case "Veterans Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_veteransday_day.copy()
                        )
                    case "Veterans Day (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Thanksgiving":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_thanksgivingday_day.copy()
                        )
                    case "Christmas Eve":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_christmas_eve_day.copy()
                        )
                    case "Christmas Eve (Observed)":
                        overlay_closed_status(mutable_calendar_img)
                    case "Christmas Day":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_christmasday_day.copy()
                        )
                    case "New Year's Eve":
                        overlay_closed_status(mutable_calendar_img)
                        overlay_artwork(
                            mutable_calendar_img, art_new_years_eve_day.copy()
                        )

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
                        "-r",
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
