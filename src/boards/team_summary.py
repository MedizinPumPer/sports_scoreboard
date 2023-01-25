"""
    Show a summary of the favorite team. (previous game, next game, stats,)

"""
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageColor
from rgbmatrix import graphics
import nfl_api
from data.scoreboard import Scoreboard
from data.team import Team
from time import sleep
from utils import convert_date_format, get_file
from renderer.logos import LogoRenderer
import debug



class TeamSummary:
    def __init__(self, data, matrix, sleepEvent):
        '''
            TODO:
                Need to move the Previous/Next game info in the data section. I think loading it in the data section
                and then taking that info here would make sense
        '''
        debug.info("Team Summary Display")
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors

        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('team_summary')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

    def render(self):
        self.matrix.clear()
        for team_id in self.preferred_teams:
            self.team_id = team_id

            team = self.teams_info[team_id]

            team_colors = self.data.config.team_colors
            bg_color = tuple(int(item) for item in ImageColor.getcolor("#" + team.color_main, "RGB"))
            txt_color = tuple(int(item) for item in ImageColor.getcolor("#" + team.color_second, "RGB"))
            prev_game = team.events.prev_event
            next_game = team.events.next_event

            logo_renderer = LogoRenderer(
                self.matrix,
                self.data.config,
                self.layout.logo,
                team,
                'team_summary'
            )

            try:
                if prev_game > 0:
                    prev_game_id = self.teams_info[team_id].events.prev_game
                    prev_game_scoreboard = Scoreboard(nfl_api.overview(prev_game_id), self.data)
                else:
                    prev_game_scoreboard = False

                self.data.network_issues = False
            except ValueError:
                prev_game_scoreboard = False
                self.data.network_issues = True

            try:
                if next_game:
                    next_game_id = self.teams_info[team_id].events.next_event
                    next_game_scoreboard = Scoreboard(nfl_api.overview(next_game_id), self.data)
                else:
                    next_game_scoreboard = False

                self.data.network_issues = False
            except ValueError:
                next_game_scoreboard = False
                self.data.network_issues = True

            stats = team.stats
            im_height = 67 if prev_game > 0 else 46
            team_abbrev = team.abbrev

            i = 0

            if not self.sleepEvent.is_set():
                image = self.draw_team_summary(
                    stats,
                    prev_game_scoreboard,
                    next_game_scoreboard,
                    bg_color,
                    txt_color,
                    im_height
                )
                self.matrix.clear()
                gradient = Image.open(get_file('assets/images/64x32_scoreboard_center_gradient.png'))

                #   For 128x64 use the bigger gradient image.
                if self.matrix.height == 64:
                    gradient = Image.open(get_file('assets/images/128x64_scoreboard_center_gradient.png'))

                logo_renderer.render()
                self.matrix.draw_image((25, 0), gradient, align="center")
                self.matrix.draw_image_layout(
                    self.layout.info,
                    image,
                )
                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

            self.sleepEvent.wait(5)

            # Move the image up until we hit the bottom.
            while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                i -= 1

                self.matrix.clear()

                logo_renderer.render()
                self.matrix.draw_image((25, 0), gradient, align="center")
                self.matrix.draw_image_layout(
                    self.layout.info,
                    image,
                    (0, i)
                )

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                self.sleepEvent.wait(0.3)

            # Show the bottom before we change to the next table.
            self.sleepEvent.wait(5)

    def draw_team_summary(self, stats, prev_game_scoreboard, next_game_scoreboard, bg_color, txt_color, im_height):

        image = Image.new('RGB', (37, im_height))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 6, 26, -1], fill=(int(bg_color[0]), int(bg_color[1]), int(bg_color[2])))

        draw.text((1, 0), "RECORD:".format(), fill=(int(txt_color[0]), int(txt_color[1]), int(txt_color[2])),
                  font=self.font)
        if stats:
            draw.text((0, 7), "GP:{}".format(stats.gamesPlayed), fill=(255, 255, 255),
                      font=self.font)
            draw.text((0, 13), "{}-{}".format(stats.gamesWins, stats.gamesLosses,), fill=(255, 255, 255),
                      font=self.font)
        else:
            draw.text((1, 7), "--------", fill=(200, 200, 200), font=self.font)

        if next_game_scoreboard:
            draw.rectangle([0, 27, 36, 21], fill=(int(bg_color[0]), int(bg_color[1]), int(bg_color[2])))
            draw.text((1, 21), "NEXT GAME:", fill=(int(txt_color[0]), int(txt_color[1]), int(txt_color[2])),
                      font=self.font)

            date = convert_date_format(next_game_scoreboard.date)
            draw.text((0, 28), "{}".format(date.upper()), fill=(255, 255, 255), font=self.font)

            if self.data.status.is_irregular(next_game_scoreboard.status):
                if next_game_scoreboard.status == "Scheduled (Time TBD)":
                    next_game_scoreboard.status = "TBD"
                draw.text((0, 34), "{}".format(next_game_scoreboard.status.upper()), fill=(255, 0, 0), font=self.font)
            else:
                draw.text((0, 34), "{}".format(next_game_scoreboard.start_time), fill=(255, 255, 255), font=self.font)

            if next_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 40), "@ {}".format(next_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                          font=self.font)
            if next_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 40), "VS {}".format(next_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                          font=self.font)
        else:
            draw.text((1, 52), "--------", fill=(200, 200, 200), font=self.font)

        if prev_game_scoreboard:
            draw.rectangle([0, 48, 36, 42], fill=(int(bg_color[0]), int(bg_color[1]), int(bg_color[2])))
            draw.text((1, 42), "LAST GAME:", fill=(int(txt_color[0]), int(txt_color[1]), int(txt_color[2])),
                      font=self.font)

            if prev_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 55), "@ {}".format(prev_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                          font=self.font)
            if prev_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 55), "VS {}".format(prev_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                          font=self.font)

            if self.data.status.is_irregular(prev_game_scoreboard.status):
                draw.text((0, 66), prev_game_scoreboard.status, fill=(255, 0, 0), font=self.font)

            else:
                if prev_game_scoreboard.winning_team == self.team_id:
                    draw.text((0, 66), "W", fill=(50, 255, 50), font=self.font)
                    draw.text((5, 66), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                      prev_game_scoreboard.home_team.goals),
                              fill=(255, 255, 255), font=self.font)

                if prev_game_scoreboard.loosing_team == self.team_id:
                    draw.text((0, 66), "L", fill=(255, 50, 50), font=self.font)
                    draw.text((5, 66), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                      prev_game_scoreboard.home_team.goals),
                              fill=(255, 255, 255), font=self.font)

        #else:
        #   draw.text((1, 27), "--------", fill=(200, 200, 200), font=self.font)
        return image