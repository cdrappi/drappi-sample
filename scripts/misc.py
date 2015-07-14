import os, datetime
import functools, operator
import math, random
import params, misc

def get_today_filename():
    if params.day_to_use:
        return params.day_to_use
    today = datetime.datetime.today()
    today = subtract_timezone(today)
    return str(today.year) + "_" + two_digit_str(today.month) + "_" + two_digit_str(today.day)

def get_today_parse_filename(df):
    parse_name = "" if not params.parse_setting else params.parse_setting
    return df + "_" + parse_name + ".csv"

def rp(n):
    return float(round(n, params.round_proj))

def rp_zero(n):
    if n == 0:
        return "-"
    return rp(n)

def round_to_nearest_multiple(n, nearest_multiple):
    return int(n/nearest_multiple)*int(nearest_multiple)

def prod(l):
    return functools.reduce(operator.mul, l, 1)

def random_filename():
    return str(random.randint(0, params.max_ev_randint)) + ".csv"

def tname(name):
    name = name.lower()
    name = name.strip()
    return name

def bm_to_dk_name(name):
        name = tname(name)
        bm_to_dk_dict = {
                        "daniel santana": "danny santana",
                        "jacob marisnick": "jake marisnick",
                        "norichika aoki": "nori aoki",
                        "daniel muno": "danny muno",
                        "jon niese": "jonathon niese",
                        "michael taylor": "michael a. taylor",
                        "enrique hernandez": "kike hernandez",
                        "jr murphy": "john ryan murphy",
                        "steven souza": "steven souza jr.",
                        "eric young": "eric young jr.",
                        "ivan de jesus": "ivan de jesus jr.",
                        "philip gosselin": "phil gosselin",
                        "kris negron": "kristopher negron",
                        "bradley boxberger": "brad boxberger",
                        "aj ramos": "a.j. ramos",
                        "robbie ross": "robbie ross jr.",
                        "zach rosscup": "zac rosscup",
                        "samuel dyson": "sam dyson",
                        "alexander torres": "alex torres",
                        "aj pollock": "a.j. pollock",
                        "c.c. sabathia": "cc sabathia",
                        "tom layne": "tommy layne",
                        "michael bolsinger": "mike bolsinger",
                        "christopher dominguez": "chris dominguez",
                        "john mayberry": "john mayberry jr.",
                        "melvin upton": "melvin upton jr.",
                        "tom kahnle": "tommy kahnle",
                        "nathan adcock": "nate adcock",
                        "daniel dorn": "danny dorn",
                        "jackie bradley": "jackie bradley jr.",
                        "joseph terdoslavich": "joey terdoslavich",
                        "thomas pham": "tommy pham",
                      }
        if name in bm_to_dk_dict:
            return bm_to_dk_dict[name]
        return name

def rps(n):
    rpstr = format(rp(n), '.'+str(params.round_proj)+'f')
    lead_index = rpstr.index(".")
    ret = rpstr[0:lead_index] + "." + rpstr[lead_index+1:lead_index+1+params.round_proj]
    if ret[0] == "0":
        ret += "0"*(2+params.round_proj-len(ret))
    return ret

def fl(s,n):
    if len(s) > n:
        return "ERROR IN fl() - too large of an argument"
    return s + " "*(n-len(s))

def avg(l):
    return rp(sum(l)/len(l))
    
def check_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return None

def parse_dk_teams(teams):
    return tuple([clean_team(t.upper()) for t in teams.split("@")][::-1])
    
def clean_team(t):
    dk_to_std = {"CHW": "CWS"}
    for k in dk_to_std:
        t = t.replace(k, dk_to_std[k])
    return t

def parse_game_info(gi):
    teams, gametime, et = gi.split(" ")
    # below gives HOME,AWAY
    teams = parse_dk_teams(teams)
    gametime = gametime.replace("PM", "")
    gametime = [float(g) for g in gametime.split(":")]
    gametime = (gametime[0] + gametime[1] / 60.0 - params.baseline_gametime)
    return (teams, gametime)

def random_pick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item

def two_digit_str(num):
    num_str = str(num)
    num_str = "0"*(2-len(num_str)) + num_str
    return num_str

def subtract_timezone(dt):
    if params.on_ec2:
        delta = datetime.timedelta(hours=5)
        dt -= delta
    return dt

def stack_pos_multiplier(pts,pos):
    mult = stack_pos_multiplier_dict[pos]
    return pts*mult

def goose_helper(n, excess_spending, player_salary,avg_pos_salary,pos,mgln=False):
    """ 
        use these new parameters to set new goose helpers 
        the probability is goosed by exp(-[the number returned])
    """
    if pos == "P":
        return 1.0
    ideal_salary = avg_pos_salary - excess_spending/n
    overshoots_ideal = max(0, player_salary - ideal_salary)
    undershoots_ideal = max(0, ideal_salary - player_salary)
    overshoot_penalty = overshoots_ideal * overshoot_n(n)
    undershoot_penalty = undershoots_ideal * undershoot_n(n) if not mgln else 1.0
    return (overshoot_penalty + undershoot_penalty)

def overshoot_n(n):
    overshoot_dict = {
                        1: 1.0/1000,
                        2: 1.0/10,
                        3: 1,
                        4: 2,
                        5: 5,
                        6: 10,
                        7: 50,
                        8: 100,
                        9: 100000, # pitcher slot 2
                        10: 100000, # pitcher slot 1
                     }
    return 1.0/overshoot_dict[n]

def undershoot_n(n):
    undershoot_dict = {
                        1: 20,
                        2: 50,
                        3: 100,
                        4: 200,
                        5: 200,
                        6: 200,
                        7: 300,
                        8: 500,
                        9: 100000, # pitcher slot 2
                        10: 100000, # pitcher slot 1
                     }
    return 1.0/undershoot_dict[n]

def goose_fn(x):
    return logistic_fn(x) # (1 + x + 0.5*(x**2))

def logistic_fn(x):
    return (math.exp(x) / (1 + math.exp(x)))

def bot_name(x):
    ret = " ".join(x.split(" ")[0:2])
    return ret

def goose_pos_salary(sal,pos,rate):
    if pos == "P":
        ret = 1 # 8000.0/sal
    else:
        ret = params.hitter_baseline_salary/sal
    ret = ret * math.exp(-params.rate_multiplier * rate)
    ret = math.pow(ret,params.bales_sal_pow)
    return ret

def avg_bales_stack_val(a,b,size):
    f_diff = math.pow(b,params.bales_stack_pow) - math.pow(a,params.bales_stack_pow)
    x_diff = b-a
    return (f_diff/x_diff)

def sort_tuples(t):
    to_str = str(t).replace("(", "").replace(")", "").replace(",", "")
    return to_str

def avg_bales_pos_val(pts,pos):
    if pos == "P":
        return max(pts-params.bales_pitcher_strike,0)
    else:
        return max(pts-params.bales_hitter_strike,0)

def global_swap(name):
    swaps = {
                "michael a. taylor": "michael taylor",
                "jung ho kang": "jung kang",
                "john ryan murphy": "john murphy",
                   
            }
    if name in swaps:
        return swaps[name]
    return name


day_file = get_today_filename()
day_file_parse = get_today_parse_filename(day_file)



