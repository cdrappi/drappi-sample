contest_name = "moonshot"
# contest_name = "moonshot_early"
# contest_name = "payoff_pitch"
# contest_name = "knuckleball"
# contest_name = "slugfest"
# contest_name = "koth"
# contest_name = "strikeout"

ignore_list = []
max_stacks_per_team = 50

day_to_use = False or "2015_07_12"

parse_setting = "SELECTALL"
# parse_setting = "EARLY"
# parse_setting = "LATE"

day_to_train = "2015_06_30"
train_contest_name = "moonshot"

contest_dict = {
                "moonshot": {
                              "buyin": 3,
                              "size": 28736,
                              "upper": "Moonshot",
                              "stack_structs": [(6,)],
                              "freq_structs": [1],
                            },
                "moonshot_early": {
                              "buyin": 3,
                              "size": 15332,
                              "upper": "(Early)",
                              "stack_structs": [(6,)],
                              "freq_structs": [1],
                            },
                "payoff_pitch": {
                              "buyin": 27,
                              "size": 4859,
                              "upper": "Payoff Pitch",
                              "stack_structs": [(6,)],
                              "freq_structs": [1],
                            },
                "knuckleball": {
                              "buyin": 5,
                              "size": 57550,
                              "upper": "Knuckleball",
                              "stack_structs": [(5,2)],
                              "freq_structs": [1],
                            },
                "koth": {
                              "buyin": 10,
                              "size": 1288,
                              "upper": "King",
                              "stack_structs": [(6,)],
                              "freq_structs": [1],
                            },
}

import math, getpass

upper_contest_name = contest_dict[contest_name]["upper"]
buyin = contest_dict[contest_name]["buyin"]
contest_size = contest_dict[contest_name]["size"]
possible_mgln_stack_structures = contest_dict[contest_name]["stack_structs"]
freq_mgln_stack_structures = contest_dict[contest_name]["freq_structs"]

mgln_frac_entry = 0.08
mgln_entries = math.ceil(mgln_frac_entry * contest_size)

noise_frac = 10

on_ec2 = getpass.getuser() in ["ubuntu", "root"]

steal_opp_multiplier = 1.0

num_innings_in_game = 9
num_outs_in_half_inning = 3
num_hitters_in_lineup = 9
teams_in_mlb = 30

round_proj = 5

draftkings_hitters_scoring = {
                                "1B": 3,
                                "2B": 5,
                                "3B": 8,
                                "HR": 10,
                                "RBI": 2,
                                "R": 2,
                                "BB": 2,
                                "HBP": 2,
                                "SB": 5,
                                "CS": -2,
                                "PA": 0,
                                "AB": 0,
                                "K": 0,
                                "O": 0
                              }

draftkings_pitchers_scoring = {
                                "IP": 2.25,
                                "K": 2,
                                "W":  4,
                                "ER": -2,
                                "1B": -0.6,
                                "2B": -0.6,
                                "3B": -0.6,
                                "HR": -0.6,
                                "BB": -0.6,
                                "HBP": -0.6,
                                "CG": 2.5,
                                "CGSO": 2.5,
                                "NH": 5,
                                "O": 0
                              }

default_pitchers_hitting_dict = {'1B': 0.12, '2B': 0.01, 'E': 0.0, '3B': 0.0, 'HR': 0.0, 'PA': 1.0, 'K': 0.25, 'R': 0.03, 'RBI': 0.03, 'HBP': 0.0, 'CS': 0.0, 'AB': 0.97, 'O': 0.87, 'SB': 0.0, 'BB': 0.03, 'positions': ['SP'], 'batting_order': 9, 'salary': 3000, 'name': 'Pitcher', "fppg": 0.0}

nl_teams = ["MIL","COL","PHI","ARI","SF","LAD","SD","MIA","ATL","WAS","NYM","CIN","PIT","STL","CHC"]

