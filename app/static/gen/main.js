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
    makeForesight('holdForesight', covid_data, clickState, statistic)
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
