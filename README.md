## Texas Hold'em Poker Hand Evaluator ##

This is an exploration of the Texas Hold'em Poker game, in python and javascript.
An IP notebook present the algorithm, originally from [SpecialK](http://specialk-coding.blogspot.fr/2010/04/texas-holdem-7-card-evaluator_23.html) and the main results.
The tables are available in csv format.
Contains fast (jit numba accelerated) Python script to create the tables.
The main results:
+ hand rank distribution per preflop hand
+ pot equity for all pair of preflop hands
+ montecarlo equity tables per preflop hand and number of opponents
are also available as [d3.js](d3js.org) visualisations.

A game simulator (also [d3.js](d3js.org) based) is also available:
+ exhaustive search if all player's cards are known.
+ montecarlo if only one player's cards are known.