transform_keys = {"pa": "PA", "ab": "AB", 
                  "singles": "1B", "doubles": "2B", "triples": "3B", "home_runs": "HR",
                  "walks": "BB", "strikeouts": "K", "sb": "SB", "cs": "CS",
                  "runs": "R", "rbi": "RBI", "hbp": "HBP", "sac_flies": "sac_flies",
                  "gidp": "GIDP", "errors": "E", "outs": "O",
                  "earned_runs": "ER", "opp_ba": "OBA", "cg": "CG", "qs": "QS",
                  "wins": "W", "losses": "L", "saves": "SV", "blown_saves": "BS", "holds": "HLD",
                  "innings": "IP", "nh": "NH", "cgso": "CGSO", "points": "PTS"}
# inverse_transform_keys = {v: k for k,v in transform_keys.items()}  

expected_pitches = 87

hits = ["1B", "2B", "3B", "HR"]
walks = ["BB", "HBP"] # , "IW", "CI"]
outs = ["K", "O"] # , "FO", "PU", "LO", "FF", "GO"]
# misc = ["E", "FC", "BI"]
non_at_bat_results = ["BB", "HBP"]
pa_sum_stats = hits+walks+["IP"]*3
outcomes = sorted(hits+walks+outs)
monster_hitter_ev_stats = ["pa","ab","singles","doubles","triples","home_runs","walks",
                    "strikeouts","sb","cs","runs","rbi","hbp","outs"]
hitter_ev_stats = [transform_keys[st] for st in monster_hitter_ev_stats]

monster_pitcher_ev_stats = ["innings","singles","doubles","triples","home_runs","walks","hbp","strikeouts","outs",
                    "earned_runs","cg","wins","hbp","nh","cgso"]
pitcher_ev_stats = [transform_keys[st] for st in monster_pitcher_ev_stats]

min_pitches_for_result = {"BB": 4, "K": 3}

users_to_pnl = ["drunkonpappy", "nattyboy79", "pips"] #, "Bales", "CSURAM88", "AshyL4rry", "maxdalury"]
min_entries_to_pnl = 20

positions_to_slots = {"P": 2, "C": 1, "1B": 1, 
                        "2B": 1, "3B": 1,
                        "SS": 1, "OF": 3}

hitter_slots_list = ["C", "1B", "2B", "3B", "SS", "OF", "OF", "OF"]
position_slots_list = ["P", "P"] + hitter_slots_list
num_hitters_in_entry = 8
num_players_in_entry = 10
min_teams_in_entry = 3

min_stack_size = 2
max_stack_size = 6
stack_size_range = list(range(min_stack_size, max_stack_size+1))
dual_stack_size_range = [2,3]

structure_types = ["-", (6), (5,2), (5),
                   (4,3), (4,2,2), (4,2), (4),
                   (3,3,2), (3,3), (3,2,2), (3,2), (3),
                   (2,2,2,2), (2,2,2), (2,2), (2)]

baseline_gametime = 7.0


order_to_positions = {0: "P", 1: "P", 2: "C", 3: "1B", 
                      4: "2B", 5: "3B", 6: "SS", 
                    7: "OF", 8: "OF", 9: "OF"}

hitter_positions = ["C", "1B", "2B", "3B", "SS", "OF"]
full_hitter_positions = ["C", "1B", "2B", "3B", "SS", "OF", "OF", "OF"]
all_positions = ["P"] + hitter_positions
full_positions = ["P", "P"] + full_hitter_positions

stack_pos_multiplier_dict = {"1B": 0.95, "OF": 0.95, "3B": 1.0, "2B": 1.05, "SS": 1.1, "C": 1.05}

kicker_point_strikes = [0, 5, 10]
kicker_strike_strings = {k: "p."+str(k)+".C" for k in kicker_point_strikes}
kicker_strike_strings_list = [kicker_strike_strings[k] for k in kicker_point_strikes]

horse_point_strikes = [0, 10, 20]
horse_strike_strings = {k: "p."+str(k)+".C" for k in horse_point_strikes}
horse_strike_strings_list = [horse_strike_strings[k] for k in horse_point_strikes]

