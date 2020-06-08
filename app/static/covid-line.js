function makeCovidTrackerLine(parentName, SVG_name, covid_data, scaleType='linear',
 state="New York", dataType='positive', simulation=null, simDataType=null){

  d3.select("#" + SVG_name).remove()
  // clears the data from the last time
  aspectRatio = 0.6

  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 25, right: 10, bottom: 20, left: 30},
  height = parentWidth * aspectRatio - margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  data = covid_data.filter(d => d.state == states_hash[state])

  if (simulation == null){
    x = d3.scaleUtc()
          .domain(d3.extent(data, d => eightToDate(d.date)))
          .range([margin.left, width - margin.right])
    if (scaleType == 'linear'){
      y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d[dataType])])
            .range([height - margin.bottom, margin.top])
    }else{
      y = d3.scaleLog()
            .domain([1, d3.max(data, d => d[dataType])])
            .range([height - margin.bottom, margin.top])
    }
  }else{
    x = d3.scaleUtc()
          .domain(d3.extent(simulation, d => new Date(d.Date)))
          .range([margin.left, width - margin.right])

    if (scaleType == 'linear'){
      y = d3.scaleLinear()
            .domain([0, d3.max(simulation, d => parseFloat(d[simDataType]))])
            .range([height - margin.bottom, margin.top])
    }else{
      y = d3.scaleLog()
            .domain([1, d3.max(simulation, d => parseFloat(d[simDataType]))])
            .range([height - margin.bottom, margin.top])
    }
  }



  var svg = d3.select("#" + parentName)
    .append("svg")
    .attr("id", SVG_name)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("g")
     .attr("transform", `translate(0,${height - margin.bottom})`)
     .call(d3.axisBottom(x).ticks(5)) ;

  svg.append("text")
    .attr("transform",
          "translate(" + (width/2) + " ," + (height + margin.top-10) + ")")
  .style("text-anchor", "middle")
  .style("font-size", "8px")
  .text("Date");

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5));

  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x",0 - (height / 2))
    .attr("dy", "1em")
    .style("font-size", "8px")
    .style("text-anchor", "middle")
    .text("Value (in Thousands)");

  drawLine = d3.line()
               .y(function(d) {return y(d[dataType])})
               .x(function(d) {return x(eightToDate(d.date))})

  if (simulation !== null){
    drawSimLine = d3.line()
                 .y(function(d) {return y(parseFloat(d[simDataType]))})
                 .x(function(d) {return x(new Date(d.Date))})

    svg.append("path")
      .datum(simulation)
      .attr('class', 'line')
      .attr("fill", "none")
      .attr("stroke", "red")
      .attr("stroke-width", 1.5)
      .attr("d", d => drawSimLine(d))

  }

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
