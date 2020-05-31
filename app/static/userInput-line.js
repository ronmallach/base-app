function makeUserInputLine(parentName, SVG_name, input_data, dataType='Cases'){

  d3.select("#" + SVG_name).remove()
  // clears the data from the last time
  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 25, right: 10, bottom: 20, left: 60},
  height = parentWidth * .75- margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  data = input_data

  x = d3.scaleUtc()
        .domain(d3.extent(data, d => new Date(d.Date)))
        .range([0, width - margin.right])

  y = d3.scaleLinear()
        .domain([0, d3.max(data, d =>  parseInt(d[dataType]))])
        .range([height - margin.bottom, margin.top])

  var svg = d3.select("#" + parentName)
    .append("svg")
    .attr("id", SVG_name)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var xAxis = svg.append("g")
     .attr("transform", "translate(0," + height + ")")
     .call(d3.axisBottom(x));

  var yAxis= svg.append("g")
     .call(d3.axisLeft(y));

  drawLine = d3.line()
               .y(function(d) {return y(d[dataType])})
               .x(function(d) {return x(new Date(d.Date))});

  // Add the line
  svg.append("path")
     .datum(input_data)
     .attr('class', 'line')
     .attr("fill", "none")
     .attr("stroke", "steelblue")
     .attr("stroke-width", 1.5)
     .attr("d", d => drawLine(d))

  svg.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .style("text-decoration", "underline")
    .text(dataType);
}
