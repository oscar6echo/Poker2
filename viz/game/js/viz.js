

var R,
	flush_suit,
	flush_rank,
	face_rank,
	nb_player,
	deck_card_data,
	deck_card,
	table_card_data,
	player_card_data,
	equity,
	nb_games,
	idx_active = -1,			// active card
	width_small_card = 17,
	height_small_card = 33,
	width_full_card = 48*1,
	height_full_card = 77*1,
	width_shuffle_small = 40,
	width_shuffle_large = 60,
	exhaustive = true,		// true for exhaustive, false for montecarlo
	mc_to_run,					// boolean to trigger monte carlo simulations
	mc_nb_games = 1e5;

var dt = 0;

var margin_1 = {top: 5, right: 0, bottom: 5, left: 0},
	width_1 = 650,
	height_1 = 90;

var margin_2 = {top: 0, right: 0, bottom: 0, left: 0},
	width_2 = 300,
	height_2 = 85;

var margin_3 = {top: 0, right: 0, bottom: 0, left: 0},
	width_3 = 300,
	height_3 = 40;

var margin_4 = {top: 0, right: 0, bottom: 0, left: 53},
	width_4 = 300,
	height_4 = 30;

var margin_5 = {top: 15, right: 0, bottom: 20, left: 53},
	width_5 = 600,
	height_5 = 100;

var margin_6 = {top: 0, right: 0, bottom: 0, left: 53},
	width_6 = 600,
	height_6 = 180;

var margin_7 = {top: 0, right: 0, bottom: 0, left: 53},
	width_7 = 600,
	height_7 = 75;


var x_11 = d3.scale.ordinal().rangeBands([0, width_1], 0.05, 0.05).domain(d3.range(2)),
	x_12 = d3.scale.ordinal().rangeBands([0, x_11.rangeBand()], 0.10, 0.05).domain(d3.range(13)),
	y_1 = d3.scale.ordinal().rangeBands([0, height_1], 0.15, 0.10).domain(d3.range(2)),

	x_2 = d3.scale.ordinal().rangeBands([0, width_2], 0.10, 0.15).domain(d3.range(5)),
	y_2 = d3.scale.ordinal().rangeBands([0, height_2], 0.10, 0.15).domain(d3.range(1)),

	x_3 = d3.scale.ordinal().rangeBands([0, width_3], 0.10, 0.15).domain(d3.range(4)),
	y_3 = d3.scale.ordinal().rangeBands([0, height_3], 0.10, 0.15).domain(d3.range(1)),

	x_4 = d3.scale.ordinal().rangeBands([0, width_4], 0.10, 0.15).domain(d3.range(1)),
	y_41 = d3.scale.ordinal().rangeBands([0, height_4], 0.10, 0.15).domain(d3.range(1)),
	y_42 = d3.scale.ordinal().rangeBands([0, height_4], 0.15, 0.15).domain(d3.range(2)),

	x_5 = d3.scale.ordinal().rangeBands([0, width_5], 0.10, 0.15),
	y_5 = d3.scale.linear().range([height_5, 0]).domain([0, 1]),

	x_6 = d3.scale.ordinal().rangeBands([0, width_6], 0.10, 0.15),
	y_6 = d3.scale.ordinal().rangeBands([0, height_6], 0.10, 0.15).domain(d3.range(2));

	x_71 = d3.scale.ordinal().rangeBands([0, width_7], 0.10, 0.15),
	x_72 = d3.scale.ordinal().rangeBands([0, width_7], 0.10, 0.15).domain(d3.range(2)),
	y_7 = d3.scale.ordinal().rangeBands([0, height_7], 0.20, 0.15).domain(d3.range(2));



var c = d3.scale.linear().domain([0, 1]).range(['blue', 'red']);
var fmt_int = d3.format(",d");
var fmt_float_tp = d3.format(".2f");

var fmt_float = function (x) {
	if (x!=0) {
		return d3.format(".2f")(x)+"%";
	}
	else {
		return "";
	}
}



var title = d3.select("#title");

var svg_1 = d3.select("#svg1")
	.append("svg")
		.attr("width", width_1 + margin_1.left + margin_1.right)
		.attr("height", height_1 + margin_1.top + margin_1.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_1.left + "," + margin_1.top + ")");

var svg_2 = d3.select("#svg2")
	.append("svg")
		.attr("width", width_2 + margin_2.left + margin_2.right)
		.attr("height", height_2 + margin_2.top + margin_2.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_2.left + "," + margin_2.top + ")");

var svg_3 = d3.select("#svg3")
	.append("svg")
		.attr("width", width_3 + margin_3.left + margin_3.right)
		.attr("height", height_3 + margin_3.top + margin_3.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_3.left + "," + margin_3.top + ")");

var svg_4 = d3.select("#svg4")
	.append("svg")
		.attr("width", width_4 + margin_4.left + margin_4.right)
		.attr("height", height_4 + margin_4.top + margin_4.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_4.left + "," + margin_4.top + ")");

var svg_5 = d3.select("#svg5")
	.append("svg")
		.attr("width", width_5 + margin_5.left + margin_5.right)
		.attr("height", height_5 + margin_5.top + margin_5.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_5.left + "," + margin_5.top + ")");

var svg_6 = d3.select("#svg6")
	.append("svg")
		.attr("width", width_6 + margin_6.left + margin_6.right)
		.attr("height", height_6 + margin_6.top + margin_6.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_6.left + "," + margin_6.top + ")");

