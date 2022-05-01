# coding=utf-8


# from getpass import getpass

from mysql.connector import connect, Error


class DatabaseController:
    def __init__(self):
        # try to connect to database
        try:
            # try to connect to the database and init connection
            self.connection = connect(
                user="root",  # str(input("[db] enter your username: ")),
                password="casperhere",  # getpass("[db] enter your password: "),
                database="alchemist",  # str(input("[db] enter database name: ")),
            )  # init db connection

            self.cursor = self.connection.cursor(buffered=True)  # init db cursor
        except Error as database_error:
            print(f"[db] an error has occurred: {database_error}")

    async def get_data_execute_query(self, database_query):
        self.cursor.execute(database_query)  # make a query

        back_data = self.cursor.fetchall()  # got data
        self.connection.commit()  # save changes

        return back_data  # return got data

    async def execute_query(self, database_query):
        self.cursor.execute(database_query)  # make a query
        self.connection.commit()  # save changes
