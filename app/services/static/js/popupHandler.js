class possibleActions 
{
    static INCOME_STATEMENT = 0
    static BALANCE_SHEET = 1
    static CASH_FLOW = 2
}

class constants
{
    static API_URL = document.URL
}

function toggleBackground() {
    let background = document.getElementById("background")
    $(background).toggleClass("hidden")
}

function closeThePopup() {
    let popup = document.getElementById("popup");
    $(popup).toggleClass("hidden");
    toggleBackground()
}   

async function openThePopup(action) {
    toggleBackground()
    let popup = document.getElementById("popup");
    $(popup).toggleClass("hidden");
    let dictionary
    let titleStr
    if (action == 0)
    {
        dictionary = (await httpGet("/getFinancials/" + document.URL.split("/").pop())).incomeStatement;
        titleStr = "Income Statement"
    } else if (action == 1)
    {
        dictionary = (await httpGet("/getFinancials/" + document.URL.split("/").pop())).balanceSheet;
        titleStr = "Balance Sheet"
    }
    else
    {
        dictionary = (await httpGet("/getFinancials/" + document.URL.split("/").pop())).cashFlow;
        titleStr = "Cash Flow"
    }
    console.log("THIS IS THE DICTIONARY BELOW:")
    console.log(dictionary)

    let title = popup.getElementsByTagName("h3")[0];
    title.removeChild(title.firstChild)
    title.appendChild(document.createTextNode(titleStr))
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

console.log(createTableRow("USD", "VALUE", "Y/Y CHANGE"))