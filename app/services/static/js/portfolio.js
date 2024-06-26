$.each(portfolio, (i, model) => {
    const model_card = $("<div>").addClass("model_card")
    console.log()

    model = sort_object(model) //Not perfect for sorting by highest priority, but loads much faster than doing it sequentially

    $.each(Object.keys(model), (i, t) => {
        fetchTickerData(t).then(ticker => {
            if (ticker !== null){
                console.log(ticker)
                const tickerElement = $("<div>").addClass("ticker_row");
                tickerElement.append($("<img>").attr("src", ticker.companyLogoUrl).addClass('ticker_logo'));
                tickerElement.append($("<p>").text(t).addClass('ticker'));
                tickerElement.append($("<p>").text(`${model[t]}%`).addClass('percentage'))

                model_card.append(tickerElement)
            }
        });
    });
    $('#main_box').prepend(model_card)
});

function fetchTickerData(ticker) {
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

$('#plus').on('click', () => {
        if ($('#plus h2').text() === 'Buy New Portfolio'){
            window.location.href = "/payment"
        }
        else {
            window.location.href = "/build-model"
        }
    }
);
