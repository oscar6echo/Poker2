

// ----------------constants

var hand_type_original = ["High Card", "One Pair", "Two Pairs", "Three Of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"],
	hand_type = [["High", "Card"], ["One", "Pair"], ["Two", "Pairs"], ["Three of", "a Kind"], ["", "Straight"], ["", "Flush"], ["Full", "House"], ["Four of", "a Kind"], ["Straight", "Flush"]];

var type_limits = [0, 1277, 4137, 4995, 5853, 5863, 7140, 7296, 7452, 7462];

var NB_FACE = 13,
	NB_SUIT = 4,
	DECK_SIZE = NB_SUIT*NB_FACE,
	SUIT_MASK = 511,
	SUIT_BIT_SHIFT = 9;

// spades, hearts, diamonds, clubs
var SUIT_KEY = [0, 1, 29, 37];

// faces 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A
var FLUSH_KEY_FIVE = new Int32Array([0, 1, 2, 4, 8, 16, 32, 56, 104, 192, 352, 672, 1288]),
	FACE_KEY_FIVE = new Int32Array([0, 1, 5, 22, 94, 312, 992, 2422, 5624, 12522, 19998, 43258, 79415]),
	FLUSH_KEY_SEVEN = new Int32Array([1, 2, 4, 8, 16, 32, 64, 128, 240, 464, 896, 1728, 3328]),
	FACE_KEY_SEVEN = new Int32Array([0, 1, 5, 22, 98, 453, 2031, 8698, 22854, 83661, 262349, 636345, 1479181]);

var CARD_FACE = new Int32Array(DECK_SIZE),
	CARD_SUIT = new Int32Array(DECK_SIZE);

for(var f=0; f<NB_FACE; f++) {
	for(var s=0; s<NB_FACE; s++) {
		CARD_FACE[NB_SUIT*f+s] = f;
		CARD_SUIT[NB_SUIT*f+s] = s;
	}
}

var CARD_FLUSH_KEY = new Int32Array(DECK_SIZE),
	CARD_FACE_KEY = new Uint32Array(DECK_SIZE);			// uint32 to avoid overflow in EvalSeven.getSevenRank_ first sum


for(var f=0; f<NB_FACE; f++) {
	for(var s=0; s<NB_FACE; s++) {
		CARD_FACE_KEY[NB_SUIT*f+s] = (FACE_KEY_SEVEN[f]<<SUIT_BIT_SHIFT) + SUIT_KEY[s];
		CARD_FLUSH_KEY[NB_SUIT*f+s] = FLUSH_KEY_SEVEN[f];
	}
}


// ----------------hand rank one hand

function handtype(r) {
	if (r<type_limits[1]) { return hand_type[0]; }
	else if (r<type_limits[2]) { return hand_type[1]; }
	else if (r<type_limits[3]) { return hand_type[2]; }
	else if (r<type_limits[4]) { return hand_type[3]; }
	else if (r<type_limits[5]) { return hand_type[4]; }
	else if (r<type_limits[6]) { return hand_type[5]; }
	else if (r<type_limits[7]) { return hand_type[6]; }
	else if (r<type_limits[8]) { return hand_type[7]; }
	else { return hand_type[8]; }
}


// ----------------hand rank one hand

