function makeLine(parentName, SVG_name, covid_data, state="New York", dataType='positive'){

  d3.select("#" + SVG_name).remove()
  // clears the data from the last time
  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 25, right: 10, bottom: 20, left: 60},
  height = parentWidth * .75- margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  data = covid_data.filter(d => d.state == states_hash[state])

  x = d3.scaleUtc()
        .domain(d3.extent(data, d => eightToDate(d.date)))
        .range([0, width - margin.right])

  y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d[dataType])])
        .range([height - margin.bottom, margin.top])

  var svg = d3.select("#" + parentName)
    .append("svg")
    .attr("id", SVG_name)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("g")
     .attr("transform", "translate(0," + height + ")")
     .call(d3.axisBottom(x));

  svg.append("g")
     .call(d3.axisLeft(y));

  drawLine = d3.line()
               .y(function(d) {return y(d[dataType])})
               .x(function(d) {return x(eightToDate(d.date))})

       // Add the line
  svg.append("path")
     .datum(data)
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


function mouseHover(svg, data, x, y, width, height){
  console.log(height)
  var mouseG = svg.append("g")
       .attr("class", "mouse-over-effects");

  mouseG.append("path") // this is the black vertical line to follow mouse
   .attr("class", "mouse-line")
   .style("stroke", "black")
   .style("stroke-width", "1px")
   .style("opacity", "0");

  var lines = document.getElementsByClassName('line');

  var mousePerLine = mouseG.selectAll('.mouse-per-line')
   .data(lines)
   .enter()
   .append("g")
   .attr("class", "mouse-per-line");

  mousePerLine.append("circle")
   .attr("r", 7)
   .style('stroke', 'steelblue')
   .style("fill", "none")
   .style("stroke-width", "1px")
   .style("opacity", "0");

  mousePerLine.append("text")
   .attr("transform", "translate(5,-10)");

  mouseG.append('svg:rect') // append a rect to catch mouse movements on canvas
   .attr('width', width) // can't catch mouse events on a g element
   .attr('height', height)
   .attr('fill', 'none')
   .attr('pointer-events', 'all')
   .on('mouseout', function() { // on mouse out hide line, circles and text
     d3.select(".mouse-line")
       .style("opacity", "0");
     d3.selectAll(".mouse-per-line circle")
       .style("opacity", "0");
     d3.selectAll(".mouse-per-line text")
       .style("opacity", "0");
   })
   .on('mouseover', function() { // on mouse in show line, circles and text
     d3.select(".mouse-line")
       .style("opacity", "1");
     d3.selectAll(".mouse-per-line circle")
       .style("opacity", "1");
     d3.selectAll(".mouse-per-line text")
       .style("opacity", "1");
   })
   .on('mousemove', function() { // mouse moving over canvas
     var mouse = d3.mouse(this);
     d3.select(".mouse-line")
       .attr("d", function() {
         var d = "M" + mouse[0] + "," + height;
         d += " " + mouse[0] + "," + 0;
         return d;
       });
     d3.selectAll(".mouse-per-line")
       .attr("transform", function(d, i) {
         var beginning = 0,
         ending = lines[i].getTotalLength(),
         target = null;
         while (true){
           target = Math.floor((beginning + ending) / 2);
           pos = lines[i].getPointAtLength(target);
           if ((target === ending || target === beginning) && pos.x !== mouse[0]) {
             break;
           }
           // this section dynamically tracks the mouse
           if (pos.x > mouse[0])      ending = target;
           else if (pos.x < mouse[0]) beginning = target;
           else break; //position found
         }
         d3.select(this).select('text')
           .text(format_datetime(x.invert(pos.x)) + "," + y.invert(pos.y).toFixed(0));

        return "translate(" + mouse[0] + "," + pos.y +")";
       });
   })
}

function format_datetime(date){
  month = '' + (date.getMonth() + 1),
  day = '' + date.getDate(),
  year = date.getFullYear();
  if (month.length < 2)
    month = '0' + month;
  if (day.length < 2)
    day = '0' + day;
  date = [year, month, day].join('-');
  return date
}
