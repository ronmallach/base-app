function makePie(data, parent, SVG_name, subcat=''){
  d3.select("#" + SVG_name).remove()
  width = 250
  height = 250

  color = d3.scaleOrdinal()
    .domain(data.map(d => d.name))
    .range(d3.quantize(t => d3.interpolateRainbow(t), data.length+1).reverse())

  pie = d3.pie()
    .sort(null)
    .value(d => d.value);

  arc = d3.arc()
    .innerRadius(0)
    .outerRadius(Math.min(width, height) / 2 - 1)

  arcLabel = d3.arc()
    .innerRadius(Math.min(width, height) *.33)
    .outerRadius(Math.min(width, height) *.33)

  const arcs = pie(data);

  const svg = d3.select(parent)
      .append("svg")
      .attr("id", SVG_name)
      .attr("height", height)
      .attr("width", width)
      .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  svg.append("g")
     .attr("stroke", "white")
     .selectAll("path")
     .data(arcs)
     .join("path")
     .attr("fill", d => color(d.data.name))
     .attr("d", arc)

  svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 12)
      .attr("text-anchor", "middle")
    .selectAll("text")
    .data(arcs)
    .join("text")
      .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
      .call(text => text.append("tspan")
          .attr("y", "-0.4em")
          .attr("font-weight", "bold")
          .text(d => d.data.name))
      .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan")
          .attr("x", 0)
          .attr("y", "0.7em")
          .attr("fill-opacity", 0.7)
          .text(d => d.data.value.toLocaleString()))
}

function to_object(name) {
  json = JSON.parse(all_data[name])
  array = [];
  Object.keys(json).forEach(function(key){array.push(json[key])})
  return array
}

