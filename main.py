

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

            # Debug variables
            # console.print(f'{puttyw} : {month_as_number} : {days_in_month} :: {start_date}, {end_date}')
            # console.print(type(puttyw), type(month_as_number), type(days_in_month), type(start_date), type(end_date))

            df = ImageFont.truetype("SF-Pro-Text-Black.ttf", 160)
            yf = ImageFont.truetype("SF-Pro-Text-Black.ttf", 124)

            img_weekday = Image.open("0_RoomSchedule_Template_Weekdays.png")
            img_fri = Image.open("1_RoomSchedule_Template_Fridays.png")
            img_sat = Image.open("2_RoomSchedule_Template_Saturdays.png")
            img_sun = Image.open("3_RoomSchedule_Template_Sundays.png")
            img_closed = Image.open("4_RoomSchedule_Template_Closed_Overlay.png")

            no_holiday = Image.open('holidays/Blank.png').convert("RGBA")
            newyearsday = Image.open('holidays/NewYearsDay.png').convert("RGBA")
            christmasday = Image.open('holidays/Halloween.png').convert("RGBA")

        except ValueError:
            console.print('\n[i]I\'m sorry. Please express the name of a month.\n\n')

        else:
            for single_date in daterange(start_date, end_date):

                # Account for days of week
                if single_date.weekday() == 6:
                    img_in_memory = img_sun.copy()
                    img_in_memory.paste(img_closed.copy())
                elif single_date.weekday() == 5:
                    img_in_memory = img_sat.copy()
                elif single_date.weekday() == 4:
                    img_in_memory = img_fri.copy()
                else:
                    img_in_memory = img_weekday.copy()

                draw = ImageDraw.Draw(img_in_memory)
                draw.text((5000, 460), single_date.strftime("%A"), (0, 0, 0), anchor="rs", font=df)
                draw.text((5000, 650), single_date.strftime("%B, %d, %Y"), (0, 0, 0), anchor="rs", font=yf)

                # Account for holiday closures and inserts
                if us_holidays.get(f"{single_date}") == "New Year's Day":
                    holiday_insert = newyearsday.copy()
                elif us_holidays.get(f"{single_date}") == "Christmas Day":
                    holiday_insert = christmasday.copy()
                else:
                    holiday_insert = no_holiday.copy()

                img_in_memory.paste(holiday_insert)
                sheet_name = single_date.strftime("sheets/X_RoomSchedule_%a-%B-%d-%Y.png")
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
