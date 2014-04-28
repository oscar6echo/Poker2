

var hand_type = ["High Card", "One Pair", "Two Pairs", "Three Of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"];
var type_limits = [0, 1277, 4137, 4995, 5853, 5863, 7140, 7296, 7452, 7462];

var H ,		//169+1 = all preflop hands + virtual 'no hand'
	R,		//7462+1 = all hand ranks + top row = hand names
	hands,
	distrib,
	distrib_ref,
	hand_matrix,
	type_low = 0,
	type_high = type_limits.length-1,
	sel_row = 0,
	sel_col = 0,
	binsize = 100,
	y_1_max = 150000,
	dt = 0;



var margin_1 = {top: 40, right: 50, bottom: 30, left: 50},
	width_1 = 650,
	height_1 = 300;

var margin_2 = {top: 15, right: 50, bottom: 10, left: 50},
	width_2 = 650,
	height_2 = 50;

var margin_3 = {top: 10, right: 50, bottom: 10, left: 50},
	width_3 = 300,
	height_3 = width_3;


var x_1 = d3.scale.linear().range([0, width_1]),
	y_1 = d3.scale.linear().range([height_1, 0]),
	x_2 = d3.scale.ordinal().rangeBands([0, width_2], 0.05, 0.05),
	y_2 = d3.scale.ordinal().rangeBands([0, height_2], 0.10, 0.05),
	x_3 = d3.scale.ordinal().rangeBands([0, width_3], 0.05, 0.05);

var c_1 = d3.scale.category20c(),
	c_3 = d3.scale.ordinal().domain([-1, 0, 1]).range(['#8dd3c7', '#ffffb3', '#bebada']);

// color brewer_rng from http://colorbrewer2.org/ qualitative scale 9 classes
var colorbrewer_rng = ['rgb(166,206,227)','rgb(31,120,180)','rgb(178,223,138)','rgb(51,160,44)','rgb(251,154,153)','rgb(227,26,28)','rgb(253,191,111)','rgb(255,127,0)','rgb(202,178,214)'],
	c_1 = d3.scale.ordinal().domain(d3.range(9)).range(colorbrewer_rng);

// var	stroke = d3.scale.category20b();
// function color(d, i) { return d.length >1 ? stroke(1+1*i) : "red"; }

var fmt = d3.format(",d");

var title = d3.select("#title")

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

var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);



d3.text("./data/df_preflop_hand_distrib.csv", "text/csv", function(text) {
	var data = d3.csv.parseRows(text);
	window.dataset = data;

	R = data.length;
	console.log("R="+R);
	H = data[0].length;
	console.log("H="+H);

	// create hands, distrib
	hands = new Array(H-1);
	distrib = new Array(H-1);
	distrib_ref = new Array(R-1);
	for (var h=0; h<H-1; h++) {
		distrib[h] = new Array(R-1);
	}

	// fill hands
	for (var h = 1; h < H; h++) {
		hands[h-1] = data[0][h];
	}

	// fill distrib, distrib_ref
	for (var r = 1; r < R; r++) {
		distrib_ref[r-1] = +data[r][0];
		for (var h = 1; h < H; h++) {
			distrib[h-1][r-1] = +data[r][h];
		}
	}

	// normalize distrib_ref
	var sum_no_hand = d3.sum(distrib_ref);
	console.log("sum_no_hand="+sum_no_hand);
	var sum_one_hand = d3.sum(distrib[0]);
	console.log("sum_one_hand="+sum_one_hand);
	for (var r = 0; r < R-1; r++) {
		distrib_ref[r] = distrib_ref[r] * sum_one_hand/sum_no_hand;
	}

	// create hand_matrix
	hand_matrix = new Array(13);
	for (var k=0; k<13; k++) {
		hand_matrix[k] = new Array(13);
	}
	s = 1;
	for (var h=0; h<H-1; h++) {
		row = Math.floor(h/13);
		col = h%13;
		hand_matrix[row][col] = { 'hand' : hands[h], 'row' : row, 'col' : col };
	}

	//create hand_type_low/high
	hand_type_low = new Array(hand_type.length);
	hand_type_high = new Array(hand_type.length);
	for (var k=0; k<hand_type.length; k++) {
		hand_type_low[k] = {'row' : 0, 'col' : k, 'type' : hand_type[k]};
		hand_type_high[k] = {'row' : 1, 'col' : k, 'type' : hand_type[k]};
	}


	create_viz(hands, distrib, type_limits);
});



