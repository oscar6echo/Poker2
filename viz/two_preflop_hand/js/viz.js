

var margin_1 = {top: 30, right: 10, bottom: 20, left: 90},
	width_1 = 600,
	height_1 = 200;

var margin_2 = {top: 15, right: 10, bottom: 20, left: 90},
	width_2 = 350,
	height_2 = 100;

var margin_3 = {top: 90, right: 10, bottom: 10, left: 90},
	width_3 = 600,
	height_3 = width_3;


var y_1 = d3.scale.linear().range([height_1, 0]),
	x_2 = d3.scale.ordinal().rangeBands([0, width_2], 0.15, 0.25),
	y_2 = d3.scale.linear().range([height_2, 0]),
	x_3 = d3.scale.ordinal().rangeBands([0, width_3], 0.05, 0.05);

var c = d3.scale.linear().domain([0, 0.5, 1]).range(['blue', 'white', 'red']);

var f = d3.format(".2f");

var title = d3.select("#title")

var svg_1 = d3.select("#container")
	.append("svg")
		.attr("width", width_1 + margin_1.left + margin_1.right)
		.attr("height", height_1 + margin_1.top + margin_1.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_1.left + "," + margin_1.top + ")");

var svg_2 = d3.select("#container")
	.append("svg")
		.attr("width", width_2 + margin_2.left + margin_2.right)
		.attr("height", height_2 + margin_2.top + margin_2.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_2.left + "," + margin_2.top + ")");

var svg_3 = d3.select("#container")
	.append("svg")
		.attr("width", width_3 + margin_3.left + margin_3.right)
		.attr("height", height_3 + margin_3.top + margin_3.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_3.left + "," + margin_3.top + ")");

var y_1_axis_text,
	sel_A_no,
	sel_B_no;

var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);

var N = 169,
	hands = new Array(N),
	equity = new Array(N),
	dataset;
for (var i=0; i<N; i++) {
	equity[i] = new Array(N);
}

d3.csv("./data/df_two_hand_equity.csv", function(data) {
	dataset = data.map(function(d) { return [ d["HandA"], +d["HandA_no"], d["HandB"], +d["HandB_no"], +d["HandA_Wins"], +d["Ties"], +d["HandB_Wins"] ]; });
	var L = dataset.length;
	for (var i=0; i<L; i++) {
		if ((i<5) || (L-i<5)){ console.log(dataset[i]); }

		var p = dataset[i][1],
			q = dataset[i][3];
		hands[p] = dataset[i][0];

		obj_1 = {};
		obj_1.A_no = p;
		obj_1.B_no = q;
		obj_1.A = dataset[i][0];
		obj_1.B = dataset[i][2];
		obj_1.A_wins = dataset[i][4];
		obj_1.Ties = dataset[i][5];
		obj_1.B_wins = dataset[i][6];

		obj_2 = {};
		obj_2.A_no = q;
		obj_2.B_no = p;
		obj_2.A = dataset[i][2];
		obj_2.B = dataset[i][0];
		obj_2.A_wins = dataset[i][6];
		obj_2.Ties = dataset[i][5];
		obj_2.B_wins = dataset[i][4];
		equity[p][q] = obj_1;
		equity[q][p] = obj_2;
	}

	create_svg(hands, equity);
});



function create_svg(hands, equity){

	x_2.domain(d3.range(3));
	x_3.domain(d3.range(N));
	y_2.domain([0, 1]);
	y_1.domain([0, 1]);

	// draw x_1 axis
	svg_1.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_1 + ")")
			.call(d3.svg.axis().scale(x_3).orient("bottom").tickFormat(""))
		.append("text")
			.attr("x", width_1)
			.attr("y", 10)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Opponent Hand");
;

	// draw y_1 axis
	y_1_axis_text = svg_1.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_1).orient("left").ticks(5, "%"))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", -50)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("Hand Equity");

	// draw x_2 axis
	svg_2.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height_2 + ")")
		.call(d3.svg.axis().scale(x_2).orient("bottom").tickFormat(""))
		.selectAll("text")
			.style("text-anchor", "middle");

	// draw y_2 axis
	svg_2.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_2).orient("left").ticks(5, "%"))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", -50)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("Fraction of Pot");


	// draw title
	title.text("Equity Distribution for All Preflop Hand Pairs");


	// build matrix
	svg_3.append("rect")
		.attr("class", "background")
		.attr("width", width_3)
		.attr("height", height_3);

	var row = svg_3.selectAll(".row")
		.data(equity)
	.enter().append("g")
		.attr("class", "row")
		.attr("transform", function(d, i) { return "translate(0," + x_3(i) + ")"; })
		.each(create_row);

	row.append("line")
		.attr("x1", 0)
		.attr("x2", width_3);

	row.append("text")
		.attr("x", function(d, i){ return -6 -20 * (i % 4); })
		.attr("y", x_3.rangeBand() / 2)
		.attr("dy", "0.25em")
		.attr("text-anchor", "end")
		.text(function(d, i) { return hands[i]; });

	var column = svg_3.selectAll(".column")
		.data(hands)
	.enter().append("g")
		.attr("class", "column")
		.attr("transform", function(d, i) { return "translate(" + x_3(i) + ")rotate(-90)"; });

	column.append("line")
		.attr("x1", -height_3)
		.attr("x0", 0);


	column.append("text")
		.attr("x", function(d, i){ return 6 +20 * (i % 4); })
		.attr("y", x_3.rangeBand() / 2)
		.attr("dy", "0.25em")
		.attr("text-anchor", "start")
		.text(function(d, i) { return d; });

	d3.select("body").on("keydown", keyboard_update);
}



