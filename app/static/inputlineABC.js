function makeABCLine(parentName, SVG_name, input_data, dataType='Cases', aspect=null){

  d3.select("#" + SVG_name).remove()
  if (aspect == null){aspect = .33}
  aspectRatio = aspect
  // clears the data from the last time
  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 25, right: 10, bottom: 20, left: 20},
  height = parentWidth * aspect - margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  data = prep_ABCpolicy_d3(input_data)

  x = d3.scaleLinear()
        .domain(d3.extent(data, d => d.x))
        .range([margin.left, width - margin.right])

  y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d3.max([d.yA,d.yB,d.yC]))])
        .range([height - margin.bottom, margin.top])

  var svg = d3.select("#" + parentName)
    .append("svg")
    .attr("id", SVG_name)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var xAxis = svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
     .call(d3.axisBottom(x));

  var yAxis= svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
     .call(d3.axisLeft(y).ticks(5));

  drawLineA = d3.line()
               .y(function(d) {return y(d.yA)})
               .x(function(d) {return x(d.x)});

  drawLineB = d3.line()
                .y(function(d) {return y(d.yB)})
                .x(function(d) {return x(d.x)});

  drawLineC = d3.line()
                .y(function(d) {return y(d.yC)})
                .x(function(d) {return x(d.x)});

  // Add the line
  svg.append("path")
     .datum(data)
     .attr('class', 'line')
     .attr("fill", "none")
     .attr("stroke", "steelblue")
     .attr("stroke-width", 1.5)
     .attr("d", d => drawLineA(d))

  svg.append("path")
    .datum(data)
    .attr('class', 'line')
    .attr("fill", "none")
    .attr("stroke", "red")
    .attr("stroke-width", 1.5)
    .attr("d", d => drawLineB(d))

  svg.append("path")
   .datum(data)
   .attr('class', 'line')
   .attr("fill", "none")
   .attr("stroke", "green")
   .attr("stroke-width", 1.5)
   .attr("d", d => drawLineC(d))

  svg.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .style("text-decoration", "underline")
    .text(dataType);
}



function prep_ABCpolicy_d3(input_data, dataType){
  data = {'x':input_data['Date'],
          'yA':input_data['PlanA'],
          'yB':input_data['PlanB'],
          'yC':input_data['PlanC'],
          }
  num_entries = data.x.length
  new_data = []
  for (var i=1; i<num_entries; i++){
    span = 7
    for (var d=0; d<span; d++){
      new_data[new_data.length] = {'x':new_data.length, 'yA':data['yA'][i-1],
                                   'yB':data['yB'][i-1], 'yC':data['yC'][i-1]}
    }
  }
  return new_data
}
