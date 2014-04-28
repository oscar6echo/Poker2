


var R ,
	C,
	hands,
	equitydata,
	handrank,
	dataset,
	hand_matrix,
	sel_row = 0,
	sel_col = 0,
	y_1_max = 1.0,
	dt = 200;



var margin_1 = {top: 40, right: 25, bottom: 30, left: 25},
	width_1 = 600,
	height_1 = 150;

var margin_2 = {top: 15, right: 25, bottom: 30, left: 25},
	width_2 = 600,
	height_2 = 150;

var margin_3 = {top: 15, right: 25, bottom: 30, left: 25},
	width_3 = 600,
	height_3 = 150;

var margin_4 = {top: 10, right: 25, bottom: 30, left: 25},
	width_4 = 300,
	height_4 = width_4;


var x_1 = d3.scale.ordinal().domain(d3.range(1, 10)).rangePoints([0, width_1], 1.5),
	y_1 = d3.scale.linear().domain([0, 1.5]).range([height_1, 0]),

	x_2 = x_1,
	y_2 = d3.scale.linear().domain([0, 1]).range([height_2, 0]),

	x_3 = x_1,
	y_3 = d3.scale.linear().domain([169, 1]).range([height_3, 0]);

	x_4 = d3.scale.ordinal().domain(d3.range(13)).rangeBands([0, width_4], 0.05, 0.05);


var c_4 = d3.scale.ordinal().domain([-1, 0, 1]).range(['#8dd3c7', '#ffffb3', '#bebada']),
	fmt_float = d3.format(".2f");
	fmt_int = d3.format("d");



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

var svg_4 = d3.select("#svg4")
	.append("svg")
		.attr("width", width_4 + margin_4.left + margin_4.right)
		.attr("height", height_4 + margin_4.top + margin_4.bottom)
	.append("g")
		.attr("transform", "translate(" + margin_4.left + "," + margin_4.top + ")");


var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);


var valueline_11,
	valueline_12,
	valueline_21,
	valueline_22,
	valueline_3;



d3.text("./data/df_equity_montecarlo_1m_300.csv", "text/csv", function(text) {
	var rawdata = d3.csv.parseRows(text);
	window.rawdata = rawdata;

	R = rawdata.length;
	console.log("nb rows (169+1 expected)="+R);
	C = rawdata[0].length;
	console.log("nb col(2*9+1 expected)="+C);

	// create hands, equitydata, handrank, dataset
	hands = new Array(169);
	equitydata = new Array(169);
	for (var r=0; r<equitydata.length; r++) {
		equitydata[r] = new Array(2*9);
	}
	handrank = new Array(169);
	for (var r=0; r<handrank.length; r++) {
		handrank[r] = new Array(9);
	}
	dataset = new Array(169);
	for (var r=0; r<169; r++) {
		dataset[r] = new Array(9);
	}

	// fill hands
	for (var r = 1; r < 169+1; r++) {
		hands[r-1] = rawdata[r][0];
	}

	// fill equitydata
	for (var r = 1; r < 169+1; r++) {
		for (var c = 1; c < 2*9+1; c++) {
			equitydata[r-1][c-1] = +rawdata[r][c];
		}
	}

	// fill handrank
	var equitydataT = d3.transpose(equitydata);
	var handrankT = d3.transpose(handrank);
	var col,
		sorted_col,
		rank_col;

	window.handrankT = handrankT;
	window.equitydataT = equitydataT;

	for (var c = 0; c < 9; c++) {
		col = new Array(169);
		for (var i = 0; i < 169; i++) {
			col[i] = equitydata[i][c] + equitydata[i][c+9];
		}
		// console.log("c="+c);
		// console.log(col);
		sorted_col = col.slice().sort(d3.descending);
		rank_col = col.slice().map(function(v){ return sorted_col.indexOf(v)+1 });
		// console.log(rank_col);
		handrankT[c] = rank_col;
	}
	handrank = d3.transpose(handrankT);

	// fill dataset
	for (var r = 0; r < 169; r++) {
		for (var c = 0; c < 9; c++) {
			dataset[r][c] = { 'nb_opp' : c+1, 'win' : equitydata[r][c], 'tie' : equitydata[r][c+9], 'rank' : handrank[r][c]};
		}
	}


	// create hand_matrix
	hand_matrix = new Array(13);
	for (var k=0; k<13; k++) {
		hand_matrix[k] = new Array(13);
	}
	for (var h=0; h<hands.length; h++) {
		row = Math.floor(h/13);
		col = h%13;
		hand_matrix[row][col] = { 'hand' : hands[h], 'row' : row, 'col' : col };
	}


	create_viz();
});