function create_viz(hands, equity, type_limits, dt){

	// y_1_max = d3.max(distrib.map(function (d) { return d3.max(d); }));

	x_1.domain([0, R-2]);
	y_1.domain([0, y_1_max]);
	x_2.domain(d3.range(hand_type.length));
	y_2.domain(d3.range(2));
	x_3.domain(d3.range(13));


	// draw title
	title.text("Hand Rank Distribution for All Preflop Hands");


	// draw x_1 axis
	svg_1.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_1 + ")")
			.call(d3.svg.axis().scale(x_1).orient("bottom").tickFormat(fmt))
		.append("text")
			.attr("x", width_1)
			.attr("y", 20)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Hand Rank");

	// draw y_1 axis
	y_1_axis_text = svg_1.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_1).orient("left").ticks(5).tickFormat(fmt))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 8)
		.attr("dy", "0.71em")
		.style("text-anchor", "end")
		.text("Nb Hands");


	// build hand_type
	svg_2.append("rect")
		.attr("class", "background")
		.attr("width", width_2)
		.attr("height", height_2);

	svg_2.selectAll("text")
			.data(["From", "To"])
		.enter().append("text")
			.attr("x", -x_2.rangeBand()/4)
			.attr("y", function(d, i){ return y_2(i) + y_2.rangeBand()/2; })
			.attr("dy", "0.4em")
			.attr("text-anchor", "end")
			.text(function (d){ return d; });


	// build hand_type
	var row_type = svg_2.selectAll(".rowtype")
		.data([hand_type_low, hand_type_high])
	.enter().append("g")
		.attr("transform", function(d, i) { return "translate(0, "+ y_2(i) +")"; })
		.each(create_row_type_hand);


	// build hand_matrix
	svg_3.append("rect")
		.attr("class", "background")
		.attr("width", width_3)
		.attr("height", height_3);

	var row_matrix = svg_3.selectAll(".row_matrix")
		.data(hand_matrix)
	.enter().append("g")
		.attr("class", "row_matrix")
		.attr("transform", function(d, i) { return "translate(0," + x_3(i) + ")"; })
		.each(create_row_hand_matrix);


	d3.select("body").on("keydown", keyboard_update);

	d3.select("#outputsliderbinsize").append("text").text(fmt(binsize));
	d3.select("#outputsliderhands").append("text").text(fmt(y_1_max));

	d3.selectAll(".typelow").classed("active", function(d, i) { return (d.col == type_low); });
	d3.selectAll(".typehigh").classed("active", function(d, i) { return (d.col == type_high-1); });
}


function create_row_type_hand(row) {
	var cell_type = d3.select(this).selectAll(".celltype")
		.data(row)
	.enter().append("g")
		.attr("class", function(d, i){ return (d.row==0) ? "typelow" : "typehigh"; })
		.attr("transform", function(d, i) { return "translate(" + x_2(i) + ", 0)"; });

	cell_type.append("rect")
		.attr("width", x_2.rangeBand())
		.attr("height", y_2.rangeBand())
		.attr("fill", function(d, i) { return c_1(i); })
		.on("click", mouseclick_2);

	cell_type.append("text")
		.attr("x", x_2.rangeBand()/2)
		.attr("y", y_2.rangeBand()/2)
		.attr("dy", "0.4em")
		.attr("text-anchor", "middle")
		.text(function(d, i) { return d.type; });
}


function create_row_hand_matrix(row) {
	var cell = d3.select(this).selectAll(".cell")
		.data(row)
	.enter().append("g")
		.attr("class", "cell")
		.attr("transform", function(d, i) { return "translate(" + x_3(i) + ", 0)"; });

	cell.append("rect")
		.attr("width", x_3.rangeBand())
		.attr("height", x_3.rangeBand())
		.attr("fill", function(d, i) { return c_3(d.row < d.col ? -1 : (d.row > d.col ? 1: 0 )); })
		.on("click", mouseclick_3);

	cell.append("text")
		.attr("x", x_3.rangeBand()/2)
		.attr("y", x_3.rangeBand()/2)
		.attr("dy", "0.3em")
		.attr("text-anchor", "middle")
		.text(function(d, i) { return d.hand; });
}