function get_today(range){
  today = new Date()
  today.setDate(today.getDate() - range)
  month = '' + (today.getMonth() + 1),
  day = '' + today.getDate(),
  year = today.getFullYear();
  if (month.length < 2)
    month = '0' + month;
  if (day.length < 2)
    day = '0' + day;
  today = [year, month, day].join('-');
  return today
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

function list_of_dates(start='2018-08-01'){
  start = new Date(start)
  end = new Date()
  dates = {}
  difference = (end - start) / (1000 * 3600 * 24)
  i = 1
  while (i < difference){
    today = new Date(start)
    today.setDate(today.getDate() + i)
    month = '' + (today.getMonth() + 1),
    day = '' + today.getDate(),
    year = today.getFullYear();
    if (month.length < 2)
      month = '0' + month;
    if (day.length < 2)
      day = '0' + day;
    today = [year, month, day].join('-');
    dates[today] = 0
    i = i + 1
  }
  return dates
}

function get_hierarchy(){
  data = to_object('expense')
  levels = ['Category', 'SubCategory', 'Business']
  json = {};
  level0 = [];
  level1 = [];
  level2 = [];
  for (entry in data) {
    l0 = data[entry][levels[0]]
    l1 = data[entry][levels[1]]
    l2 = data[entry][levels[2]]
    date = data[entry]['Date']
    amount = data[entry]['Amount']
    if (level0.includes(l0) == false){
      level0.push(l0)
      json[l0] = {}
    }
    if (level1.includes(l1) == false){
      level1.push(l1)
      json[l0][l1] = {}
    }
    if (level2.includes(l2) == false){
      level2.push(l2)
      json[l0][l1][l2] = list_of_dates()
    }
    else{
      json[l0][l1][l2][date] += amount
    }
  }
  return json
}

function reverse_hierarchy(){
  expense = to_object('expense')
  biz_json = {};
  sc_json = {};
  businesses = [];
  subcats = [];
  for (trans in expense) {
    subcat = expense[trans]['SubCategory']
    cat = expense[trans]['Category']
    business = expense[trans]['Business']
    if (businesses.includes(business) == false){
      businesses.push(business)
      biz_json[business] = {'category':cat,
                        'subcategory':subcat}
    }
    if (subcats.includes(subcat) == false){
      subcats.push(subcat)
      sc_json[subcat] = {'category':cat}
    }

  }
  return [biz_json, sc_json]
}

function get_pieData(data, granularity, timeRange) {
  unique = [...new Set(data.map(x => x[granularity]))]
  pieData = [];
  range = document.getElementById(timeRange).value;
  today = get_today(range)
  subset = data.filter(d => d.Date >= today)
  for (u in unique) {
    lookAt = unique[u]
    total = 0
    for (trans in subset) {
      if (subset[trans][granularity] == lookAt){
        total = total + subset[trans]["Amount"]
      }
    }
    if (total > 0){
      pieData.push({"name": unique[u], "value":parseInt(total)})
    }
  }
  return pieData
}

function get_lineData(lineRange, lineType){
  linerange = document.getElementByID(lineRange).value;
  source = document.getElementByID(lineType).value;
  data = to_object("Summary")
}

function sunFromTrans(timeRange){
  object = to_object('expense')
  unique = [...new Set(object.map(x => x['Business']))] // gets all business
  rawSun = [{"name":"root", "parent":""}];
  subcats = [];
  categories = [];
  range = document.getElementById(timeRange).value;
  today = get_today(range)
  subset = object.filter(d => d.Date >= today)
  for (u in unique) {
    lookAt = unique[u]
    total = 0
    for (trans in subset) {
      if (subset[trans]['Business'] == lookAt){
        total = total + subset[trans]["Amount"]
        subcat = subset[trans]['SubCategory']
        cat = subset[trans]['Category']
        if (categories.includes(cat) == false){
          categories.push(cat)
          rawSun.push({"name":cat, "parent":"root"})
        }
        if (subcats.includes(subcat) == false){
          subcats.push(subcat)
          rawSun.push({"name":subcat, "parent":cat})
        }
      }
    }
    if (total > 0){
      rawSun.push({"name": unique[u], "parent": subcat, "value":parseInt(total)})
    }
  }
  strat = d3.stratify()
            .id(d => d.name)
            .parentId(d => d.parent)
            (rawSun)
  root = d3.hierarchy(strat)
          .sum(d => d.data.value)
          .sort((a,b) => b.data.value - a.data.value)
  return root
}

function get_stackData(lineRange){
  linerange = document.getElementById(lineRange).value;
  data = to_object("stackCat")
  today = get_today(linerange)
  data = data.filter(d => d.Date >= today)
  let normal = {}; // objCopy will store a copy of the mainObj
  let key;
  for (key in data[0]) {
    normal[key] = data[0][key]; }// copies each property to the objCopy object
  for (day in Object.values(data)){
    Object.keys(data[day]).forEach(function(key,index) {
      if (key != 'Date'){
        data[day][key] = data[day][key] - normal[key]
  }})}
  last_day = data[Object.keys(data).length-1]
  values = Object.values(last_day)
  values[0] = 0
  max_val = d3.sum(values)

  let categories = []; // objCopy will store a copy of the mainObj
  Object.keys(data[0]).forEach(function(key,index){
    if (key != 'Date'){
      categories.push(key)
    }
  })
  return [categories, max_val, data];
}

function summary_statistics(){
  summary = to_object('Summary')
  days = summary.length - 1
  most_recent = summary[days]
  last_week = summary[days - 7]
  last_biweek = summary[days - 14]
  last_month = summary[days - 28]
  checking = Math.round(most_recent.Checking)
  saving = Math.round(most_recent.Savings)
  spent7 = Math.round(most_recent.Spent - last_week.Spent)
  spent14 = Math.round(most_recent.Spent - last_biweek.Spent)
  spent28 = Math.round(most_recent.Spent - last_month.Spent)
  income28 = Math.round(most_recent.Income - last_month.Income)
  net = income28 - spent28
  document.getElementById("currentchecking").innerHTML = '&#36; ' + checking
  document.getElementById("currentsaving").innerHTML = '&#36; ' + saving
  document.getElementById("spentlast7").innerHTML = '7 Days:     &#36;' + spent7
  document.getElementById("spentlast14").innerHTML = '2 Weeks:     &#36;' + spent14
  document.getElementById("spentlast28").innerHTML = 'Month:     &#36;' + spent28
  document.getElementById("incomelast28").innerHTML = '&#36; ' + income28
  document.getElementById("netmonth").innerHTML = '&#36; ' + net
}

function prep_calender(){
  expense = to_object('expense')
  dates = Object.keys(list_of_dates())
  categories = Object.keys(to_object('stackCat')[0])
  today = new Date()
  year_now = today.getYear()
  month_now = today.getMonth() + 1
  dummy = {'base':0}
  for (category in categories){
    dummy[categories[category]] = 0
  }
  json = {}
  for (date in dates){
    time = dates[date]
    json[time] = JSON.parse(JSON.stringify(dummy))
    cell = 25
    json[time]['Date'] = time
    json[time]['y-offset'] = (12 * (year_now - year + 1900)) + (month_now - month)
    json[time]['x-offset'] = day
  }
  for (trans in expense) {
    cat = expense[trans]['Category']
    date = expense[trans]['Date']
    amount = expense[trans]['Amount']
    if (Object.keys(json).includes(date)) {
        json[date][cat] += amount
        json[date]['base'] += amount
    }
  }
  array = [];
  Object.keys(json).forEach(function(key){array.push(json[key])})
  return array
}

function getDateXY(date){
  year = parseInt(time.split('-')[0])
  month = parseInt(time.split('-')[1])
  day = parseInt(time.split('-')[2])
  monthY = Math.floor((month_now - month) / 3) + 2
  monthX = Math.floor((month_now - month) / 4) + 4

}

function makeLine(parentName, lineRange, lineType, SVG_name) {
  d3.select("#" + SVG_name).remove()
  linerange = document.getElementById(lineRange).value;
  source = document.getElementById(lineType).value;
  data = to_object("Summary")
  start = new Date()
  start.setDate(start.getDate() - linerange)
  end = new Date()
  today = get_today(linerange)
  data = data.filter(d => d.Date > today)
  // set the dimensions and margins of the graph
  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 10, right: 10, bottom: 30, left: 60},
  height = parentWidth / 2 - margin.top - margin.bottom
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
  var x = d3.scaleTime()
    .domain([start, end])
    .range([ 0, width]);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

  var normalize = 0
    // Add Y axis
  var y = d3.scaleLinear()
    .domain([d3.min(data, function(d){return +d[source];})-500-normalize,
             d3.max(data, function(d) {return +d[source];})+500-normalize])
    .range([ height, 0 ]);

  if (source == 'Spent'){
    var normalize = d3.min(data, d => d[source])
    var maxOut = d3.max(data, d => d[source])
    var minIn = d3.min(data, d => d.Income)
    var maxIn = d3.max(data, d => d.Income)
    var bufferIn = maxIn - minIn - maxOut + normalize + 500
    var bufferOut = maxOut - normalize - maxIn + minIn + 500
    var buffer = d3.max([bufferIn, bufferOut])
    var y = d3.scaleLinear()
      .domain([d3.min(data, function(d){return +d[source];})-500-normalize,
               d3.max(data, function(d) {return +d[source];})+buffer-normalize])
      .range([height, 0]);
  }

  svg.append("g")
    .call(d3.axisLeft(y));

  test = d3.line()
      .y(function(d) {return y(d[source]-normalize)})
      .x(function(d) {return x(new Date(d.Date)) })

    // Add the line
  svg.append("path")
    .datum(data)
    .attr('class', 'line')
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5)
    .attr("d", d => test(d))

  if (source == 'Spent'){
    var normalize = d3.min(data, function(d){return +d.Income;})
    svg.append("path")
      .datum(data)
      .attr('class', 'line')
      .attr("fill", "none")
      .attr("stroke", "red")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
          .y(function(d) { return y(d.Income - normalize)})
          .x(function(d) { return x(new Date(d.Date)) })
      )
  }

  mouseHover(svg, data, x, y, width, height)
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
           .text(format_datetime(x.invert(pos.x)) + ", $ " + y.invert(pos.y).toFixed(2));
           // ^ triggers the response... make this a function tied to
           // expenses
        return "translate(" + mouse[0] + "," + pos.y +")";
       });
   })
   .on("click", function(){
     var mouse = d3.mouse(this);
     table = document.getElementById('lineExpense')
     if (table.children.length > 1){table.children[table.children.length-1].remove()}
     expense = to_object('expense')
     expenseDay = expense.filter(e => e.Date == format_datetime(x.invert(pos.x)))
     makeClickTable(expenseDay, 'lineExpense')
    });
}

