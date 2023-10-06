document.addEventListener('DOMContentLoaded', function () {
  const arrow = document.getElementById('arrow');
  const sidebar = document.getElementById('sidebar');

  arrow.addEventListener('click', function () {
    if (sidebar.style.right === '0px' || sidebar.style.right === '') {
      sidebar.style.right = '-40vw';
    } else {
      sidebar.style.right = '0px';
    }
  });
});

function fetchDataAndCreateChart(containerId, chartTitle, type) {
  fetch(document.URL.split("/").slice(0, 3).join("/") + '/getLog/' + document.URL.split("/").pop())
    .then(function (response) {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(function (data) {
      // Create a chart and add series with the fetched data
      var chart = anychart.line();
      // Manually set series colors
      var colors = ["#FF5733", "#FFD933", "#33FF57", "#3377FF", "#FF33CC"];

      // Add each header (except "Date", "model", and "action") as a series with a specified color
      Object.keys(data[0]).forEach(function (key, index) {
        if (type == 1) {
          if (key !== "Date") {
            var series = chart.line(data.map(function (entry) {
              return [entry.Date, entry[key]];
            }));
            series.name(key);
  
            // Set the color from the predefined array
            series.color(colors[index % colors.length]);
          }
        }
        else  if (type == 2) {
          if (key !== "Date" && key !== "model" && key !== "action" && key !== "benchmark") {
            var series = chart.line(data.map(function (entry) {
              return [entry.Date, entry[key]];
            }));
            series.name(key);
  
            // Set the color from the predefined array
            series.color(colors[index % colors.length]);
          }
  
        }
        else {
          if (key !== "Date" && key !== "model" && key !== "action") {
            var series = chart.line(data.map(function (entry) {
              return [entry.Date, entry[key]];
            }));
            series.name(key);
  
            // Set the color from the predefined array
            series.color(colors[index % colors.length]);
          }  
        }
      });

      // Customize chart appearance
      chart.title(chartTitle);
      chart.container(containerId);

      // Configure X-axis
      chart.xAxis().title("Date");

      // Configure Y-axis
      chart.yAxis().title("Value");

      // Enable grid lines
      chart.xGrid().enabled(true);
      chart.yGrid().enabled(true);

      // Enable tooltips with custom format
      chart.tooltip().titleFormat("{%SeriesName}");
      chart.tooltip().format("{%SeriesName}: {%Value}");

      // Add a range selector
      // chart.plot(0).ui().append("rangeSelector");

      // Draw the chart
      chart.draw();
    })
    .catch(function (error) {
      console.error('Error:', error);
    });
}

anychart.onDocumentReady(function () {
  // Call the function for the 'reward' chart
  fetchDataAndCreateChart("reward", "Reward", 1);
});

anychart.onDocumentReady(function () {
  // Call the function for the 'state' chart
  fetchDataAndCreateChart("state", "State", 2);
});
