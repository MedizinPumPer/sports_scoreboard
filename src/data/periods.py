class Periods:
    PLAYOFF = 'P'
    END = 'End'
    FINAL = 'Final'
    ORDINAL = ['Scheduled', '1st', '2nd', '3rd', '4th', 'OT']
    ORDINAL_PLAYOFF = ['Scheduled', '1st', '2nd', '3rd', '4th', 'OT']

    def __init__(self, overview):
        period_info = overview.linescore
        try:
            intermission_info = period_info.type
            #self.is_intermission = intermission_info.inIntermission
            self.intermission_time_remaining = intermission_info.clock
        except AttributeError:
            self.is_intermission = False

        self.gameType = overview.game_type
        try:
            self.number = overview.quarter
        except:
            self.number = 4

        try:
            self.clock = overview.time
        except AttributeError:
            self.clock = '00:00'
        self.get_ordinal()

    def get_ordinal(self):
        if self._is_playoff():
            self.ordinal = Periods.ORDINAL_PLAYOFF[self.number + 1]
        else:
            self.ordinal = Periods.ORDINAL[self.number + 1]

    def _is_playoff(self):
        return self.gameType is self.PLAYOFF