function create_viz(){


	// draw title
	title.text("Preflop Hand Equity - Monte Carlo estimation");


	// draw x_1 axis
	svg_1.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_1 + ")")
			.call(d3.svg.axis().scale(x_1).orient("bottom"))
		.append("text")
			.attr("x", width_1)
			.attr("y", 20)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Nb of Opponents");

	// draw y_1 axis
	y_1_axis_text = svg_1.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_1).orient("left").ticks(5))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 8)
		.attr("dy", "0.71em")
		.style("text-anchor", "end")
		.text("Equity as fraction of player bet");


	// draw x_2 axis
	svg_2.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_2 + ")")
			.call(d3.svg.axis().scale(x_2).orient("bottom"))
		.append("text")
			.attr("x", width_2)
			.attr("y", 20)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Nb of Opponents");

	// draw y_2 axis
	y_2_axis_text = svg_2.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_2).orient("left").ticks(5))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 8)
		.attr("dy", "0.71em")
		.style("text-anchor", "end")
		.text("Equity as fraction of pot");

	// draw x_3 axis
	svg_3.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height_3 + ")")
			.call(d3.svg.axis().scale(x_3).orient("bottom"))
		.append("text")
			.attr("x", width_3)
			.attr("y", 20)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Nb of Opponents");

	// draw y_3 axis
	y_3_axis_text = svg_3.append("g")
		.attr("class", "y axis")
		.call(d3.svg.axis().scale(y_3).orient("left").ticks(6))
	.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 8)
		.attr("dy", "0.71em")
		.style("text-anchor", "end")
		.text("Hand rank");




	// line_11 win+tie
	valueline_11 = d3.svg.line()
			.x(function(d) { return x_1(d.nb_opp); })
			.y(function(d, i) { return y_1((d.nb_opp + 1) * (d.win + d.tie)); })
			.interpolate("linear");

	// line_12 win
	valueline_12 = d3.svg.line()
			.x(function(d) { return x_1(d.nb_opp); })
			.y(function(d, i) { return y_1((d.nb_opp + 1) * d.win); })
			.interpolate("linear");

	// line_21 win
	valueline_21 = d3.svg.line()
			.x(function(d) { return x_2(d.nb_opp); })
			.y(function(d) { return y_2(d.win + d.tie); })
			.interpolate("linear");

	// line_22 win
	valueline_22 = d3.svg.line()
			.x(function(d) { return x_2(d.nb_opp); })
			.y(function(d) { return y_2(d.win); })
			.interpolate("linear");

	// line_3 win
	valueline_3 = d3.svg.line()
			.x(function(d) { return x_3(d.nb_opp); })
			.y(function(d) { return y_3(d.rank); })
			.interpolate("linear");



	// build hand_matrix
	svg_4.append("rect")
		.attr("class", "background")
		.attr("width", width_3)
		.attr("height", height_3);

	var row_matrix = svg_4.selectAll(".row_matrix")
		.data(hand_matrix)
	.enter().append("g")
		.attr("class", "row_matrix")
		.attr("transform", function(d, i) { return "translate(0," + x_4(i) + ")"; })
		.each(create_row_hand_matrix);


	d3.select("body").on("keydown", keyboard_update);

	d3.select("#outputslidery1max").append("text").text(fmt_int(100*y_1_max) + "%");

	d3.selectAll(".typelow").classed("active", function(d, i) { return (d.col == type_low); });
	d3.selectAll(".typehigh").classed("active", function(d, i) { return (d.col == type_high-1); });
}





