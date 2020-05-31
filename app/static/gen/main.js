function dummy(){

}

function makeMap(parentName, SVG_name, fromDate, colorBy, map_data, covid_data){
  d3.select("#" + SVG_name).remove()

  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 10, right: 10, bottom: 10, left: 10},
  height = parentWidth - margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  color = d3.scaleSequentialLog([1, 10**5], d3.interpolateReds)

  var svg = d3.select("#" + parentName)
    .append("svg")
      .attr("id", SVG_name)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .attr("viewBox", [0, 0, 975, 610])
      .on("click", reset)
    .append("g")
      .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

  const g = svg.append("g");

  path = d3.geoPath()

  data = {}
  covid_data_filter = covid_data.filter(d =>  d.date == fromDate)
  Object.entries(covid_data_filter).forEach(d => data[d[1].fips] = d[1][colorBy])

  g.append("g")
    .attr("fill", "#444")
    .attr("cursor", "pointer")
    .selectAll("path")
    .data(topojson.feature(map_data, map_data.objects.states).features)
    .join("path")
      .attr("fill", d =>  color(data[d.id]))
      .on('click', clicked)
      .attr("d", path)
    .append("title")
      .text(d => d.properties.name + ' Value , ' + data[d.id]);


  const zoom = d3.zoom()
    .scaleExtent([1, 4])
    .on("zoom", zoomed);

  g.append("path")
    .attr("fill", "none")
    .attr("stroke", "white")
    .attr("stroke-linejoin", "round")
    .attr("d", path(topojson.mesh(map_data, map_data.objects.states, (a, b) => a !== b)));

  svg.call(zoom);

  function reset() {
    svg.transition().duration(750).call(
      zoom.transform,
      d3.zoomIdentity,
      d3.zoomTransform(svg.node()).invert([width / 2, height / 2])
    );
  }

  function clicked(d) {
    clickState = d.properties.name
    document.getElementById('selectState').value = clickState
    statistic = d3.select("#colorState")._groups[0][0].value
    updateMap()
  }

  function clicked_zoom(d) {
    const [[x0, y0], [x1, y1]] = path.bounds(d);
    d3.event.stopPropagation();
    svg.transition().duration(750).call(
      zoom.transform,
      d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(Math.min(8, 0.9 / Math.max((x1 - x0) / width, (y1 - y0) / height)))
        .translate(-(x0 + x1) / 2, -(y0 + y1) / 2),
      d3.mouse(svg.node())
    );
  }

  function zoomed() {
    const {transform} = d3.event;
    g.attr("transform", transform);
    g.attr("stroke-width", 1 / transform.k);
  }
}



function dateToEight(date){
  year = String(date.getFullYear())
  month = String(date.getMonth() + 1)
  day = String(date.getDate())
  if (day.length == 1){
    day = '0' + day
  }
  if (month.length == 1){
    month = '0' + month
  }
  eightDate = year + month + day
  return eightDate
}

function eightToDate(eight){
  eight = String(eight)
  year = parseInt(eight.substring(0,4))
  month = parseInt(eight.substring(4,6))-1
  day = parseInt(eight.substring(6,8))
  date = new Date(year,month,day)
  return date
}


function weekOfYear(date) {
  // from date input
  //year = parseInt(date.substring(0,4))
  //month = parseInt(date.substring(5,7))-1
  //day = parseInt(date.substring(8,10))
  //date = new Date(year,month,day)
  // dayOfWeek = date.getDay()
  year= date.getFullYear()
  start = new Date(year, 0, 0)
  diff = date - start
  oneWeek = 1000 * 60 * 60 * 24 * 7
  week = Math.floor(diff / oneWeek)
  return week
}

function makeForesight(parentName, covid_data, state="New York", dataType='positive'){

  document.getElementById(parentName).innerHTML = ""
  // clears the data from the last time

  console.log(dataType)

  config = {
  pointType: 'mmwr-week', // Default is week
  axes: {
    y: {
      title: dataType // Title for the y axis
    },
    x: {
      title: 'Week of 2020'
    }
    },
  confidenceIntervals: ['50%', '75%'],
  }


  weekToEight = {}
  filtered = covid_data.filter(d => eightToDate(d.date).getDay() == 0)
  filtered = filtered.filter(d => d.state == states_hash[state])
  Object.entries(filtered).forEach(d => weekToEight[weekOfYear(eightToDate(d[1].date))] = d[1][dataType] )


  timePoints = [...Array(51).keys()].map(w => {
    return { week: w + 1, year: 2020 }
  })


  weekNow = weekOfYear(new Date())

  actual = []
  for (i = 0; i < 51; i++) {
    if (i in weekToEight){
      actual.push(weekToEight[i])
    }else{
      actual.push(null)
    }}

  // this is where the RL/simulations models comes in
  predictions = timePoints.map(tp => {
    if (tp.week >= weekNow) {
    // We only predict upto week 30
      return null
    } else {
      to_plot = []
      for (i = tp.week; i < weekNow; i++) {
        if (typeof weekToEight[i] == "number"){
          r = parseFloat(weekToEight[i])
          to_plot.push({point: r,
                        low: [Math.max(0, r - (r * .1)), Math.max(0, r - r * 0.2)],
                        high: [Math.max(0, r + (r * .1)), Math.max(0, r + (r * .2))]})
        } else {
          to_plot.push({point: parseFloat(0)})
        }
      }
      return {
        series: Array.from(to_plot)
      }
    }
  })

  data = {
    timePoints,
    actual: actual,
    models: [
      {
        id: 'actual tester',
        meta: {
          name: 'Name',
          description: 'Model description here',
          url: 'http://github.com'
        },
        pinned: false, // Setting true shows the model in top section of the legend
                       // In case of absence of `pinned` key (or false), the model
                       // goes in the bottom section
        predictions: predictions,
        style: { // Optional parameter for applying custom css on svg elements
          color: '#4682b4', // Defaults to values from the internal palette
          point: {
            // Style for the dots in prediction
          },
          area: {
            // Style for the confidence area (shaded region around the line)
          },
          line: {
            // Style for the main line
          }
        }
      }
    ]
  }

  timeChart = new d3Foresight.TimeChart('#' + parentName, config)
  timeChart.plot(data)
  timeChart.update(10)
  timeChart.moveForward()
  timeChart.moveBackward()

}

function makeCoivdTrackerLine(parentName, SVG_name, covid_data, state="New York", dataType='positive'){

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
