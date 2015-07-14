import csv
import copy
import params
import player


class Team:
    def __init__(self, team_name, away, team_dict, in_nl_park):
        # players: a list of Player objects
        # lineup: a dictionary mapping tuple (order, position) to player_name string
        self.name = team_name
        self.away = away
        self.in_nl_park = in_nl_park
        self.pitchers = self.parse_players("pitchers", team_dict["pitchers"])
        self.hitters = self.parse_players("hitters", team_dict["hitters"])
        self.over_under = self.parse_ou(team_dict["hitters"])
        self.pitcher_id = self.initialize_pitcher_id()
        self.starting_pitcher = self.fetch_player_by_id(self.pitcher_id)
        self.winning_pitcher_id = None
        self.batting_order = self.get_batting_order()
        self.defensive_alignment = self.get_defensive_alignment()

    def set_winning_pitcher(self):
        self.winning_pitcher_id = self.pitcher_id

    def unset_winning_pitcher(self):
        self.winning_pitcher_id = None

    def add_setting(self, setting):
        self.setting = setting
        for player in (self.hitters+self.pitchers):
            player.setting = setting
            player.set_player_factors()
        return None

    def parse_players(self, hop, players_dict):
        players = list()
        for pid in players_dict:
            if hop == "hitters":
                players.append(player.Hitter(pid, players_dict[pid], self.name))
            elif hop == "pitchers":
                if players_dict[pid]["starting"]:
                    temp_dict = self.get_bullpen_temp_dict(players_dict, pid)
                    players.append(copy.deepcopy(player.Pitcher(pid, players_dict[pid], self.name, temp_dict)))
                    players.append(copy.deepcopy(player.Pitcher(-2, temp_dict, self.name, players_dict[pid], name=(self.name+ " bullpen"))))
        if hop == "hitters" and (self.in_nl_park):
            players.append(copy.deepcopy(player.Hitter(-1, params.default_pitchers_hitting_dict, self.name)))
        return sorted(players)

    def get_bullpen_temp_dict(self, players_dict, sp_pid):
        # ['CGSO', '1B', 'name', '2B', 'BS', '3B', 'HLD', 'salary', 'HBP', 'starting', 'SV', 'CG', 'BB', 'positions', 'HR', 'IP', 'W', 'L', 'K', 'QS', 'NH', 'R', 'O', 'OBA', 'fppg', 'ER']
        ret = {"starting": False, "salary": 0, "positions": [], "fppg": 0.0}
        # print(self.name)
        for pid in players_dict:
            if players_dict[pid]["starting"]:
                # for k in sorted(players_dict[pid].keys()):
                #     print(k + ": " + str(players_dict[pid][k]))
                continue
            for stat in params.outcomes+["IP", "ER", "CG", "W", "NH", "CGSO"]:
                if stat not in ret:
                    ret[stat] = 0.0
                ret[stat] += players_dict[pid][stat]
        ret["O"] = ret["IP"] * 3.0 - ret["K"]
        # print("------------------")
        # for k in sorted(ret.keys()):
        #     print(k + ": " + str(ret[k]))
        # print("------------------")
        # print("------------------")
        batters_faced = sum(ret[s] for s in params.pa_sum_stats)
        return ret

    """
    right now: EV[SP's stat i]*EV[SP's batters faced] + EV[BP's stat i]*EV[BP's batters faced]
            should equal sum over of all hitters: EV[H's stat i]*EV[H's stat i]

    currently this is true, by consistency mandate.

    however, EV[SP's stat i] * EV[SP's batters faced] should also equal:
            sum over all H: EV[H faces SP] * EV[H's stat i against SP]

    and also: EV[BP's stat i] * EV[BP's batters faced] should also equal:
            sum over all H: EV[H faces BP] * EV[H's stat i against BP]

    how to do this?
    solution: look at EV[SP's batters faced] and EV[BP's batters faced].
    compute a SP factor set and a BP factor set, which influences hitters'
    probabilities.

    So if BP is expected to:
    face 12 batters, give up 0.5 HR, 1.0 1B, get 3Ks, ... etc. ...
    and SP is expected to:
    face 28 batters, give up 0.5 HR, 3.0 1B, get 7Ks, ... etc. ...

    Then we should multiply each hitter's stats by a factor for SP
    and a factor for BP

    hitter expected to get 1.5 singles, 1.5 Ks 1 BB and 1 out...

    then of those 1.5 1B, we should expect 75 pct to come from SP...
    so multiply this 1.5 1B by 0.75, divide by (28/40) and divide by E[PA]

    or simply: his normal rate * pct of SP giving up stat / (pct of SP's batters faced)

    so for each pitcher, store these numbers:
    -- expected pct of each stat given up
    -- expected pct of total batters faced

    exp pct of stat given up = amt pitcher gives up stat / (amt pitcher gives up stat + amt comp gives up stat)
    factor[stat] = (amt pitcher gets stat / exp batters pitcher faces) / ((amt pitcher + comp gives up stat) / (amt pitcher + comp  batters faced))

    """

    def parse_ou(self, hitters_dict):
        odds_line = "over_under"
        for h in hitters_dict:
            if hitters_dict[h][odds_line]:
                line = hitters_dict[h][odds_line]
                return line
        return False

    def get_batting_order(self):
        # returns a dictionary of Player objects {order: Player}
        batting_order_dict = dict()
        players_in_batting_order = [p for p in self.hitters if p.batting_order]
        if len(players_in_batting_order) != params.num_hitters_in_lineup:
            print(self.name + " has " + str(len(players_in_batting_order)) + " players in batting order")
            quit()
        players_by_batting_order = sorted(players_in_batting_order, key=lambda k: k.batting_order)
        for i,p in enumerate(players_by_batting_order):
            batting_order_dict[i+1] = p
        return batting_order_dict

    def compute_lineup_points(self):
        self.lineup_points = sum(self.batting_order[p].points for p in self.batting_order if p != params.num_hitters_in_lineup)
        return None


    def add_stat(self, player_id, stat, n=1.0):
        for p in self.hitters+self.pitchers:
            if p.player_id == player_id:
                p.stats[stat] += n
                return
        print("NEVER ADDS STAT")
        return None

    def fetch_player_by_id(self, player_id):
        for p in (self.hitters+self.pitchers):
            if p.player_id == player_id:
                return p
        return None

    def initialize_pitcher_id(self):
        for p in self.pitchers:
            if p.pitching:
                return p.player_id
        print("there is no current pitcher!")
        return False

    def get_defensive_alignment(self):
        # returns a dictionary {position: Player}
        return dict()

    def __str__(self):
        ret = "team: " + self.name
        ret += "batting_order:\n"
        for bo in self.batting_order:
            ret += str(self.batting_order[bo])
            ret += "---------"
        return ret


