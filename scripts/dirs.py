# directories
import os
import params

mlb_dir = ""

downloads_dir = ["monster_hitters", "monster_pitchers", "salaries", "/"]
mlb_subdirs = ["projections", "runs_dist", "points_dist", "contests", 
                "factors", "races", "laboratory", "entries", "multibot", "rates",
                "results/hitter_evs", "results/pitcher_evs", "results/sims"]

if params.on_ec2:
    ec2_dir = "/home/ubuntu/dfs/"
    mlb_dir = dfs_dir + mlb_dir
else:
    local_dir = os.path.expanduser("~") + "/Downloads/drappi_sample/"
    mlb_dir = local_dir + mlb_dir

dir_dict = {d: mlb_dir+d+"/" for d in mlb_subdirs}
dir_dict["downloads"] = {d: mlb_dir+"/".join(["downloads",d])+"/" for d in downloads_dir}