async function fetchFinancialData(symbol, startDate, endDate) {

  const apiKey = 'b0446da02c01a0943a01730dc2343e34'; // Replace with your FMP API key
  const apiUrl = `https://financialmodelingprep.com/api/v3/historical-price-full/${symbol}?from=${startDate}&to=${endDate}&apikey=${apiKey}`;
  console.log(apiUrl);
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    return data.historical;
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}


function getDate() {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0'); // January is 0!
  var yyyy = today.getFullYear();

  today = yyyy + '-' + mm + '-' + dd;
  return today;
}

function convertDataToCSV(data) {
  var csv = 'date,open,high,low,close\n';
  data.forEach(function (item) {
    csv += item.date + ',' + item.open + ',' + item.high + ',' + item.low + ',' + item.close + '\n';
  });
  return csv;
}


function createCandlestickChart(data, name) {
  var dataCSV = convertDataToCSV(data); // Assuming data is an array of symbols, and you're using the data for the first symbol.
  var dataTable = anychart.data.table();
  var csvSettings = { ignoreFirstRow: true, columnsSeparator: ",", rowsSeparator: "\n" };
  dataTable.addData(dataCSV, csvSettings);
  // Create a mapping for the candlestick chart
  var mapping = dataTable.mapAs({
    "open": 1,
    "high": 2,
    "low": 3,
    "close": 4
  });

  // Create the chart with the mapping and other settings
  var chart = anychart.stock();
  var plot = chart.plot(0);
  var series = plot.candlestick(mapping);
  var controller = plot.annotations();
  // ...
    controller.verticalLine({
  xAnchor: getDate()
  });

  plot.yGrid(true).xGrid(true).yMinorGrid(false).xMinorGrid(false);
  plot.xGrid().stroke({
  color: "#707070",
  thickness: 1
  });
  plot.yGrid().stroke({
  color: "#707070",
  thickness: 1
  });

  series.name(name);

  series.legendItem().iconType('rising-falling');
  series.risingFill("#00FF19");
  series.risingStroke("rgba(45, 89, 64,1)");
  series.fallingFill("#FF0000");
  series.fallingStroke("rgba(89, 46, 45,1)");

  chart.container('graph');
  chart.background().fill("rgba(0,0,0,0)");
  chart.draw();

  console.log("finished drawing chart");
  changeTableStyle();
  $('#loadingText').fadeOut("slow");
  chart.draw();
}

// Main function to fetch data and create the chart
async function main() {
  const symbol = document.URL.split("/").pop(); // Replace with the desired stock symbol
  const startDate = '1900-01-01';
  const endDate = new Date().toISOString().split('T')[0];

  // Fetch financial data
  const financialData = await fetchFinancialData(symbol, startDate, endDate);
  console.log(financialData)
  // Create and render the candlestick chart
  if (financialData.length > 0) {
    createCandlestickChart(financialData, symbol);
  } else {
    console.error('No data available for the specified symbol and date range.');
  }
}

// Call the main function to initiate the process
main();




