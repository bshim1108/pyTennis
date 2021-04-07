import sqlite3
from sqlite3 import Error
import pandas as pd


class SQL(object):
    def __init__(self, db_file=r"/Users/brandonshimiaie/Projects/pyTennis/sqlite/db/tennis.db"):
        self.db_file = db_file
        self.conn = None

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def create_connection(self):
        try:
            print(self.db_file)
            self.conn = sqlite3.connect(self.db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)

    def excecute(self, sql_command, values=None):
        if self.conn is None:
            print('Connection not established')
            return
        try:
            c = self.conn.cursor()
            if values is None:
                c.execute(sql_command)
            else:
                c.execute(sql_command, values)
            self.conn.commit()
            return c.fetchall()
        except Error as e:
            print(e)

    def create_tables(self):
        sql_create_results_table = """CREATE TABLE IF NOT EXISTS RESULTS (
                                    ID text PRIMARY KEY,
                                    LEAGUE text NOT NULL,
                                    LOCATION text NOT NULL,
                                    TOURNAMENT text NOT NULL,
                                    DATE text NOT NULL,
                                    SERIES text NOT NULL,
                                    COURT text NOT NULL,
                                    SURFACE text NOT NULL,
                                    ROUND text NOT NULL,
                                    BEST_OF integer NOT NULL,
                                    WINNER text NOT NULL,
                                    LOSER text NOT NULL
                                );"""
        self.excecute(sql_create_results_table)

        sql_create_details_table = """CREATE TABLE IF NOT EXISTS DETAILS (
                                    ID text PRIMARY KEY,
                                    WRANK integer NOT NULL,
                                    LRANK integer NOT NULL,
                                    WPTS integer NOT NULL,
                                    LPTS integer NOT NULL,
                                    W1 integer NOT NULL,
                                    W2 integer NOT NULL,
                                    W3 integer NOT NULL,
                                    W4 integer NOT NULL,
                                    W5 integer NOT NULL,
                                    L1 integer NOT NULL,
                                    L2 integer NOT NULL,
                                    L3 integer NOT NULL,
                                    L4 integer NOT NULL,
                                    L5 integer NOT NULL,
                                    WSETS text NOT NULL,
                                    LSETS text NOT NULL,
                                    COMMENT text NOT NULL
                                );"""
        self.excecute(sql_create_details_table)

        sql_create_odds_table = """CREATE TABLE IF NOT EXISTS ODDS (
                                    ID text PRIMARY KEY,
                                    BOOKIE text NOT NULL,
                                    W_MONEYLINE integer NOT NULL,
                                    L_MONEYLINE integer NOT NULL,
                                    W_POINTSPREAD real NOT NULL,
                                    TOTAL real NOT NULL
                                );"""
        self.excecute(sql_create_odds_table)

    def insert_result(self, result):
        sql_result = """INSERT INTO RESULTS(ID, LEAGUE, LOCATION, TOURNAMENT, DATE, SERIES, COURT,
                                        SURFACE, ROUND, BEST_OF, WINNER, LOSER)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_result, result)

    def insert_details(self, details):
        sql_details = """INSERT INTO DETAILS(ID, WRANK, LRANK, WPTS, LPTS, W1, W2, W3, W4, W5,
                                        L1, L2, L3, L4, L5, WSETS, LSETS, COMMENT)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_details, details)

    def insert_odds(self, details):
        sql_details = """INSERT INTO DETAILS(ID, BOOKIE, W_MONEYLINE, L_MONEYLINE, W_POINTSPREAD, TOTAL)
                        VALUES(?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_details, details)

    def select_data(self, query):
        return pd.read_sql_query(query, self.conn)

if __name__ == "__main__":
    sql = SQL()
    sql.create_connection()
    sql.create_tables()