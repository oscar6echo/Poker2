## Texas Hold'em Poker Hand Evaluator ##

This is an exploration of the Texas Hold'em Poker game, in python and javascript.  
An IPython notebook ([here](http://oscar6echo.github.io/Poker2/viz/nbviewer/Poker.html) it is in its html form) presents the algorithm, originally from [SpecialK](http://specialk-coding.blogspot.fr/2010/04/texas-holdem-7-card-evaluator_23.html) and the main results.  
The tables are available in csv format.  
The repo contains fast (jit numba accelerated) Python script to create the tables.  
The main results are also available as [d3.js](http://d3js.org) visualisations :
+ [hand rank distribution per preflop hand](http://oscar6echo.github.io/Poker2/viz/one_preflop_hand/index.html)
+ [preflop hand pair equity distribution](http://oscar6echo.github.io/Poker2/viz/two_preflop_hand/index.html)
+ [preflop hand equity distribution per number of opponents](http://oscar6echo.github.io/Poker2/viz/one_preflop_hand_montecarlo/index.html)  

And an [odd calculator](http://oscar6echo.github.io/Poker2/viz/game/index.html) (also [d3.js](http://d3js.org) based) :
+ running exhaustively if all player's cards are known.
+ running montecarlo simulations if only one player's cards are known (and some other players's cards may be gueesed).