function rank(card) {
	// requires following global variables:
	// CARD_FLUSH_KEY, CARD_FACE_KEY, CARD_SUIT, SUIT_MASK, SUIT_BIT_SHIFT		hard coded
	// flush_rank, face_rank, flush_suit														loaded from disk

	var c1 = card[0],
		c2 = card[1],
		c3 = card[2],
		c4 = card[3],
		c5 = card[4],
		c6 = card[5],
		c7 = card[6];
	var hand_key = CARD_FACE_KEY[c1]+CARD_FACE_KEY[c2]+CARD_FACE_KEY[c3]+CARD_FACE_KEY[c4]+CARD_FACE_KEY[c5]+CARD_FACE_KEY[c6]+CARD_FACE_KEY[c7];
	var hand_suit_key = hand_key & SUIT_MASK;
	var hand_suit = flush_suit[hand_suit_key];
	if (hand_suit == -1) {
		var hand_face_key = hand_key >>> SUIT_BIT_SHIFT;
		var hand_rank = face_rank[hand_face_key];
	}
	else {
		hand_flush_key = (CARD_FLUSH_KEY[c1]*(CARD_SUIT[c1]==hand_suit)+
			CARD_FLUSH_KEY[c2]*(CARD_SUIT[c2]==hand_suit)+
			CARD_FLUSH_KEY[c3]*(CARD_SUIT[c3]==hand_suit)+
			CARD_FLUSH_KEY[c4]*(CARD_SUIT[c4]==hand_suit)+
			CARD_FLUSH_KEY[c5]*(CARD_SUIT[c5]==hand_suit)+
			CARD_FLUSH_KEY[c6]*(CARD_SUIT[c6]==hand_suit)+
			CARD_FLUSH_KEY[c7]*(CARD_SUIT[c7]==hand_suit));
		var hand_rank = flush_rank[hand_flush_key];
	}
	// console.log("hand_rank="+hand_rank);
	return hand_rank;
}



// ----------------exhaustive search through all possible hands

