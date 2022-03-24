from data.team import TeamScore
from data.periods import Periods
from utils import convert_time
from time import sleep
import debug
import nfl_api

"""
    TODO:
        Split the current Scoreboard class into two:
            - scoreboard (subclass of game, only showing minimum data of a game like the status, score, away and home etc...  )
            - game (for the overview, load all the static data like players, away and home teams etc... on init 
            and have methods to refresh the dynamic data like score, goals, penalty etc...)

        This will affect how the Data module init and refresh games. Need to test figure what this change will affect.
"""

def filter_plays(plays, away_id, home_id):
    """
        Take a list of scoring plays and split them into their cooresponding team.
        return two list, one for each team.
    """
    all_plays = plays.allPlays
    scoring_plays = []
    penalty_plays = []
    away_goals = []
    away_penalties  = []
    home_goals = []
    home_penalties = []

    # Filter the scoring plays out of all the plays
    for i in plays.scoringPlays:
        scoring_plays.append(all_plays[i])
    
    # Filter the Penalty plays out of all the plays
    for i in plays.penaltyPlays:
        penalty_plays.append(all_plays[i])

    away_goals = [ x for x in scoring_plays if x['team']['id'] == away_id]
    home_goals = [ x for x in scoring_plays if x['team']['id'] == home_id]
    away_penalties = [ x for x in penalty_plays if x['team']['id'] == away_id]
    home_penalties = [ x for x in penalty_plays if x['team']['id'] == home_id]

    return away_goals, away_penalties, home_goals, home_penalties


def get_goal_players(players_list, roster, opposing_roster):
    """
        Grab the list of players involved in a goal and return their Id except for assists which is a list of Ids
    """
    scorerId = ""
    assistsId = ""
    goalieId = ""
    scorer = {}
    assists = []
    goalie = {}
    
    for player in players_list:

        if player["playerType"] == "Scorer":
            scorerId = player['player']['id']
            scorer["info"] = roster[scorerId]
            scorer["points"] = player['seasonTotal']
        if player["playerType"] == "Assist":
            assistsId = player['player']['id']
            assists.append({"info":roster[assistsId], "points":player['seasonTotal']}) 
        if player["playerType"] == "Goalie":
            goalieId = player['player']['id']
            goalie = opposing_roster[goalieId]

    return {"scorer":scorer, "assists":assists, "goalie":goalie}

def get_penalty_players(players_list, roster):
    
    for p in players_list:
        if p["playerType"] == "PenaltyOn":
            playerId = p['player']['id']
            try:
                return roster[playerId]
            except KeyError:
                return {}

    return {}

class Scoreboard:
    def __init__(self, overview, data):
        time_format = data.config.time_format
        #linescore = overview.linescore


        away_id = overview.away_team_id
        home_id = overview.home_team_id


        away_abbrev = data.teams_info[away_id].abbrev
        #self.away_roster = data.teams_info[away_id].roster

        #home = linescore.competitors[0]
        debug.info(home_id)
        home_abbrev = data.teams_info[home_id].abbrev
        #self.home_roster = data.teams_info[home_id].roster

        away_goal_plays = []
        home_goal_plays = []

        away_penalties = []
        home_penalties = []

        if hasattr(overview,"plays"):
            plays = overview.plays
            away_scoring_plays, away_penalty_play, home_scoring_plays, home_penalty_play = filter_plays(plays,overview.away_team_id,overview.home_team_id)
            
            # Get the Away Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in away_scoring_plays:
                try:
                    players = get_goal_players(play['players'], self.away_roster, self.home_roster)
                    away_goal_plays.append(Goal(play, players))
                except KeyError:
                    debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                    away_goal_plays = []
                    break
            # Get the Home Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in home_scoring_plays:
                try:
                    players = get_goal_players(play['players'], self.home_roster, self.away_roster)
                    home_goal_plays.append(Goal(play,players))
                except KeyError:
                    debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                    home_goal_plays = []
                    break


        self.away_team = TeamScore(away_id, away_abbrev, overview.away_team_name, overview.away_score)
        self.home_team = TeamScore(home_id, home_abbrev, overview.home_team_name, overview.home_score)

        self.date = convert_time(overview.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(overview.game_date).strftime(time_format)
        self.status = overview.status
        self.periods = Periods(overview)


        if data.status.is_final(overview.status) and hasattr(overview, "w_score") and hasattr(overview, "l_score"):
            self.winning_team = overview.w_team
            self.winning_score = overview.w_score
            self.loosing_team = overview.l_team
            self.loosing_score = overview.l_score

    

    def __str__(self):
        output = "<{} {}> {} (G {}, SOG {}) @ {} (G {}, SOG {}); Status: {}; Period : {} {};".format(
            self.__class__.__name__, hex(id(self)),
            self.away_team.name, str(self.away_team.goals), str(self.away_team.shot_on_goal),
            self.home_team.name, str(self.home_team.goals), str(self.home_team.shot_on_goal),
            self.status,
            self.periods.ordinal,
            self.periods.clock
        )
        return output

class Goal:
    def __init__(self, play, players):
        self.scorer = players["scorer"]
        self.assists = players["assists"]
        self.goalie = players["goalie"]
        self.team = play['team']['id']
        self.period = play['about']['ordinalNum']
        self.periodTime = play['about']['periodTime']
        self.strength = play['result']['strength']['name']
        
class Penalty:
    def __init__(self, play, player):
        self.player = player
        self.penaltyType = play['result']['secondaryType']
        self.severity = play['result']['penaltySeverity']
        self.penaltyMinutes = str(play['result']['penaltyMinutes'])
        self.team_id = play['team']['id']
        self.period = play['about']['ordinalNum']
        self.periodTime = play['about']['periodTime']
