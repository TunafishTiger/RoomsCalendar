

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

    console = Console()

    console.print('\n')
    console.print(Panel(' \n This program creates the calendar sheets for our room schedule. \n'
                        ' (Just type the name of a month, like [cyan b]June[/], and [green bold]press enter[/].)',
                        title='Caroline Kennedy Library', subtitle=' :books: :books: :books: :books: :books:'
                                                                   ' :books: '), width=80)
    console.print('\n')

    while True:
        try:
            def daterange(first_date, last_date):
                for n in track(range(int((last_date - first_date).days)), description="[i]Compiling calendar...[/]"):
                    yield first_date + timedelta(n)

            puttyw = Prompt.ask('What month should be printed?')            # str
            month_as_number = int(datetime.strptime(puttyw, '%B').month)    # int

            if puttyw in ('January', 'january'):
                wanted_year = datetime.today().year + 1
            else:
                wanted_year = datetime.today().year

            start_date = date(wanted_year, month_as_number, 0o1)      # date
            end_date = date(wanted_year, month_as_number + 1, 0o1)    # date

            us_holidays = country_holidays('US', subdiv='MI', years=wanted_year)

            # Debug holidays
            # for day in us_holidays.items():
            #     console.print(day)

            # Debug variables
            # console.print(f'{puttyw} : {month_as_number} : {days_in_month} :: {start_date}, {end_date}')
            # console.print(type(puttyw), type(month_as_number), type(days_in_month), type(start_date), type(end_date))

            # Define our fonts.
            df = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            yf = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            # Define our week.
            img_closed = Image.open("4_RoomSchedule_Template_Closed_Overlay.png").convert("RGBA")
            img_weekday = Image.open("0_RoomSchedule_Template_Weekdays.png").convert("RGB")
            img_fri = Image.open("1_RoomSchedule_Template_Fridays.png").convert("RGB")
            img_sat = Image.open("2_RoomSchedule_Template_Saturdays.png").convert("RGB")
            img_sun = Image.open("3_RoomSchedule_Template_Sundays.png").convert("RGB")

            # Define our observed holidays and special closures.
            no_holiday = Image.open('holidays/Blank.png').convert("RGBA")
            newyearsday = Image.open('holidays/NewYearsDay.png').convert("RGBA")
            newyearsdayobserved = Image.open('holidays/NewYearsDayObserved.png').convert("RGBA")
            mlkday = Image.open('holidays/MLKDay.png').convert("RGBA")
            washingday = Image.open('holidays/WashingtonsBirthday.png').convert("RGBA")
            memorialday = Image.open('holidays/MemorialDay.png').convert("RGBA")
            juneteenthnationalindependenceday = Image.open('holidays/JuneteenthNationalIndependenceDay.png')\
                .convert("RGBA")
            independenceday = Image.open('holidays/IndependenceDay.png').convert("RGBA")
            independencedayobserved = Image.open('holidays/IndependenceDayObserved.png').convert("RGBA")
            laborday = Image.open('holidays/LaborDay.png').convert("RGBA")
            columbusday = Image.open('holidays/ColumbusDay.png').convert("RGBA")
            veteransday = Image.open('holidays/VeteransDay.png').convert("RGBA")
            veteransdayobserved = Image.open('holidays/VeteransDayObserved.png').convert("RGBA")
            thanksgiving = Image.open('holidays/ThanksgivingDay.png').convert("RGBA")
            christmaseve = Image.open('holidays/ChristmasEve.png').convert("RGBA")
            christmaseveobserved = Image.open('holidays/ChristmasEveObserved.png').convert("RGBA")
            christmasday = Image.open('holidays/ChristmasDay.png').convert("RGBA")
            newyearseve = Image.open('holidays/NewYearsEve.png').convert("RGBA")

        except ValueError:
            console.print('\n[i]I\'m sorry. Please express the name of a month.\n\n')

        else:
            for single_date in daterange(start_date, end_date):

                # Define our filename.
                sheet_name = single_date.strftime("sheets/X_RoomSchedule_%a-%B-%d-%Y.png")

                # Account for days of week.
                if single_date.weekday() == 6:
                    img_in_memory = img_sun.copy()
                    img_in_memory.paste(img_closed, (0, 0), mask=img_closed)
                    img_in_memory.save(sheet_name, format='png')
                    img_in_memory = Image.open(sheet_name)
                elif single_date.weekday() == 5:
                    img_in_memory = img_sat.copy()
                elif single_date.weekday() == 4:
                    img_in_memory = img_fri.copy()
                else:
                    img_in_memory = img_weekday.copy()

                draw = ImageDraw.Draw(img_in_memory)
                draw.text((5000, 460), single_date.strftime("%A"), (0, 0, 0), anchor="rs", font=df)
                draw.text((5000, 650), single_date.strftime("%B, %d, %Y"), (0, 0, 0), anchor="rs", font=yf)

                # Account for holiday closures and inserts.
                if us_holidays.get(f"{single_date}") == "New Year's Day":
                    holiday_insert = newyearsday.copy()
                elif us_holidays.get(f"{single_date}") == "New Year's Day (Observed)":
                    holiday_insert = newyearsdayobserved.copy()
                elif us_holidays.get(f"{single_date}") == "Martin Luther King Jr. Day":
                    holiday_insert = mlkday.copy()
                elif us_holidays.get(f"{single_date}") == "Washington's Birthday":
                    holiday_insert = washingday.copy()
                elif us_holidays.get(f"{single_date}") == "Memorial Day":
                    holiday_insert = memorialday.copy()
                elif us_holidays.get(f"{single_date}") == "Juneteenth National Independence Day":
                    holiday_insert = juneteenthnationalindependenceday.copy()
                elif us_holidays.get(f"{single_date}") == "Independence Day":
                    holiday_insert = independenceday.copy()
                elif us_holidays.get(f"{single_date}") == "Independence Day (Observed)":
                    holiday_insert = independencedayobserved.copy()
                elif us_holidays.get(f"{single_date}") == "Labor Day":
                    holiday_insert = laborday.copy()
                elif us_holidays.get(f"{single_date}") == "Columbus Day":
                    holiday_insert = columbusday.copy()
                elif us_holidays.get(f"{single_date}") == "Veterans Day":
                    holiday_insert = veteransday.copy()
                elif us_holidays.get(f"{single_date}") == "Veterans Day (Observed)":
                    holiday_insert = veteransdayobserved.copy()
                elif us_holidays.get(f"{single_date}") == "Thanksgiving":
                    holiday_insert = thanksgiving.copy()
                elif us_holidays.get(f"{single_date}") == "Christmas Eve":
                    holiday_insert = christmaseve.copy()
                elif us_holidays.get(f"{single_date}") == "Christmas Eve (Observed)":
                    holiday_insert = christmaseveobserved.copy()
                elif us_holidays.get(f"{single_date}") == "Christmas Day":
                    holiday_insert = christmasday.copy()
                elif us_holidays.get(f"{single_date}") == "New Year's Eve":
                    holiday_insert = newyearseve.copy()
                else:
                    holiday_insert = no_holiday.copy()

                img_in_memory.paste(holiday_insert, (0, 0), mask=holiday_insert)
                img_in_memory.save(sheet_name, format='png')

                # UNIX-type systems.
                subprocess.call([
                    'lpr',
                    '-o media=Custom.11x17in',
                    '-o print-quality=5',
                    '-# 1',
                    # '-r',
                    sheet_name
                ])

            console.print(f'\nThe sheets for [cyan]{puttyw.upper()} {wanted_year}[/] are being sent to the Staff RICOH'
                          f' IM C4500.\nYou can close the window and go to collect the calendar.\n\n')
            break


if __name__ == "__main__":
    main()