var svg_7 = d3.select("#svg7")
	.append("svg")
		.attr("width", width_7 + margin_7.left + margin_7.right)
		.attr("height", height_7 + margin_7.top + margin_7.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_7.left + "," + margin_7.top + ")");


var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);



queue()
	.defer(load_table, './tables/flush_suit.txt')
	.defer(load_sparse_table, './tables/sparse_flush_rank_seven.csv')
	.defer(load_sparse_table, './tables/sparse_face_rank_seven.csv')
	.defer(load_card_path, ['./cards/full/', '.png'])
	.defer(load_card_path, ['./cards/small/Small-', '.gif'])
	.awaitAll(all_loaded);



function load_card_path(input, callback) {
	var path = input[0],
		ext = input[1];

	var card = new Array(53);
	for (var i=0; i<53; i++){
		card[i] = path+(i+1)+ext;
		}
	callback(null, card);
}


function load_table(path, callback) {
	d3.text(path, "text/csv", function(text) {
		var data = d3.csv.parseRows(text);
		// window.dataset = data;

		var n = data.length;
		var table = new Array(n);
		for (var i = 0; i < n; i++) {
			table[i] = +data[i];
		}
		// console.log("table="+table);
		callback(null, table);
	});

}


function load_sparse_table(path, callback) {
	d3.text(path, "text/csv", function(text) {
		var data = d3.csv.parseRows(text);
		// window.dataset = data;

		var n = data.length;
		var sparse_table = new Array(n);
		for (var i = 0; i < n; i++) {
			sparse_table[i] = new Array(2);
			sparse_table[i][0] = +data[i][0];
			sparse_table[i][1] = +data[i][1];
		}
		// console.log("sparse_table="+sparse_table);

		N = sparse_table[n-1][0];
		var table = new Array(N);
		for (var i = 0; i < N; i++) {
			table[i] = 0;
		}
		for (var i = 0; i < n; i++) {
			table[sparse_table[i][0]] = sparse_table[i][1];
		}
		callback(null, table);
	});
}


function all_loaded(error, results) {
	// results = [flush_suit, flush_rank, face_rank, full_card, small_card]
	// console.log('error='+error);
	console.log('all data loaded from disk');
	window.results = results;

	// init data: tables and images
	flush_suit = results[0];
	flush_rank = results[1];
	face_rank = results[2];
	full_card = results[3];
	small_card = results[4];

	init_variables();
	init_viz();
}

// convert card no to face and suit
function to_no(f, s) {
	return 4 * f + s;
}

// convert face and suit to card no
function to_fs(no) {
	var f = Math.floor(no / 4);
		s = no % 4;
	return [f, s];
}


function init_variables() {

	nb_player = 10;

	deck_card_data = new Array(4);
	deck_card = new Array(52);

	table_card_data = new Array(5);

	player_card_data = new Array(nb_player);

	for (var s=0; s<4; s++) {
		deck_card_data[s] = new Array(13);
		for (var f=0; f<13; f++) {
			var card_no = to_no(f, s);
			deck_card_data[s][f] = {'card_no' : card_no, 'avail' : 1};
			deck_card[card_no] = 1;
		}
	}

	for (var t=0; t<5; t++) {
		table_card_data[t] = {'idx' : t, 'card_no' : -1};
	}


	for (var p=0; p<nb_player; p++) {
		player_card_data [p] = new Array(2)
		for (var c=0; c<2; c++) {
			player_card_data[p][c] = {'player' : p, 'card' : c, 'card_no' : -1, 'idx' : 6+2*p+c};
		}
	}

	equity = new Array(nb_player);
	for(var p=0; p<nb_player; p++) {
		equity[p] = { 'win' : 0, 'tie' : 0 };
	}

}

function init_viz(){

	// draw title
	title.text("Hand Equity Calculator");


	// build table cards shuffle/reset buttons
	var shuffletable = svg_3.selectAll(".shuffletable")
			.data([{'name' : 'reset table', 'func' : reset_table}, {'name' : 'shuffle flop', 'func' : shuffle_flop}, {'name' : 'shuffle turn', 'func' : shuffle_turn}, {'name' : 'shuffle river', 'func' : shuffle_river}])
		.enter().append("g")
			.attr("class", "shuffletable")
			.attr("transform", function(d, i){ return "translate(" + (x_3(i) + x_3.rangeBand()/2 - width_shuffle_large/2) + ", " + y_3(0) + ")"; });

	shuffletable.append("rect")
		.attr("width", width_shuffle_large)
		.attr("height", y_3.rangeBand())
		.on("click", function(d, i){ return d.func(); });

	shuffletable.append("text")
		.attr("x", width_shuffle_large/2)
		.attr("y", y_7.rangeBand()/2)
		.attr("dy", "0.3em")
		.attr("text-anchor", "middle")
		.text(function(d, i){ return d.name; });


	// build all player cards shuffle/reset button
	var shuffleplayerall = svg_7.selectAll(".shuffleplayerall")
			.data([{'name' : 'reset all', 'func' : reset_player_all}, {'name' : 'shuffle all', 'func' : shuffle_player_all}])
		.enter().append("g")
			.attr("class", "shuffleplayerall")
			.attr("transform", function(d, i){ return "translate(" + (x_72(i) + x_72.rangeBand()/2 - width_shuffle_large/2) + ", " + y_7(1) + ")"; });

	shuffleplayerall.append("rect")
		.attr("width", width_shuffle_large)
		.attr("height", y_7.rangeBand())
		.on("click", function(d, i){ return d.func(); });

	shuffleplayerall.append("text")
		.attr("x", width_shuffle_large/2)
		.attr("y", y_7.rangeBand()/2)
		.attr("dy", "0.3em")
		.attr("text-anchor", "middle")
		.text(function(d, i){ return d.name; });



	update_viz(nb_player);
}



