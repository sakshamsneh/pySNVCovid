import sqlite3


class database():
    def init(self):
        try:
            sqliteConnection = sqlite3.connect('data.db')
            cursor = sqliteConnection.cursor()
            print("Connected")

            sqlite_select_Query = "select sqlite_version();"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            print("SQLite Database Version is: ", record)
            cursor.close()

        except sqlite3.Error as error:
            print("Error", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("Closed")