function makeClickTable(data, tableName){
		var entries = data.length;
		if(entries>0){
      var table = document.getElementById(tableName);
			// CREATE DYNAMIC TABLE.
      //Retrieve Column Headers
      var col = ['Date', 'Business', 'Amount']; // define an empty array
			// CREATE TABLE BODY .
			var tBody = document.createElement("tbody");
      tBody.setAttribute('id', tableName + 'body')
			// ADD COLUMN HEADER TO ROW OF TABLE HEAD.
			for (var i = entries-1; i >-1; i--) {

  			var bRow = document.createElement("tr"); // CREATE ROW FOR EACH RECORD .

  			for (var j = 0; j < col.length; j++) {
          var td = document.createElement("td");
          td.innerHTML = data[i][col[j]];
  				bRow.appendChild(td);
  			}
        tBody.appendChild(bRow)
		  }
		table.appendChild(tBody);
	}
}

function makeBar(data, parentName, SVG_name){
  // data as object keys of [name, value]

  d3.select("#" + SVG_name).remove()
    // set the dimensions and margins of the graph
  parentWidth = document.getElementById(parentName).offsetWidth
  parentHeight = document.getElementById(parentName).offsetHeight
  var margin = {top: 25, right: 25, bottom: 60, left: 50},
  height = parentHeight - margin.top - margin.bottom
  width = parentWidth - margin.left - margin.right

  // append the svg object to the body of the page
  var svg = d3.select("#" + parentName)
    .append("svg")
      .attr("id", SVG_name)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

  // X axis
  var x = d3.scaleBand()
    .range([ 0, width ])
    .domain(data.map(function(d) { return d.name; }))
    .padding(0.2);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-15)")
      .style("text-anchor", "end");

  // Add Y axis
  var y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value) * 1.1])
    .range([height, 0]);
  svg.append("g")
    .call(d3.axisLeft(y));

  // Bars
  svg.selectAll("mybar")
    .data(data)
    .enter()
    .append("rect")
      .attr("x", function(d) { return x(d.name); })
      .attr("y", function(d) { return y(d.value); })
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(d.value); })
      .attr("fill", "#69b3a2")
  }

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