function update_viz(nb_player) {

	console.log("nb_player="+nb_player);

	// init scales
	x_6.domain(d3.range(nb_player));
	x_5.domain(d3.range(nb_player));
	x_71.domain(d3.range(nb_player));


	// compute equity
	if (exhaustive) {
		console.log("exhaustive_mode in update_viz");
		update_equity_exhaustive(nb_player);
	}
	else {
		if (mc_to_run) {
			console.log("montecarlo_mode in update_viz");
			// equity = compute_equity_fake_mc(nb_player);
			update_equity_montecarlo(nb_player);
		}
	}


	// build/update slider counter
	var slidertext = d3.select("#outputsliderplayers").selectAll("text")
		.data([nb_player]);

	slidertext.enter()
		.append("text")
			.text(fmt_int(nb_player));

	slidertext.transition()
		.duration(dt)
		.text(fmt_int(nb_player));



	// build deck cards
	var suit_row = svg_1.selectAll(".suitrow")
		.data(deck_card_data)
	.enter().append("g")
		.attr("class", "suitrow")
		.attr("transform", function(d, i) { return "translate("+ x_11(i % 2) +", "+ (y_1(~~(i / 2)) + y_1.rangeBand()/2 - height_small_card/2) +")"; })
		.each(function(row) {
			var deckcard = d3.select(this).selectAll(".deckcard")
				.data(row)
			.enter().append("g")
				.attr("class", "deckcard")
				.attr("transform", function(d, i) { return "translate(" + (x_12(i) + x_12.rangeBand()/2 - width_small_card/2) + ", 0)"; });

			deckcard.append("image")
				.attr("xlink:href", function(d, i){ return small_card[d.card_no]; })
				.attr("width", width_small_card)
				.attr("height", height_small_card);

			deckcard.append("rect")
				.attr("width", width_small_card)
				.attr("height", height_small_card)
				.on("click", mouseclick_deck);
		});

	// update deck cards
	svg_1.selectAll(".suitrow")
		.data(deck_card_data)
		.each(function(row, i) {
			var deckcard = d3.select(this).selectAll(".deckcard")
				.data(row, function(d, i) { return i; });

			deckcard.classed("hidden", function (d, i) { return d.avail==0; });
		});



	// build table cards
	var tablecard = svg_2.selectAll(".tablecard")
			.data(table_card_data);

	tablecard.enter()
		.append("g")
			.attr("class", "tablecard")
			.attr("transform", function(d, i) { return "translate(" + (x_2(i)  + x_2.rangeBand()/2 - width_full_card/2 ) + ", "+ (y_2(i) + y_2.rangeBand()/2 - height_full_card/2) +")"; })
			.each(function(d) {
				var card = d3.select(this);

				card.append("image")
					.attr("xlink:href", function(d, i){ return d.card_no==-1 ? full_card[52] : full_card[d.card_no] ; })
					.attr("width", width_full_card)
					.attr("height", height_full_card);

				card.append("rect")
					.attr("width", width_full_card)
					.attr("height", height_full_card)
					.on("click", mouseclick_table);
			});

	tablecard.select("image")
		.attr("xlink:href", function(d, i){ return d.card_no==-1 ? full_card[52] : full_card[d.card_no]; });



	// build equity histogram y axis
	var yAxis = svg_5.selectAll(".y.axis")
		.data([0]);

	yAxis.enter()
		.append("g")
			.attr("class", "y axis")
			.call(d3.svg.axis().scale(y_5).orient("left").ticks(4, "%"))
		.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", -50)
			.attr("dy", "0.71em")
			.style("text-anchor", "end")
			.text("Pot Equity");


	// build/update equity histogram x axis
	var xAxis = svg_5.selectAll(".x.axis")
		.data([0]);

	xAxis.enter()
		.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_5 + ")")
			.call(d3.svg.axis().scale(x_5).orient("bottom").tickFormat(fmt_int).ticks(d3.range(nb_player)));

	xAxis.transition()
		.duration(dt)
		.call(d3.svg.axis().scale(x_5).orient("bottom").tickFormat(fmt_int).ticks(d3.range(nb_player)));



	// build/update player cards
	var playerhand = svg_6.selectAll(".playerhand")
		.data(player_card_data);

	playerhand.enter()
		.append("g")
			.attr("class", "playerhand")
			.attr("transform", function(d, i) { return "translate("+ (x_6(i) + x_6.rangeBand()/2 - width_full_card/2) +", 0)"; })
			.each(function(hand) {
				var playercard = d3.select(this).selectAll(".playercard")
						.data(hand)
					.enter().append("g")
						.attr("class", "playercard")
						.attr("transform", function(d, i) { return "translate(0, " + (y_6(i) + y_6.rangeBand()/2 - height_full_card/2) + ")"; });

				playercard.append("image")
					.attr("xlink:href", function(d, i){ return d.card_no==-1 ? full_card[52] : full_card[d.card_no]; })
					.attr("width", width_full_card)
					.attr("height", height_full_card);

				playercard.append("rect")
					.attr("width", width_full_card)
					.attr("height", height_full_card)
					.on("click", mouseclick_player);
			});

	playerhand.transition()
		.duration(dt)
		.attr("transform", function(d, i) { return "translate("+ (x_6(i) + x_6.rangeBand()/2 - width_full_card/2) +", 0)"; })
		.each(function(hand) {
			var playercard = d3.select(this).selectAll(".playercard")
					.data(hand);

			playercard.select("image")
				.attr("xlink:href", function(d, i){ return d.card_no==-1 ? full_card[52] : full_card[d.card_no]; });
		});

	playerhand.exit().transition().duration(dt).remove();



	// build/update player cards shuffle buttons
	var shuffleplayer = svg_7.selectAll(".shuffleplayer")
			.data(d3.range(nb_player));

	shuffleplayer.enter()
		.append("g")
			.attr("class", "shuffleplayer")
			.attr("transform", function(d, i){ return "translate(" + (x_71(i) + x_71.rangeBand()/2 - width_shuffle_small/2) + ", " + y_7(0) + ")"; })
			.each(function(data) {
				var button = d3.select(this)

				button.append("rect")
					.attr("width", width_shuffle_small)
					.attr("height", y_7.rangeBand())
					.on("click", shuffle_player);

				button.append("text")
					.attr("x", width_shuffle_small/2)
					.attr("y", y_7.rangeBand()/2)
					.attr("dy", "0.3em")
					.attr("text-anchor", "middle")
					.text("shuffle ");
			});

	shuffleplayer.transition()
		.duration(dt)
		.attr("transform", function(d, i){ return "translate(" + (x_71(i) + x_71.rangeBand()/2 - width_shuffle_small/2) + ", " + y_7(0) + ")"; });

	shuffleplayer.exit().transition().duration(dt).remove();



	if (exhaustive) {
		// remove mc button
		svg_4.selectAll(".mcbutton").remove();

		// build/update nb of games
		var nbgames = svg_4.selectAll(".nbgames")
			.data([nb_games]);

		nbgames.enter()
			.append("text")
				.attr("class", "nbgames")
				.attr("x", x_4(0) + x_4.rangeBand()/2)
				.attr("y", y_41(0) + y_41.rangeBand()/2)
				.attr("dy", "0.3em")
				.attr("text-anchor", "middle")
				.text(function (d) { return nb_games!=undefined ? fmt_int(nb_games)+" game(s)": " "; });

		nbgames.transition()
			.duration(dt)
			.text(function (d) { return nb_games!=undefined ? fmt_int(nb_games)+" game(s)": " "; });
	}
	else {
		// remove nbgames text
		svg_4.selectAll(".nbgames").remove();

		// build/update mc button
		var mcbutton = svg_4.selectAll(".mcbutton")
				.data([mc_nb_games]);

		var mcgames = svg_4.selectAll(".mcgames")
				.data([mc_nb_games]);

		mcbutton.enter()
			.append("g")
				.attr("class", "mcbutton")
				.attr("transform", x_4(0))
				.each(function(data) {

					var button = d3.select(this)
						small_width = 20,
						gap = 10;

					// run button
					button.append("rect")
						.attr("y", y_41(0))
						.attr("width", x_4.rangeBand())
						.attr("height", y_41.rangeBand())
						.on("click", run_montecarlo);

					button.append("text")
						.attr("class", "mcgames")
						.attr("x", x_4.rangeBand()/2)
						.attr("y", y_41(0) + y_41.rangeBand()/2)
						.attr("dy", "0.3em")
						.attr("text-anchor", "middle")
						.text(function (d) { return "run monte carlo: " + fmt_int(mc_nb_games) + " games" ; });

					// plus button
					button.append("rect")
						.attr("x", x_4.rangeBand() + gap)
						.attr("y", y_42(0))
						.attr("width", small_width)
						.attr("height", y_42.rangeBand())
						.on("click", mc_nb_games_plus);

					button.append("text")
						.attr("x", x_4.rangeBand() + gap + small_width/2)
						.attr("y", y_42(0) + y_42.rangeBand()/2)
						.attr("dy", "0.3em")
						.attr("text-anchor", "middle")
						.text("+");

					// minus button
					button.append("rect")
						.attr("x", x_4.rangeBand() + gap)
						.attr("y", y_42(1))
						.attr("width", small_width)
						.attr("height", y_42.rangeBand())
						.on("click", mc_nb_games_minus);

					button.append("text")
						.attr("x", x_4.rangeBand() + gap + small_width/2)
						.attr("y", y_42(1) + y_42.rangeBand()/2)
						.attr("dy", "0.3em")
						.attr("text-anchor", "middle")
						.text("-");
				});

	mcgames.transition()
		.duration(0)
		.text(function (d) { return "run monte carlo: " + fmt_int(mc_nb_games) + " games" ; });

	}


	// build/update equity histogram
	var bars = svg_5.selectAll(".bar")
		.data(equity);

	var labels = svg_5.selectAll(".label")
		.data(equity);

	d3.selectAll(".showlabel").remove();
	var showlabels = svg_5.selectAll(".showlabel")
		.data(equity);


	bars.enter()
		.append("g")
			.attr("class", "bar")
			.attr("transform", function(d, i){ return "translate(" + x_5(i) + ", 0)"; })
			.on('mouseover', mouseover_bar)
			.on('mouseout', mouseout_bar)
			.each(function(d) {
				var bar = d3.select(this);

				bar.append("rect")
					.attr("class", "win")
					.attr("width", x_5.rangeBand())
					.attr("y", function(d) { return y_5(d.win); })
					.attr("height", function(d) { return height_5 - y_5(d.win); });

				bar.append("rect")
					.attr("class", "tie")
					.attr("width", x_5.rangeBand())
					.attr("y", function(d) { return y_5(d.win + d.tie); })
					.attr("height", function(d) { return y_5(d.win) - y_5(d.win + d.tie); });
			});

	bars.transition()
			.duration(0)
			.attr("transform", function(d, i){ return "translate(" + x_5(i) + ", 0)"; })
			.each(function(d, i) {
				var bar = d3.select(this);

				bar.select(".win")
					.attr("width", x_5.rangeBand())
					.attr("y", function(d) { return y_5(d.win); })
					.attr("height", function(d) { return height_5 - y_5(d.win); });

				bar.select(".tie")
					.attr("width", x_5.rangeBand())
					.attr("y", function(d) { return y_5(d.win + d.tie); })
					.attr("height", function(d) { return y_5(d.win) - y_5(d.win + d.tie); });
			});

	bars.exit().transition().duration(dt).remove();

	labels.enter()
		.append("text")
			.attr("class", "label")
			.attr("x", function(d, i) { return x_5(i)+x_5.rangeBand()/2; })
			.attr("y", function(d, i) { return y_5(d.win + d.tie + 0.1); })
			.attr("text-anchor", "middle")
			.text(function(d) { return fmt_float(d.win + d.tie); });

	labels.transition()
			.duration(0)
			.attr("x", function(d, i) { return x_5(i)+x_5.rangeBand()/2; })
			.attr("y", function(d, i) { return y_5(d.win + d.tie + 0.05); })
			.text(function(d) { return fmt_float(100 * (d.win + d.tie)); });

	labels.exit().transition().duration(dt).remove();


	showlabels.enter()
		.append("g")
			.attr("class", "showlabel")
			.attr("transform", function(d, i){ return "translate(" + (x_5(i)+x_5.rangeBand()/2) + ", 0)"; })
			.each(function(d) {
				var showlabel = d3.select(this);

				showlabel.append("text")
					.attr("class", "handtype")
					.attr("y", function(d, i) { return d.winner==1 ? y_5(pos_showlabel(d)) : y_5(1/3) ; })
					.attr("dy", "-1.1em")
					.attr("text-anchor", "middle")
					.text(function(d) { return d.rank!=undefined ? d.handtype1 : " " ; })

				showlabel.append("text")
					.attr("class", "handtype")
					.attr("y", function(d, i) { return d.winner==1 ? y_5(pos_showlabel(d)) : y_5(1/3) ; })
					.attr("dy", "0.0em")
					.attr("text-anchor", "middle")
					.text(function(d) { return d.rank!=undefined ? d.handtype2 : " " ; })

				showlabel.append("text")
					.attr("class", "handrank")
					.attr("y", function(d, i) { return d.winner==1 ? y_5(pos_showlabel(d)) : y_5(1/3) ; })
					.attr("dy", "1.3em")
					.attr("text-anchor", "middle")
					.text(function(d) { return d.rank!=undefined ? d.rank : " " ; })
			});


	if (exhaustive) {
		svg_6.selectAll(".playermc").remove();
	}
	else {
		var playermc = svg_6.selectAll(".playermc")
			.data([0]),
		gap = 5;

		playermc.enter()
			.append("rect")
				.attr("class", "playermc")
				.attr("x", function(d) { return x_6(d) + x_6.rangeBand()/2 - width_full_card/2 -gap; })
				.attr("y", y_6(0) -gap)
				.attr("width", width_full_card + 2*gap)
				.attr("height", 2*height_full_card + 3*gap);


		playermc.transition()
				.duration(0)
				.attr("class", "playermc")
				.attr("x", function(d) { return x_6(d) + x_6.rangeBand()/2 - width_full_card/2 -gap; })
				.attr("y", y_6(0) -gap)
				.attr("width", width_full_card + 2*gap)
				.attr("height", 2*height_full_card + 3*gap);
	}



	// show active card
	d3.selectAll(".tablecard rect").classed("active", function(d, i) {  return d.idx == idx_active; });
	d3.selectAll(".playercard rect").classed("active", function(d, i) { return d.idx == idx_active; });

	// mc runs can only be lauched from mc buttonf
	mc_to_run = false;
}


