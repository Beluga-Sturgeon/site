async function updatevals() {
    // Generate placeholder values for demonstration purposes
    dictionary = (await httpGet("https://financialmodelingprep.com/api/v3/quote-short/" + document.URL.split("/").pop() + "?apikey=b0446da02c01a0943a01730dc2343e34"));
    var newChange = dictionary[0].price;
    var newMarketStatus = (await httpGet("/getChangestr/" + document.URL.split("/").pop()));

    // Update the change and market status elements
    $(".change").text(newChange);
    $(".market-status").text(newMarketStatus);
}

// Call the function initially
await updatevals();

// Set up the interval to call the function every minute
setInterval(await updatevals, 60000); // 60000 milliseconds = 1 

console.log("UPDATEEEE")


window.onload = function() {
    console.log("I AM READING THE SCRIPT");
   document.getElementById('bodytext').innerHTML = "I AM READING THE SCRIPT";
};