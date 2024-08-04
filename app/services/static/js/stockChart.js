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
  var csv = 'date,open,high,low,close,action\n';
  data.forEach(function (item) {
    csv += item.date + ',' + item.open + ',' + item.high + ',' + item.low + ',' + item.close + ',' + item.action + '\n';
  });
  return csv;
}


async function createCandlestickChart(data, name) {
  try {
    fetch(document.URL.split("/").slice(0, 3).join("/") + '/getLog/' + document.URL.split("/").pop())
  .then(function (response) {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(function (fetchedData) {
    const fetchedSeries = fetchedData.map(entry => ({ date: entry.Date, action: entry.action }));
    let tempJ = 0;
    let isOver = false;

    console.log(fetchedSeries);

    for (let i = 0; i < data.length; i++) {
      if (isOver) break;

      for (let j = tempJ; j < fetchedSeries.length; j++) {
        const fetchedDate = new Date(fetchedSeries[j].date).toISOString().split('T')[0];

        if (fetchedDate === data[i].date) {
          data[i].action = fetchedSeries[j].action;
          tempJ = j + 1;
          break;
        } else {
          console.log(`No action found for data index ${i} or date mismatch (data date: ${data[i].date}, fetched date: ${fetchedDate})`);
        }

        if (j === fetchedSeries.length) {
          isOver = true;
        }
      }
    }

    const dataCSV = convertDataToCSV(data);

    const dataTable = anychart.data.table();

    const csvSettings = { ignoreFirstRow: true, columnsSeparator: ",", rowsSeparator: "\n" };
    dataTable.addData(dataCSV, csvSettings);

    const mapping = dataTable.mapAs({
      "open": 1,
      "high": 2,
      "low": 3,
      "close": 4
    });

    console.log(mapping);

    const chart = anychart.stock();
    const plot = chart.plot(0);
    const series = plot.candlestick(mapping);

    plot.yGrid(true).xGrid(true).yMinorGrid(false).xMinorGrid(false);
    plot.xGrid().stroke({ color: "#707070", thickness: 1 });
    plot.yGrid().stroke({ color: "#707070", thickness: 1 });

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

    const rangeSelector = anychart.ui.rangeSelector();
    const rangePicker = anychart.ui.rangePicker();

    changeTableStyle();
    $('#loadingText').fadeOut("slow");
    chart.draw();
    rangePicker.render(chart);
    rangeSelector.render(chart);

    // Add marker series for the "action" attribute
    const actionData = data.filter(item => item.action).map(item => [item.date, item.action]);
    const actionDataTable = anychart.data.table();
    actionDataTable.addData(actionData);

    const actionMapping = actionDataTable.mapAs({
      "x": 0,
      "value": 1
    });

    const markerSeries = plot.marker(actionMapping);
    markerSeries.name("action");
    markerSeries.type('circle');
    markerSeries.size(0);
    console.log("added marker series for action attribute");
  });
  } catch (error) {
    console.error('Error:', error);
  }
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