function create_row(row) {
	var cell = d3.select(this).selectAll(".cell")
		.data(row)
	.enter().append("svg:rect")
		.attr("class", "cell")
		.attr("x", function(d, i) { return x_3(i); })
		.attr("width", x_3.rangeBand())
		.attr("height", x_3.rangeBand())
		.attr("fill", function(d, i) { return c(d.A_wins+0.5*d.Ties); })
		.on("mouseover", mouseover_3)
		.on("mouseout", mouseout_3)
		.on("click", mouseclick_3);
}



function update(sel_A_no, sel_B_no){

	var selection = d3.selectAll(".cell").filter(function(d, i) { return (d.A_no == sel_A_no) && (d.B_no == sel_B_no); });
	var cell = selection.data()[0];
	window.cell = cell;

	var h = cell.A;
	var hist_data = [cell.A_wins, cell.Ties, cell.B_wins],
		hist_label = [cell.A+" wins", "Ties", cell.B+" wins"];

	d3.selectAll(".cell").classed("active", function(d, i) { return (d.A_no == sel_A_no) && (d.B_no == sel_B_no); });

	var plot_data = new Array(N);
	for (var i=0; i<N; i++) {
		var d = equity[sel_A_no][i];
		var obj = {};
		obj.hand = d.B;
		obj.hand_no = d.B_no;
		obj.eq = d.B_wins + 0.5 * d.Ties;
		plot_data[i] = obj;
	}

	window.hist_label = hist_label;
	window.hist_data = hist_data;
	window.plot_data = plot_data;

	// create/update histo svg_2
	var bars = svg_2.selectAll(".bar")
		.data(hist_data);

	var labels = svg_2.selectAll(".label")
		.data(hist_data);

	bars.enter()
		.append("svg:rect")
			.attr("class", "bar")
			.attr("x", function(d, i) { return x_2(i); })
			.attr("width", x_2.rangeBand())
			.attr("y", function(d) { return y_2(d); })
			.attr("height", function(d) { return height_2 - y_2(d); })
			.attr("fill", function(d){ return c(d);});

	bars.transition()
			.duration(0)
			.attr("x", function(d, i) { return x_2(i); })
			.attr("width", x_2.rangeBand())
			.attr("y", function(d) { return y_2(d); })
			.attr("height", function(d) { return height_2 - y_2(d); })
			.attr("fill", function(d){ return c(d);});;

	labels.enter()
		.append("svg:text")
			.attr("class", "label")
			.attr("x", function(d, i) { return x_2(i)+x_2.rangeBand()/2; })
			.attr("y", function(d, i) { return y_2(d + 0.1); })
			.attr("text-anchor", "middle")
			.text(function(d) { return f(100 * d)+"%"; });

	labels.transition()
			.duration(0)
			.attr("y", function(d, i) { return y_2(d + 0.1); })
			.text(function(d) { return f(100 * d)+"%"; });

	svg_2.selectAll(".x.axis")
		.transition()
			.duration(0)
			.call(d3.svg.axis().scale(x_2).orient("bottom").tickFormat(function(d, i) { return hist_label[i]; }));


	// create/update histo svg_1
	var circles = svg_1.selectAll(".circle")
		.data(plot_data);

	circles.enter()
		.append("svg:circle")
			.attr("class", "circle")
			.attr("r", 1.5)
			.attr("cx", function(d, i) { return x_3(i); })
			.attr("cy", function(d, i) { return y_1(d.eq); })
			.style("fill", function(d){ return c(d.eq);})
			.on('mouseover', mouseover_1)
			.on('mouseout', mouseout_1);

	circles.transition()
			.duration(0)
			.attr("r", 1.5)
			.attr("cx", function(d, i) { return x_3(i); })
			.attr("cy", function(d, i) { return y_1(d.eq); });


	y_1_axis_text.text(h+" Equity");
}


function mouseover_1(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<strong>" + circle.hand +"</strong> <span style='color:black'>" + f(100 * circle.eq) + "%</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 60) + "px");

	d3.selectAll(".column text").classed("active", function(d, i) { return i == circle.hand_no; });
}


function mouseout_1(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0);

	d3.selectAll(".column text").classed("active", false);
}


function mouseover_3(cell) {
	window.cell = cell;

	d3.selectAll(".row text").classed("active", function(d, i) { return i == cell.A_no; });
	d3.selectAll(".column text").classed("active", function(d, i) { return i == cell.B_no; });
}


function mouseout_3() {
	d3.selectAll(".row text").classed("active", false);
	d3.selectAll(".column text").classed("active", false);
}


function mouseclick_3(cell) {
	window.cell = cell;

	sel_A_no = cell.A_no;
	sel_B_no = cell.B_no;

	update(sel_A_no, sel_B_no);
}



function keyboard_update() {
	console.log("d3.event.keyCode = ", d3.event.keyCode);

	d3.selectAll(".row text").classed("active", function(d, i) { return i == sel_A_no; });
	d3.selectAll(".column text").classed("active", function(d, i) { return i == sel_B_no; });

	// left arrow	 37
	if (d3.event.keyCode==37) {
		sel_B_no = Math.max(0, sel_B_no-1);
	}

	// 	up arrow 38
	if (d3.event.keyCode==38) {
		sel_A_no = Math.max(0, sel_A_no-1);
	}

	// right arrow 39
	if (d3.event.keyCode==39) {
		sel_B_no = Math.min(N-1, sel_B_no+1);
	}

	// down arrow 40
	if (d3.event.keyCode==40) {
		sel_A_no = Math.min(N-1, sel_A_no+1);
	}

	update(sel_A_no, sel_B_no);
}


