import nfl_api.data
from nfl_api.object import Object, MultiLevelObject
from nameparser import HumanName
import debug


def team_info():
    """
        Returns a list of team information dictionaries
    """
    res = nfl_api.data.get_nfl_teams()
    res = res.json()

    teams = []

    for g in res['sports'][0]['leagues'][0]['teams']:
        try:
            team = {
                'team_id': int(g['team']['id']),
                'name': g['team']['displayName'],
                'abbrev': g['team']['abbreviation'],
                'team_name': g['team']['name'],
                'location_name': g['team']['location'],
                'short_name': g['team']['shortDisplayName'],
                'longname': g['team']['displayName'],
                'color_main': g['team']['color'],
                'color_second': g['team']['alternateColor'],
                'stats': g['team']['record']['items'][0]['stats'],
                'stats''gamesPlayed': g['team']['record']['items'][0]['stats'],
                'logo': g['team']['logos'][0]['href']
            }
            teams.append(team)
        except:
            debug.error("Missing data in current team info")
    return teams


def player_info(playerId):
    data = nfl_api.data.get_nfl_player(playerId)
    parsed = data.json()
    player = parsed["people"][0]

    return MultiLevelObject(player)


def status():
    data = nfl_api.data.get_nfl_game_status().json()
    return data


def current_season():
    data = nfl_api.data.get_nfl_current_season().json()
    return data


##Disabled for NFL
# def playoff_info(season):
#     data = nfl_api.data.get_playoff_data(season)
#     parsed = data.json()
#     season = parsed["requestedSeason"]
#     output = {'requestedSeason': season}
#     try:
#         playoff_rounds = parsed["rounds"]
#         rounds = {}
#         for r in range(len(playoff_rounds)):
#             rounds[str(playoff_rounds[r]["number"])] = MultiLevelObject(playoff_rounds[r])
#
#         output['rounds'] = rounds
#     except KeyError:
#         debug.error("No data for {} Playoff".format(season))
#         output['rounds'] = False
#
#     try:
#         default_round = parsed["defaultRound"]
#         output['default_round'] = default_round
#     except KeyError:
#         debug.error("No default round for {} Playoff.".format(season))
#         default_round = 1
#         output['default_round'] = default_round
#
#     return output

def series_record(seriesCode, season):
    data = data = nfl_api.data.get_nfl_series_record(seriesCode, season)
    parsed = data.json()
    return parsed["data"]


def standings():
    standing_records = {}

    wildcard_records = {
        'eastern': [],
        'western': []
    }

    data = nfl_api.data.get_nfl_standings().json()
    divisions = data['records']

    data_wildcard = nfl_api.data.get_nfl_standings_wildcard().json()
    try:
        wildcard = data_wildcard['records']
        for division in range(len(divisions)):
            team_records = divisions[division]['teamRecords']
            division_full_name = divisions[division]['division']['name'].split()
            division_name = division_full_name[-1]
            conference_name = divisions[division]['conference']['name']

            for team in range(len(team_records)):
                team_id = team_records[team]['team']['id']
                team_name = team_records[team]['team']['name']
                team_records[team].pop('team')
                standing_records[team_id] = {
                    'division': division_name,
                    'conference': conference_name,
                    'team_name': team_name,
                    'team_id': team_id
                }
                for key, value in team_records[team].items():
                    standing_records[team_id][key] = value

        for record in wildcard:
            if record['conference']['name'] == 'Eastern':
                wildcard_records['eastern'].append(record)
            elif record['conference']['name'] == 'Western':
                wildcard_records['western'].append(record)

        return standing_records, wildcard_records
    except KeyError:
        return False, False


class Standings(object):
    """
        Object containing all the standings data per team.

        Contains functions to return a dictionary of the data reorganised to represent
        different type of Standings.

    """

    def __init__(self, records, wildcard):
        self.data = records
        self.data_wildcard = wildcard
        self.get_conference()
        self.get_division()
        self.get_wild_card()

    def get_conference(self):
        eastern, western = self.sort_conference(self.data)
        self.by_conference = nfl_api.info.Conference(eastern, western)

    def get_division(self):
        metropolitan, atlantic, central, pacific = self.sort_division(self.data)
        self.by_division = nfl_api.info.Division(metropolitan, atlantic, central, pacific)

    def get_wild_card(self):
        """
            This function take the wildcard data from the API and turn them into objects.
            TODO:
                the way I wrote this function is not pythonic at all (but works). Need to rewrite this part.
        """
        conferences_data = self.data_wildcard
        eastern = []
        western = []
        for conference in conferences_data:
            """ Reset variables """
            metropolitan = []
            atlantic = []
            central = []
            pacific = []
            wild_card = []
            for record in conferences_data[conference]:
                if record['standingsType'] == "wildCard":
                    wild_card = record['teamRecords']
                elif record['standingsType'] == "divisionLeaders":
                    if record['division']['name'] == "Metropolitan":
                        metropolitan = record
                    elif record['division']['name'] == "Atlantic":
                        atlantic = record
                    elif record['division']['name'] == "Central":
                        central = record
                    elif record['division']['name'] == "Pacific":
                        pacific = record

            division = nfl_api.info.Division(metropolitan, atlantic, central, pacific)

            if conference == 'eastern' and wild_card and division:
                eastern = nfl_api.info.Wildcard(wild_card, division)
            elif conference == 'western':
                western = nfl_api.info.Wildcard(wild_card, division)

        self.by_wildcard = nfl_api.info.Conference(eastern, western)

    def _league(self):
        pass

    @staticmethod
    def sort_conference(data):
        eastern = []
        western = []
        for item in data:
            if data[item]['conference'] == 'Eastern':
                eastern.append(data[item])

            elif data[item]['conference'] == 'Western':
                western.append(data[item])

        eastern = sorted(eastern, key=lambda i: int(i['conferenceRank']))
        western = sorted(western, key=lambda i: int(i['conferenceRank']))
        return eastern, western

    @staticmethod
    def sort_division(data):
        metropolitan = []
        atlantic = []
        central = []
        pacific = []

        for item in data:
            if data[item]['division'] == 'Metropolitan':
                metropolitan.append(data[item])

            elif data[item]['division'] == 'Atlantic':
                atlantic.append(data[item])

            elif data[item]['division'] == 'Central':
                central.append(data[item])

            elif data[item]['division'] == 'Pacific':
                pacific.append(data[item])

        metropolitan = sorted(metropolitan, key=lambda i: int(i['conferenceRank']))
        atlantic = sorted(atlantic, key=lambda i: int(i['conferenceRank']))
        central = sorted(central, key=lambda i: int(i['conferenceRank']))
        pacific = sorted(pacific, key=lambda i: int(i['conferenceRank']))

        return metropolitan, atlantic, central, pacific


class Conference:
    def __init__(self, east, west):
        if east:
            self.eastern = east
        if west:
            self.western = west


class Division:
    def __init__(self, met, atl, cen, pac):
        if met:
            self.metropolitan = met
        if atl:
            self.atlantic = atl
        if cen:
            self.central = cen
        if pac:
            self.pacific = pac


class Wildcard:
    def __init__(self, wild, div):
        self.wild_card = wild
        self.division_leaders = div


class Playoff():
    def __init__(self, data):
        self.season = data['season']
        self.default_round = data['default_round']
        self.rounds = data['rounds']

    def __str__(self):
        return (f"Season: {self.season}, Current round: {self.default_round}")

    def __repr__(self):
        return self.__str__()


class Info(nfl_api.object.Object):
    pass
