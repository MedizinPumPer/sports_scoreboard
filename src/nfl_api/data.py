import json
import requests
import debug

"""
    TODO:
        Add functions to call single series overview (all the games of a single series) using the NHL record API. 
        https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter="A" and seasonId=20182019
"""

BASE_URL = "https://site.api.espn.com"
BASE_NFL_URL = BASE_URL + '/apis/site/v2/sports/football/nfl'
SCHEDULE_URL = BASE_NFL_URL + '/scoreboard'
TEAM_URL = BASE_NFL_URL + '/teams'
TEAM_URL_DETAIL = TEAM_URL + '/{0}'
TEAM_URL_SCHEDULE = TEAM_URL_DETAIL + '/schedule'
PLAYER_URL = '{0}people/{1}'
#OVERVIEW_URL = BASE_URL + 'game/{0}/feed/live?site=en_nhl'
OVERVIEW_URL = BASE_NFL_URL + '/scoreboard/{}'
STATUS_URL = BASE_URL + '/apis/v2/scoreboard/header?sport=football&league=nfl'
CURRENT_SEASON_URL = BASE_NFL_URL + '/scoreboard'
STANDINGS_URL = BASE_URL + '/apis/standings'
STANDINGS_WILD_CARD = STANDINGS_URL + '/wildCardWithLeaders'
#PLAYOFF_URL = BASE_URL + "tournaments/playoffs?expand=round.series,schedule.game.seriesSummary&season={}"
PLAYOFF_URL = BASE_URL + "/apis/common/v3/sports/football/nfl/statistics/byteam?region=us&lang=en&contentorigin=espn&sort=team.passing.netYardsPerGame%3Adesc&limit=32&season={}}&seasontype=3"
SERIES_RECORD = "https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter='{}' and seasonId={}"
REQUEST_TIMEOUT = 5

TIMEOUT_TESTING = 0.001  # TO DELETE


def get_nfl_schedule():
    try:
        data = requests.get(SCHEDULE_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_nfl_teams():
    try:
        data = requests.get(TEAM_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_nfl_team(teamID):
    try:
        data = requests.get(TEAM_URL_DETAIL.format(teamID), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_nfl_player(playerId):
    try:
        data = requests.get(PLAYER_URL.format(BASE_URL, playerId), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_nfl_overview(game_id):
    try:
        data = requests.get(OVERVIEW_URL.format(game_id), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_nfl_game_status():
    try:
        data = requests.get(STATUS_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_nfl_current_season():
    try:
        data = requests.get(CURRENT_SEASON_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_nfl_standings():
    try:
        data = requests.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_nfl_standings_wildcard():
    try:
        data = requests.get(STANDINGS_WILD_CARD, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

##Disabled for NFL
# def get_nfl_playoff_data(season):
#     try:
#         data = requests.get(PLAYOFF_URL.format(season), timeout=REQUEST_TIMEOUT)
#         return data
#     except requests.exceptions.RequestException as e:
#         raise ValueError(e)

def get_nfl_series_record(seriesCode, season):
    try:
        data = requests.get(SERIES_RECORD.format(seriesCode, season), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

## DEBUGGING DATA (TO DELETE)
def dummie_nfl_overview():
    with open('dummie_nfl_data/overview_reg_final.json') as json_file:
        data = json.load(json_file)
        return data