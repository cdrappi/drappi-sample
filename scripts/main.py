import sys
import params
import mlb


def sim_games(n):
    mlb_obj = mlb.MLB(n, write_sanity=True)
    mlb_obj.write_results()
    return None

def sysargs_to_function(sa):
    fn = sa[0]
    args = sa[1:]
    fn_call = fn + "(" + ",".join(args) + ")"
    return fn_call

def run_main():
    if len(sys.argv) >= 2:
        to_exec = sysargs_to_function(sys.argv[1:])
        eval(to_exec)
    else:
        print("please enter a command to run")
    return None

if __name__ == "__main__":
    run_main()








