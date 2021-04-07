LEAGUES = ['ATP', 'WTA']

LEAGUE_START_YEAR = {
    'ATP': 2001
    'WTA': 2007
}

LEAGUE_URL_TEMPLATE = {
    'ATP': 'http://www.tennis-data.co.uk/{}/{}'
    'WTA': 'http://www.tennis-data.co.uk/{}w/{}'
}

YEAR_URL_SUFFIX = {
    2001: '.xls',
    2002: '.xls',
    2003: '.xls',
    2004: '.xls',
    2005: '.xls',
    2006: '.xls',
    2007: '.xls',
    2008: '.xls',
    2009: '.xls',
    2010: '.xls',
    2011: '.xls',
    2012: '.xls',
    2013: '.xlsx',
    2014: '.xlsx',
    2015: '.xlsx',
    2016: '.xlsx',
    2017: '.xlsx',
    2018: '.xlsx',
    2019: '.xlsx',
    2020: '.xlsx',
    2021: '.xlsx',
    2022: '.xlsx',
}

LEAGUE_SPORTSBOOK_URL = {
    'ATP': 'atp-tennis',
    'WTA': 'wta-tennis'
}

BET_TYPES = ['money-line', 'pointspread', 'totals']

BET_TYPE_TO_CLASS = {
    'money-line': '',
    'pointspread': 'adjust-1uDgI',
    'totals': 'adjust-1uDgI'    
}

BOOKIE_TO_DVS = {
    'Bookmaker': '93',
    'Pinnacle': '238'
}

COMPLETE_YEARS = {}