function Sunburst(parentName, SVG_name, timeRange){
  var root = sunFromTrans(timeRange)
  d3.select("#" + SVG_name).remove()
  root = d3.partition()
          .size([2 * Math.PI, root.height+1])
          (root)

  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 10, right: 10, bottom: 10, left: 10},
  width = parentWidth - margin.left - margin.right
  height = width
  radius = width / 8
  color = d3.scaleOrdinal()
    .domain(root.data.children.map(d => d.data.name))
    .range(d3.quantize(d => d3.interpolateRainbow(d), root.data.children.length + 1).reverse())

  const svg = d3.select('#' + parentName).append("svg")
      .attr("id", SVG_name)
      .attr("height", height)
      .attr("width", width)
      .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
    .padRadius(radius * 1.5)
    .innerRadius(d => d.y0 * radius)
    .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

  root.each(d => d.current = d);

  //draw the path
  svg.append("g")
    .selectAll("path")
    .data(root.descendants().slice(1))
    .join("path")
      .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.data.name); })
      .attr("fill-opacity", .8)
      .attr("d", d => arc(d.current))
    .append("title")
      .text(d => d.data.data.name + '\n' + '$' + d.value + ',   ' + Math.round(1000*d.value/root.value)/10 + '%');

  // add the labels
  svg.append("g")
      .attr("pointer-events", "none")
      .attr("text-anchor", "middle")
      .style("user-select", "none")
      .attr("font-size", 10)
    .selectAll("text")
    .data(root.descendants().slice(1))
    .join("text")
      .attr("dy", "0.35em")
      .attr("fill-opacity", d => +labelVisible(d.current))
      .attr("transform", d => labelTransform(d.current))
      .text(d => d.data.data.name);

  function labelVisible(d) {
    return d.value / root.value > 0.01;
  }
  function labelTransform(d) {
    const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
    const y = (d.y0 + d.y1) / 2 * radius;
    return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
  }
}

function clickSunburst(parentName, SVG_name, timeRange){
  var root = sunFromTrans(timeRange)
  d3.select("#" + SVG_name).remove()
  root = d3.partition()
          .size([2 * Math.PI, root.height+1])
          (root);

  parentWidth = document.getElementById(parentName).offsetWidth
  var margin = {top: 10, right: 10, bottom: 10, left: 10},
  width = parentWidth - margin.left - margin.right
  height = width
  radius = width / 6
  color = d3.scaleOrdinal()
    .domain(root.data.children.map(d => d.data.name))
    .range(d3.quantize(d => d3.interpolateRainbow(d), root.data.children.length + 1).reverse())

  const svg = d3.select('#' + parentName).append("svg")
      .attr("id", SVG_name)
      .attr("height", height)
      .attr("width", width)
      .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
    .padRadius(radius * 1.5)
    .innerRadius(d => d.y0 * radius)
    .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

  root.each(d => d.current = d);

  const path = svg.append("g")
    .selectAll("path")
    .data(root.descendants().slice(1))
    .join("path")
      .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.data.name); })
      .attr("fill-opacity", d => arcVisible(d.current) ? 1 : 0)
      .attr("d", d => arc(d.current))

  path.append("title")
      .text(d => d.data.data.name + '\n' + '$' + d.value + ',   ' + Math.round(1000*d.value/root.value)/10 + '%')

  path.filter(d => d.children)
      .style("cursor", "pointer")
      .on("click", clicked);

  const label = svg.append("g")
      .attr("pointer-events", "none")
      .attr("text-anchor", "middle")
      .style("user-select", "none")
      .attr("font-size", 10)
    .selectAll("text")
    .data(root.descendants().slice(1))
    .join("text")
      .attr("dy", "0.35em")
      .attr("fill-opacity", d => +labelVisible(d.current))
      .attr("transform", d => labelTransform(d.current))
      .text(d => d.data.data.name);

  const parent = svg.append("circle")
      .datum(root)
      .attr("r", radius)
      .attr("fill", "none")
      .attr("pointer-events", "all")
      .on("click", clicked)

  lastClick = 0
  function clicked(p) {
    fillSunTable(p)
    parent.datum(p.parent || root);

    if (p.depth < lastClick) {p = root} // if click center, retract to top level
    lastClick = p.depth
    root.each(d => d.target = {
      x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      y0: Math.max(0, d.y0 - p.depth),
      y1: Math.max(0, d.y1 - p.depth)
    });
    const t = svg.transition().duration(1000);
    // Transition the data on all arcs, even the ones that aren’t visible,
    // so that if this transition is interrupted, entering arcs will start
    // the next transition from the desired position.
    path.transition(t)
        .tween("data", d => {
          const i = d3.interpolate(d.current, d.target);
          return t => d.current = i(t);
        })
      .filter(function(d) {
        return +this.getAttribute("fill-opacity") || arcVisible(d.target);
      })
        .attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.8 : 0.4) : 0)
        .attrTween("d", d => () => arc(d.current));

    label.filter(function(d) {
        return +this.getAttribute("fill-opacity") || labelVisible(d.target);
      }).transition(t)
        .attr("fill-opacity", d => +labelVisible(d.target))
        .attrTween("transform", d => () => labelTransform(d.current));
  }

  function arcVisible(d) {
    return d.y1 <= 3 && d.y0 >= 1 && d.x1 > d.x0;
  }

  function labelVisible(d) {
    return d.y1 <= 3 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03;
  }

  function labelTransform(d) {
    const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
    const y = (d.y0 + d.y1) / 2 * radius;
    return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
  }
}