function pos_showlabel(d) {
	if (d.win+d.tie>1-0.01) { return 0.66; }
	else if (d.win+d.tie>1/2-0.01) { return 0.85; }
	else if (d.win+d.tie>1/3-0.01) { return 0.75; }
	else { return 0.66; }
}


function onchange_players(d) {
	var old_nb_player = nb_player,
		no,fs, f, s;

	nb_player = +d.value;

	for (var p=old_nb_player-1; p>=nb_player; p--) {
		for(var c=0; c<2; c++) {
			window.p = p;
			window.c = c;

			if (player_card_data[p][c].card_no!=-1) {
				no = player_card_data[p][c].card_no;
				fs = to_fs(no);
				f = fs[0];
				s = fs[1];

				deck_card[no] = 1;
				deck_card_data[s][f].avail = 1;
			}
			if (player_card_data[p][c].card_no==idx_active) {
				idx_active = -1;
			}
		}
		player_card_data.pop();
	}

	for (var p=old_nb_player; p<nb_player; p++) {
		player_card_data [p] = new Array(2)
		for (var c=0; c<2; c++) {
			// player_card_data[p][c] = {'player' : p, 'card' : c, 'card_no' : -1};
			player_card_data[p][c] = {'player' : p, 'card' : c, 'card_no' : -1, 'idx' : 6+2*p+c};
		}
	}

	equity = equity_zero(nb_player);

	update_viz(nb_player);
}



