const suggestionsContainer = document.getElementById("suggestions");
const searchInput = document.getElementById("search");
const searchForm = document.getElementById("searchForm");

async function fetchSuggestions(query) {
    const response = await fetch(`https://financialmodelingprep.com/api/v3/search?query=${query}&limit=10&exchange=NASDAQ&apikey=b0446da02c01a0943a01730dc2343e34`);
    const data = await response.json();
    return data;
}

function showSuggestions(query) {
    fetchSuggestions(query)
        .then(suggestions => {
            suggestionsContainer.innerHTML = "";

            suggestions.forEach(suggestion => {
                const suggestionElement = document.createElement("div");
                suggestionElement.classList.add("suggestion");
                suggestionElement.innerHTML = `
                    <div class="symbol">${suggestion.symbol}</div>
                    <div class="name">${suggestion.name}</div>
                    <div class="exchange">${suggestion.exchangeShortName}</div>
                `;

                suggestionElement.addEventListener("click", () => {
                    searchInput.value = suggestion.symbol;
                    suggestionsContainer.innerHTML = "";
                    searchForm.requestSubmit();
                });

                suggestionsContainer.appendChild(suggestionElement);
            });
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

searchInput.addEventListener("input", () => {
    const query = searchInput.value;
    if (query) {
        showSuggestions(query);
    } else {
        suggestionsContainer.innerHTML = "";
    }
});

// Close suggestions when clicking outside
window.addEventListener("click", event => {
    if (!suggestionsContainer.contains(event.target) && event.target !== searchInput) {
        suggestionsContainer.innerHTML = "";
    }
});


function handleSearchSubmit() {
    const query = searchInput.value;
    if (query) {
        fetchSuggestions(query)
            .then(suggestions => {
                if (suggestions.length === 0) {
                    showInvalidTickerMessage(query);
                } else {
                    const highestSuggestion = suggestions[0];
                    window.location.href = `/data/${highestSuggestion.symbol}`;
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    } else {
        showInvalidTickerMessage("");
    }
}

function showInvalidTickerMessage(query) {
    suggestionsContainer.innerHTML = "";
    const invalidMessage = document.createElement("div");
    invalidMessage.classList.add("suggestion");
    invalidMessage.textContent = `${query} is not a valid ticker!`;

    suggestionsContainer.appendChild(invalidMessage);
}