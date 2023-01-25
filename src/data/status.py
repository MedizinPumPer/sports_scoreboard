from datetime import datetime
from nfl_api import game_status_info, current_season_info
from utils import convert_time
import debug

class Status:
    def __init__(self):
        debug.error("status")
        game_status = game_status_info()['sports'][0]['leagues'][0]
        self.season_info = current_season_info()['leagues'][0]['calendar']
        #self.season_id = self.season_info['value']
        self.Preview = []
        self.Live = []
        self.GameOver = []
        self.Final = []
        self.Irregular = []

        #
        # https://www.espn.com/apis/devcenter/docs/scores.html
        #

        for status in game_status['events']:
            if status['fullStatus']['type']['id'] == "1" or status['fullStatus']['type']['id'] == '7':
                self.Preview.append(status['fullStatus']['type']['description'])
            elif status['fullStatus']['type']['id'] == '2':
                self.Live.append(status['fullStatus']['type']['description'])
            elif status['fullStatus']['type']['id'] == '3':
                self.Final.append(status['fullStatus']['type']['description'])
            elif status['fullStatus']['type']['id'] == '5':
                self.Irregular.append(status['fullStatus']['type']['description'])


    def is_scheduled(self, status):
        return status in self.Preview

    def is_live(self, status):
        return status in self.Live

    def is_game_over(self, status):
        return status in self.GameOver

    def is_final(self, status):
        return status in self.Final

    def is_irregular(self, status):
        return status in self.Irregular

    def is_offseason(self, date):
        try:
            pre_season_startdate = convert_time(datetime.strptime(self.season_info[0]['startDate'], '%Y-%m-%dT%H:%MZ').date())
            pre_season_enddate = convert_time(datetime.strptime(self.season_info[0]['endDate'], '%Y-%m-%dT%H:%MZ').date())
            regular_season_startdate = convert_time(datetime.strptime(self.season_info[1]['startDate'], '%Y-%m-%dT%H:%MZ').date())
            end_of_season = convert_time(datetime.strptime(self.season_info[1]['endDate'], '%Y-%m-%dT%H:%MZ').date())
            return date < regular_season_startdate or date > end_of_season
        except:
            debug.error('The Argument provided for status.is_offseason is missing or not right.')
            return False

    def is_preseason(self, date):
        try:
            pre_season_startdate = convert_time(datetime.strptime(self.season_info[0]['startDate'], '%Y-%m-%dT%H:%MZ').date())
            pre_season_enddate = convert_time(datetime.strptime(self.season_info[0]['endDate'], '%Y-%m-%dT%H:%MZ').date())
            return date < pre_season_startdate or date > pre_season_enddate
        except:
            debug.error('The Argument provided for status.is_preseason is missing or not right.')
            return False



    def is_playoff(self, date, playoff_obj):
        try:
            # Get dates of the planned end of regular season and end of season
            regular_season_enddate = convert_time(datetime.strptime(self.season_info[2]['endDate'], "%Y-%m-%d").date())
            end_of_season = convert_time(datetime.strptime(self.season_info[2]['startDate'], "%Y-%m-%d").date())

            return regular_season_enddate < date <= end_of_season and playoff_obj.rounds
        except TypeError:
            debug.error('The Argument provided for status.is_playoff is missing or not right.')
            return False

    