function mouseclick_deck(card_selected) {
	console.log("deckcard, card_no="+card_selected.card_no+", "+"avail="+card_selected.avail);

	var no, fs, f, s, t, p , c;

	if (idx_active!=-1) {
		no = card_selected.card_no;
		fs = to_fs(no);
		f = fs[0];
		s = fs[1];

		deck_card[no] = 0;
		deck_card_data[s][f].avail = 0;

		if (idx_active<5) {
			t = idx_active;
			table_card_data[t].card_no = no;
		}
		else {
			p = Math.floor((idx_active - 6) / 2);
			c = (idx_active - 6) % 2;
			player_card_data[p][c].card_no = no;
		}

		card_selected.avail = 0;
		idx_active = -1;
	}

	update_viz(nb_player);
}

function mouseclick_table(card_selected) {
	console.log("tablecard, idx="+card_selected.idx+", "+"card_no="+card_selected.card_no);

	var idx_selected = card_selected.idx,
		card_no_selected = card_selected.card_no;

	if (idx_active==idx_selected) {
		idx_active = -1;
	}
	else if (card_no_selected==-1) {
		idx_active = idx_selected;
	}
	else if ((card_no_selected!=-1) && (idx_active!=-1)) {
		idx_active = -1;
	}
	else if ((card_no_selected!=-1) && (idx_active==-1)) {
		reset_tablecards([idx_selected]);
	}

	update_viz(nb_player);
}

