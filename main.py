

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

    console.print('\n')
    console.print(Panel(' \n This program creates the calendar sheets for our room schedule. \n'
                        ' (Just type the name of a month, like [cyan b]June[/], and [green bold]press enter[/].)',
                        title='Caroline Kennedy Library', subtitle=' :books: :books: :books: :books: :books:'
                                                                   ' :books: '), width=80)
    console.print('\n')

    # Begin 1 infinite loop.
    while True:
        try:
            # Define an elegant way to compute deltas. Wrap it in console UI output.
            def daterange(first_date, last_date):
                for n in track(range(int((last_date - first_date).days)), description="[i]Compiling calendar...[/]"):
                    yield first_date + timedelta(n)

            # When are we in real time?
            current_month = datetime.today().month

            # Require one question and map native language to month integers.
            putty = Prompt.ask('What month should be printed?')
            month_as_number = int(datetime.strptime(putty, '%B').month)

            # If we're in December and ask for January, treat it as next year's.
            if putty in ('January', 'january') and current_month in ('December', 'december'):
                wanted_year = datetime.today().year + 1
            else:
                wanted_year = datetime.today().year

            start_date = date(wanted_year, month_as_number, 0o1)

            # Always compute December with a range ending on Jan. 1 of next year.
            if putty in ('December', 'december'):
                end_date = date(wanted_year + 1, month_as_number, 0o1)
            else:
                end_date = date(wanted_year, month_as_number + 1, 0o1)

            # Initialize a list of US federal holidays specific to Michigan.
            us_holidays = country_holidays('US', subdiv='MI', years=wanted_year)

            # Debug holidays
            # for day in us_holidays.items():
            #     console.print(day)

            # Debug variables
            # console.print(f'{putty} : {month_as_number} : {days_in_month} :: {start_date}, {end_date}')
            # console.print(type(putty), type(month_as_number), type(days_in_month), type(start_date), type(end_date))

            # Define our fonts and sizes.
            df = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            yf = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            # Define our standard week.
            img_closed = Image.open("4_RoomSchedule_Template_Closed_Overlay.png").convert("RGBA")
            img_weekday = Image.open("0_RoomSchedule_Template_Weekdays.png").convert("RGB")
            img_fri = Image.open("1_RoomSchedule_Template_Fridays.png").convert("RGB")
            img_sat = Image.open("2_RoomSchedule_Template_Saturdays.png").convert("RGB")
            img_sun = Image.open("3_RoomSchedule_Template_Sundays.png").convert("RGB")

            # Define our observed holidays and special closures.
            no_holiday = Image.open('holidays/Blank.png').convert("RGBA")
            new_years_day = Image.open('holidays/NewYearsDay.png').convert("RGBA")
            new_years_day_observed = Image.open('holidays/NewYearsDayObserved.png').convert("RGBA")
            mlk_day = Image.open('holidays/MLKDay.png').convert("RGBA")
            washingtons_birthday = Image.open('holidays/WashingtonsBirthday.png').convert("RGBA")
            memorial_day = Image.open('holidays/MemorialDay.png').convert("RGBA")
            juneteenth_national_independence_day = Image.open('holidays/JuneteenthNationalIndependenceDay.png')\
                .convert("RGBA")
            independence_day = Image.open('holidays/IndependenceDay.png').convert("RGBA")
            independence_day_observed = Image.open('holidays/IndependenceDayObserved.png').convert("RGBA")
            labor_day = Image.open('holidays/LaborDay.png').convert("RGBA")
            columbus_day = Image.open('holidays/ColumbusDay.png').convert("RGBA")
            veterans_day = Image.open('holidays/VeteransDay.png').convert("RGBA")
            veterans_day_observed = Image.open('holidays/VeteransDayObserved.png').convert("RGBA")
            thanksgiving = Image.open('holidays/ThanksgivingDay.png').convert("RGBA")
            christmas_eve = Image.open('holidays/ChristmasEve.png').convert("RGBA")
            christmas_eve_observed = Image.open('holidays/ChristmasEveObserved.png').convert("RGBA")
            christmas_day = Image.open('holidays/ChristmasDay.png').convert("RGBA")
            new_years_eve = Image.open('holidays/NewYearsEve.png').convert("RGBA")

        # Nuh-uh-uh. You didn't say the magic word.
        except ValueError:
            console.print('\n[i]I\'m sorry. Please express the name of a month.\n\n')

        # Continue... Iterate through our given month...
        else:
            for single_date in daterange(start_date, end_date):

                # Define filename.
                sheet_name = single_date.strftime("sheets/X_RoomSchedule_%a-%B-%d-%Y.png")

                # Account for days of the standard week.
                match single_date.weekday():
                    case 6:
                        img_in_memory = img_sun.copy()
                        img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                        img_in_memory.save(sheet_name, format='png')
                        img_in_memory = Image.open(sheet_name)
                    case 5:
                        img_in_memory = img_sat.copy()
                    case 4:
                        img_in_memory = img_fri.copy()
                    case _:
                        img_in_memory = img_weekday.copy()

                # Place correct dates onto the calendar sheet.
                draw = ImageDraw.Draw(img_in_memory)
                draw.text((5000, 460), single_date.strftime("%A"), (0, 0, 0), anchor="rs", font=df)
                draw.text((5000, 650), single_date.strftime("%B, %d, %Y"), (0, 0, 0), anchor="rs", font=yf)

                # Account for holiday closures and inserts.
                match us_holidays.get(f"{single_date}"):
                    case "New Year's Day":
                        holiday_insert = new_years_day.copy()
                    case "New Year's Day (Observed)":
                        holiday_insert = new_years_day_observed.copy()
                    case "Martin Luther King Jr. Day":
                        holiday_insert = mlk_day.copy()
                    case "Washington's Birthday":
                        holiday_insert = washingtons_birthday.copy()
                    case "Memorial Day":
                        holiday_insert = memorial_day.copy()
                    case "Juneteenth National Independence Day":
                        holiday_insert = juneteenth_national_independence_day.copy()
                    case "Independence Day":
                        holiday_insert = independence_day.copy()
                    case "Independence Day (Observed)":
                        holiday_insert = independence_day_observed.copy()
                    case "Labor Day":
                        holiday_insert = labor_day.copy()
                    case "Columbus Day":
                        holiday_insert = columbus_day.copy()
                    case "Veterans Day":
                        holiday_insert = veterans_day.copy()
                    case "Veterans Day (Observed)":
                        holiday_insert = veterans_day_observed.copy()
                    case "Thanksgiving":
                        holiday_insert = thanksgiving.copy()
                    case "Christmas Eve":
                        holiday_insert = christmas_eve.copy()
                    case "Christmas Eve (Observed)":
                        holiday_insert = christmas_eve_observed.copy()
                    case "Christmas Day":
                        holiday_insert = christmas_day.copy()
                    case "New Year's Eve":
                        holiday_insert = new_years_eve.copy()
                    case _:
                        holiday_insert = no_holiday.copy()

                img_in_memory.paste(holiday_insert, (0, 0), mask=holiday_insert)
                img_in_memory.save(sheet_name, format='png')

                # We use CUPS for printing, which should be available for all UNIX-type systems.
                subprocess.call([
                    'lpr',
                    '-o media=Custom.11x17in',
                    '-o print-quality=5',
                    '-# 1',
                    # '-r',
                    sheet_name
                ])

            # Fin.
            console.print(f'\nThe sheets for [cyan]{putty.upper()} {wanted_year}[/] are being sent to the Staff RICOH'
                          f' IM C4500.\nYou can close the window and go to collect the calendar.\n\n')
            break


if __name__ == "__main__":
    main()
