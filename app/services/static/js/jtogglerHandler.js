function swapStyleSheet(dominantColor, index) {
    console.log(dominantColor);
    if (index == 0) {
        document.getElementById("pageStyle").setAttribute('href', "/static/styles/lightDataStyles.css");
        document.body.setAttribute('style', "background:linear-gradient(157deg, #ffffff 0%, rgb" + dominantColor + " 180%);");
    } else if (index == 1) {
        document.getElementById("pageStyle").setAttribute('href', '/static/styles/blueDataStyles.css');
        document.body.setAttribute('style', "background:linear-gradient(157deg, #001e30 0%, rgb" + dominantColor + " 180%);");
    } else {
        document.getElementById("pageStyle").setAttribute('href', '/static/styles/blueDataStyles.css');
        document.body.setAttribute('style', "background:linear-gradient(157deg, #000000 0%, rgb" + dominantColor + " 180%);");
    }
}