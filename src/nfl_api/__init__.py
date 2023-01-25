import nfl_api.game
import nfl_api.info
import calendar
import debug

def day(year, month, day):
    """
        Return a list of games for a certain day.
    """

    # get the days per month
    daysinmonth = calendar.monthrange(year, month)[1]
    # do not even try to get data if day is too high
    if daysinmonth < day:
        return []
    # get data
    data = nfl_api.game.scoreboard(year, month, day)
    return [nfl_api.game.GameScoreboard(data[x]) for x in data]


def teams():
    """Return list of Info objects for each team"""
    return [nfl_api.info.Info(x) for x in nfl_api.info.team_info()]

def player(playerId):
    """Return an Info object of a player information"""
    return nfl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    restult = nfl_api.game.overview(game_id)
    return nfl_api.game.Overview(restult)


def game_status_info():
    return nfl_api.info.status()


def current_season_info():
    return nfl_api.info.current_season()


def standings():
    try:
        standings, wildcard = nfl_api.info.standings()
        return nfl_api.info.Standings(standings, wildcard)
    except:
        return False

#disabled for NFL
#def playoff(season = ""):
#    return nfl_api.info.Playoff(nfl_api.info.playoff_info(season))

def series_game_record(seriesCode, season):
    return nfl_api.info.series_record(seriesCode, season)
