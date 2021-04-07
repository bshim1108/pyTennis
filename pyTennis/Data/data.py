import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pyTennis.Data.helpers import Helpers
from pyTennis.Data.sql import SQL
from pyTennis.Data.constants import LEAGUE_START_YEAR, COMPLETE_YEARS, LEAGUE_SPORTSBOOK_URL, BET_TYPES, BET_TYPE_TO_CLASS, BOOKIE_TO_DVS

class UpdateData(object):
    def __init__(self, sql):
        self.sql = sql
        self.helpers = Helpers()

    def update_results_data(self):
        query = """SELECT * FROM RESULTS"""
        sql_data = self.sql.select_data(query)

        driver = ChromeDriverManager().install()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=5000,5000")
        browser = webdriver.Chrome(driver, options=chrome_options)

        current_year = datetime.now().year
        for league in LEAGUES:
            for year in range(LEAGUE_START_YEAR[league], current_year+1):
                if year in COMPLETE_YEARS:
                    continue

                league_url = LEAGUE_URL_TEMPLATE[league].format(str(year), str(year)) + YEAR_URL_SUFFIX[year]
                league_data = pd.read_excel(league_url)

                id = 0
                if not sql_data.empty:
                    id = sql_data['ID'].max() + 1
                    filtered_sql_data = sql_data.loc[
                        (sql_data['LEAGUE'] == league) &
                        (sql_data['DATE'].dt.year == year)
                        ]
                    if not filtered_sql_data.empty:
                        max_date = filtered_sql_data['DATE'].max()
                        league_data = league_data.loc[league_data['DATE'] > max_date]

                league_data = league_data.sort_values(by='DATE')
                for date, daily_data in league_data.groupby('DATE'):
                    print(date)
                    formatted_date = datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d').replace('-', '')

                    odds_data = pd.DataFrame(
                        columns=['DATE', 'WINNER', 'LOSER', 'BOOKIE', 'W_MONEYLINE', 'L_MONEYLINE', 'W_POINTSPREAD', 'TOTAL']
                    )
                    for bet_type in BET_TYPES:
                        URL = 'https://www.sportsbookreview.com/betting-odds/{}/{}/?date={}'.format(LEAGUE_SPORTSBOOK_URL[league], bet_type, formatted_date)

                        browser.get(URL)
                        time.sleep(3.000)
                        soup = BeautifulSoup(browser.page_source, 'html.parser')

                        light_games = soup.find_all('div', class_='eventMarketGridContainer-3QipG neverWrap-lD_Yj compact-2-t2Y')
                        dark_games = soup.find_all('div', class_='eventMarketGridContainer-3QipG neverWrap-lD_Yj compact-2-t2Y darkBackground-LTnfM')
                        games = light_games + dark_games
                        for game in games:
                            players = game.find_all('span', class_='participantBox-3ar9Y')
                            winner = game.find('i', class_='actionIcon-3v50- sbr-icon-caret-left winnerIcon-1QZdE smallFont-W5dE8').parent.parent.text
                            
                            if winner == players[0].text:
                                winner_index = 0
                                loser = players[1].text
                                loser_index = 1
                            else:
                                winner_index = 1
                                loser = players[0].text
                                loser_index = 0
                                
                            winner_name = clean_name(winner)
                            loser_name = clean_name(loser)
                                
                            for bookie in BOOKIE_TO_DVS:
                                if bet_type == 'money-line':
                                    temp = pd.Series(
                                        [date, winner_name, loser_name, bookie, np.nan, np.nan, np.nan, np.nan],
                                        index=['DATE', 'WINNER', 'LOSER', 'BOOKIE', 'W_MONEYLINE', 'L_MONEYLINE', 'W_POINTSPREAD', 'TOTAL']
                                        )
                                    odds_data = odds_data.append(temp, ignore_index=True)
                                
                                bookie_info = game.find(
                                    'section',
                                    {'class': 'numbersContainer-29L5c', 'data-vertical-sbid': BOOKIE_TO_DVS[bookie]}
                                )

                                odds = bookie_info.find_all(
                                    'span',
                                    {'class': BET_TYPE_TO_CLASS[bet_type]}
                                )

                                if len(odds) == 0:
                                    odds = [np,nan, np.nan]
                                else:
                                    odds = [odds[0].text.replace('½', '.5').replace('-½', '-.5'), odds[1].text.replace('½', '.5').replace('-½', '-.5')]
                                    
                                if bet_type == 'money-line':
                                    w_moneyline = odds[winner_index]
                                    l_moneyline = odds[loser_index]
                                        
                                    odds_data.loc[
                                        (odds_data['DATE'] == date) &
                                        (odds_data['WINNER'] == winner_name) &
                                        (odds_data['LOSER'] == loser_name) &
                                        (odds_data['BOOKIE'] == bookie),
                                        'W_MONEYLINE'
                                    ] = w_moneyline
                                    
                                    odds_data.loc[
                                        (odds_data['DATE'] == date) &
                                        (odds_data['WINNER'] == winner_name) &
                                        (odds_data['LOSER'] == loser_name) &
                                        (odds_data['BOOKIE'] == bookie),
                                        'L_MONEYLINE'
                                    ] = l_moneyline
                                    
                                elif bet_type == 'pointspread':
                                    w_pointspread = odds[winner_index]
                                        
                                    odds_data.loc[
                                        (odds_data['DATE'] == date) &
                                        (odds_data['WINNER'] == winner_name) &
                                        (odds_data['LOSER'] == loser_name) &
                                        (odds_data['BOOKIE'] == bookie),
                                        'W_POINTSPREAD'
                                    ] = w_pointspread
                                    
                                else:
                                    odds_data.loc[
                                        (odds_data['DATE'] == date) &
                                        (odds_data['WINNER'] == winner_name) &
                                        (odds_data['LOSER'] == loser_name) &
                                        (odds_data['BOOKIE'] == bookie),
                                        'TOTAL'
                                    ] = odds[0]
                    
                    for _, row in daily_data.iterrows():
                        result = (id, league, row['Location'], row['Tournament'], date,
                                row['Series'], row['Court'], row['Surface'], row['Round'],
                                row['Best of'], row['Winner'], row['Loser'])

                        details = (id, row['WRank'], row['LRank'], row['WPts'], row['LPts'],
                                row['W1'], row['W2'], row['W3'], row['W4'], row['W5'],
                                row['L1'], row['L2'], row['L3'], row['L4'], row['L5'],
                                row['WSets'], row['LSets'], row['Comment'])

                        game_odds = odds_data.loc[
                            (odds_data['DATE'] == date) &
                            (odds_data['WINNER'] == row['Winner']) &
                            (odds_data['LOSER'] == row['Loser'])
                            ]

                        odds_list = []
                        for bookie, book_odds in game_odds.groupby('BOOKIE'):
                            odds.append((id, bookie, book_odds['W_MONEYLINE'], book_odds['L_MONEYLINE'], book_odds['W_POINTSPREAD'], book_odds['TOTAL']))

                        self.sql.insert_result(result)
                        self.sql.insert_details(details)
                        for odds in odds_list:
                            self.sql.insert_odds(odds)

                        id += 1

                    query = """SELECT * FROM RESULTS"""
                    sql_data = self.sql.select_data(query)
                    print(sql_data)

class QueryData(object):
    def __init__(self, update=False):
        self.sql = SQL()
        self.sql.create_connection()
        self.update = update
        self.update_data = UpdateData(sql=self.sql)

    def query_results_data(self):
        if self.update:
            self.update_data.update_game_data()
        query = """SELECT * FROM RESULTS"""
        sql_data = self.sql.select_data(query)

        cutoff = datetime.now()
        if cutoff.hour < 8:
            cutoff = cutoff - timedelta(days=1)
        sql_data = sql_data.loc[sql_data['DATE'] < cutoff.strftime("%Y-%m-%d")]

        return sql_data

if __name__ == "__main__":
    query_data = QueryData(update=True)
    data = query_data.query_results_data()
    print(data)