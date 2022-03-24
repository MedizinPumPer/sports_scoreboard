"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from nfl_api.utils import convert_time
import nfl_api.data
import nfl_api.object


def scoreboard(year, month, day):
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = nfl_api.data.get_nfl_schedule()
    if not data:
        return data
    parsed = data.json()

    if parsed["events"]:
        games_data = parsed["events"]
        games = {}
        for game in games_data:
            game_id = game['id']
            season = game['season']['year']
            game_type = game['season']['type']
            game_date = game['date']

            if game['competitions'][0]['competitors'][0]['homeAway'] == 'home':
                home_team_id = int(game['competitions'][0]['competitors'][1]['id'])
                home_team_name = game['competitions'][0]['competitors'][1]['team']['shortDisplayName']
                home_score = game['competitions'][0]['competitors'][1]['score']
                away_team_id = int(game['competitions'][0]['competitors'][0]['id'])
                away_team_name = game['competitions'][0]['competitors'][0]['team']['shortDisplayName']
                away_score = game['competitions'][0]['competitors'][0]['score']
            else:
                home_team_id = int(game['competitions'][0]['competitors'][0]['id'])
                home_team_name = game['competitions'][0]['competitors'][0]['team']['shortDisplayName']
                home_score = game['competitions'][0]['competitors'][0]['score']
                away_team_id = int(game['competitions'][0]['competitors'][1]['id'])
                away_team_name = game['competitions'][0]['competitors'][1]['team']['shortDisplayName']
                away_score = game['competitions'][0]['competitors'][1]['score']
            status = game['competitions'][0]['status']['type']['description']
            status_code = game['competitions'][0]['status']['type']['id']
            status_abstract_state = game['competitions'][0]['status']['type']['state']
            linescore = game['competitions'][0]['status']

            output = {
                'game_id': game_id,
                'season': season,
                'game_type': game_type,
                'game_date': game_date,
                'home_team_id': home_team_id,
                'home_team_name': home_team_name,
                'away_team_id': away_team_id,
                'away_team_name': away_team_name,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                'status_code': status_code,
                'status_abstract_state': status_abstract_state,
                # All the linescore information (goals, sog, periods etc...)
                'linescore': linescore,
            }

            # put this dictionary into the larger dictionary
            games[game_id] = output
        return games
    else:
        return []


class GameScoreboard(object):

    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                obj = nfl_api.object.Object(data[x])
                setattr(self, x, obj)

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})').format(self)

    def __repr__(self):
        return self.__str__()


def overview(game_id):
    #data = nfl_api.data.get_overview(game_id)
    data = nfl_api.data.get_nfl_schedule()
    parsedData = data.json()
    output = []
    i = 0
    for parsed in parsedData['events']:
        if parsedData['id'] in game_id:
            # Top level information (General)
            id = parsed['id']
            time_stamp = parsed['date']
            game_type = parsed['season']['type']
            status = parsed['status']['type']['description']
            status_code = parsed['status']['type']['id']
            status_abstract_state = parsed['status']['type']['name']
            game_date = parsed['date']

            # Sub level information (Details)
            plays = parsed['liveData']['plays']
            linescore = parsed['competitions'][0].get('situation', {})
            boxscore = parsed['competitions'][0].get('situation', {})
            away_score = linescore['competitions'][0].get('situation', {})
            home_score = linescore['competitions'][0]['competitors'][0]['score']

            # Team details
            away_team_id = parsed['competitions'][0]['competitors'][1]['team']['id']
            away_team_name = parsed['competitions'][0]['competitors'][1]['team']['shortDisplayName']
            away_team_abrev = parsed['competitions'][0]['competitors'][1]['team']['abbreviation']
            home_team_id = parsed['competitions'][0]['competitors'][0]['team']['id']
            home_team_name = parsed['competitions'][0]['competitors'][0]['team']['shortDisplayName']
            home_team_abrev = parsed['competitions'][0]['competitors'][0]['team']['abbreviation']

            # 3 stars (if any available)
            try:
                first_star = parsed['liveData']['decisions']['firstStar']
                second_star = parsed['liveData']['decisions']['secondStar']
                third_star = parsed['liveData']['decisions']['thirdStar']

            except:
                first_star = {}
                second_star = {}
                third_star = {}

            output = {
                'id': id,  # ID of the game
                'time_stamp': time_stamp,  # Last time the data was refreshed (UTC)
                # Type of game ("R" for Regular season, "P" for Post season or playoff)
                'game_type': game_type,
                'status': status,   # Status of the game.
                'status_code': status_code,
                'status_abstract_state': status_abstract_state,
                'game_date': game_date,  # Date and time of the game
                'away_team_id': away_team_id,  # ID of the Away team
                'away_team_name': away_team_name,  # Away team name
                'away_team_abrev': away_team_abrev,  # Away team name abbreviation
                'home_team_id': home_team_id,  # ID of the Home team
                'home_team_name': home_team_name,  # Home team name
                'home_team_abrev': home_team_abrev,  # Home team name abbreviation
                # All the linescore information (goals, sog, periods etc...)
                'linescore': linescore,
                # All the boxscore information (players, onice, team's stats, penalty box etc...)
                'boxscore': boxscore,
                'away_score': away_score,  # Away team goals
                'home_score': home_score,  # Home team goals
                'plays': plays,  # Dictionary of all the plays of the game.
                'first_star': first_star,
                'second_star': second_star,
                'third_star': third_star
            }

    return output


class Overview(object):
    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                obj = nfl_api.object.Object(data[x])
                setattr(self, x, obj)
        
        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.w_score = self.home_score
            self.l_team = self.away_team_id
            self.l_score = self.away_score
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.w_score = self.away_score
            self.l_team = self.home_team_id
            self.l_score = self.home_score