function create_row_hand_matrix(row) {
	var cell = d3.select(this).selectAll(".cell")
		.data(row)
	.enter().append("g")
		.attr("class", "cell")
		.attr("transform", function(d, i) { return "translate(" + x_4(i) + ", 0)"; });

	cell.append("rect")
		.attr("width", x_4.rangeBand())
		.attr("height", x_4.rangeBand())
		.attr("fill", function(d, i) { return c_4(d.row < d.col ? -1 : (d.row > d.col ? 1: 0 )); })
		.on("click", mouseclick_4);

	cell.append("text")
		.attr("x", x_4.rangeBand()/2)
		.attr("y", x_4.rangeBand()/2)
		.attr("dy", "0.3em")
		.attr("text-anchor", "middle")
		.text(function(d, i) { return d.hand; });
}





function mouseclick_4(cell) {
	window.cell = cell;

	sel_row = cell.row;
	sel_col = cell.col;
	update(sel_row, sel_col, y_1_max, dt);
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
	update(sel_row, sel_col, y_1_max, dt);
}

function onchange_y_1_max(d) {
	y_1_max = +d.value;
	d3.select("#outputslidery1max").selectAll("text")
		.transition()
		.duration(dt)
		.text(fmt_int(100*y_1_max) + " %");

	y_1.domain([0, y_1_max]);
	update(sel_row, sel_col, y_1_max, dt);
}



function mouseover_sum_1(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<span style='color:black'>" + fmt_float(100 * (circle.nb_opp + 1) * (circle.win + circle.tie)) + "%</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 30) + "px");
}

function mouseover_sum_2(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<span style='color:black'>" + fmt_float(100 * (circle.win + circle.tie)) + "%</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 30) + "px");
}

function mouseover_win_1(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<span style='color:black'>" + fmt_float(100 * (circle.nb_opp) * circle.win) + "%</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 30) + "px");
}

function mouseover_win_2(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<span style='color:black'>" + fmt_float(100 * circle.win) + "%</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 30) + "px");
}

function mouseover_rank(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0.9);

	tooltip.html(function(d) { return "<span style='color:black'>" + circle.rank + "</span>"; })
		.style("left", (d3.event.pageX - 25) + "px")
		.style("top", (d3.event.pageY - 30) + "px");
}



function mouseout(circle){
	tooltip.transition()
		.duration(100)
		.style("opacity", 0);
}