function mouseclick_player(card_selected) {
	console.log("tablecard, card="+card_selected.card+", "+"card_no="+card_selected.card_no+", idx="+card_selected.idx);

	var idx_selected = card_selected.idx,
		card_no_selected = card_selected.card_no;

	if (idx_active==idx_selected) {
		idx_active = -1;
	}
	else if (card_no_selected==-1) {
		idx_active = idx_selected;
	}
	else if ((card_no_selected!=-1) && (idx_active!=-1)) {
		idx_active = -1;
	}
	else if ((card_no_selected!=-1) && (idx_active==-1)) {
		reset_one_playercard([idx_selected]);
	}

	update_viz(nb_player);
}



function reset_tablecards(cards) {
	var fs, f, s, no;

	// put card(s) back to deck
	for (var q=0; q<cards.length; q++) {
		k = cards[q];
		no = table_card_data[k].card_no;
		if (no!=-1) {
			fs = to_fs(no);
			f = fs[0];
			s = fs[1];

			deck_card[no] = 1;
			deck_card_data[s][f].avail = 1;

			table_card_data[k].card_no = -1;
		}
	}
}


function reset_table(cards) {
	reset_tablecards([0, 1, 2, 3, 4]);

	update_viz(nb_player);
}


function shuffle_flop() {
	console.log("shuffle_flop");

	var fs, f, s, no;

	// put card(s) back to deck
	reset_tablecards([0, 1, 2]);

	// random draw card(s) and update deck data
	var draw = draw_deck_cards(3);

	// update table data
	for(var k=0; k<3; k++) {
		table_card_data[k].card_no = draw[k];
	}

	// deactivate card(s)
	if (idx_active<3) {
		idx_active = -1;
	}

	update_viz(nb_player);
}


function shuffle_turn() {
	console.log("shuffle_turn");

	var fs, f, s, no, k = 3;

	// put card(s) back to deck
	reset_tablecards([k]);

	// random draw card(s) and update deck data
	var draw = draw_deck_cards(1)[0];

	// update table data
	table_card_data[k].card_no = draw;

	// deactivate card(s)
	if (idx_active==k) {
		idx_active = -1;
	}

	update_viz(nb_player);
}


function shuffle_river() {
	console.log("shuffle_river");

	var fs, f, s, no, k = 4;

	// put card(s) back to deck
	reset_tablecards([k]);

	// random draw card(s) and update deck data
	var draw = draw_deck_cards(1)[0];

	// update table data
	table_card_data[k].card_no = draw;

	// deactivate card(s)
	if (idx_active==k) {
		idx_active = -1;
	}

	update_viz(nb_player);
}


function reset_one_playercard(idx) {

	var p = Math.floor((idx - 6) / 2),
		c = (idx - 6) % 2,
		fs, f, s, no;

	// console.log("p="+p+", c="+c+", idx="+idx);
	no = player_card_data[p][c].card_no;
	if (no!=-1) {
		fs = to_fs(no);
		f = fs[0];
		s = fs[1];
		// console.log("f="+f+", s="+s+", no="+no);
		deck_card[no] = 1;
		deck_card_data[s][f].avail = 1;

		player_card_data[p][c].card_no = -1;
	}
}




