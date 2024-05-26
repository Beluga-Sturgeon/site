

function fetchDataAndCreateChart(containerId, chartTitle, type, data) {
  console.log(data);
  // Create a chart and add series with the fetched data
  var chart = anychart.stock();
  // Manually set series colors
  var colors = ["#FF5733", "#FFD933", "#33FF57", "#3377FF", "#FF33CC"];

  // Add each header (except "Date", "model", and "action") as a series with a specified color
  Object.keys(data[0]).forEach(function (key, index) {
    if (type == 1) {
      if (key !== "Date") {
        var series = chart.plot(0).line(data.map(function (entry) {
          return [entry.Date, entry[key]];
        }));
        series.name(key);

        // Set the color from the predefined array
        series.color(colors[index % colors.length]);
      }
    } else if (type == 2) {
      if (key !== "Date" && key !== "model" && key !== "action" && key !== "benchmark") {
        var series = chart.plot(0).line(data.map(function (entry) {
          return [entry.Date, entry[key]];
        }));
        series.name(key);

        // Set the color from the predefined array
        series.color(colors[index % colors.length]);
      }
    } else {
      if (key === "action") {
        var series = chart.plot(0).line(data.map(function (entry) {
          return [entry.Date, entry[key]];
        }));
        series.name(key);

        // Set the color from the predefined array
        series.color(colors[index % colors.length]);
      }
    }
  });

  // Customize chart appearance
  chart.plot(0).title(chartTitle);
  chart.container(containerId);
  chart.background().fill("rgba(0,0,0,0)");
  // Configure X-axis
  // chart.xAxis().title("Date");

  // // Configure Y-axis
  // chart.yAxis().title("Value");

  // Enable grid lines
  chart.plot(0).xGrid().enabled(true);
  chart.plot(0).yGrid().enabled(true);

  // Enable tooltips with custom format
  chart.tooltip().titleFormat("{%SeriesName}");
  chart.tooltip().format("{%SeriesName}: {%Value}");

  // Draw the chart
  chart.draw();
}

// Fetch the data once and pass it into the function
fetch(document.URL.split("/").slice(0, 3).join("/") + '/getLog/' + document.URL.split("/").pop())
  .then(function (response) {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(function (data) {
    anychart.onDocumentReady(function () {
      // Call the function for the 'reward' chart
      fetchDataAndCreateChart("reward", "Reward", 1, data);
    });
    anychart.onDocumentReady(function () {
      // Call the function for the 'state' chart
      fetchDataAndCreateChart("state", "State", 2, data);
    });
    anychart.onDocumentReady(function () {
      // Call the function for the 'reward' chart
      fetchDataAndCreateChart("actiongraph", "Actions", 3, data);
    });
  })
  .catch(function (error) {
    console.error('Error:', error);
  });
