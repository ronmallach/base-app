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
  Object.entries(covid_data.cases).forEach(d => data[covid_data.fips[d[0]]] = d[1])
  console.log(data)

  g.append("g")
    .attr("fill", "#444")
    .attr("cursor", "pointer")
    .selectAll("path")
    .data(topojson.feature(map_data, map_data.objects.counties).features)
    .join("path")
      .attr("fill", d =>  color(data[d.id]))
      .on('click', clicked)
      .attr("d", path)
    .append("title")
      .text(d => d.properties.name + ', Cases:' + data[d.id]);


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
