$.each(portfolio, (i, model) => {
    const model_card = $("<div>").addClass("model_card");
    console.log(model);

    const tickerPromises = [];
    keys = [];

    $.each(Object.keys(model), (i, t) => {
        // Skip 'last_updated' key
        if (t === 'last_updated') {
            return true;
        }

        keys.push(t);
        tickerPromises.push(fetchTickerData(t).then(ticker => {
            if (ticker !== null) {
                console.log(ticker);
                const tickerElement = $("<div>").addClass("ticker_row");
                tickerElement.append($("<img>").attr("src", ticker.companyLogoUrl).addClass('ticker_logo'));
                tickerElement.append($("<p>").text(t).addClass('ticker'));
                tickerElement.append($("<p>").text(`${model[t]}%`).addClass('percentage'));

                model_card.append(tickerElement);
            }
        }));
    });

    Promise.all(tickerPromises).then(() => {
        model_card.append($("<p>").text("Last Updated: " + model.last_updated).addClass('update_text').css('color', 'white'));

        const today = new Date();
        const yyyy = today.getFullYear();
        let mm = today.getMonth() + 1; // Months start at 0!
        let dd = today.getDate();

        if (dd < 10) dd = '0' + dd;
        if (mm < 10) mm = '0' + mm;

        const formattedToday = mm + '-' + dd + '-' + yyyy;
        console.log(formattedToday)
        if (model.last_updated != formattedToday){
            const refresh = $("<img>").attr("src", `static/images/reload.png`).addClass('reload_img');
            refresh.on('click', e => {
                console.log(keys)
                refreshPortfolio(keys)
            });
            model_card.append(refresh);
        }

        $('#main_box').prepend(model_card);
    });
});

$('#plus').on('click', () => {
        if ($('#plus h2').text() === 'Buy New Portfolio'){
            window.location.href = "/payment"
        }
        else {
            window.location.href = "/build-model"
        }
    }
);

function refreshPortfolio(tickers) {
    fetch(document.URL.split("/").slice(0, 3).join("/") + '/runPortfolio', 
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(tickers)
        })
        .then(function(response) {
            return response.text();
        })
        .then(function(text) {
            //Check every ten seconds
            if (text === "Not Ready") {
                setTimeout(function() {
                    refreshPortfolio(tickers);
                }, 10000);
            } else {
                window.location.href = text;
            }
        })
        .catch(function(error) {
            console.error(error);
        });
}


function fetchTickerData(ticker) {
    console.log("Ticker is " + ticker)
    return new Promise((resolve, reject) => {
        const xhttp = new XMLHttpRequest();
        
        xhttp.onreadystatechange = function() {
            if (xhttp.status === 0 || (xhttp.status >= 200 && xhttp.status < 400)) {
                try {
                    const tickerData = JSON.parse(this.responseText);
                    xhttp.abort();
                    resolve(tickerData);
                } catch (e) {
                }
            } 
        };
        
        xhttp.open("GET", "/getInfo/" + ticker, true);
        xhttp.send();
    });
}

function sort_object(obj) {
    items = Object.keys(obj).map(function(key) {
        return [key, obj[key]];
    });
    items.sort(function(first, second) {
        return second[1] - first[1];
    });
    sorted_obj={}
    $.each(items, function(k, v) {
        use_key = v[0]
        use_value = v[1]
        sorted_obj[use_key] = use_value
    })
    return(sorted_obj)
} 
