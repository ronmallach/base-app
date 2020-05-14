function makeStackArea(parentName, lineRange, SVG_name){
  processed = get_stackData(lineRange)
  categories = processed[0]
  max_val = processed[1]
  stacks = processed[2]
  d3.select("#" + SVG_name).remove()

  linerange = document.getElementById(lineRange).value;
  start = new Date()
  start.setDate(start.getDate() - linerange)
  end = new Date()

  // set the dimensions and margins of the graph
  parentWidth = document.getElementById(parentName).offsetWidth
  parentHeight = document.getElementById(parentName).offsetHeight
  var margin = {top: 10, right: 40, bottom: 30, left: 60},
  height = parentHeight - margin.top - margin.bottom;
  width = parentWidth - margin.left - margin.right
  var svg = d3.select("#" + parentName)
    .append("svg")
      .attr("id", SVG_name)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

    // Add X axis --> it is a date format
  var x = d3.scaleLinear()
    .domain([0,linerange])
    .range([ 0, width ]);
  var xaxis = d3.scaleTime()
    .domain([start, end])
    .range([ 0, width]);

  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xaxis));

    // Add Y axis
  var y = d3.scaleLinear()
    .domain([0 , max_val])
    .range([ height, 0 ]);
  svg.append("g")
    .call(d3.axisLeft(y));

  // color palette
  var color = d3.scaleOrdinal()
    .domain(categories)
    .range(d3.quantize(t => d3.interpolateRainbow(t), categories.length+1).reverse());

  // stack the data
  var stackedData = d3.stack()
      .keys(categories)
      (stacks);
    // Show the areas
  svg.selectAll("mylayers")
    .data(stackedData)
    .enter()
    .append("path")
      .style("fill", function(d) {return color(d.key); })
      .attr("class", function(d) { return "myArea " + d.key })
      .attr("d", d3.area()
        .x(function(d, i) {return x(i); })
        .y0(function(d) { return y(d[0]); })
        .y1(function(d) { return y(d[1]); })
  )

  var highlight = function(d){
    // reduce opacity of all groups
    d3.selectAll(".myArea").style("opacity", .1)
    // expect the one that is hovered
    d3.select("."+d).style("opacity", 1)
  }

  // And when it is not hovered anymore
  var noHighlight = function(d){
    d3.selectAll(".myArea").style("opacity", 1)
  }

  // Add one dot in the legend for each name.
  var size = 20
  svg.selectAll("myrect")
    .data(categories)
    .enter()
    .append("rect")
      .attr("x", 25)
      .attr("y", function(d,i){ return 10 + i*(size+5)}) // 100 is where the first dot appears. 25 is the distance between dots
      .attr("width", size)
      .attr("height", size)
      .style("fill", function(d){ return color(d)})
      .on("mouseover", highlight)
      .on("mouseleave", noHighlight)

  // Add one dot in the legend for each name.
  svg.selectAll("mylabels")
    .data(categories)
    .enter()
    .append("text")
      .attr("x", 25 + size*1.2)
      .attr("y", function(d,i){ return 10 + i*(size+5) + (size/2)}) // 100 is where the first dot appears. 25 is the distance between dots
      .style("fill", function(d){ return "black"})
      .text(function(d){ return d})
      .attr("text-anchor", "left")
      .style("alignment-baseline", "middle")
      .style("font-size", "16px")
      .on("mouseover", highlight)
      .on("mouseleave", noHighlight)

}
