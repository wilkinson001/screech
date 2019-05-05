function scatter(data){
	d3.selectAll("svg").remove();
	var div_width = d3.select("#main_div").style("width");
	div_width=div_width.replace("px", "");
	
	var margin = {top: 20, right: 20, bottom: 50, left: 50},
		width = div_width-margin.left-margin.right,
		height = (document.documentElement.clientHeight*0.7)-margin.top-margin.bottom;
		
	var x = d3.scaleLinear().range([0, width])
	var y = d3.scaleLinear().range([height, 0])
	
	var svg = d3.select("#main_div").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.style("display","block")
		.style("margin","auto")
	.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top +")");
		
	//data processing - this will be done using flask in the future
	data.forEach(function(d){
		d.height = +d.height;        
		d.weight = +d.weight;
	})
	
	var min_x = d3.min(data, function(d){ return d.weight}),
		max_x =  d3.max(data, function(d){ return d.weight}),
		min_y = d3.min(data, function(d){ return d.height}), 
		max_y = d3.max(data, function(d){ return d.height});
		
	x.domain([min_x-0.1*min_x, max_x+0.1*max_x]);
	y.domain([min_y-0.1*min_y, max_y+0.1*max_y]);
	
	svg.selectAll("dot")
		.data(data)
	.enter().append("circle")
		.style("fill", "steelblue")
		.attr("r", 5)
		.attr("cx", function(d){ return x(d.weight)})
		.attr("cy", function(d){ return y(d.height)});
	
	svg.append("g")
		.attr("transform", "translate(0,"+height+")")
		.call(d3.axisBottom(x));
	
	svg.append("text")
		.attr("transform", "translate(" + (width/2) + "," + (height+margin.top+20) +")")
		.style("text-anchor", "middle")
		.text("Weight");
	
	svg.append("g")
		.call(d3.axisLeft(y));
		
	svg.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 0-margin.left)
		.attr("x", 0-(height/2))
		.attr("dy", "1em")
		.style("text-anchor", "middle")
		.text("Height");
}