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
