#  Copyright (c) 2022.
#  Sean Gibson (SeanGibsonBooks@outlook.com)

#  RoomsCalendarPrinter
#  main.py

import subprocess
from PIL import Image, ImageFont, ImageDraw
from datetime import date, datetime, timedelta

from rich.panel import Panel
from rich.progress import track
from rich.console import Console
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

    # Begin 1 infinite loop.
    while True:
        try:
            # Define an elegant way to compute deltas. Wrap iteration in console UI output.
            def daterange(first_date, last_date):
                for n in track(
                    range(int((last_date - first_date).days)),
                    description="[i]Compiling calendar...[/]",
                ):
                    yield first_date + timedelta(n)

            # When are we in real time?
            current_month = datetime.today().month

            # Require one question and map native language to month integers.
            putty = Prompt.ask("What month should be printed?")
            month_as_number = int(datetime.strptime(putty, "%B").month)

            # If we're in December and ask for January, treat it as next year's January.
            if putty in ("January", "january") and current_month in (
                "December",
                "december",
            ):
                wanted_year = datetime.today().year + 1
            else:
                wanted_year = datetime.today().year

            start_date = date(wanted_year, month_as_number, 0o1)

            # Always compute December with a range ending on Jan. 1 of next year.
            if putty in ("December", "december"):
                end_date = date(wanted_year + 1, 0o1, 0o1)
            else:
                end_date = date(wanted_year, month_as_number + 1, 0o1)

            # Initialize a list of US federal holidays specific to Michigan.
            us_holidays = country_holidays("US", subdiv="MI", years=wanted_year)

            # Debug holidays
            #   for day in us_holidays.items():
            #   console.print(day)

            # Debug variables
            # console.print(f'{putty} : {month_as_number} : {days_in_month} :: {start_date}, {end_date}')
            # console.print(type(putty), type(month_as_number), type(days_in_month), type(start_date), type(end_date))

            # Define our fonts and sizes.
            df = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            yf = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            # Initialize variables for the standard week, reading into memory only once.
            img_closed = Image.open("4_RoomSchedule_Template_Closed_Overlay.png").convert("RGBA")
            img_weekday = Image.open("0_RoomSchedule_Template_Weekdays.png").convert("RGB")
            img_fri = Image.open("1_RoomSchedule_Template_Fridays.png").convert("RGB")
            img_sat = Image.open("2_RoomSchedule_Template_Saturdays.png").convert("RGB")
            img_sun = Image.open("3_RoomSchedule_Template_Sundays.png").convert("RGB")

            # Define artwork for all of our observed holidays and special closures.
            no_holiday = Image.open("holidays/Blank.png").convert("RGBA")
            new_years_day = Image.open("holidays/NewYearsDay.png").convert("RGBA")
            mlk_day = Image.open("holidays/MLKDay.png").convert("RGBA")
            valentines_day = Image.open("holidays/ValentinesDay.png").convert("RGBA")
            good_friday = Image.open("holidays/GoodFriday.png").convert("RGBA")
            memorial_day = Image.open("holidays/MemorialDay.png").convert("RGBA")
            independence_day = Image.open("holidays/IndependenceDay.png").convert("RGBA")
            labor_day = Image.open("holidays/LaborDay.png").convert("RGBA")
            veterans_day = Image.open("holidays/VeteransDay.png").convert("RGBA")
            halloween = Image.open("holidays/Halloween.png").convert("RGBA")
            thanksgiving = Image.open("holidays/Thanksgiving.png").convert("RGBA")
            christmas_eve = Image.open("holidays/ChristmasEve.png").convert("RGBA")
            christmas_day = Image.open("holidays/ChristmasDay.png").convert("RGBA")
            new_years_eve = Image.open("holidays/NewYearsEve.png").convert("RGBA")

        # Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print("\n[i]I'm sorry. Please express the name of a month.\n\n")

        # Iterate through our given month...
        else:
            for single_date in daterange(start_date, end_date):

                # Define a filename scheme.
                sheet_name = single_date.strftime(
                    "sheets/X_RoomSchedule_%a-%B-%d-%Y.png"
                )

                # Assign days of the standard week.
                match single_date.weekday():
                    case 6:
                        img_in_memory = img_sun.copy()
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case 5:
                        img_in_memory = img_sat.copy()
                    case 4:
                        img_in_memory = img_fri.copy()
                    case _:
                        img_in_memory = img_weekday.copy()

                # Place correct dates onto the calendar sheet.
                draw = ImageDraw.Draw(img_in_memory)
                draw.text(
                    (5000, 460),
                    single_date.strftime("%A"),
                    (0, 0, 0),
                    anchor="rs",
                    font=df,
                )
                draw.text(
                    (5000, 650),
                    single_date.strftime("%B, %d, %Y"),
                    (0, 0, 0),
                    anchor="rs",
                    font=yf,
                )

                holiday_insert = no_holiday

                # Account manually each year for long weekends around holidays or for in-staff days.
                match datetime.strftime(single_date, "%Y-%m-%d"):
                    case "2022-02-14":  # Valentine's Day.
                        holiday_insert = valentines_day.copy()
                    case "2022-04-16":  # Good Friday weekend.
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "2022-05-28":  # Memorial Day weekend.
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "2022-09-03" | "2022-09-05":  # Labor Day weekend.
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "2022-10-31":  # Halloween.
                        holiday_insert = halloween.copy()
                    case "2022-11-25" | "2022-11-26":  # Thanksgiving Day weekend.
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "2022-12-23" | "2022-12-24" | "2022-12-26":  # Christmas weekend.
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)

                # Account for holidays based on algorithm, never needing updating.
                # 'Observed' days do not get holiday inserts, only closure status.
                match us_holidays.get(f"{single_date}"):
                    case "New Year's Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = new_years_day.copy()
                    case "New Year's Day (Observed)":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "Martin Luther King Jr. Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = mlk_day.copy()
                    case "Good Friday":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = good_friday.copy()
                    case "Memorial Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = memorial_day.copy()
                    case "Independence Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = independence_day.copy()
                    case "Independence Day (Observed)":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "Labor Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = labor_day.copy()
                    case "Veterans Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = veterans_day.copy()
                    case "Veterans Day (Observed)":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "Thanksgiving":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = thanksgiving.copy()
                    case "Christmas Eve":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = christmas_eve.copy()
                    case "Christmas Eve (Observed)":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                    case "Christmas Day":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = christmas_day.copy()
                    case "New Year's Eve":
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format="png")
                        img_in_memory = Image.open(sheet_name)
                        holiday_insert = new_years_eve.copy()

                img_in_memory.paste(holiday_insert, (0, 0), mask=holiday_insert)
                img_in_memory.save(sheet_name, format="png")

                # We use CUPS for printing, which should be available for all UNIX-type systems.
                # Rely on configuring Windows Subsystem for Linux as a suitable environment in the office.
                # Further networked-printer configuration takes place there.
                subprocess.call(
                    [
                        "lpr",
                        "-o media=Custom.11x17in",
                        "-o print-quality=5",
                        "-# 1",
                        # '-r',
                        sheet_name,
                    ]
                )

            # Fin.
            console.print(
                f"\nThe sheets for [cyan]{putty.upper()} {wanted_year}[/] are being sent to the Staff RICOH"
                f" IM C4500.\nYou can close the window and go to collect the calendar.\n\n"
            )
            break


if __name__ == "__main__":
    main()
