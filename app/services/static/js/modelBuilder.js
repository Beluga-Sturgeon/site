function handleTickerSubmit(){
    $('.search-container').toggleClass('hidden');
    const query = searchInput.value;
    if (query) {
        $('#searchForm')[0].reset();
        fetchSuggestions(query)
            .then(suggestions => {
                if (suggestions.length === 0) {
                    showInvalidTickerMessage(query);
                } else {
                    ticker = query
                    xhttp=new XMLHttpRequest();

                    xhttp.onreadystatechange = function() {
                        if (xhttp.status === 0 || (xhttp.status >= 200 && xhttp.status < 400)) {
                            const newTicker = JSON.parse(this.responseText);
                            newTicker.ticker = query
                            console.log(newTicker);
                            const tickerList = $('#ticker_list').tickers('option', 'tickers');
                            const tickerExists = tickerList.some(ticker => ticker.ticker === newTicker);
                            if (!tickerExists) {
                                $('#ticker_list').tickers('addTicker', newTicker);
                                console.log($('#ticker_list').tickers('option', 'tickers'));
                                xhttp.abort()
                            }
                        }
                    };

                    xhttp.open("GET", "/getInfo/" + ticker, true);
                    xhttp.send();
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    } else {
        showInvalidTickerMessage("");
    }
}

$(document).ready(() => {
    $('#ticker_list').tickers();

    $('#plus').on('click', e => {
        $('.search-container').toggleClass('hidden');
        $('#search').focus();
    });

    $('#build').on('click', e => {
        if ($('#warning').hasClass('hidden')){
            $('#warning').removeClass('hidden')
            $('#build p').text('I understand, build the model');
        } else {
            $('#ticker_list').tickers('export');
            window.location.href = "/portfolio";
        }
    });
});

$.widget("custom.tickers", {
    options: {
        tickers: [] 
    },

    _create: function() {
    },

    _refresh: function() {
        this.element.find('.ticker_row').remove();

        $.each(this.options.tickers, (index, ticker) => {
            this._renderTicker(ticker);
        });
    },

    _renderTicker: function(ticker) {
        const tickerElement = $("<div>").addClass("ticker_row").addClass('list_item');

        const tickerLogo = $("<div>").addClass("logo_box");
        const tickerImage = $("<img>").attr("src", ticker.companyLogoUrl).addClass('ticker_logo');
        tickerImage.on('load', () => {
            const averageRGB = getDominantColor(tickerImage.get(0));
            if (averageRGB.b >= 200 && averageRGB.g >= 200 && averageRGB.r >= 200){
                tickerImage.addClass('white_logo')
            }
        });
        tickerLogo.append(tickerImage);
        tickerLogo.append($("<p>").text(ticker.ticker).addClass('ticker'));
        tickerElement.append(tickerLogo)

        const nameBox = $("<div>").addClass("name_box");
        nameBox.append($("<h1>").text(`${ticker.companyName}`));
        nameBox.append($("<p>").text(`${ticker.marketStatus}`));
        tickerElement.append(nameBox)

        const shareBox = $("<div>").addClass("name_box").addClass('share_box');
        shareBox.append($("<p>").text('Current Share Price:'))
        const change = $("<h2>").text(`$${ticker.currentValue.value}`).addClass('price');

        if (ticker.currentValue.change.includes('-')){
            change.addClass('negative')
        } else {
            change.addClass('positive')
        }
        shareBox.append(change)
        tickerElement.append(shareBox)

        const remove = $("<div>").addClass('remove_box');
        const svg = $(`
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0.849199 0.571699C1.03266 0.38824 1.28148 0.285173 1.54093 0.285173C1.80038 0.285173 2.04921 0.38824 2.23267 0.571699L6.1525 4.49153L10.0723 0.571699C10.2558 0.38824 10.5046 0.285173 10.7641 0.285173C11.0235 0.285173 11.2723 0.38824 11.4558 0.571699C11.6393 0.755159 11.7423 1.00398 11.7423 1.26343C11.7423 1.52288 11.6393 1.77171 11.4558 1.95517L7.53597 5.875L11.4558 9.79483C11.6393 9.97829 11.7423 10.2271 11.7423 10.4866C11.7423 10.746 11.6393 10.9948 11.4558 11.1783C11.2723 11.3618 11.0235 11.4648 10.7641 11.4648C10.5046 11.4648 10.2558 11.3618 10.0723 11.1783L6.1525 7.25847L2.23267 11.1783C2.04921 11.3618 1.80038 11.4648 1.54093 11.4648C1.28148 11.4648 1.03266 11.3618 0.849199 11.1783C0.66574 10.9948 0.562673 10.746 0.562673 10.4866C0.562673 10.2271 0.66574 9.97829 0.849199 9.79483L4.76903 5.875L0.849199 1.95517C0.66574 1.77171 0.562673 1.52288 0.562673 1.26343C0.562673 1.00398 0.66574 0.755159 0.849199 0.571699Z" fill="white"/>
            </svg>        
        `);
        remove.append(svg);
        remove.on('click', e=> {
            $('#ticker_list').tickers('removeTicker', ticker);
        });

        tickerElement.append(remove);


        this.element.append(tickerElement);
    },

    addTicker: function(ticker) {
        this.options.tickers.push(ticker);
        this._renderTicker(ticker);
        if ($('#ticker_list').outerHeight() >= window.innerHeight * 0.5) {
            $('#ticker_list').addClass('masked');
        } else {
            $('#ticker_list').removeClass('masked');
        }
    },

    removeTicker: function(ticker) {
        const index = this.options.tickers.findIndex(t => t.ticker === ticker.ticker);
        if (index !== -1) {
            this.options.tickers.splice(index, 1);
            this._refresh();
        }
    },

    export: function() {
        const tickers = []
        $.each(this.options.tickers, (index, ticker) => {
            tickers.push(ticker.ticker);
        });
        console.log(tickers);
    
        const xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/build-model/save", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify(tickers.sort()));
    }
});

$('#ticker_list').tickers();