function fillSunTable(d){
  leaves = d.leaves()
  const names = [];
  leaves.forEach(e => names.push(e.data.id))
  range = document.getElementById('suntime').value;
  today = get_today(range)
  expense = to_object('expense')
  expenseGroup = expense.filter(e => e.Date >= today)
  expenseGroup = expenseGroup.filter(d => names.includes(d.Business) )
  table = document.getElementById('sunExpense')
  if (table.children.length > 1){table.children[table.children.length-1].remove()}
  makeClickTable(expenseGroup, 'sunExpense')
}

function generateDynamicTable(data, tableName){
		var entries = data.length;
		if (tableName != 'budgetTable'){
	    data.sort(function (a, b) {
	      return a.Date.localeCompare(b.Date);
	    } );
		}
		if(entries>0){

      var table = document.getElementById(tableName);
			// CREATE DYNAMIC TABLE.
      //Retrieve Column Headers
      var col = []; // define an empty array
			for (var i = 0; i < entries; i++) {
				for (var key in data[i]) {
					if (col.indexOf(key) === -1) {
						col.push(key);
					}
				}
			}

			// CREATE TABLE BODY .
			var tBody = document.createElement("tbody");
      tBody.setAttribute('id', tableName + 'body')
			// ADD COLUMN HEADER TO ROW OF TABLE HEAD.
			for (var i = entries-1; i >-1; i--) {

			var bRow = document.createElement("tr"); // CREATE ROW FOR EACH RECORD .

			for (var j = 0; j < col.length + 1; j++) {
        var td = document.createElement("td");
        if (j == col.length){
          td.innerHTML = '<input type="button" value="&#9998;" onclick="EditRow(this)">'
        } else{
          td.innerHTML = data[i][col[j]];
        }
				bRow.appendChild(td);
			}
      tBody.appendChild(bRow)
		}
		table.appendChild(tBody);
	}
}

function EditRow(r){
  var i = r.parentNode.parentNode.rowIndex;
  tableName = r.parentNode.parentNode.parentNode.parentNode.id
  var c = document.getElementById(tableName).rows[0].cells.length
  for (var j = 0; j < c-1; j++) {
    document.getElementById(tableName).rows[i].cells[j].setAttribute('contenteditable','true')
    document.getElementById(tableName).rows[i].cells[j].style.backgroundColor = "lightblue"
  }
  document.getElementById(tableName).rows[i].cells[c-1].innerHTML = '<input type="button" value="&#128190;" onclick="FreezeRow(this)"><input type="button" value="&#10060;" onclick="deleteRow(this)">'
}

function FreezeRow(r){
  var i = r.parentNode.parentNode.rowIndex;
  tableName = r.parentNode.parentNode.parentNode.parentNode.id
  var c = document.getElementById(tableName).rows[0].cells.length
  for (var j = 0; j < c-1; j++) {
    document.getElementById(tableName).rows[i].cells[j].setAttribute('contenteditable','false')
    document.getElementById(tableName).rows[i].cells[j].style.backgroundColor = "#fdf6e3"
  }
  document.getElementById(tableName).rows[i].cells[c-1].innerHTML = '<input type="button" value="&#9998;" onclick="EditRow(this)">'
}

function initialize_input(){
  reverse_h = reverse_hierarchy()
  biz_h = reverse_h[0]
  sc_h = reverse_h[1]
  var biz_options = ''; // inilialize 'datalist' ul's
  var sc_options = '';
  Object.keys(biz_h).forEach(function(key) {
    biz_options += '<option value="'+key+'" />'; // add option to autocomplete list
  });
  document.getElementById('businesslist').innerHTML = biz_options;
  Object.keys(sc_h).forEach(function(key) {
    sc_options += '<option value="'+key+'" />'; // add option to autocomplete list
  });
  document.getElementById('subcatlist').innerHTML = sc_options;
}

function fill(){
  biz_h = reverse_hierarchy()[0]
  val = document.getElementById('EBiz').value
  if (val in biz_h){
    document.getElementById('ESub').value = biz_h[val]['subcategory']
    fill_c()
  }else{
    alert('Please choose a subcategory this new business')
  }
}