function mouseclick_2(cell) {
	window.cell = cell;
	var row = cell.row;
	var col = cell.col;

	if (cell.row==0){
		type_low = Math.min(cell.col, type_high-1);
	}
	else{
		type_high = Math.max(cell.col, type_low)+1;
	}
	d3.selectAll(".bar").remove();
	d3.selectAll(".refbar").remove();
	dt = 0;
	update(sel_row, sel_col, type_low, type_high, binsize, dt);
}


function mouseclick_3(cell) {
	window.cell = cell;

	sel_row = cell.row;
	sel_col = cell.col;
	dt = 500;
	update(sel_row, sel_col, type_low, type_high, binsize, dt);
}


function keyboard_update() {
	// console.log("d3.event.keyCode = ", d3.event.keyCode);

	// left arrow	 37
	if (d3.event.keyCode==37) {
		sel_col = Math.max(0, sel_col-1);
	}

	// 	up arrow 38
	if (d3.event.keyCode==38) {
		sel_row = Math.max(0, sel_row-1);
	}

	// right arrow 39
	if (d3.event.keyCode==39) {
		sel_col = Math.min(13-1, sel_col+1);
	}

	// down arrow 40
	if (d3.event.keyCode==40) {
		sel_row = Math.min(13-1, sel_row+1);
	}

	d3.selectAll(".cell").classed("active", function(d, i) { return (d.row == sel_row) & (d.col == sel_col); });
	dt = 500;
	update(sel_row, sel_col, type_low, type_high, binsize, dt);
}

function onchange_binsize(d) {
	binsize = +d.value;
	d3.select("#outputsliderbinsize").selectAll("text")
		.transition()
		.duration(0)
		.text(fmt(binsize));

	d3.selectAll(".bar").remove();
	d3.selectAll(".refbar").remove();
	dt = 0;
	update(sel_row, sel_col, type_low, type_high, binsize, dt);
}

function onchange_hands(d) {
	y_1_max = +d.value;
	d3.select("#outputsliderhands").selectAll("text")
		.transition()
		.duration(0)
		.text(fmt(y_1_max));

	y_1.domain([0, y_1_max]);
	dt = 0;
	update(sel_row, sel_col, type_low, type_high, binsize, dt);
}


function mouseover_1(bar){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "Bin # : <strong>"+fmt(bar.bin_no)+"</strong><br>" +
										"Low : <strong>"+fmt(bar.low)+"</strong><br>" +
										"High : <strong>"+fmt(bar.high-1)+"</strong><br>" +
										"NbHands : <strong>"+fmt(bar.nb_hands)+"</strong><br>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 80) + "px");
}


function mouseout_1(bar){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0);
}


function type_no(n) {
	if (n==0){
		return 0;
	}
	else{
		var k = 0;
		while (type_limits[k]<=n){
			k++;
		}
		return k-1;
	}
}



