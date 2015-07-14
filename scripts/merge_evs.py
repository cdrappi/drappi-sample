# mlb_merge_evs.py

import os, csv
import random
import params, misc, dirs


def parse_pnl_file(filename):
    lineups_dict = dict()
    with open(filename, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            ev = float(r[header.index("ev")])
            mc = int(r[header.index("mc")])
            lineup = tuple(r[2:])
            lineups_dict[lineup] = {"ev": ev, "mc": mc}
    return lineups_dict

def load_files_dict(contest_dir):
    files_dict = dict()
    for filename in [contest_dir+f for f in os.listdir(contest_dir) if f.endswith(".csv")]:
        files_dict[filename] = parse_pnl_file(filename)
    return files_dict

def get_merged_evs(files_dict):
    merged_ev_dict = dict()
    lineup_mcs = dict()
    for f in files_dict:
        for lineup in files_dict[f]:
            if lineup not in lineup_mcs:
                lineup_mcs[lineup] = 0
            lineup_mcs[lineup] += files_dict[f][lineup]["mc"]
    for f in files_dict:    
        for lineup in files_dict[f]:
            if lineup not in merged_ev_dict:
                merged_ev_dict[lineup] = {"ev": 0.0, "mc": lineup_mcs[lineup]}
            if lineup_mcs[lineup] != 0:
                merged_ev_dict[lineup]["ev"] += (files_dict[f][lineup]["ev"]*files_dict[f][lineup]["mc"]) / lineup_mcs[lineup]
    return merged_ev_dict

def write_merged_evs(merged_ev_dict):
    ev_dir = dirs.dir_dict["laboratory"]+misc.day_file+"/agg/"
    misc.check_dir(ev_dir)
    with open(ev_dir+params.contest_name+".csv", "w") as f:
        writer = csv.writer(f)
        header = ["ev", "mc"] + params.position_slots_list
        writer.writerow(header)
        for lineup in sorted(merged_ev_dict.keys(), key=lambda k: merged_ev_dict[k]["ev"], reverse=True):
            ev, mc = [merged_ev_dict[lineup][col] for col in ["ev", "mc"]]
            writer.writerow([ev, mc]+list(lineup))
    return None
    
if __name__ == "__main__":
    contest_dir = dirs.dir_dict["laboratory"]+misc.day_file+"/"+params.contest_name+"/"
    if os.path.exists(contest_dir) and bool([l for l in os.listdir(contest_dir) if l.endswith(".csv")]):
        files_dict = load_files_dict(contest_dir)
        merged_evs = get_merged_evs(files_dict)
        write_merged_evs(merged_evs)

    

