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





  function getDate()
  {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();
    
    today = yyyy + '-' + mm + '-' + dd;
    return today
  }
  
  
  
anychart.onDocumentReady(function () {
    anychart.data.loadCsvFile(
    document.URL.split("/")[0]+'/getLog/' + document.URL.split("/").pop(),
    function (data) {
        
        console.log(data)
        data = data.replace(/['"]/g, '');
        console.log(data)
        // create data table on loaded data
        var lines = data.trim().split('\n');
        var headers = lines[0].split(',');
        
        // Parse the data into an array of objects
        var parsedData = [];
        for (var i = 1; i < lines.length; i++) {
            var values = lines[i].split(',');
        
            // Check if the row has the expected number of columns (same as headers)
            if (values.length !== headers.length) {
                console.warn('Skipping row ' + i + ' due to inconsistent column count.');
                continue;
            }
        
            var entry = {};
            for (var j = 0; j < headers.length; j++) {
                // Remove leading/trailing whitespace and quotes before parsing
                var cleanedValue = values[j].trim().replace(/['"]/g, '');
                entry[headers[j]] = parseFloat(cleanedValue);
        
                // Check if the parsed value is NaN
                if (isNaN(entry[headers[j]])) {
                    console.warn('Value in row ' + i + ', column ' + headers[j] + ' is not a valid number.');
                }
            }
            parsedData.push(entry);
        }

        console.log(parsedData);
        var dataTable = anychart.data.table();
        dataTable.addData(parsedData);


        var ticker = document.URL.split("/").pop();
        var mapping = dataTable.mapAs(
            {
            ticker: 0,
            "SPY":1,
            "IEF":2,
            "GSG":3,
            "EUR=x":4,
            "action":5,
            "model":6
        }
        );

        // Create a chart and set the data
        var chart = anychart.stock();
        plot = chart.plot(0)

        var series = plot.candlestick(mapping);

        series.name(ticker);

        series.legendItem().iconType('rising-falling');

        chart.background().fill("#141414")


        // Set container and draw the chart
        chart.container('state');
        chart.draw();
    }
    );
});
  