function update(sel_row, sel_col, type_low, type_high, binsize, dt){

	d3.selectAll(".typelow").classed("active", function(d, i) { return (d.col == type_low); });
	d3.selectAll(".typehigh").classed("active", function(d, i) { return (d.col == type_high-1); });
	d3.selectAll(".cell").classed("active", function(d, i) { return (d.row == sel_row) && (d.col == sel_col); });

	// compute values
	var hand_no = sel_row*13+sel_col;
	var values = distrib[hand_no];
	var limits = type_limits.slice(type_low, type_high+1);
	var limit_low = limits[0],
		limit_high = limits[limits.length-1];
	x_1.domain([limit_low, limit_high]);

	// compute bounds
	var bounds = d3.range(limit_low, limit_high+1, binsize);
	for (var k=0; k<limits.length; k++) {
		if (bounds.indexOf(limits[k])==-1) {
			bounds.push(limits[k]);
		}
	}
	bounds.sort(d3.ascending);

	// compute data
	var data = new Array(bounds.length-1);
	for (var k=0; k<bounds.length-1; k++) {
		data[k] = {"bin_no" : k, "low" : bounds[k], "high" : bounds[k+1], "nb_hands" : d3.sum(values.slice(bounds[k], bounds[k+1]))};
	}

	// compute data_ref
	var values_ref = distrib_ref;
	var data_ref = new Array(bounds.length-1);
	for (var k=0; k<bounds.length-1; k++) {
		data_ref[k] = {"bin_no" : k, "low" : bounds[k], "high" : bounds[k+1], "nb_hands" : d3.sum(values_ref.slice(bounds[k], bounds[k+1]))};
	}


	// console.log("sel_row="+sel_row);
	// console.log("sel_col="+sel_col);
	// console.log("hand_no="+hand_no);
	// console.log("x_1.domain()="+x_1.domain());
	// console.log("x_1.range()="+x_1.range());
	// console.log("type_low="+type_low);
	// console.log("type_high="+type_high);
	// console.log("limit_low="+limit_low);
	// console.log("limit_high="+limit_high);
	// console.log("type_limits="+type_limits);
	// console.log("y_1_max="+y_1_max);

	window.limits = limits;
	window.limit_low = limit_low;
	window.limit_high = limit_high;
	window.bounds = bounds;
	window.data = data;
	window.data_ref = data_ref;
	window.values = values;



	// create/update histo REF svg_1
	var refbars = svg_1.selectAll(".refbar")
			.data(data_ref);

	refbars.enter()
		.append("rect")
			.attr("class", "refbar")
			.attr("x", function(d, i){ return x_1(d.low); })
			.attr("y", function(d, i){ return y_1(d.nb_hands); })
			.attr("width", function(d, i){ return x_1(d.high-1) - x_1(d.low); })
			.attr("height", function(d) { return height_1 - y_1(d.nb_hands); })
			.attr("fill", function(d){ return c_1(type_no(d.low)); });

	refbars.transition()
		.duration(dt)
		.attr("x", function(d, i){ return x_1(d.low); })
		.attr("y", function(d, i){ return y_1(d.nb_hands); })
		.attr("width", function(d, i){ return x_1(d.high-1) - x_1(d.low); })
		.attr("height", function(d) { return height_1 - y_1(d.nb_hands); })
		.attr("fill", function(d){ return c_1(type_no(d.low)); });


	// create/update histo svg_1
	var bars = svg_1.selectAll(".bar")
			.data(data);

	bars.enter()
		.append("rect")
			.attr("class", "bar")
			.attr("x", function(d, i){ return x_1(d.low); })
			.attr("y", function(d, i){ return y_1(d.nb_hands); })
			.attr("width", function(d, i){ return x_1(d.high-1*0) - x_1(d.low); })
			.attr("height", function(d) { return height_1 - y_1(d.nb_hands); })
			.attr("fill", function(d){ return c_1(type_no(d.low)); })
			.on('mouseover', mouseover_1)
			.on('mouseout', mouseout_1);

	bars.transition()
		.duration(dt)
		.attr("x", function(d, i){ return x_1(d.low); })
		.attr("y", function(d, i){ return y_1(d.nb_hands); })
		.attr("width", function(d, i){ return x_1(d.high-1*0) - x_1(d.low); })
		.attr("height", function(d) { return height_1 - y_1(d.nb_hands); })
		.attr("fill", function(d){ return c_1(type_no(d.low)); });

	// update x_1
	svg_1.selectAll(".x.axis")
		.transition()
			.duration(dt)
			.call(d3.svg.axis().scale(x_1).orient("bottom").tickFormat(fmt));



	// update x_1
	svg_1.selectAll(".x.axis")
		.transition()
			.duration(dt)
			.call(d3.svg.axis().scale(x_1).orient("bottom").tickFormat(fmt));


	// var y_1_min = d3.min(data.map(function (d) { return d.nb_hands; }));
	// var y_1_max = d3.max(data.map(function (d) { return d.nb_hands; }));
	// y_1.domain([0, y_1_max]);

	// update y_1
	svg_1.selectAll(".y.axis")
		.transition()
			.duration(dt)
			.call(d3.svg.axis().scale(y_1).orient("left").ticks(5).tickFormat(fmt));


}




