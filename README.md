# CIS667
## CIS667 Crouse Project - Blackjack AI with Monte Carlo Tree Search and Neural Network

It's the source code and data of the CIS667 Crouse Project

### Requirement:
Pytorch, Numpy, Pandas, Matplotlib

### Sturcture:

./data/ 			place to put the generated data
filter.py 			train a nn model for the game and dump it to a file
player.py 			implementation of MCTS player and dummy player
game.py 			the main implementation of the blackjack game
baseline_game.py 	a baseline with uniform random choice


### To run:
To get the baseline data and statistic result: python3 baseline_game.py 
To train the nn models: python3 filter.py
To run the game with differnt model: change the constant in player.py, then run python3 game.py

