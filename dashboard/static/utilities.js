// Functions used for sorting tables. Call enableTableSorter() from a page to
// make all tables on the page sortable by clicking at the th.
function comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? 
              valA - valB : valA.toString().localeCompare(valB)
    }
}
function getCellValue(row, index){ return $(row).children('td').eq(index).text() }

function enableTableSorter() {
  $('th').click(function(){
      var table = $(this).parents('table').eq(0)
      var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
      this.asc = !this.asc
      if (!this.asc){rows = rows.reverse()}
      for (var i = 0; i < rows.length; i++){table.append(rows[i])}
  })
}

// A function used for displaying alerts which should disappear after a couple
// of seconds.
function printMessage(loc, text, type) {
  var element = $('<div>', {
    class: 'alert alert-' + type,
    id: text,
    text: text,
  })
  $(loc).append(element);
  setTimeout(function() { $(element).fadeOut(500); }, 2000);
  setTimeout(function() { $(element).remove(); }, 3000);
}
