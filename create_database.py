import sqlite3

def create_database():
    conn = sqlite3.connect("train.db")

    cur = conn.cursor()
    with open ("SQL-script.sql") as file:
        sqlScript = file.read()
    cur.executescript(sqlScript)
    conn.commit()