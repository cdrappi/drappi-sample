import csv, copy
import params, misc, dirs

class Player:
    def __init__(self, player_id, player_dict, team, name=False):
        self.player_id = player_id
        self.name = name if name else player_dict["name"]
        self.team = team
        self.salary = player_dict["salary"]
        self.positions = player_dict["positions"]
        self.fppg = player_dict["fppg"]
        # self.tuple_id = self.get_tuple_id()
        self.long_id = self.get_long_id()
        return None
    def is_eligible(self, position):
        if position == "P" and any(p in self.positions for p in ("SP","RP")):
            print("why do we have an SP or RP?")
            return True
        return position in self.positions
    def __gt__(self, p2):
        return self.player_id > p2.player_id
    def __eq__(self, p2):
        return self.player_id == p2.player_id and self.name == p2.name
    def __ne__(self, player2):
        return not self.__eq__(player2)
    def __hash__(self):
        return self.salary
    def __str__(self):
        ret =  ("id: " + str(self.player_id)+"\n")
        ret += ("name: " + self.name+"\n")
        ret += ("salary: " + str(self.salary)+"\n")
        ret += ("positions: " + str(self.positions)+"\n")
        return ret

    def set_player_factors(self):
        self.player_factors = dict()
        self.player_factors["salary"] = self.salary
        self.player_factors["gametime"] = self.setting.gametime
        self.player_factors["fppg"] = self.fppg
        return None

    def get_tuple_id(self):
        return self.name # (self.player_id, self.name, self.team, "/".join(sorted(self.positions)))
    
    def get_long_id(self):
        return " -- ".join([str(self.player_id), self.name, self.team, "/".join(sorted(self.positions))])

class Pitcher(Player):
    def __init__(self, player_id, player_dict, team, comp_dict, name=False):
        Player.__init__(self, player_id, player_dict, team, name=name)
        self.pitching = self.initialize_pitching(player_dict)
        self.monster_stats = self.get_monster_stats(player_dict)
        self.goose_comp_factors = self.get_goose_comp_factors(self.monster_stats, comp_dict)
        self.init_horse_factors(player_dict)
        self.stats = {st: 0.0 for st in params.draftkings_pitchers_scoring}
        self.pitch_count = 0
        return None

    def initialize_pitching(self, player_dict):
        return player_dict["starting"]

    def get_goose_comp_factors(self, player_dict, comp_dict):
        goose_comp_factors = dict()
        pitcher_bf = sum(player_dict[s] for s in params.pa_sum_stats)
        comp_bf = sum(comp_dict[s] for s in params.pa_sum_stats)
        tot_bf = pitcher_bf + comp_bf
        pitcher_frac = pitcher_bf/tot_bf
        
        for stat in params.outcomes:
            tot_stat = player_dict[stat]+comp_dict[stat]
            if tot_stat == 0:
                goose_comp_factors[stat] = 0
            else:
                goose_comp_factors[stat] = (player_dict[stat]) / (pitcher_frac*tot_stat)
        
        return goose_comp_factors

    def compute_points(self, wp=None):
        if self.stats["IP"] >= 9 and self.stats["IP"] == int(self.stats["IP"]):
            self.stats["CG"] = 1
            if self.stats["ER"] == 0:
                self.stats["CGSO"] = 1
            if sum(self.stats[ht] for ht in ["1B", "2B", "3B", "HR"]) == 0:
                self.stats["NH"] = 1
        if self.player_id == wp:
            self.stats["W"] = 1
        self.points = sum(self.stats[s] * params.draftkings_pitchers_scoring[s] for s in self.stats)
        return None

    def get_monster_stats(self,player_dict):
        monster_stats = dict()
        for s in params.pitcher_ev_stats:
            monster_stats[s] = player_dict[s]
        monster_stats["PTS"] = sum(params.draftkings_pitchers_scoring[dk] * player_dict[dk] 
                                    for dk in params.draftkings_pitchers_scoring)
        return monster_stats

    def init_horse_factors(self, player_dict):
        self.horse_factors = dict()
        self.horse_factors["K"] = player_dict["K"]
        self.horse_factors["IP"] = player_dict["IP"]
        self.horse_factors["ER"] = player_dict["ER"]
        self.horse_factors["W"] = player_dict["W"]
        return None

    def get_horse_factors(self):
        factors = copy.deepcopy(self.player_factors)
        factors.update(copy.deepcopy(self.horse_factors))
        return self.positions, factors

class Hitter(Player):
    def __init__(self, player_id, player_dict, team):
        Player.__init__(self, player_id, player_dict, team)
        self.batting_order = player_dict["batting_order"]
        self.probs = self.get_probs(player_dict)
        self.monster_stats = self.get_monster_stats(player_dict)
        self.stats = {st: 0.0 for st in params.draftkings_hitters_scoring}
        self.init_kicker_factors()
        return None

    def __str__(self):
        ret += Player.__str__()
        ret += ("batting order: " + str(self.batting_order)+"\n")
        ret += ("probs: " + str(self.probs)+"\n")
        return ret

    def get_probs(self, player_dict):
        pa = player_dict["PA"]
        stats_list = copy.deepcopy(params.hits+params.walks+["K"])
        stats = {st: player_dict[st]/pa for st in stats_list}
        stats["O"] = 1.0 - sum(stats[s] for s in stats_list)
        steal_opportunity = params.steal_opp_multiplier * sum(player_dict[fb] for fb in ["BB", "HBP", "1B"])
        stats["prob_SB"] = player_dict["SB"]/steal_opportunity if steal_opportunity > 0 else 0.0
        stats["prob_CS"] = player_dict["CS"]/steal_opportunity if steal_opportunity > 0 else 0.0
        stats["PA"] = pa
        return stats

    def get_monster_stats(self,player_dict):
        monster_stats = dict()
        for s in params.hitter_ev_stats:
            monster_stats[s] = player_dict[s]
        monster_stats["PTS"] = sum(params.draftkings_hitters_scoring[dk] * player_dict[dk] 
                                    for dk in params.draftkings_hitters_scoring)
        return monster_stats

    def init_kicker_factors(self):
        self.kicker_factors = dict()
        self.kicker_factors["batting.order"] = self.batting_order
        self.kicker_factors["HR"] = self.probs["HR"]
        self.kicker_factors["SB"] = self.probs["prob_SB"]
        return None

    def get_kicker_factors(self):
        factors = copy.deepcopy(self.player_factors)
        factors.update(copy.deepcopy(self.kicker_factors))
        return self.positions, factors

    def compute_points(self, wp=None):
        self.points = sum(self.stats[s] * params.draftkings_hitters_scoring[s] for s in self.stats)
        return None