function reset_playercards(players) {
	var fs, f, s, no;

	for (var q=0; q<players.length; q++) {
		p = players[q];
		for (var k=0; k<2; k++) {
			no = player_card_data[p][k].card_no;

			if (no!=-1) {
				fs = to_fs(no);
				f = fs[0];
				s = fs[1];

				deck_card[no] = 1;
				deck_card_data[s][f].avail = 1;

				player_card_data[p][k].card_no = -1;
			}
		}
	}
}


function reset_player_all(players) {
	reset_playercards(d3.range(nb_player));

	// deactivate card(s)
	if (idx_active>5) {
		idx_active = -1;
	}

	update_viz(nb_player);
}


function shuffle_player(p) {
	console.log("shuffle_player no "+p);

	var fs, f, s, no;

	// put card(s) back to deck
	reset_playercards([p]);

	// random draw card(s) and update deck data
	var draw = draw_deck_cards(2);

	// update table data
	for(var k=0; k<2; k++) {
		player_card_data[p][k].card_no = draw[k];
	}

	// deactivate card(s)
	if ((idx_active==6+2*p) || (idx_active==6+2*p+1) ) {
		idx_active = -1;
	}

	update_viz(nb_player);
}



function shuffle_player_all() {
	console.log("shuffle_player_all");

	var fs, f, s, no;

	// put card(s) back to deck
	reset_playercards(d3.range(nb_player));

	// random draw card(s) and update deck data
	var draw = draw_deck_cards(2*nb_player);

	// update table data
	for (var p=0; p<nb_player; p++) {
		for(var k=0; k<2; k++) {
			player_card[2*p+k] = draw[2*p+k];
			player_card_data[p][k].card_no = draw[2*p+k];
		}
	}

	// deactivate card(s)
	if (idx_active>5) {
		idx_active = -1;
	}

	update_viz(nb_player);
}



function draw_deck_cards(n) {
	var unavail_card = [],
		c = 0,
		draw = [],
		rnd, valid, fs, f, s;

	for(var k=0; k<deck_card.length; k++) {
		if (deck_card[k]==-1) {
			unavail_card.push(k);
		}
	}

	while (draw.length<n) {
		rnd = Math.min(Math.floor(Math.random()*(51-unavail_card.length+1)), 51);
		valid = 1;
		for(var k=0; k<unavail_card.length; k++) {
			if (rnd==unavail_card[k]) { valid = 0; }
		}
		if (valid==1) {
			draw.push(rnd);
			fs = to_fs(rnd);
			f = fs[0];
			s = fs[1];
			// console.log("f="+f+", s="+s+", rnd="+rnd);
			unavail_card.push(rnd);
			deck_card[rnd] = -1;
			deck_card_data[s][f].avail = 0;
		}
	}

	window.unavail_card = unavail_card;
	window.draw = draw;

	return	draw;
}



function update_equity_exhaustive(nb_player) {
	console.log("update_equity_exhaustive");

	var valid_players = [],
		nb_valid_players,
		player_card,
		table_card,
		valid_table,
		equity_valid_players,
		results;

	equity = new Array(nb_player);

	for(var p=0; p<nb_player; p++) {
		if ((player_card_data[p][0].card_no!=-1) && (player_card_data[p][1].card_no!=-1)) {
			valid_players.push(p);
		}
	}


	player_card = new Array(valid_players.length);
	for(var p=0; p<player_card.length; p++) {
		player_card[p] = new Array(2);
		player_card[p][0] = player_card_data[valid_players[p]][0].card_no;
		player_card[p][1] = player_card_data[valid_players[p]][1].card_no;
	}


	if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no!=-1) && (table_card_data[4].card_no!=-1)) {
		table_card = new Array(5);
		for(var t=0; t<5; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no!=-1) && (table_card_data[4].card_no==-1)) {
			table_card = new Array(4);
		for(var t=0; t<4; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no==-1) && (table_card_data[4].card_no==-1)) {
		table_card = new Array(3);
		for(var t=0; t<3; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no==-1) && (table_card_data[1].card_no==-1) && (table_card_data[2].card_no==-1) && (table_card_data[3].card_no==-1) && (table_card_data[4].card_no==-1)) {
		table_card = [];
		valid_table = true;
	}


	if ((valid_players.length>1) && (valid_table==1)) {
		// equity_valid_players = compute_equity_fake_exhaustive(valid_players.length);
		results = compute_equity_exhaustive(player_card, table_card);
		equity_valid_players = results[0];
		nb_games = results[1];


		k = 0;
		for(var p=0; p<nb_player; p++) {
			if (p==valid_players[k]) {
				equity[p] = equity_valid_players[k];
				k ++;
			}
			else {
				equity[p] = { 'win' : 0, 'tie' : 0 };
			}
		}
	}
	else {
		for(var p=0; p<nb_player; p++) {
			equity[p] = { 'win' : 0, 'tie' : 0 };
		}
	}

	window.valid_players = valid_players;
	window.player_card = player_card;
	window.table_card = table_card;
	window.equity_valid_players = equity_valid_players;
}




