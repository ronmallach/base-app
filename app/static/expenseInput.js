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
