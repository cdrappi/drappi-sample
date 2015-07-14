import csv
import copy
import params, misc, dirs
import player, team, setting, game, sim

class MLB:
    def __init__(self, num_sims, write_sanity=False):
        self.ignore_list = params.ignore_list
        self.set_games()
        self.n = num_sims
        self.noise = max(1, int(self.n / params.noise_frac))
        self.set_sims_list()
        self.games = [s.game for s in self.sims_list[0]]
        self.set_opponent_dict()
        self.teams = [g.home for g in self.games] + [g.away for g in self.games]
        self.team_names = [t.name for t in self.teams]
        self.hitters = [h for t in self.teams for h in t.hitters]
        self.pitchers = [p for t in self.teams for p in t.pitchers]
        self.players = [p for t in self.teams for p in t.hitters+t.pitchers]
        self.set_player_salaries_dict()
        self.set_player_teams_dict()
        self.set_points_dict_list()
        self.set_points_list_dict()
        if write_sanity:
            self.set_hitter_evs()
            self.set_pitcher_evs()
            self.write_hitter_evs()
            self.write_pitcher_evs()
        return None

    def write_results(self):
        with open(dirs.dir_dict["results/sims"]+misc.day_file+".csv", "w") as f:
            writer = csv.writer(f)
            header = [g for g in self.sorted_gd_keys]
            writer.writerow(header)
            for mlb_sim in self.sims_list:
                writer.writerow([(s.score[True],s.score[False]) for s in mlb_sim])
        return None

    def set_games(self):
        dk_players, gametimes = self.load_dk_salaries()
        hd, pd = self.load_hitters_monster_file(), self.load_pitchers_monster_file()
        hd, pd = self.merge_bm_dk(hd,dk_players), self.merge_bm_dk(pd,dk_players)
        hd, pd = self.get_consistent_hdpd(hd,pd)
        teams_dict = self.get_teams_dict(hd,pd)
        games_dict = self.get_games_dict(teams_dict, gametimes)
        sorted_gd_keys = sorted(list(games_dict.keys()))
        self.games_dict = games_dict
        self.sorted_gd_keys = sorted_gd_keys
        return None

    def get_consistent_hdpd(self,hd,pd):
        ret_hd, ret_pd = copy.deepcopy(hd), copy.deepcopy(pd)
        all_team_opps = list(hd.keys())
        sum_hd = {team_opp: {stat: 0.0 for stat in params.outcomes} for team_opp in all_team_opps}
        sum_pd = {team_opp: {stat: 0.0 for stat in params.outcomes} for team_opp in all_team_opps}
        for team_opp in all_team_opps:
            rev_team_opp = self.get_rev_team_opp(team_opp)
            for stat in params.outcomes:
                for pid in hd[team_opp]:
                    sum_hd[team_opp][stat] += hd[team_opp][pid][stat]
                for pid in pd[rev_team_opp]:
                    sum_pd[rev_team_opp][stat] += pd[rev_team_opp][pid][stat]
                pd_over_hd = sum_pd[rev_team_opp][stat]/sum_hd[team_opp][stat] if sum_hd[team_opp][stat] != 0 else 0
                hd_over_pd = sum_hd[team_opp][stat]/sum_pd[rev_team_opp][stat] if sum_pd[rev_team_opp][stat] != 0 else 0
                for pid in hd[team_opp]:
                    ret_hd[team_opp][pid][stat] = 0.5 * hd[team_opp][pid][stat] * (1 + pd_over_hd) 
                for pid in pd[rev_team_opp]:
                    ret_pd[rev_team_opp][pid][stat] = 0.5 * pd[rev_team_opp][pid][stat] * (1 + hd_over_pd)
        return ret_hd, ret_pd

    def get_rev_team_opp(self,to):
        team,opp = to
        team = team.replace("@ ","")
        opp = opp.replace("@ ","")
        if "@" in " ".join(to):
            return (opp,team)
        else:
            return (opp,"@ " + team)

    def set_opponent_dict(self):
        opponent_dict = dict()
        for g in self.games:
            opponent_dict[g.home.name] = g.away.name
            opponent_dict[g.away.name] = g.home.name
        self.opponent_dict = opponent_dict
        return None

    def set_player_salaries_dict(self):
        player_salaries_dict = dict()
        for player in self.players:
            player_salaries_dict[player.long_id] = player.salary
        self.player_salaries_dict = player_salaries_dict
        return None

    def set_player_teams_dict(self):
        player_teams_dict = dict()
        for player in self.players:
            player_teams_dict[player.long_id] = player.team
        self.player_teams_dict = player_teams_dict
        return None

    def set_sims_list(self):
        """ 
            A sims list is a list of lists,
            where each list contains one simulation
            of an entire day in the MLB. That is,
            for each list in sims list, there is
            one Sim object corresponding to each
            MLB game. These are all stored in order,
            according to the list sorted_gd_keys
        """
        sl = list()
        for i in range(self.n):
            sims = list()
            for g in self.sorted_gd_keys:
                sim_obj = copy.deepcopy(sim.Sim(self.games_dict[g]))
                sim_obj.simulate_game()
                sims.append(sim_obj)
            sl.append(sims)
            if (i+1)%self.noise == 0:
                print(str(i+1) + " MLB sims finished")
        self.sims_list = sl
        return None

    def get_player_by_name(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    def get_player_by_long_id(self, long_id):
        for p in self.players:
            if str(p.long_id) == long_id:
                return p
        return None

    def get_player_by_name_posns(self, name, posns):
        list_posns = posns.replace("(","").replace(")","").split("/")
        for p in self.players:
            if p.name == name and all(p.is_eligible(pos) for pos in list_posns):
                return p
        return None

    def set_points_dict_list(self):
        points_dict_list = list()
        for sl in self.sims_list:
            sl_points_dict = dict()
            for game in sl:
                for player in game.points_dict:
                    sl_points_dict[player] = game.points_dict[player]
            points_dict_list.append(sl_points_dict)
        self.points_dict_list = points_dict_list
        return None

    def set_points_list_dict(self):
        points_list_dict = dict()
        for points_dict in self.points_dict_list:
            for player in points_dict:
                if player not in points_list_dict:
                    points_list_dict[player] = list()
                points_list_dict[player].append(points_dict[player])
        self.points_list_dict = points_list_dict
        return None

    def set_hitter_evs(self):
        hitter_ev_stats = dict()
        init_hitter_evs = {outcome: 0.0 for outcome in params.hitter_ev_stats}
        for sl in self.sims_list:
            for sim in sl:
                for team in [sim.teams[tf] for tf in [False, True]]:
                    for h in team.hitters:
                        if h.name == "Pitcher":
                            continue
                        if h.long_id not in hitter_ev_stats:
                            hitter_ev_stats[h.long_id] = copy.deepcopy(init_hitter_evs)
                        for stat in h.stats:
                            hitter_ev_stats[h.long_id][stat] += (float(h.stats[stat]) / self.n)
                        hitter_ev_stats[h.long_id]["PTS"] = sum(hitter_ev_stats[h.long_id][s] * params.draftkings_hitters_scoring[s] 
                                                            for s in params.draftkings_hitters_scoring)
        self.hitter_ev_stats = hitter_ev_stats
        return None

    def set_pitcher_evs(self):
        pitcher_ev_stats = dict()
        init_pitcher_evs = {outcome: 0.0 for outcome in params.pitcher_ev_stats}
        for sl in self.sims_list:
            for sim in sl:
                for team in [sim.teams[tf] for tf in [False, True]]:
                    for p in team.pitchers:
                        # if "bullpen" in p.name:
                        #     continue
                        if p.long_id not in pitcher_ev_stats:
                            pitcher_ev_stats[p.long_id] = copy.deepcopy(init_pitcher_evs)
                        for stat in p.stats:
                            pitcher_ev_stats[p.long_id][stat] += (float(p.stats[stat]) / self.n)
                        pitcher_ev_stats[p.long_id]["PTS"] = sum(pitcher_ev_stats[p.long_id][s] * params.draftkings_pitchers_scoring[s] 
                                                            for s in params.draftkings_pitchers_scoring)

        self.pitcher_ev_stats = pitcher_ev_stats
        return None

    def write_hitter_evs(self):
        with open(dirs.dir_dict["results/hitter_evs"]+misc.day_file_parse, "w") as f:
            writer = csv.writer(f)
            header = ["long"] + ["points","PTS"] + [me for m in params.monster_hitter_ev_stats for me in [m, params.transform_keys[m]]]
            writer.writerow(header)
            for h in sorted(self.hitters, key=lambda k: k.monster_stats["PTS"], reverse=True):
                if h.name == "Pitcher":
                    continue
                to_write = [h.long_id]
                to_write += [misc.rps(me) for m in ["PTS"]+params.hitter_ev_stats for me in [h.monster_stats[m], self.hitter_ev_stats[h.long_id][m]]]
                writer.writerow(to_write)
        return None

    def write_pitcher_evs(self):
        with open(dirs.dir_dict["results/pitcher_evs"]+misc.day_file_parse, "w") as f:
            writer = csv.writer(f)
            header = ["long_id"] + ["points","PTS"] + [me for m in params.monster_pitcher_ev_stats for me in [m, params.transform_keys[m]]]
            writer.writerow(header)
            for p in sorted(self.pitchers, key=lambda k: k.monster_stats["PTS"], reverse=True):
                # if "bullpen" in p.name:
                #     continue
                to_write = [p.long_id]
                to_write += [misc.rps(me) for m in ["PTS"]+params.pitcher_ev_stats for me in [p.monster_stats[m], self.pitcher_ev_stats[p.long_id][m]]]
                writer.writerow(to_write)
        return None


    @staticmethod
    def get_teams_dict(hd,pd):
        teams_dict = dict()
        for hpd in hd, pd:
            for team_opp in hpd:
                if team_opp not in teams_dict:
                    teams_dict[team_opp] = {"hitters": dict(), "pitchers": dict()}
                for pid in hpd[team_opp]:
                    hop = "hitters" if ("batting_order" in hpd[team_opp][pid]) else "pitchers"
                    teams_dict[team_opp][hop][pid] = hpd[team_opp][pid]
        return teams_dict

    def get_games_dict(self, teams_dict, gametimes):
        games_dict = dict()
        home_teams = [team for (team, opp) in teams_dict.keys() if "@" not in opp]
        matchups_dict = {misc.clean_team(home): misc.clean_team(away) for (home, away) in teams_dict if home in home_teams}

        for home_name in matchups_dict:

            in_nl_park = bool(home_name in params.nl_teams)
            away_name = matchups_dict[home_name]
            
            if (home_name in self.ignore_list or away_name in self.ignore_list):
                continue
            
            home_team_dict = teams_dict[(home_name, away_name)]
            away_team_dict = teams_dict[(away_name, "@ "+home_name)]
            home_team = team.Team(home_name, False, home_team_dict, in_nl_park)
            away_team = team.Team(away_name, True, away_team_dict, in_nl_park)
            gametime = gametimes[(home_name, away_name)]
            setting_obj = setting.Setting(gametime,0,0,0,0,0)
            game_obj = game.Game(home_team, away_team, setting_obj)
            games_dict[(away_name, "@ "+home_name)] = game_obj
        return games_dict

    @classmethod
    def load_monster_file(self, hp, start, stop):
        monster_dict = dict()
        with open(dirs.dir_dict["downloads"]["monster_"+hp]+misc.day_file_parse, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            pa_index = header.index(start)
            outs_index = header.index(stop)
            for r in reader:
                player_id = int(r[header.index("id")])
                player_dict = {params.transform_keys[h]: float(r[header.index(h)]) for h in header[pa_index:outs_index+1]}
                player_dict["name"] = misc.bm_to_dk_name(" ".join([r[header.index(n)] for n in ("first_name", "last_name")]))
                if hp == "hitters":
                    player_dict["O"] = player_dict["O"] - player_dict["K"]
                    player_dict["batting_order"] = self.strip_batting_order(r[header.index("matchup")])
                    over_under = self.strip_ou(r[header.index("odds")])
                    player_dict["over_under"] = over_under
                else:
                    player_dict["O"] = player_dict["IP"]*3 - player_dict["K"]
                    player_dict["NH"] = 0.0
                    player_dict["CGSO"] = 0.0

                game_tuple = tuple([misc.clean_team(r[header.index(s)]) for s in ["team", "opponent"]])
                if game_tuple not in monster_dict:
                    monster_dict[game_tuple] = dict()
                monster_dict[game_tuple][player_id] = player_dict
            if hp == "pitchers":
                for g in monster_dict:
                    ## very hacky... but will probably never fail...
                    starter_id = max((p for p in monster_dict[g]), key=lambda k: monster_dict[g][k]["IP"])
                    monster_dict[g][starter_id]["starting"] = True
                    for p in monster_dict[g]:
                        if p != starter_id:
                            monster_dict[g][p]["starting"] = False
        return monster_dict

    @classmethod
    def load_hitters_monster_file(self):
        return self.load_monster_file("hitters", "pa", "outs")

    @classmethod
    def load_pitchers_monster_file(self):
        return self.load_monster_file("pitchers", "innings", "outs")

    @staticmethod
    def load_dk_salaries():
        dk_salaries = dict()
        gametimes = dict()
        with open(dirs.dir_dict["downloads"]["salaries"]+misc.day_file_parse, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for r in reader:
                posns = r[header.index("Position")].replace("SP","P").replace("RP","P").split("/")
                name = r[header.index("Name")].lower()
                salary = int(r[header.index("Salary")])
                home_away, gametime = misc.parse_game_info(r[header.index("GameInfo")])
                fppg = float(r[header.index("AvgPointsPerGame")])
                dk_salaries[(name,home_away)] = {"positions": posns, "salary": salary, "fppg": fppg}
                gametimes[home_away] = gametime
        return dk_salaries, gametimes

    @staticmethod
    def merge_bm_dk(bmd, dkd):
        ret = dict()
        for team_opp in bmd:
            ret[team_opp] = dict()
            for player_id in bmd[team_opp]:
                name = bmd[team_opp][player_id]["name"]
                matching_team_opp = tuple(to.replace("@ ", "") for to in sorted(team_opp, key=lambda k: bool("@" not in k)))
                ret[team_opp][player_id] = bmd[team_opp][player_id]
                if (name,matching_team_opp) in dkd:
                    for key in ["salary", "positions", "fppg"]:
                        ret[team_opp][player_id][key] = dkd[name,matching_team_opp][key]
                else:
                    # print(matching_team_opp)
                    # print([teams for name,teams in dkd.keys()])
                    order = False
                    if "batting_order" in bmd[team_opp][player_id]:
                        order = bmd[team_opp][player_id]["batting_order"]
                    order = " ("+str(order)+")" if order else ""
                    ret[team_opp][player_id]["salary"] = 0
                    ret[team_opp][player_id]["positions"] = []
                    ret[team_opp][player_id]["fppg"] = 0.0
                    print(name + " [" + str(matching_team_opp) + "] " + order + " is not in DK salaries")  
        return ret

    @staticmethod
    def strip_ou(odds):
        if "o/u" not in odds:
            return 8.33 # average over under
        split_odds = odds.split("(")
        ou = [so for so in split_odds if "o/u" in so][0].replace("o/u", "").replace(")", "").replace(" ", "")
        return float(ou)

    @staticmethod
    def strip_batting_order(matchup):
        matchup_list = matchup.split()
        ord_index = matchup_list.index("Ord") if "Ord" in matchup_list else False
        batting_order = int(matchup_list[ord_index+1]) if ord_index else False
        return batting_order



