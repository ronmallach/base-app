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
