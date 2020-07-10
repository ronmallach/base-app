function makeSimLine(parentName, SVG_name, covid_data, state="New York",
                     dataType='positive', cumulative='cumulative',
                     simDataType=null, simA=null, simB=null, simC=null){

  d3.select("#" + SVG_name).remove()
  // clears the data from the last time
  aspectRatio = .33

  title_mapping = {'positive':' Positive Cases - Cumulative',
                   'positiveIncrease': ' Positive Cases - Daily Increase',
                   'death':' Deaths - Cumulative',
                   'deathIncrease': ' Deaths - Daily Increase',
                   'hospitalized':' Hospitilizations - Cumulative',
                   'hospitalizedIncrease': ' Hospitilizations - Daily Increase',
                   'totalTestResults': ' Tests Taken - Cumulative',
                   'totalTestResultsIncrease': ' Tests Taken - Daily Increase',
                  }

  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 30, right: 20, bottom: 20, left: 30},
  height = parentWidth * aspectRatio - margin.top// - margin.bottom
  width = parentWidth - margin.left - margin.right

  data = covid_data.filter(d => d.state == states_hash[state])

  if (cumulative == 'daily'){
    dataType = dataType + 'Increase'
  }

  if (simA == null){
    x = d3.scaleUtc()
          .domain(d3.extent(data, d => eightToDate(d.date)))
          .range([margin.left, width - margin.right])
    y = d3.scaleLinear()
          .domain([d3.min(data, d => d[dataType]), d3.max(data, d => d[dataType])])
          .range([height - margin.bottom, margin.top])
  }else{
    //x = d3.scaleUtc()
    //      .domain(d3.extent(simulation, d => new Date(d.Date)))
    //      .range([margin.left, width - margin.right])
    if (simA != null){maxA = d3.max(simA, d => parseFloat(d[simDataType]))}else{maxA=0}
    if (simB != null){maxB = d3.max(simB, d => parseFloat(d[simDataType]))}else{maxB=0}
    if (simC != null){maxC = d3.max(simC, d => parseFloat(d[simDataType]))}else{maxC=0}
    total_max = Math.max(maxA, maxB, maxC)
    x = d3.scaleLinear()
          .domain(d3.extent(simA, d => parseInt(d.Date)))
          .range([margin.left, width - margin.right])
    y = d3.scaleLinear()
          .domain([0, total_max])
          .range([height - margin.bottom, margin.top])
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
     .call(d3.axisBottom(x).ticks(10)) ;

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y)
            .ticks(5)
          );

    svg.append("g")
    .attr("stroke", "currentColor")
    .attr("stroke-opacity", 0.1)
    .call(g => g.append("g")
      .selectAll("line")
      .data(x.ticks())
      .join("line")
        .attr("x1", d => 0.5 + x(d))
        .attr("x2", d => 0.5 + x(d))
        .attr("y1", margin.top)
        .attr("y2", height - margin.bottom))
    .call(g => g.append("g")
      .selectAll("line")
      .data(y.ticks())
      .join("line")
        .attr("y1", d => 0.5 + y(d))
        .attr("y2", d => 0.5 + y(d))
        .attr("x1", margin.left)
        .attr("x2", width - margin.right));

  //drawLine = d3.line()
  //             .y(function(d) {return y(d[dataType])})
  //             .x(function(d) {return x(eightToDate(d.date))})

       // Add the line
  //svg.append("path")
  //   .datum(data)
  //   .attr('class', 'line')
  //   .attr("fill", "none")
  //   .attr("stroke", "steelblue")
  //   .attr("stroke-linejoin", "round")
  //   .attr("stroke-linecap", "round")
  //   .attr("stroke-width", 2.25)
  //   .attr("d", d => drawLine(d))

     if (simA !== null){
       //drawSimLine = d3.line()
      //              .y(function(d) {return y(parseFloat(d[simDataType]))})
      //              .x(function(d) {return x(new Date(d.Date))})
       drawSimLine = d3.line()
                       .y(function(d) {return y(parseFloat(d[simDataType]))})
                       .x(function(d) {return x(parseInt(d.Date))})

       const pathA = svg.append("path")
         .datum(simA)
         .attr('class', 'line')
         .attr("fill", "none")
         .attr("stroke", "steelblue")
         .attr("stroke-width", 1.5)
         .attr("d", d => drawSimLine(d))

        const pathLength = pathA.node().getTotalLength();
       // D3 provides lots of transition options, have a play around here:
       // https://github.com/d3/d3-transition
       const transitionPath = d3
         .transition()
         .ease(d3.easeSin)
         .duration(10000);
       pathA.attr("stroke-dashoffset", pathLength)
         .attr("stroke-dasharray", pathLength)
         .transition(transitionPath)
         .attr("stroke-dashoffset", 0);
     }
     if (simB !== null){
       //drawSimLine = d3.line()
      //              .y(function(d) {return y(parseFloat(d[simDataType]))})
      //              .x(function(d) {return x(new Date(d.Date))})
       drawSimLine = d3.line()
                       .y(function(d) {return y(parseFloat(d[simDataType]))})
                       .x(function(d) {return x(parseInt(d.Date))})

       const pathB = svg.append("path")
         .datum(simB)
         .attr('class', 'line')
         .attr("fill", "none")
         .attr("stroke", "red")
         .attr("stroke-width", 1.5)
         .attr("d", d => drawSimLine(d))

         const pathLength = pathB.node().getTotalLength();
          // D3 provides lots of transition options, have a play around here:
          // https://github.com/d3/d3-transition
          const transitionPath = d3
            .transition()
            .ease(d3.easeSin)
            .duration(10000);
          pathB.attr("stroke-dashoffset", pathLength)
            .attr("stroke-dasharray", pathLength)
            .transition(transitionPath)
            .attr("stroke-dashoffset", 0);
     }
     if (simC !== null){
       //drawSimLine = d3.line()
      //              .y(function(d) {return y(parseFloat(d[simDataType]))})
      //              .x(function(d) {return x(new Date(d.Date))})
       drawSimLine = d3.line()
                       .y(function(d) {return y(parseFloat(d[simDataType]))})
                       .x(function(d) {return x(parseInt(d.Date))})

       const pathC = svg.append("path")
         .datum(simC)
         .attr('class', 'line')
         .attr("fill", "none")
         .attr("stroke", "green")
         .attr("stroke-width", 1.5)
         .attr("d", d => drawSimLine(d))

         const pathLength = pathC.node().getTotalLength();
        // D3 provides lots of transition options, have a play around here:
        // https://github.com/d3/d3-transition
        const transitionPath = d3
          .transition()
          .ease(d3.easeSin)
          .duration(10000);
        pathC.attr("stroke-dashoffset", pathLength)
          .attr("stroke-dasharray", pathLength)
          .transition(transitionPath)
          .attr("stroke-dashoffset", 0);
     }
  // add the title
  svg.append("text")
       .attr("font-family", "sans-serif")
       .attr("font-size", 18)
       .attr("x", (width / 2))
       .attr("y", 10 - (margin.top / 2))
       .attr("text-anchor", "middle")
       .text(title_mapping[dataType]);
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
