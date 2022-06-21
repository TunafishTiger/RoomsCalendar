import sqlite3


def grapefruit():
    con = sqlite3.connect('grapefruit.db')
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS holidays
                        (observance text, date date, if_artwork real, artwork_img text)''')

    cur.execute('''INSERT INTO holidays VALUES
                        ('Juneteenth', '06-19', '0', '/')''')

    con.commit()