function compute_equity_exhaustive(player_card, table_card) {
	// requires following global variables:
	// CARD_FLUSH_KEY, CARD_FACE_KEY, CARD_SUIT, SUIT_MASK, SUIT_BIT_SHIFT		hard coded
	// flush_rank, face_rank, flush_suit														loaded from disk


	var p = player_card.length,
		t = table_card.length,
		known_cards = new Int32Array (2*p+t),
		deck = new Int32Array (52-(2*p-t)),
		card = new Int32Array (7),
		hand_rank = new Int32Array(p),
		eq_w = new Float32Array(p),
		eq_t = new Float32Array(p),
		eq_agg = new Array(p),
		winner = new Array(p),
		n = 0,
		showdown =0,
		k, cand, idx, max_rank, nb_best_hand;

	// for(var k=0; k<p; k++) {
	// 	eq_agg[k] = new Float32Array(2);
	// }


	// build known cards
	for(var k=0; k<p; k++) {
		known_cards[2*k] = player_card[k, 0];
		known_cards[2*k+1] = player_card[k, 1];
	}
	for(var k=0; k<t; k++) {
		known_cards[2*p+k] = table_card[k]
	}

	// build deck of cards in stack
	k = 0;
	for(var c=0; c<DECK_SIZE; c++) {
		cand = 1;
		idx = 0;
		while ((idx<k) && cand) {
			if (c==known_cards[idx]) {
				cand = 0;
			}
			idx += 1;
		}
		if (cand==1){
			deck[k] = c;
			k += 1;
		}
	}


	// go through all games exhaustively
	// no table cards
	if (t==0) {
		for(var idx1=0; idx1<DECK_SIZE-(2*p+t); idx1++) {
			for(var idx2=0; idx2<idx1; idx2++) {
				for(var idx3=0; idx3<idx2; idx3++) {
					for(var idx4=0; idx4<idx3; idx4++) {
						for(var idx5=0; idx5<idx4; idx5++) {
							n++;

							// hand ranking all players
							for(var h=0; h<p; h++) {
								card[0] = player_card[h][0];
								card[1] = player_card[h][1];
								card[2] = deck[idx1];
								card[3] = deck[idx2];
								card[4] = deck[idx3];
								card[5] = deck[idx4];
								card[6] = deck[idx5];
								hand_rank[h] = rank(card);
							}

							// compute max_rank and nb_best_hand
							max_rank = hand_rank[0];
							nb_best_hand = 1;
							for(var h=1; h<p; h++) {
								if (hand_rank[h]>max_rank) {
									max_rank = hand_rank[h]
									nb_best_hand = 1
								}
								else if (hand_rank[h]==max_rank) {
									nb_best_hand += 1
								}
							}

							// compute equity_win and equity_tie
							for(var h=0; h<p; h++) {
								if (hand_rank[h]==max_rank) {
									if (nb_best_hand==1) { eq_w[h] += 1; }
									else{ eq_t[h] += 1.0/nb_best_hand; }
								}
							}
						}
					}
				}
			}
		}
	}

	// 3 table cards
	else if (t==3) {
		for(var idx4=0; idx4<DECK_SIZE-(2*p+t); idx4++) {
			for(var idx5=0; idx5<idx4; idx5++) {
				n++;

				// hand ranking all players
				for(var h=0; h<p; h++) {
					card[0] = player_card[h][0];
					card[1] = player_card[h][1];
					card[2] = table_card[0];
					card[3] = table_card[1];
					card[4] = table_card[2];
					card[5] = deck[idx4];
					card[6] = deck[idx5];
					hand_rank[h] = rank(card);
				}

				// compute max_rank and nb_best_hand
				max_rank = hand_rank[0];
				nb_best_hand = 1;
				for(var h=1; h<p; h++) {
					if (hand_rank[h]>max_rank) {
						max_rank = hand_rank[h]
						nb_best_hand = 1
					}
					else if (hand_rank[h]==max_rank) {
						nb_best_hand += 1
					}
				}

				// compute equity_win and equity_tie
				for(var h=0; h<p; h++) {
					if (hand_rank[h]==max_rank) {
						if (nb_best_hand==1) { eq_w[h] += 1; }
						else{ eq_t[h] += 1.0/nb_best_hand; }
					}
				}
			}
		}
	}

	// 4 table cards
	else if (t==4) {
		for(var idx5=0; idx5<DECK_SIZE-(2*p+t); idx5++) {
			n++;

			// hand ranking all players
			for(var h=0; h<p; h++) {
				card[0] = player_card[h][0];
				card[1] = player_card[h][1];
				card[2] = table_card[0];
				card[3] = table_card[1];
				card[4] = table_card[2];
				card[5] = table_card[3];
				card[6] = deck[idx5];
				hand_rank[h] = rank(card);
			}

			// compute max_rank and nb_best_hand
			max_rank = hand_rank[0];
			nb_best_hand = 1;
			for(var h=1; h<p; h++) {
				if (hand_rank[h]>max_rank) {
					max_rank = hand_rank[h]
					nb_best_hand = 1
				}
				else if (hand_rank[h]==max_rank) {
					nb_best_hand += 1
				}
			}

			// compute equity_win and equity_tie
			for(var h=0; h<p; h++) {
				if (hand_rank[h]==max_rank) {
					if (nb_best_hand==1) { eq_w[h] += 1; }
					else{ eq_t[h] += 1.0/nb_best_hand; }
				}
			}
		}
	}

	// 5 table cards
	else if (t==5) {
		showdown = 1;
		n++;

		// hand ranking all players
		for(var h=0; h<p; h++) {
			card[0] = player_card[h][0];
			card[1] = player_card[h][1];
			card[2] = table_card[0];
			card[3] = table_card[1];
			card[4] = table_card[2];
			card[5] = table_card[3];
			card[6] = table_card[4];
			hand_rank[h] = rank(card);
		}

		// compute max_rank and nb_best_hand
		max_rank = hand_rank[0];
		nb_best_hand = 1;
		for(var h=1; h<p; h++) {
			if (hand_rank[h]>max_rank) {
				max_rank = hand_rank[h]
				nb_best_hand = 1
			}
			else if (hand_rank[h]==max_rank) {
				nb_best_hand += 1
			}
		}

		// compute equity_win and equity_tie
		for(var h=0; h<p; h++) {
			if (hand_rank[h]==max_rank) {
				if (nb_best_hand==1) {
					eq_w[h] += 1;
					winner[h] = 1;
				}
				else{
					eq_t[h] += 1.0/nb_best_hand;
					winner[h] = 1;
				}
			}
		}
	}

	// impossible : error
	else {
		console.log("error in compute_equity: wrong number of table cards");
		return -1;
	}

	// normalize eq_w_agg and eq_t_agg
	if (showdown==1) {
		for(var h=0; h<p; h++) {
			eq_agg[h] = { 'win' : eq_w[h]/n,
							'tie' : eq_t[h]/n,
							'rank' : hand_rank[h],
							'handtype1' : handtype(hand_rank[h])[0],
							'handtype2' : handtype(hand_rank[h])[1],
							'winner' : winner[h]};
		}
	}
	else {
		for(var h=0; h<p; h++) {
			eq_agg[h] = { 'win' : eq_w[h]/n,
							'tie' : eq_t[h]/n};
		}
	}


	window.eq_agg = eq_agg;
	window.eq_w = eq_w;
	window.eq_t = eq_t;
	window.n = n;
	window.p = p;
	window.t = t;
	window.max_rank = max_rank;
	window.nb_best_hand = nb_best_hand;


	return [eq_agg, n];
}






