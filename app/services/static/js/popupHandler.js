class possibleActions 
{
    static CHARTS = 0
    static INCOME_STATEMENT = 1
    static BALANCE_SHEET = 2
    static CASH_FLOW = 3
    static NEWS = 4
}

class constants
{
    static API_URL = document.URL
}

function closeThePopup() {
    let popup = document.getElementById("popup");
    $(popup).toggleClass("hidden");
    toggleBackground()
}   

async function openThePopup(action, tab) {
    Array.from(document.getElementById("tab_bar").children).forEach( x => x.classList.remove("selected_tab"))
    tab.classList.add("selected_tab")
    Array.from(document.getElementById("window").children).forEach( x => x.classList.add("hidden"))

    let popup = document.getElementById("main_table")
    let dictionary
    let titleStr
    if (action == 0)
    {
        document.getElementById("charts").classList.remove("hidden")
    }
    else if (action == 1)
    {
        dictionary = await getIncomeStatement()
    } else if (action == 2)
    {
        dictionary = await getBalanceSheet()
    } else if (action == 3)
    {
        dictionary = await getCashFlow()
    }
    if (action == 4)
    {
        document.getElementById("news").classList.remove("hidden")
    }

    if (action == 1 || action == 2 || action == 3)
    {
        document.getElementById("main_table").classList.remove("hidden")
        console.log("THIS IS THE DICTIONARY BELOW:")
        console.log(dictionary)
        let table = popup.getElementsByTagName("table")[0];
        let tbody = table.getElementsByTagName("tbody")[0];
        while (tbody.firstChild)
        {
            tbody.removeChild(tbody.firstChild);
        }
        tbody.appendChild(createTableRow("(USD)", "Value", "Y/Y change", true));

        for (const property in dictionary)
        {
            tbody.appendChild(
                createTableRow(
                    property,
                    dictionary[property].value,
                    dictionary[property].change
                )
            )
        }
        console.log(tbody)
        changeColor()
    }
}


function createTableRow(label, value, change, isHeader=false)
{
    let row = document.createElement("tr");
    let labelElement = document.createElement("td");
    labelElement.classList.add("label")
    labelElement.appendChild(document.createTextNode(label));
    let valueElement = document.createElement("td");
    valueElement.appendChild(document.createTextNode(value));
    let changeElement = document.createElement("td");
    changeElement.appendChild(document.createTextNode(change));
    if (!isHeader)
    {
       changeElement.classList.add("change")
    }
    row.appendChild(labelElement)
    row.appendChild(valueElement)
    row.appendChild(changeElement)
    return row
}

async function httpGet(urlAddOon)
{
    urllist = document.URL.split("/");
    const response = await fetch(urllist.slice(0, urllist.length - 2).join("/") + urlAddOon);
    const data = await response.json();
    return data
}


function human_format(num) {
    num = parseFloat(num.toPrecision(3));
    var magnitude = 0;
  
    while (Math.abs(num) >= 1000) {
      magnitude++;
      num /= 1000.0;
    }
  
    return num.toFixed(2).replace(/\.00$/, '') + ['', 'K', 'M', 'B', 'T'][magnitude];
  }

async function getBalanceSheet() {
    balanceSheet = fetchData("balance-sheet-statement");
    return balanceSheet;
}

async function getCashFlow(){
    cashFlowStatement = fetchData("cash-flow-statement");
    return cashFlowStatement;
}

async function getIncomeStatement(){
    incomestatement = fetchData("income-statement");
    return incomestatement;
}


async function fetchData(dataCategory){
    url = "https://financialmodelingprep.com/api/v3/";
    url += dataCategory;
    url += "/"
    data = await fetch(url + document.URL.split("/").pop() + "?period=quarter&limit=120&apikey=b0446da02c01a0943a01730dc2343e34")
    data = await data.json()
    try {
        var latest = data[data.length - 1];
        var older = data[data.length - 2];
      } 
    catch {
        var latest = data[data.length - 1];
        var older = data[data.length - 1];
      }
      
    var output = {};
    
    for (var key in latest) {
        var newAmount = latest[key];
        var oldAmount = older[key];
        
        try {
            var change = ((newAmount - oldAmount) / oldAmount) * 100;
            console.log(change)
            if (!isNaN(change)) {
                var formattedChange = change > 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`;
                var formattedValue = human_format(newAmount);
                output[key] = {
                value: formattedValue,
                change: formattedChange,
                };
    
            }
        } catch (error) {
            // Handle errors if necessary
            console.error('Error updating values:', error);
        }
    }
    return output 
}

console.log(createTableRow("USD", "VALUE", "Y/Y CHANGE"))