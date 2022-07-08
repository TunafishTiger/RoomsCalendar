import sqlite3

from rich.prompt import Prompt


def add_holiday():
    con = sqlite3.connect('grapefruit.db')
    cur = con.cursor()

    answer = Prompt.ask("What Holiday should be added?")

    answer = answer.capitalize()

    answer_as_number = int(datetime.strptime(answer, "%B").month)

    cur.execute('''CREATE TABLE IF NOT EXISTS holidays
                        (observance text, date date, if_artwork real, artwork_img text)''')

    cur.execute('''INSERT INTO holidays VALUES
                        (answer, '06-19', '0', '/')''')

    con.commit()