function fill_c(){
  sc_h = reverse_hierarchy()[1]
  val = document.getElementById('ESub').value
  document.getElementById('ECat').innerHTML = sc_h[val]['category']
}

function CommitExpense(){
  var table = document.getElementById("expenseTable")
  var row = table.insertRow(2)
  var datecell = row.insertCell(0)
	var catcell = row.insertCell(1)
	var subcell = row.insertCell(2)
	var loccell = row.insertCell(3)
  var bizcell = row.insertCell(4)
  var amcell = row.insertCell(5)
  var delcell = row.insertCell(6)
  datecell.innerHTML = document.getElementById('EDate').value
  bizcell.innerHTML = document.getElementById('EBiz').value
  amcell.innerHTML = document.getElementById('EAm').value
  loccell.innerHTML = document.getElementById('ELoc').value
  subcell.innerHTML = document.getElementById('ESub').value
  catcell.innerHTML = document.getElementById('ECat').innerHTML
  delcell.innerHTML = '<input type="button" value="&#10060;" onclick="deleteRow(this)">'

  document.getElementById('EDate').value = ''
  document.getElementById('EBiz').value = ''
  document.getElementById('EAm').value = 0
  document.getElementById('ELoc').value = ''
  document.getElementById('ESub').value = ''
  document.getElementById('ECat').innerHTML = ''
}

function CommitIncome(){
  var table = document.getElementById("incomeTable")
  var row = table.insertRow(2)
  var datecell = row.insertCell(0)
  var loccell = row.insertCell(1)
  var amcell = row.insertCell(2)
  var delcell = row.insertCell(3)
  datecell.innerHTML = document.getElementById('IDate').value
  loccell.innerHTML = document.getElementById('ILoc').value
  amcell.innerHTML = document.getElementById('IAm').value
  delcell.innerHTML = '<input type="button" value="&#10060;" onclick="deleteRow(this)">'

  document.getElementById('IDate').value = ''
  document.getElementById('IAm').value = 0
  document.getElementById('ILoc').value = ''
}

function CommitGoal(){
  var table = document.getElementById("goalTable")
  var row = table.insertRow(2)
  var datecell = row.insertCell(0)
  var amcell = row.insertCell(1)
	var comcell = row.insertCell(2)
  var delcell = row.insertCell(3)
  datecell.innerHTML = document.getElementById('GDate').value
  amcell.innerHTML = document.getElementById('GAm').value
	comcell.innerHTML = document.getElementById('GCom').value
  delcell.innerHTML = '<input type="button" value="&#10060;" onclick="deleteRow(this)">'

  document.getElementById('GDate').value = ''
  document.getElementById('GAm').value = 0
  document.getElementById('GCom').value = ''
}

function deleteRow(r) {
  var i = r.parentNode.parentNode.rowIndex;
  tableName = r.parentNode.parentNode.parentNode.parentNode.id
  document.getElementById(tableName).deleteRow(i);
}

function clearTable(id){
  table = document.getElementById(id)
  table.children[table.children.length-1].remove()
}

function tableToJson(id) {
  var table = document.getElementById(id)
  var data = [];
  // first row needs to be headers
  var headers = [];
  for (var i=0; i<table.rows[0].cells.length; i++) {
      headers[i] = table.rows[0].cells[i].innerHTML.replace(/ /gi,'');
  }
  // go through cells
	start = 2
	if (id == 'budgetTable'){start = 1}
  for (var i=start; i<table.rows.length; i++) {
      var tableRow = table.rows[i];
      var rowData = {};
      for (var j=0; j<tableRow.cells.length -1; j++) {
          rowData[headers[j]] = tableRow.cells[j].innerHTML;
      }
      data.push(rowData);
  }
  return data;
}

