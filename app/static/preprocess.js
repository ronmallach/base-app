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
