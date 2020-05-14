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