function makeCalender(){
  data = prep_calender()
  data.sort((a, b) => new Date(a.Date) - new Date(b.Date));

  //filter = dropdownoption
  var w = 1250
  var h = 600
  var cellSize = 20
  color = d3.interpolateReds

  const dateValues = data.map(dv => ({
    date: d3.timeDay(new Date(dv.Date).setDate(new Date(dv.Date).getDate() + 1)),
    // ^ need to add 1 day to string value when working with days
    value: Number(dv.base)
  }));

  var svg = d3.select("#holdCalender")
      .append("svg")
      .attr("id", 'calender')
      .attr("width", w)
      .attr("height", h)
      .append("g");

  const { width, height } = document
    .getElementById("calender")
    .getBoundingClientRect();

  //draw_github()
  draw_months()

  function draw_github() {
    const years = d3
      .nest()
      .key(d => d.date.getUTCFullYear())
      .entries(dateValues)
      .reverse();

    const months = d3
      .nest()
      .key(d => d.date.getUTCMonth())
      .entries(dateValues)
      .reverse();

    const values = dateValues.map(c => c.value);
    const maxValue = d3.max(values);
    const minValue = d3.min(values);
    const yearHeight = cellSize * 7;
    const group = svg.append("g");
    const year = group
      .selectAll("g")
      .data(years)
      .join("g")
      .attr(
        "transform",
        (d, i) => `translate(50, ${yearHeight * i + cellSize * 1.5})`
      );

    year
      .append("text")
      .attr("x", -5)
      .attr("y", -30)
      .attr("text-anchor", "end")
      .attr("font-size", 16)
      .attr("font-weight", 550)
      .attr("transform", "rotate(270)")
      .text(d => d.key);

    const formatDay = d =>
      ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"][d.getUTCDay()];
    const countDay = d => d.getUTCDay();
    const timeWeek = d3.utcSunday;
    const formatDate = d3.utcFormat("%x");
    const colorFn = d3
      .scaleThreshold()
      .domain([-0.001,1,10,25,50,100,250,500,1000,1500,2000,maxValue])
      .range([0.01,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    const format = d3.format("+.2%");

    year
      .append("g")
      .attr("text-anchor", "end")
      .selectAll("text")
      .data(d3.range(7).map(i => new Date(1995, 0, i)))
      .join("text")
      .attr("x", -5)
      .attr("y", d => (countDay(d) + 0.5) * cellSize)
      .attr("dy", "0.31em")
      .attr("font-size", 12)
      .text(formatDay);

    year
      .append("g")
      .selectAll("rect")
      .data(d => d.values)
      .join("rect")
      .attr("width", cellSize - 1.5)
      .attr("height", cellSize - 1.5)
      .attr("x",(d, i) => timeWeek.count(d3.utcYear(d.date), d.date) * cellSize + 10)
      .attr("y", d => countDay(d.date) * cellSize + 0.5)
      .attr("fill", d => color(colorFn(d.value)))
      .on("click", function(d){
        table = document.getElementById('calExpense')
        if (table.children.length > 1){table.children[table.children.length-1].remove()}
        expense = to_object('expense')
        expenseDay = expense.filter(e => e.Date == format_datetime(new Date(d.date)))
        makeClickTable(expenseDay, 'calExpense')
       })
      .append("title")
      .text(d => `${formatDate(new Date(d.date))}: ${d.value.toFixed(2)}`)

    const legend = group
      .append("g")
      .attr(
        "transform",
        `translate(10, ${years.length * yearHeight + cellSize * 4})`
      );

      const staircase = [-0.001,1,10,25,50,100,250,500,1000,1500,2000,maxValue]
      const categoriesCount = staircase.length-1;
      const categories = [...Array(categoriesCount)].map((_, i) => {
      const upperBound = staircase[i + 1]
      const lowerBound = staircase[i]

      return {
        upperBound,
        lowerBound,
        color: color((i + 1) / categoriesCount),
        selected: true
      };
    });

    console.log(categories)

    const legendWidth = 60;
    function toggle(legend) {
      const { lowerBound, upperBound, selected } = legend;

      legend.selected = !selected;
      const highlightedDates = years.map(y => ({
        key: y.key,
        values: y.values.filter(
          v => v.value > lowerBound && v.value <= upperBound
        )
      }));

      year
        .data(highlightedDates)
        .selectAll("rect")
        .data(d => d.values, d => d.date)
        .transition()
        .duration(500)
        .attr("fill", d => (legend.selected ? color(colorFn(d.value)) : "white"));
    }

    legend
      .selectAll("rect")
      .data(categories)
      .enter()
      .append("rect")
      .attr("fill", d => d.color)
      .attr("x", (d, i) => legendWidth * i)
      .attr("width", legendWidth)
      .attr("height", 15)
      .on("click", toggle);

    legend
      .selectAll("text")
      .data(categories)
      .join("text")
      .attr("transform", "rotate(90)")
      .attr("y", (d, i) => -legendWidth * i)
      .attr("dy", -30)
      .attr("x", 18)
      .attr("text-anchor", "start")
      .attr("font-size", 11)
      .text(d => `${d.lowerBound.toFixed(0)} - ${d.upperBound.toFixed(0)}`);

    legend
      .append("text")
      .attr("dy", -5)
      .attr("font-size", 14)
      .attr("text-decoration", "underline")
      .text("Click on category to select/deselect days");
  }

  function draw_months() {
    const months = d3
      .nest()
      .key(d => d.date.getUTCMonth())
      .entries(dateValues)
      .reverse();

    console.log(months)

    const values = dateValues.map(c => c.value);
    const maxValue = d3.max(values);
    const minValue = d3.min(values);
    const yearHeight = cellSize * 7;
    const group = svg.append("g");
    const year = group
      .selectAll("g")
      .data(months)
      .join("g")
      .attr("transform",(d, i) => `translate(50, 10)`);

    year
      .append("text")
      .attr("x", -5)
      .attr("y", -30)
      .attr("text-anchor", "end")
      .attr("font-size", 16)
      .attr("font-weight", 550)
      .attr("transform", "rotate(270)")
      .text(d => d.key);

    const formatMonth = d =>
      ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getUTCMonth()];
    const formatDay = d =>
      ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"][d.getUTCDay()];

    const countDay = d => d.getUTCDay();
    const countMonth = d => d.getUTCMonth();
    const timeWeek = d3.utcSunday;
    const formatDate = d3.utcFormat("%x");
    today = new Date()
    year_now = today.getYear()
    month_now = today.getMonth() + 1
    const colorFn = d3
      .scaleThreshold()
      .domain([-0.001,1,10,25,50,100,250,500,1000,1500,2000,maxValue])
      .range([0.01,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    const format = d3.format("+.2%");

    year
      .append("g")
      .attr("text-anchor", "end")
      .selectAll("text")
      .data(d3.range(12).map(i => new Date(1995, i, 1)))
      .join("text")
      .attr("x", d => (countMonth(d)%4) * 9 * cellSize + 4.5 * cellSize)
      .attr("y", d =>  Math.floor((countMonth(d)/4)) * 7 * cellSize)
      .attr("dy", "0.31em")
      .attr("font-size", 12)
      .text(formatMonth);

    year
      .append("g")
      .selectAll("rect")
      .data(d => d.values)
      .join("rect")
      .attr("width", cellSize - 1.5)
      .attr("height", cellSize - 1.5)
      .attr("x",function(d){
        month_x = (d.date.getMonth()%4) * 9 * cellSize
        day_x = countDay(d.date) * cellSize
        return month_x + day_x
      })
      .attr("y", function(d){
        month_y = Math.floor((d.date.getMonth()/4)) * 7 * cellSize + 5
        week_y = d3.utcWeek.count(d3.utcMonth(d.date), d.date) * cellSize
        return month_y + week_y
      })
      .attr("fill", d => color(colorFn(d.value)))
      .on("click", function(d){
        table = document.getElementById('calExpense')
        if (table.children.length > 1){table.children[table.children.length-1].remove()}
        expense = to_object('expense')
        expenseDay = expense.filter(e => e.Date == format_datetime(new Date(d.date)))
        makeClickTable(expenseDay, 'calExpense')
       })
      .append("title")
      .text(d => `${formatDate(new Date(d.date))}: ${d.value.toFixed(2)}`)

    const legend = group
      .append("g")
      .attr(
        "transform",
        `translate(10, ${3 * cellSize * 7 + 50})`
      );

      const staircase = [-0.001,1,10,25,50,100,250,500,1000,1500,2000,maxValue]
      const categoriesCount = staircase.length-1;
      const categories = [...Array(categoriesCount)].map((_, i) => {
      const upperBound = staircase[i + 1]
      const lowerBound = staircase[i]

      return {
        upperBound,
        lowerBound,
        color: color((i + 1) / categoriesCount),
        selected: true
      };
    });

    const legendWidth = 60;
    function toggle(legend) {
      const { lowerBound, upperBound, selected } = legend;

      legend.selected = !selected;
      const highlightedDates = months.map(y => ({
        key: y.key,
        values: y.values.filter(
          v => v.value > lowerBound && v.value <= upperBound
        )
      }));

      year
        .data(highlightedDates)
        .selectAll("rect")
        .data(d => d.values, d => d.date)
        .transition()
        .duration(500)
        .attr("fill", d => (legend.selected ? color(colorFn(d.value)) : "white"));
    }

    legend
      .selectAll("rect")
      .data(categories)
      .enter()
      .append("rect")
      .attr("fill", d => d.color)
      .attr("x", (d, i) => legendWidth * i)
      .attr("width", legendWidth)
      .attr("height", 15)
      .on("click", toggle);

    legend
      .selectAll("text")
      .data(categories)
      .join("text")
      .attr("transform", "rotate(90)")
      .attr("y", (d, i) => -legendWidth * i)
      .attr("dy", -30)
      .attr("x", 18)
      .attr("text-anchor", "start")
      .attr("font-size", 11)
      .text(d => `${d.lowerBound.toFixed(0)} - ${d.upperBound.toFixed(0)}`);

    legend
      .append("text")
      .attr("dy", -5)
      .attr("font-size", 14)
      .attr("text-decoration", "underline")
      .text("Click on category to select/deselect days");
  }
}



function makeMap(parentName, SVG_name, map_data, covid_data){
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
  today = 20200514
  fdata = covid_data.filter(d => d.date == today)
  Object.entries(fdata).forEach(d => data[d[1].fips] = d[1].positive)


  g.append("g")
    .attr("fill", "#444")
    .attr("cursor", "pointer")
    .selectAll("path")
    .data(topojson.feature(map_data, map_data.objects.states).features)
    .join("path")
      .attr("fill", d => color(data[parseInt(d.id)]))
      .on('click', clicked)
      .attr("d", path)
    .append("title")
      .text(d => d.properties.name + ', Cases:' + data[parseInt(d.id)]);


  const zoom = d3.zoom()
    .scaleExtent([1, 8])
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
