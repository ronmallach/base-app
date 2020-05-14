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
