async function updatevals() {
    try {
      // Generate placeholder values for demonstration purposes
      const quoteData = await httpGet("https://financialmodelingprep.com/api/v3/quote-short/" + document.URL.split("/").pop() + "?apikey=b0446da02c01a0943a01730dc2343e34");
      const newChange = quoteData[0].price;
      const newMarketStatus = await httpGet("/getChangestr/" + document.URL.split("/").pop());
  
      // Update the change and market status elements
      $(".change").text(newChange);
      $(".market-status").text(newMarketStatus);
    } catch (error) {
      console.error('Error updating values:', error);
    }
  }
  
async function updateLoop() {
    await updatevals();
    setTimeout(updateLoop, 60000); // 60000 milliseconds = 1 minute
}

console.log("UPDATEEEE");

window.onload = function () {
    console.log("I AM READING THE SCRIPT");
    document.getElementById('bodytext').innerHTML = "I AM READING THE SCRIPT";
    updateLoop(); // Start the update loop after the page loads
};