general_player_factors = ["salary", "last.clean.rate", "gametime", "fppg", "twitter.noise"]
monster_kicker_factors = ["batting.order", "HR", "SB"]
monster_horse_factors = ["K", "ER", "IP", "W"]
all_kicker_factors = general_player_factors + monster_kicker_factors + kicker_strike_strings_list
all_horse_factors = general_player_factors + monster_horse_factors + horse_strike_strings_list

team_run_strikes = [0,5,10]
team_run_strike_strings = {k: "r."+str(k)+".C" for k in team_run_strikes}
team_run_strike_strings_list = [team_run_strike_strings[k] for k in team_run_strikes]

team_point_strikes = [0,50,100]
team_point_strike_strings = {k: "p."+str(k)+".C" for k in team_point_strikes}
team_point_strike_strings_list = [team_point_strike_strings[k] for k in team_point_strikes]

stack_factors_list = ["over.under", "twitter.noise"] #, "opp.pitcher.salary", "opp.pitcher.ER"]
past_rate_factors = ["p.c."+str(s) for s in stack_size_range]
all_stack_factors_list = stack_factors_list + past_rate_factors + team_run_strike_strings_list + team_point_strike_strings_list


start_runs = 0
end_runs = 16
by_runs = 1
sort_runs_index = 8

start_pts = 40
end_pts = 120
by_pts = 10
sort_pts_index = 4

bales_stack_pow = 0.6
rate_multiplier = 1.0/300
hitter_baseline_salary = 4000
bales_sal_pow = 0.25

bales_hitter_strike = 15
bales_pitcher_strike = 25

num_racers_hitting = 3
num_racers_by_pos = {pos: num_racers_hitting for pos in hitter_positions}
num_racers_by_pos["P"] = 6

num_racers_by_stack_size = {2: 300, 3: 300, 4: 300, 5: 300, 6: 300}

prob_mgln_stack_structures = [f/sum(freq_mgln_stack_structures) for f in freq_mgln_stack_structures]

num_dual_stacks_by_pos = 3
max_dual_stacks_per_team = 1

goose_n_multiple = 1
goose_es_multiple = 500

goose_n_range = list(range(1,10+goose_n_multiple,goose_n_multiple))
goose_es_range = list(range(-25000,20000+goose_es_multiple,goose_es_multiple))

max_salary = 50000
max_bad_count = 5

max_ev_randint = 99999999

""" Twitter search params """
team_search_names_dict = {
                            "TEX": "rangers",
                            "MIL": "brewers",
                            "MIN": "twins",
                            "WAS": "nationals",
                            "SEA": "mariners",
                            "CLE": "indians",
                            "COL": "rockies",
                            "BOS": "red sox",
                            "SF": "giants",
                            "NYY": "yankees",
                            "LAD": "dodgers",
                            "PIT": "pirates",
                            "CHC": "cubs",
                            "KC": "royals",
                            "CWS": "white sox",
                            "ARI": "diamondbacks",
                            "ATL": "braves",
                            "BAL": "orioles",
                            "CIN": "reds",
                            "DET": "tigers",
                            "HOU": "astros",
                            "LAA": "angels",
                            "MIA": "marlins",
                            "NYM": "mets",
                            "OAK": "oakland",
                            "PHI": "phillies",
                            "SD": "padres",
                            "STL": "cardinals",
                            "TB": "rays",
                            "TOR": "blue jays",
                          }


""" parse sites params """
monster_login = "https://baseballmonster.com/Login.aspx"
monster_daily = "https://baseballmonster.com/Daily.aspx"
monster_results = "https://baseballmonster.com/PlayerRankings.aspx"

""" bot params """
sleep_expo_pre_sleepy = 100
sleep_expo_sleepy = 100
sleep_expo_random = 100

sleep_x_random_login = 0.01
sleep_random_enter = 0.01
sleep_x_random_withdraw = 0.01

global_player_swap = True
page_load_timeout = 30

username = "drunkonpappy"
password = "L2esadws"

draftkings_contests = "https://www.draftkings.com/mycontests"
draftkings_login = "https://www.draftkings.com/contest-lobby"
draftkings_draft_stem = "https://www.draftkings.com/contest/draftteam/"










