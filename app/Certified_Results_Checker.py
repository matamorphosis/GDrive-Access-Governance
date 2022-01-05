#!/usr/bin/python3
import sqlite3
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def Check(DB_Filename):
    DB_Conn = sqlite3.connect(DB_Filename)
    DB_Cursor = DB_Conn.cursor()
    DB_Cursor.execute("""SELECT * FROM certified_results;""")
    Cert_Results = DB_Cursor.fetchall()

    for Cert_Result in Cert_Results:
        date_time_obj = datetime.strptime(Cert_Result[4], '%Y-%m-%d %H:%M:%S').date()
        today = date.today()
        diff = relativedelta(today, date_time_obj).months
        print(diff)

        if diff >= 6:
            DB_Cursor.execute(f"""DELETE from certified_results where id = "{Cert_Result[0]}";""")
            DB_Conn.executescript(f"""INSERT INTO open_results (id, file_name, trashed, emails, created_at) values ('{Cert_Result[0]}', '{Cert_Result[1]}', '{Cert_Result[2]}', '{Cert_Result[3]}', '{Cert_Result[4]}');""")
            DB_Conn.commit()

if __name__ == "__main__":
    Check("GDriveAGApp.db")