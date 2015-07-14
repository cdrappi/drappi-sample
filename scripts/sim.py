import csv
import numpy
import params, misc, dirs


class Sim:
    # convention: to access the team at bat,
    # use dictionary[self.away_at_bat], and to
    # access the team that is in the field,
    # use dictionary[not self.away_at_bat]
    def __init__(self, game):
        self.game = game
        self.teams = {False: self.game.home, True: self.game.away}
        self.setting = self.game.setting
        self.score = {False: 0, True: 0}
        self.bats_next = {False: 1, True: 1}
        self.away_at_bat = True
        self.batter_id = self.get_batter_id()
        self.inning = 1
        self.outs = 0
        self.on_base = [False, False, False]

    def draw_ab_result(self):
        probs_list = self.get_probs_list()
        at_bat_result = misc.random_pick(params.outcomes, probs_list)
        return at_bat_result

    def get_total_score(self):
        return self.score[False]+self.score[True]

    def get_probs_list(self):
        # simulate at bat
        # outcomes can be:
        # Single, Double, Triple, Home run
        # Walk, Intentional walk, Hit by pitch
        # Fielder's choice, Catcher interference, Batter interference, Reached on error
        # Flied out, Popped up, Lined out, Fouled out, Grounded out #
        # Struck out
        batter = self.teams[self.away_at_bat].batting_order[self.bats_next[self.away_at_bat]]
        prob_outcomes_dict = {oc: batter.probs[oc] for oc in params.outcomes}
        pitcher_gooser = self.get_pitcher().goose_comp_factors
        probs_list = [prob_outcomes_dict[oc]*pitcher_gooser[oc] for oc in params.outcomes]
        probs_list = [p/sum(probs_list) for p in probs_list]
        return probs_list

    def simulate_plate_appearance(self):
        result = self.draw_ab_result()
        self.teams[self.away_at_bat].add_stat(self.batter_id, "PA")
        if self.get_pitcher_id() != -2:
            self.update_pitch_count(result)
        if result not in params.non_at_bat_results:
            self.teams[self.away_at_bat].add_stat(self.batter_id, "AB")
        self.update_score_and_bases(result)
        self.update_outs(result)
        self.advance_batting_order()
        return None

    def get_batter_id(self):
        batter = self.teams[self.away_at_bat].batting_order[self.bats_next[self.away_at_bat]]
        return batter.player_id

    def get_pitcher_id(self):
        return self.teams[not self.away_at_bat].pitcher_id

    def get_pitcher(self):
        return self.teams[not self.away_at_bat].fetch_player_by_id(self.get_pitcher_id())

    def update_score_and_bases(self, result):
        process_dict = {"O": self.process_out, "K": self.process_k,
                        "1B": self.process_1b, "2B": self.process_2b,
                        "3B": self.process_3b, "HR": self.process_hr,
                        "HBP": self.process_hbp, "BB": self.process_bb}
        return process_dict[result]()

    def update_score(self, runs_scored):
        ha_to_tf = {"home": False, "away": True}
        team_ahead_before = self.get_team_ahead()
        self.score[self.away_at_bat] += runs_scored
        team_ahead_after = self.get_team_ahead()
        if team_ahead_before != team_ahead_after:
            if team_ahead_after:
                team_to_add = ha_to_tf[team_ahead_after]
                self.teams[team_to_add].set_winning_pitcher()
                self.teams[not team_to_add].unset_winning_pitcher()
            else:
                self.teams[True].unset_winning_pitcher()
                self.teams[False].unset_winning_pitcher()        
        return None

    def get_team_ahead(self):
        if self.score[True] < self.score[False]:
            return "home"
        elif self.score[True] > self.score[False]:
            return "away"
        else:
            return None

    def add_pitcher_stat(self, st, n=1):
        pitcher_id = self.teams[not self.away_at_bat].pitcher_id
        self.teams[not self.away_at_bat].add_stat(pitcher_id, st, n)
        return None

    def update_pitch_count(self, result):
        pitches_for_pa = self.get_min_pitches(result)
        expected_outs = self.get_pitcher().monster_stats["IP"] * 3.0
        expected_ks = self.get_pitcher().monster_stats["K"]
        expected_walks = sum(self.get_pitcher().monster_stats[w] for w in ["BB", "HBP"])
        expected_hits = sum(self.get_pitcher().monster_stats[h] for h in ["1B", "2B", "3B", "HR"])
        expected_batters_faced = expected_outs+expected_walks+expected_hits
        """
            on average, will have:
            ep = 4 * E[BB] + 3 * E[K] + E(tot # batters) * lambda
            lambda = (ep-4*E[BB]-3*E[K]) / E[tot # batters]
        """
        lambda_excess = (params.expected_pitches - 4*expected_walks - 3*expected_ks) / expected_batters_faced
        excess_pitches = numpy.random.poisson(lambda_excess)
        pitches_for_pa += excess_pitches
        self.get_pitcher().pitch_count += pitches_for_pa
        return None
    
    @staticmethod
    def get_min_pitches(result):
        if result in params.min_pitches_for_result:
            return params.min_pitches_for_result[result]
        return 1

    def process_hr(self):
        runs_scored = 1 + sum(1 for s in self.on_base if s)
        self.update_score(runs_scored)
        # update batter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "HR")
        self.teams[self.away_at_bat].add_stat(self.batter_id, "RBI", runs_scored)
        self.teams[self.away_at_bat].add_stat(self.batter_id, "R")
        # update runner's stats
        for r in [r for r in self.on_base if r]:
            self.teams[self.away_at_bat].add_stat(r, "R")
        # update hitter's stats
        self.add_pitcher_stat("HR")
        self.add_pitcher_stat("ER", n=runs_scored)
        self.on_base = [False, False, False]
        return None

    def process_3b(self):
        runs_scored = sum(1 for s in self.on_base if s)
        self.update_score(runs_scored)
        # update batter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "3B")
        self.teams[self.away_at_bat].add_stat(self.batter_id, "RBI", runs_scored)
        # update runner's stats
        for r in [r for r in self.on_base if r]:
            self.teams[self.away_at_bat].add_stat(r, "R")
        # update pitcher's stats
        self.add_pitcher_stat("3B")
        self.add_pitcher_stat("ER", n=runs_scored)
        self.on_base = [False, False, self.batter_id]
        return None

    def process_2b(self):
        runs_scored = sum(1 for s in self.on_base if s)
        self.update_score(runs_scored)
        # update batter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "2B")
        self.teams[self.away_at_bat].add_stat(self.batter_id, "RBI", runs_scored)
        # update runner's stats
        for r in [r for r in self.on_base if r]:
            self.teams[self.away_at_bat].add_stat(r, "R")
        # update pitcher's stats
        self.add_pitcher_stat("2B")
        self.add_pitcher_stat("ER", n=runs_scored)
        self.on_base = [False, self.batter_id, False] # self.on_base[0]]
        return None

    def process_1b(self):
        runs_scored = sum(1 for s in self.on_base[1:] if s)
        self.update_score(runs_scored)
        # update batter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "1B")
        self.teams[self.away_at_bat].add_stat(self.batter_id, "RBI", runs_scored)
        # update runner's stats
        for r in [r for r in self.on_base[1:] if r]:
            self.teams[self.away_at_bat].add_stat(r, "R")
        # update pitcher's stats
        self.add_pitcher_stat("1B")
        self.add_pitcher_stat("ER", n=runs_scored)
        self.on_base = [self.batter_id, self.on_base[0], False]# self.on_base[1]]
        return None

    def process_bb(self):
        self.process_walk()
        # update batter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "BB")
        # update runner's stats
        # update pitcher's stats
        self.add_pitcher_stat("BB")
        return None

    def process_hbp(self):
        self.process_walk()
        # update hitter's stats
        self.teams[self.away_at_bat].add_stat(self.batter_id, "HBP")
        # update runner's stats
        # update pitcher's stats
        self.add_pitcher_stat("HBP")
        return None

    def process_walk(self):
        if not (False in self.on_base):
            self.score[self.away_at_bat] += 1
            self.teams[self.away_at_bat].add_stat(self.on_base[2], "R")
            self.teams[self.away_at_bat].add_stat(self.batter_id, "RBI")
            self.add_pitcher_stat("ER")
        if not (False in self.on_base[0:2]):
            self.on_base = [self.batter_id] + self.on_base[0:2]
        elif not (False in self.on_base[0:1]):
            self.on_base = [self.batter_id, self.on_base[0], self.on_base[2]]
        else:
            self.on_base = [self.batter_id, False, False]
        return None

    def process_k(self):
        self.teams[self.away_at_bat].add_stat(self.batter_id, "K")
        self.add_pitcher_stat("K")
        self.process_out(k=True)
        return None

    def process_out(self, k=False):
        self.teams[self.away_at_bat].add_stat(self.batter_id, "O")
        self.add_pitcher_stat("IP", 1.0/3)
        if not k:
            self.add_pitcher_stat("O", 1.0)
        return None

    def update_outs(self, res):
        if res in ["K", "O"]:
            self.outs += 1
        return None

    def advance_batting_order(self):
        if self.bats_next[self.away_at_bat] == params.num_hitters_in_lineup:
            self.bats_next[self.away_at_bat] = 1
        else:
            self.bats_next[self.away_at_bat] += 1
        self.batter_id = self.get_batter_id()
        return None

    def check_substitutions(self):
        # set pitcher id
        self.check_pitcher_sub()
        return None

    def check_pitcher_sub(self):
        if self.should_sub_pitcher():
            self.teams[not self.away_at_bat].pitcher_id = -2
        return None


    def should_sub_pitcher(self):
        if self.get_pitcher_id() == -2:
            return False
        ra = self.score[not self.away_at_bat]
        pitcher = self.get_pitcher()
        pitch_count = pitcher.pitch_count
        if ra >= 8:
            return True
        elif ra >= 7 and pitch_count >= 55:
            return True
        elif ra >= 6 and pitch_count >= 65:
            return True
        elif ra >= 5 and pitch_count >= 75:
            return True
        elif ra >= 4 and pitch_count >= 85:
            return True
        elif ra >= 3 and pitch_count >= 95:
            return True
        elif ra >= 2 and pitch_count >= 105:
            return True
        elif ra >= 0 and pitch_count >= 115:
            return True
        # elif pitch_count >= 120:
        #     return True
        # if pitch_count >= 100:
        #     return True
        else:
            return False

    def check_steals(self):
        # reassign on_base values
        if self.on_base[0] and (not any([self.on_base[i] for i in [1,2]])):
            player_on_first = self.teams[self.away_at_bat].fetch_player_by_id(self.on_base[0])
            prob_sb = player_on_first.probs["prob_SB"]
            prob_cs = player_on_first.probs["prob_CS"]
            outcome_list = [1.0-(prob_sb-prob_cs), prob_sb, prob_cs]
            outcome_list = [o/sum(outcome_list) for o in outcome_list]
            outcome = misc.random_pick([None, "SB", "CS"], outcome_list)
            if outcome == "SB":
                self.on_base[1] = self.on_base[0]
                self.on_base[0] = False
                self.teams[self.away_at_bat].add_stat(player_on_first.player_id, "SB")
            elif outcome == "CS":
                self.on_base[0] = False
                self.teams[self.away_at_bat].add_stat(player_on_first.player_id, "CS")
                self.outs += 1
        return None

    def simulate_half_inning(self):
        while not self.inning_over():
            self.check_substitutions()
            self.check_steals()
            if not self.inning_over():
                self.simulate_plate_appearance()
        return None

    def __str__(self):
        top_bottom = "top" if self.away_at_bat else "bottom"
        half_inning_str = "\n" + top_bottom + " of the " + str(self.inning)
        scoreboard = " | H: " + str(self.score[False]) + ", A: " + str(self.score[True])
        team_at_bat = " | at bat: " + ("away" if self.away_at_bat else "home")
        
        ret_str = half_inning_str if not self.game_over() else "\nend of game"
        ret_str += scoreboard
        if not self.game_over():
            ret_str += team_at_bat
        else:
            ret_str += "\n"
        return ret_str

    def simulate_game(self):
        while not self.game_over():
            self.simulate_half_inning()
            if not self.game_over():
                self.advance_inning()
        self.set_final_score()
        self.compute_player_points()
        return None

    def set_final_score(self):
        self.total_score = self.score[True] + self.score[False]
        return None

    def compute_player_points(self):
        points_dict = dict()
        for tb in self.teams:
            wp_id = self.teams[tb].winning_pitcher_id
            for p in list(self.teams[tb].hitters+self.teams[tb].pitchers):
                if p.player_id > 0:
                    p.compute_points(wp=wp_id)
                    points_dict[p.long_id] = p.points
        self.points_dict = points_dict
        for tf in [False, True]:
            self.teams[tf].compute_lineup_points()
        return None

    def advance_inning(self):
        if not self.away_at_bat:
            self.inning += 1
        self.away_at_bat = not self.away_at_bat
        self.outs = 0
        self.on_base = [False, False, False]
        self.batter_id = self.get_batter_id()
        return None

    def inning_over(self):
        # if there are 3 outs, then it is the end of the inning
        if self.outs == params.num_outs_in_half_inning:
            return True
        return self.game_over()

    def game_over(self):
        # if we are in the 8th or earlier then the game is not over
        # eventually, modify this for rain cancellations
        # NOTE: in all dictionaries, False = home, True = away
        if self.inning < params.num_innings_in_game:
            return False
        # if we are in the 9th or later, the game is over if:
        # (1) the away team finished hitting and is behind
        # (2) the home team is hitting and is ahead
        # (2) the home team finished hitting and is behind
        if self.away_at_bat:
            # sitation (1)
            if self.outs == params.num_outs_in_half_inning:
                # the away team finished hitting and
                # the home team is winning
                return self.score[True] < self.score[False]
            else:
                return False
        # the home team is hitting
        if (not self.away_at_bat):
            # situation (2)
            if self.score[False] > self.score[True]:
                # the home team is hitting and is ahead (walk-off)
                return True
            # situation (3)
            if self.outs == params.num_outs_in_half_inning:
                # the away team closed out the game
                return self.score[True] > self.score[False]
            else:
                return False
        print("should never get here")
        quit()
        return False
            