function update(sel_row, sel_col, y_1_max, dt){

	d3.selectAll(".cell").classed("active", function(d, i) { return (d.row == sel_row) && (d.col == sel_col); });

	// compute values
	var hand_no = sel_row*13+sel_col;
	var data = dataset[hand_no];


	// console.log("sel_row="+sel_row);
	// console.log("sel_col="+sel_col);
	// console.log("hand_no="+hand_no);
	// console.log("y_1_max="+y_1_max);

	window.data = data;
	window.hand_no = hand_no;



	// create/update line_12
	var line_12 =  svg_1.selectAll(".line12")
		.data(data);

	line_12.enter()
		.append("path")
			.attr("class", "line12")
			.attr("d", valueline_12(data));

	line_12.transition()
		.duration(dt)
		.attr("d", valueline_12(data));

	// create/update circle_12
	var circles_12 = svg_1.selectAll(".circle12")
		.data(data);

	circles_12.enter()
		.append("circle")
			.attr("class", "circle12")
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_1(d.nb_opp); })
			.attr("cy", function(d, i) { return y_1((d.nb_opp + 1) * d.win); })
			.on('mouseover', mouseover_win_1)
			.on('mouseout', mouseout);

	circles_12.transition()
			.duration(dt)
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_1(d.nb_opp); })
			.attr("cy", function(d, i) { return y_1((d.nb_opp + 1) * d.win); });


	// create/update line_11
	var line_11 =  svg_1.selectAll(".line11")
		.data(data);

	line_11.enter()
		.append("path")
			.attr("class", "line11")
			.attr("d", valueline_11(data));

	line_11.transition()
		.duration(dt)
		.attr("d", valueline_11(data));


	// create/update circle_11
	var circles_11 = svg_1.selectAll(".circle11")
		.data(data);

	circles_11.enter()
		.append("circle")
			.attr("class", "circle11")
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_1(d.nb_opp); })
			.attr("cy", function(d, i) { return y_1((d.nb_opp + 1) * (d.win +d.tie)); })
			.on('mouseover', mouseover_sum_1)
			.on('mouseout', mouseout);

	circles_11.transition()
			.duration(dt)
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_1(d.nb_opp); })
			.attr("cy", function(d, i) { return y_1((d.nb_opp + 1) * (d.win +d.tie)); });


	// create/update line_22
	var line_22 =  svg_2.selectAll(".line22")
		.data(data);

	line_22.enter()
		.append("path")
			.attr("class", "line22")
			.attr("d", valueline_22(data));

	line_22.transition()
		.duration(dt)
		.attr("d", valueline_22(data));


	// create/update circle_22
	var circles_22 = svg_2.selectAll(".circle22")
		.data(data);

	circles_22.enter()
		.append("circle")
			.attr("class", "circle22")
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_2(d.nb_opp); })
			.attr("cy", function(d, i) { return y_2(d.win); })
			.on('mouseover', mouseover_win_2)
			.on('mouseout', mouseout);

	circles_22.transition()
			.duration(dt)
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_2(d.nb_opp); })
			.attr("cy", function(d, i) { return y_2(d.win); });



	// create/update line_21
	var line_21 =  svg_2.selectAll(".line21")
		.data(data);

	line_21.enter()
		.append("path")
			.attr("class", "line21")
			.attr("d", valueline_21(data));

	line_21.transition()
		.duration(dt)
		.attr("d", valueline_21(data));



	// create/update circle_21
	var circles_21 = svg_2.selectAll(".circle21")
		.data(data);

	circles_21.enter()
		.append("circle")
			.attr("class", "circle21")
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_2(d.nb_opp); })
			.attr("cy", function(d, i) { return y_2(d.win +d.tie); })
			.on('mouseover', mouseover_sum_2)
			.on('mouseout', mouseout);

	circles_21.transition()
			.duration(dt)
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_2(d.nb_opp); })
			.attr("cy", function(d, i) { return y_2(d.win +d.tie); });



	// create/update line_3
	var line_3 =  svg_3.selectAll(".line3")
		.data(data);

	line_3.enter()
		.append("path")
			.attr("class", "line3")
			.attr("d", valueline_3(data));

	line_3.transition()
		.duration(dt)
		.attr("d", valueline_3(data));


	// create/update circle_3
	var circles_3 = svg_3.selectAll(".circle3")
		.data(data);

	circles_3.enter()
		.append("circle")
			.attr("class", "circle3")
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_3(d.nb_opp); })
			.attr("cy", function(d, i) { return y_3(d.rank); })
			.on('mouseover', mouseover_rank)
			.on('mouseout', mouseout);

	circles_3.transition()
			.duration(dt)
			.attr("r", 2)
			.attr("cx", function(d, i) { return x_3(d.nb_opp); })
			.attr("cy", function(d, i) { return y_3(d.rank); });






	// update y_1
	svg_1.selectAll(".y.axis")
		.transition()
			.duration(dt)
			.call(d3.svg.axis().scale(y_1).orient("left").ticks(5));


}