// ----------------montecarlo : creation of random hands



function random_games(G, P, deck) {

	var r, deck_cc,
		start_time1, start_time2, end_time,
		rnd_int = function (d) { return Math.min(Math.floor(Math.random()*d), deck.length-1); };



	// version 1
	start_time1 = new Date().getTime();

	var games = new Array(G);
	for(var g=0; g<G; g++) {
		games[g] = new Int32Array(P);
	}

	for(var g=0; g<G; g++) {
		games[g][0] = deck[rnd_int(deck.length)];
		// console.log("-- games["+g+", "+0+"]"+"="+games[g][0]);
		for(var p=1; p<P; p++) {
			overlap = 1;
			while (overlap) {
				games[g][p] = deck[rnd_int(deck.length)];
				// console.log("-- games["+g+", "+p+"]"+"="+games[g][p]);
				overlap = 0;
				i = 0;
				while ((i<p) && (!overlap)) {
					if (games[g][p]==games[g][i]) {
						overlap = 1;
					}
				i += 1;
				}
			// console.log("games["+g+", "+p+"]"+"="+games[g][p]);
			}
		}
	}

	end_time = new Date().getTime();
	console.log("rng time 1 = "+(end_time - start_time1));



	// version 2
	// start_time2 = new Date().getTime();

	// var games = new Array(G);
	// for(var g=0; g<G; g++) {
	// 	games[g] = new Int32Array(P);
	// }

	// for(var g=0; g<G; g++) {
	// 	deck_cc = deck.slice()
	// 	for(var p=0; p<P; p++) {
	// 		r = rnd_int(deck_cc.length);
	// 		// console.log("r="+r+", deck["+r+"]="+deck_cc[r]);
	// 		games[g][p] = deck_cc[r];
	// 		// console.log("games["+g+"]="+games[g]);
	// 		deck_cc.splice(r, 1);
	// 		// console.log("deck_cc="+deck_cc);
	// 	}
	// }

	// end_time = new Date().getTime();
	// console.log("rng time 2 = "+(end_time - start_time2));


	window.rnd_int = rnd_int;
	console.log("random games computed");
	return games;
}




function test_random_games(games, unavail_card) {
	var overlap = 0;

	for(var g=0; g<games.length; g++) {
		for(var c=0; c<games[g].length; c++) {

			for(var c2=0; c2<c; c2++) {
				if (games[g][c]==games[g][c2]) {
					overlap = 1;
				}
			}

			for(var u=0; u<unavail_card.length; u++) {
				if (games[g][c]==unavail_card[u]) {
					overlap = 1;
				}
			}
		}
	}
	console.log("test_random_games="+(overlap==0) ? "ok" : "not ok");
}




// ----------------monte carlo random generation and evaluation of a given nb of possible hands

