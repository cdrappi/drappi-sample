To run the script

cd into the directory:

drappi_sample/scripts/

and run the command:

python3 main.py sim_games <n>

where n is an integer, representing the number of games you want to simulate.

for example, "python3 main.py sim_games 1000" would simulate 1000 games.

-----------------------

To view results, go to the folder results/

There are three sub-directories. The "pitcher_evs" and "hitter_evs"
contain information about mean box score statistics about players.
The lower case statistic is the player's projection, and the
upper case statistic is the sample average. The two should be pretty close.

The "sims" folder contains scores from games that were simulated.

-----------------------

Let me know if you have any questions!