function update_equity_montecarlo(nb_player) {
	console.log("update_equity_montecarlo");

	var active_player,
		player_card,
		table_card,
		valid_active_player,
		valid_table,
		equity_active_player,
		results,
		q;

	equity = new Array(nb_player);
	active_player = 0;


	player_card = new Array(nb_player);
	for(var p=0; p<nb_player; p++) {

		player_card[p] = new Array(2);
		player_card[p][0] = player_card_data[p][0].card_no;
		player_card[p][1] = player_card_data[p][1].card_no;
	}
	console.log("player_card[0]="+player_card[0]);


	if ((player_card[0][0]!=-1) && (player_card[0][1]!=-1)) {
		valid_active_player  = true;
	}
	else {
		valid_active_player = false;
	}


	if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no!=-1) && (table_card_data[4].card_no!=-1)) {
		table_card = new Array(5);
		for(var t=0; t<5; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no!=-1) && (table_card_data[4].card_no==-1)) {
			table_card = new Array(4);
		for(var t=0; t<4; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no!=-1) && (table_card_data[1].card_no!=-1) && (table_card_data[2].card_no!=-1) && (table_card_data[3].card_no==-1) && (table_card_data[4].card_no==-1)) {
		table_card = new Array(3);
		for(var t=0; t<3; t++) {
			table_card[t] = table_card_data[t].card_no;
		}
		valid_table = true;
	}
	else if ((table_card_data[0].card_no==-1) && (table_card_data[1].card_no==-1) && (table_card_data[2].card_no==-1) && (table_card_data[3].card_no==-1) && (table_card_data[4].card_no==-1)) {
		table_card = [];
		valid_table = true;
	}

	console.log("valid_table="+valid_table);
	console.log("valid_active_player="+valid_active_player);

	if ((valid_active_player==1) && (valid_table==1)) {
		// equity_active_player = compute_equity_fake_mc(nb_player);
		equity_active_player = compute_equity_montecarlo(player_card, table_card, mc_nb_games);

		equity[0] = equity_active_player;
		for(var p=1; p<nb_player; p++) {
			equity[p] = { 'win' : 0, 'tie' : 0 };
		}
	}
	else {
		for(var p=0; p<nb_player; p++) {
			equity[p] = { 'win' : 0, 'tie' : 0 };
		}
	}

	window.active_player = active_player;
	window.table_card_update_mc = table_card;
	window.player_card_update_mc = player_card;
	window.equity_active_player = equity_active_player;
}




function compute_equity_fake(nb_player) {
	var rnd = new Array(2*nb_player),
		curr_sum = 0,
		eqty = new Array(nb_player);

	for(var r=0; r<2*nb_player-1; r++) {
		rnd[r] = Math.random()/(2*nb_player)*1.5;
		curr_sum += rnd[r];
	}
	rnd[2*nb_player-1] = 1-curr_sum;

	for(var p=0; p<nb_player; p++) {
		eqty[p] = { 'win' : rnd[2*p], 'tie' : rnd[2*p+1] };
	}

	return eqty;
}


function compute_equity_fake_mc(nb_player) {
	var	rnd = [Math.random()/2, Math.random()/2];

	return { 'win' : rnd[0], 'tie' : rnd[1] };;
}

function equity_zero(nb_player) {
	var eqty = new Array(nb_player);

	for(var p=0; p<nb_player; p++) {
		eqty[p] = { 'win' : 0, 'tie' : 0 };
	}

	return eqty;
}


function mouseover_bar(bar){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "Eqty : <strong>"+fmt_float_tp(100 * (bar.win + bar.tie))+" %</strong><br>" +
										"Wins : <strong>"+fmt_float_tp(100 * bar.win)+" %</strong><br>" +
										"Ties : <strong>"+fmt_float_tp(100 * bar.tie)+" %</strong><br>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 60) + "px");
}

function mouseout_bar(bar){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0);
}



function test_draw() {
	// debugging
	// test if same card twice in game
	var cc = 0,
		arr = [],
		valid,
		cand,
		test = 1;
	for(var k=0; k<5; k++) {
		cand = table_card_data[k].card_no;
		if (cand!=-1) {
			valid = 1;
			for(var q=0; q<arr.length; q++) {
				if (cand==arr[q]) { valid = 0; test = 0;}
			}
			if (valid) { arr.push(cand); }
		}
	}
	for(var p=0; p<nb_player; p++) {
		for(var c=0; c<2; c++) {
			cand = player_card_data[p][c].card_no;
			if (cand!=-1) {
				valid = 1;
				for(var q=0; q<arr.length; q++) {
					if (cand==arr[q]) { valid = 0; test = 0;}
				}
				if (valid) { arr.push(cand); }
			}
		}
	}
	console.log("test="+(test==1) ? "ok" : "not ok");
	// console.log("nb different cards="+arr.length);
	// console.log("cards="+arr);
}


function exhaustive_mode() {
	console.log("exhaustive_mode");
	exhaustive = true;

	equity = equity_zero(nb_player);

	update_viz(nb_player);
}


function montecarlo_mode() {
	console.log("montecarlo_mode");
	exhaustive = false;

	equity = equity_zero(nb_player);
	mc_to_run = false;

	update_viz(nb_player);
}


function run_montecarlo() {
	console.log("run_montecarlo");
	mc_to_run = true;

	update_viz(nb_player);
}


function mc_nb_games_plus() {
	console.log("mc_nb_games_plus");
	mc_nb_games = mc_nb_games + 1e4;
	mc_to_run = false;

	update_viz(nb_player);
}

function mc_nb_games_minus() {
	console.log("mc_nb_games_minus");
	mc_nb_games = Math.max(1e4, mc_nb_games - 1e4);
	mc_to_run = false;

	update_viz(nb_player);
}