function compute_equity_montecarlo(player_card, table_card, G) {

	window.player_card_comp_mc = player_card;
	window.table_card_comp_mc = table_card;

	var unavail_card = table_card.slice(0);

	for(var p=0; p<nb_player; p++) {
		for(var c=0; c<2; c++) {
			if (player_card_data[p][c].card_no!=-1) {
				unavail_card.push(player_card_data[p][c].card_no);
			}
		}
	}

	var deck = [],
		overlap, i, u;

	for(var c=0; c<DECK_SIZE; c++) {
		overlap = 0;
		u = 0;
		while ((overlap===0) && (u<unavail_card.length)) {
			if (c==unavail_card[u]) {
				overlap = 1;
			}
			u += 1;
		}
		if (!overlap) {
			deck.push(c);
		}
	}
	console.log("deck="+deck);
	window.deck = deck;
	window.unavail_card = unavail_card;

	var games = random_games(G, (5 + 2 * nb_player) - unavail_card.length, deck);
	window.games = games;

	var mc_player_card = new Int32Array(2*nb_player),
		mc_table_card = new Int32Array(5),
		hand_rank = new Int32Array(nb_player),
		hand = new Int32Array(7),
		nb_table_card,
		mc_player_idx,
		eq_w = 0,
		eq_t = 0,
		k = 0;

	// mc_table cards fixed
	nb_table_card = 0;
	for(var t=0; t<table_card.length; t++) {
		mc_table_card[t] = table_card[t];
		nb_table_card++;
	}

	// mc_player_card fixed
	mc_player_idx = [];
	for(var p=0; p<nb_player; p++) {
		for(var c=0; c<2; c++) {
			if (player_card_data[p][c].card_no!=-1) {
				mc_player_card[2*p+c] = player_card_data[p][c].card_no;
			}
			else {
				mc_player_idx.push(2*p+c);
			}
		}
	}

		// go through all random games
	for(var g=0; g<games.length; g++) {
		k = 0;

		// mc_table_card variable
		for(var t=nb_table_card; t<5; t++) {
			mc_table_card[t] = games[g][k];
			k++;
		}

		// mc_player_card variable
		for(var i=0; i<mc_player_idx.length; i++) {
			mc_player_card[mc_player_idx[i]] = games[g][k];
			k++;
		}


		// hand ranking all players
		for(var p=0; p<nb_player; p++) {
			hand[0] = mc_player_card[2*p+0];
			hand[1] = mc_player_card[2*p+1];
			hand[2] = mc_table_card[0];
			hand[3] = mc_table_card[1];
			hand[4] = mc_table_card[2];
			hand[5] = mc_table_card[3];
			hand[6] = mc_table_card[4];
			hand_rank[p] = rank(hand);
			// console.log.apply(console, [hand, hand_rank[p]]);
		}


		// compute equity_win and equity_tie
		var i = 1,
			nb_best_hand = 1;
		while ((i<nb_player) && (nb_best_hand>0)) {
			if (hand_rank[0]<hand_rank[i]) { nb_best_hand = 0; }
			else if (hand_rank[0]==hand_rank[i]) { nb_best_hand += 1; }
			i += 1;
		}
		if ((i==nb_player) && (nb_best_hand>0)) {
			if (nb_best_hand==1) { eq_w += 1; }
			else { eq_t += 1.0/nb_best_hand; }
		}

		// console.log.apply(console, hand_rank);
		// console.log("-----------g="+g+", eq_w="+eq_w+", eq_t="+eq_t);
	}

	// normalize eq_w_agg and eq_t_agg
	var eq_agg_w = eq_w/G,
		eq_agg_t = eq_t/G;


	window.G = G;
	window.hand = hand;
	window.hand_rank = hand_rank;
	window.mc_table_card = mc_table_card;
	window.mc_player_card = mc_player_card;
	window.mc_player_idx = mc_player_idx;
	window.eq_w = eq_w;
	window.eq_t = eq_t;
	window.eq_agg_w = eq_agg_w;
	window.eq_agg_t = eq_agg_t;

	return { 'win' : eq_agg_w, 'tie' : eq_agg_t};
}




